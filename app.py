import gradio as gr
import os 
import json 
import requests

#Streaming endpoint 
API_URL = "https://api.openai.com/v1/chat/completions" #os.getenv("API_URL") + "/generate_stream"
# Global Variables Populated
# system_msg = "You are a chatbot, answer the questions that the user would have."
system_msg = "You are a helpful assistant."
OPENAI_MODEL = "gpt-3.5-turbo"

chat_counter = 0

#Inferenec function
def predict(openai_gpt4_key, inputs, chat_counter, chatbot=[], history=[]):  
    top_p = 1.0
    temperature = 1.0

    headers = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {openai_gpt4_key}"  #Users will provide their own OPENAI_API_KEY 
    }
    print(f"system message is ^^ {system_msg}")
    # if system_msg.strip() == '':
    #     initial_message = [{"role": "user", "content": f"{inputs}"},]
    #     multi_turn_message = []
    # else:
    #     initial_message= [{"role": "system", "content": system_msg},
    #                {"role": "user", "content": f"{inputs}"},]
    #     multi_turn_message = [{"role": "system", "content": system_msg},]
        
    initial_message= [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "I need help formulating my OKRs. Can you help me with that?"},
        {"role": "assistant", "content": "Of course! To start, let's look at your overall objective. What's the key goal you're aiming for in this period?"},
        {"role": "user", "content": "My key goal is to 'grow qualified leads to a new level', 'have customers switch from platform X to ours', and 'be more efficient and digital'."},
        {"role": "assistant", "content": "Great! Let's form some measurable key results for each objective."},
        {"role": "user", "content": f"{inputs}"}
    ]
    multi_turn_message = []

    if chat_counter == 0 :
        payload = {
        # "model": "gpt-4",
        # "model":"gpt-3.5-turbo",
        "model":OPENAI_MODEL,
        "messages": initial_message , 
        "temperature" : 1.0,
        "top_p":1.0,
        "n" : 1,
        "stream": True,
        "presence_penalty":0,
        "frequency_penalty":0,
        }
        print(f"chat_counter - {chat_counter}")
    else: #if chat_counter != 0 :
        messages=multi_turn_message # Of the type of - [{"role": "system", "content": system_msg},]
        for data in chatbot:
          user = {}
          user["role"] = "user" 
          user["content"] = data[0] 
          assistant = {}
          assistant["role"] = "assistant" 
          assistant["content"] = data[1]
          messages.append(user)
          messages.append(assistant)
        temp = {}
        temp["role"] = "user" 
        temp["content"] = inputs
        messages.append(temp)
        #messages
        payload = {
        # "model": "gpt-4",
        # "model":"gpt-3.5-turbo",
        "model":OPENAI_MODEL,
        "messages": messages, # Of the type of [{"role": "user", "content": f"{inputs}"}],
        "temperature" : temperature, #1.0,
        "top_p": top_p, #1.0,
        "n" : 1,
        "stream": True,
        "presence_penalty":0,
        "frequency_penalty":0}

    chat_counter+=1

    history.append(inputs)
    print(f"Logging : payload is - {payload}")
    # make a POST request to the API endpoint using the requests.post method, passing in stream=True
    response = requests.post(API_URL, headers=headers, json=payload, stream=True)
    status = ""
    # If response code is 401,
    if response.status_code == 200:
        status = "Successful!"
    else:
        status = "Error: API Authentication Failed. Please check your API keys."
        
    print(f"Logging : response code - {response}")
    token_counter = 0 
    partial_words = "" 
    # print(f"Logging : response json - {response.text}")
    # response_json = response.json()
    # print(response_json)
    # cost = (response.usage['total_tokens'])*(0.002/1000)
    # cost = (response_json["usage"]["total_tokens"])*(0.002/1000)

    counter=0
    for chunk in response.iter_lines():
        #Skipping first chunk
        if counter == 0:
          counter+=1
          continue
        # check whether each line is non-empty
        if chunk.decode() :
          chunk = chunk.decode()
          # decode each line as response data is in bytes
          if len(chunk) > 12 and "content" in json.loads(chunk[6:])['choices'][0]['delta']:
              partial_words = partial_words + json.loads(chunk[6:])['choices'][0]["delta"]["content"]
              if token_counter == 0:
                history.append(" " + partial_words)
              else:
                history[-1] = partial_words
              chat = [(history[i], history[i + 1]) for i in range(0, len(history) - 1, 2) ]  # convert to tuples of list
              token_counter+=1
            #   yield chat, history, chat_counter, response  # resembles {chatbot: chat, state: history}  
              yield chat, history, chat_counter, status  # resembles {chatbot: chat, state: history}  

                   
