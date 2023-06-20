import gradio as gr
import os
import json
import requests

# Streaming endpoint
API_URL = "https://api.openai.com/v1/chat/completions"  
# Global Variables Populated
system_msg = "You are a helpful assistant."
OPENAI_MODEL = "gpt-3.5-turbo"

chat_counter = 0


# Inferenec function
def predict(openai_gpt4_key, inputs, chat_counter, chatbot=[], history=[]):
    top_p = 1.0
    temperature = 1.0

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {openai_gpt4_key}",  # Users will provide their own OPENAI_API_KEY
    }

    initial_message = [
        {"role": "system", "content": "You are a helpful assistant."},
        {
            "role": "user",
            "content": "I need help formulating my Goals and Success Indicators. Can you help me with that?",
        },
        {
            "role": "assistant",
            "content": "Of course! To start, let's look at your overall goals or objective. What's the key goal you're aiming for in this period?",
        },
        {
            "role": "user",
            "content": "My key goal is to 'grow qualified customer leads to a new level', 'have customers switch from platform X to ours', and 'be more efficient and digital'.",
        },
        {
            "role": "assistant",
            "content": "Great! Let's form some measurable success indicators results for each goal or objective.",
        },
        {"role": "user", "content": f"{inputs}"},
    ]
    multi_turn_message = []
    messages_in_api_payload = []

    if chat_counter == 0:
        # payload = {
        #     "model": OPENAI_MODEL,
        #     "messages": initial_message,
        #     "temperature": 1.0,
        #     "top_p": 1.0,
        #     "n": 1,
        #     "stream": True,
        #     "presence_penalty": 0,
        #     "frequency_penalty": 0,
        # }
        messages_in_api_payload = initial_message
        print(f"chat_counter - {chat_counter}")
    else:  # if chat_counter != 0 :
        messages = multi_turn_message  # Of the type of - [{"role": "system", "content": system_msg},]
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
        messages_in_api_payload = messages
        # payload = {
        #     "model": OPENAI_MODEL,
        #     "messages": messages,  # Of the type of [{"role": "user", "content": f"{inputs}"}],
        #     "temperature": temperature,  # 1.0,
        #     "top_p": top_p,  # 1.0,
        #     "n": 1,
        #     "stream": True,
        #     "presence_penalty": 0,
        #     "frequency_penalty": 0,
        # }

    payload = {
        "model": OPENAI_MODEL,
        "messages": messages_in_api_payload,  # Of the type of [{"role": "user", "content": f"{inputs}"}],
        "temperature": temperature,  # 1.0,
        "top_p": top_p,  # 1.0,
        "n": 1,
        "stream": True,
        "presence_penalty": 0,
        "frequency_penalty": 0,
    }
    
    chat_counter += 1

    history.append(inputs)
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

    counter = 0
    for chunk in response.iter_lines():
        # Skipping first chunk
        if counter == 0:
            counter += 1
            continue
        # check whether each line is non-empty
        if chunk.decode():
            chunk = chunk.decode()
            # decode each line as response data is in bytes
            if (
                len(chunk) > 12
                and "content" in json.loads(chunk[6:])["choices"][0]["delta"]
            ):
                partial_words = (
                    partial_words
                    + json.loads(chunk[6:])["choices"][0]["delta"]["content"]
                )
                if token_counter == 0:
                    history.append(" " + partial_words)
                else:
                    history[-1] = partial_words
                chat = [
                    (history[i], history[i + 1]) for i in range(0, len(history) - 1, 2)
                ]  # convert to tuples of list
                token_counter += 1
                #   yield chat, history, chat_counter, response  # resembles {chatbot: chat, state: history}
                yield chat, history, chat_counter, status  # resembles {chatbot: chat, state: history}


# Resetting to blank
def reset_textbox():
    return gr.update(value="")


# to set a component as visible=False
def set_visible_false():
    return gr.update(visible=False)


# to set a component as visible=True
def set_visible_true():
    return gr.update(visible=True)


title = """<h1 align="center">
Welcome to Goals and Success Indicators Assistance Tool!</h1>
<h2>
This tool is designed to help you refine your Goals and Success Indicators.
'Goals' define what we aim to achieve and 'Success Indicators' are measurable ways to track the progress towards these goals.
By providing your Goals and Success Indicators, the tool will provide feedback and suggestions on how to make them more effective."
</h2>"""
# display message for themes feature
theme_addon_msg = """
<h2>
When submitting your goals and success indicators draft for review: <br>
    1. Detail Your Goals and Success Indicators: More context helps generate better feedback.<br>
    2. Clarify Your Request: If you seek specific guidance, like making your success indicators more quantifiable or aligning them with certain objectives, you can specify.<br>
</h2>
"""

# Modifying existing Gradio Theme
theme = gr.themes.Soft(
    primary_hue="zinc",
    secondary_hue="green",
    neutral_hue="green",
    text_size=gr.themes.sizes.text_lg,
)

with gr.Blocks(
    css="""#col_container { margin-left: auto; margin-right: auto;} #chatbot {height: 520px; overflow: auto;} footer {visibility: hidden}""",
    title="Goals and Success Assistance Tool"
) as demo:
    gr.HTML(title)
    gr.HTML(theme_addon_msg)

    with gr.Column(elem_id="col_container"):
        # Users need to provide their own OpenAI API key, it is no longer provided by Huggingface
        with gr.Row():
            openai_gpt4_key = gr.Textbox(
                label="OpenAI Key",
                value="",
                type="password",
                placeholder="sk..",
                info="""
            You can follow these guidelines to collect your API key here - https://tinyurl.com/5y49xfyy
            """,
            )

    with gr.Column(elem_id="col_container"):
        chatbot = gr.Chatbot(label="GPT4", elem_id="chatbot")
        with gr.Row():
            inputs = gr.Textbox(
                value="",
                label="Enter your Goals and Success indicators",
                info="""
            In order to get suggestions, submit your Goals and Success with clarity
            """,
            )
        state = gr.State([])
        with gr.Row():
            with gr.Column(scale=7):
                b1 = gr.Button().style(full_width=True)
            with gr.Column(scale=3):
                server_status_code = gr.Textbox(
                    label="Status code from OpenAI server",
                )

        chat_counter = gr.Number(value=0, visible=False, precision=0)

    # Event handling
    inputs.submit(
        predict,
        [openai_gpt4_key, inputs, chat_counter, chatbot, state],
        [chatbot, state, chat_counter, server_status_code],
    )  # openai_api_key
    b1.click(
        predict,
        [openai_gpt4_key, inputs, chat_counter, chatbot, state],
        [chatbot, state, chat_counter, server_status_code],
    )  # openai_api_key

    b1.click(reset_textbox, [], [inputs])
    inputs.submit(reset_textbox, [], [inputs])

demo.queue().launch(server_name="0.0.0.0", server_port=8000, debug=True, show_api=False)