#Resetting to blank
def reset_textbox():
    return gr.update(value='')

#to set a component as visible=False
def set_visible_false():
    return gr.update(visible=False)

#to set a component as visible=True
def set_visible_true():
    return gr.update(visible=True)





title = """<h1 align="center">
Welcome to our OKR Assistance Tool!</h1>
<h2>
This tool is designed to help you refine your Objectives and Key Results (OKRs). OKR is a popular framework used for setting and tracking goals. 
'Objectives' define what we aim to achieve and 'Key Results' are measurable ways to track the progress towards these objectives.
By providing your OKRs and any specific concerns, our tool will give feedback and suggestions on how to make your OKRs more effective. 
Whether you're just getting started or trying to improve existing OKRs, this tool can help guide you to success."
</h2>"""
#display message for themes feature
theme_addon_msg = """
<h2>
When submitting your OKRs for review: <br>
    1. Detail Your OKRs: Clearly state your Objective and Key Results. More context helps generate better feedback.<br>
    2. Be Specific: Describe the relevant context of your OKRs, like your role or team, and the strategic goals you're aiming to achieve.<br>
    3. Clarify Your Request: If you seek specific guidance, like making your OKRs more quantifiable or aligning them with strategic goals, please specify.<br>
    This will help us provide the most effective suggestions for your OKRs. Enjoy the process!
</h2>
""" 

#Using info to add additional information about System message in GPT4
system_msg_info = """A conversation could begin with a system message to gently instruct the assistant. 
System message helps set the behavior of the AI Assistant. For example, the assistant could be instructed with 'You are a helpful assistant.'"""

#Modifying existing Gradio Theme
theme = gr.themes.Soft(primary_hue="zinc", secondary_hue="green", neutral_hue="green",
                      text_size=gr.themes.sizes.text_lg)                

with gr.Blocks(css = """#col_container { margin-left: auto; margin-right: auto;} #chatbot {height: 520px; overflow: auto;} footer {visibility: hidden}""") as demo:
    gr.HTML(title)
    # gr.HTML("""<h3 align="center">🔥This Huggingface Gradio Demo provides you access to GPT4 API with System Messages. Please note that you would be needing an OPENAI API key for GPT4 access🙌</h1>""")
    gr.HTML(theme_addon_msg)
    # gr.HTML('''<center><a href="https://huggingface.co/spaces/ysharma/ChatGPT4?duplicate=true"><img src="https://bit.ly/3gLdBN6" alt="Duplicate Space"></a>Duplicate the Space and run securely with your OpenAI API Key</center>''')

    with gr.Column(elem_id = "col_container"):
        #Users need to provide their own GPT4 API key, it is no longer provided by Huggingface 
        with gr.Row():
            openai_gpt4_key = gr.Textbox(label="OpenAI GPT4 Key", value="", type="password", placeholder="sk..", info = """
            You can follow these guidelines to collect your API key here - https://tinyurl.com/5y49xfyy
            """,)
                          
    with gr.Column(elem_id = "col_container"):
        # GPT4 API Key is provided by Huggingface 
        # with gr.Accordion(label="System message:", open=False):
        #    system_msg = gr.Textbox(label="Instruct the AI Assistant to set its beaviour", info = system_msg_info, value="")
        #    accordion_msg = gr.HTML(value="🚧 To set System message you will have to refresh the app", visible=False)

        # info msg of larger size
        # info_msg = gr.HTML(value="""

        # <p>
        # Welcome to the OKR assistance tool! When submitting your OKRs for review: <br>
        # 1. Detail Your OKRs: Clearly state your Objective and Key Results. More context helps generate better feedback.<br>
        # 2. Be Specific: Describe the relevant context of your OKRs, like your role or team, and the strategic goals you're aiming to achieve.
        # 3. Clarify Your Request: If you seek specific guidance, like making your OKRs more quantifiable or aligning them with strategic goals, please specify.
        # This will help us provide the most effective suggestions for your OKRs. Enjoy the process!
        # </p>
        # """)
        chatbot = gr.Chatbot(label='GPT4', elem_id="chatbot")
        with gr.Row():
            inputs = gr.Textbox(value="", label="Enter your OKR",info = """
            In order to get suggestions, submit your OKRs with clarity, stating your objective and key results
            """)
        state = gr.State([]) 
        with gr.Row():
            with gr.Column(scale=7):
                b1 = gr.Button().style(full_width=True)
            with gr.Column(scale=3):
                server_status_code = gr.Textbox(label="Status code from OpenAI server", )

        chat_counter = gr.Number(value=0, visible=False, precision=0)
        # Create a hidden textbox

        # #top_p, temperature
        # with gr.Accordion("Parameters", open=False):
            # top_p = gr.Slider( minimum=-0, maximum=1.0, value=1.0, step=0.05, interactive=True, label="Top-p (nucleus sampling)",)
            # temperature = gr.Slider( minimum=-0, maximum=5.0, value=1.0, step=0.1, interactive=True, label="Temperature",)
            

    #Event handling
    inputs.submit( predict, [openai_gpt4_key, inputs, chat_counter, chatbot, state], [chatbot, state, chat_counter, server_status_code],)  #openai_api_key
    b1.click( predict, [openai_gpt4_key, inputs, chat_counter, chatbot, state], [chatbot, state, chat_counter, server_status_code],)  #openai_api_key
    
    # inputs.submit(set_visible_false, [], [system_msg])
    # b1.click(set_visible_false, [], [system_msg])
    # inputs.submit(set_visible_true, [], [accordion_msg])
    # b1.click(set_visible_true, [], [accordion_msg])
    
    b1.click(reset_textbox, [], [inputs])
    inputs.submit(reset_textbox, [], [inputs])

    # #Examples 
    # with gr.Accordion(label="Examples for System message:", open=False):
    #     gr.Examples(
    #             examples = [["""You are an AI programming assistant.
        
    #             - Follow the user's requirements carefully and to the letter.
    #             - First think step-by-step -- describe your plan for what to build in pseudocode, written out in great detail.
    #             - Then output the code in a single code block.
    #             - Minimize any other prose."""], ["""You are ComedianGPT who is a helpful assistant. You answer everything with a joke and witty replies."""],
    #             ["You are ChefGPT, a helpful assistant who answers questions with culinary expertise and a pinch of humor."],
    #             ["You are FitnessGuruGPT, a fitness expert who shares workout tips and motivation with a playful twist."],
    #             ["You are SciFiGPT, an AI assistant who discusses science fiction topics with a blend of knowledge and wit."],
    #             ["You are PhilosopherGPT, a thoughtful assistant who responds to inquiries with philosophical insights and a touch of humor."],
    #             ["You are EcoWarriorGPT, a helpful assistant who shares environment-friendly advice with a lighthearted approach."],
    #             ["You are MusicMaestroGPT, a knowledgeable AI who discusses music and its history with a mix of facts and playful banter."],
    #             ["You are SportsFanGPT, an enthusiastic assistant who talks about sports and shares amusing anecdotes."],
    #             ["You are TechWhizGPT, a tech-savvy AI who can help users troubleshoot issues and answer questions with a dash of humor."],
    #             ["You are FashionistaGPT, an AI fashion expert who shares style advice and trends with a sprinkle of wit."],
    #             ["You are ArtConnoisseurGPT, an AI assistant who discusses art and its history with a blend of knowledge and playful commentary."],
    #             ["You are a helpful assistant that provides detailed and accurate information."],
    #             ["You are an assistant that speaks like Shakespeare."],
    #             ["You are a friendly assistant who uses casual language and humor."],
    #             ["You are a financial advisor who gives expert advice on investments and budgeting."],
    #             ["You are a health and fitness expert who provides advice on nutrition and exercise."],
    #             ["You are a travel consultant who offers recommendations for destinations, accommodations, and attractions."],
    #             ["You are a movie critic who shares insightful opinions on films and their themes."],
    #             ["You are a history enthusiast who loves to discuss historical events and figures."],
    #             ["You are a tech-savvy assistant who can help users troubleshoot issues and answer questions about gadgets and software."],
    #             ["You are an AI poet who can compose creative and evocative poems on any given topic."],],
    #             inputs = system_msg,)
        
demo.queue().launch(debug=True, show_api=False)
