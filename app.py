from flask import Flask, render_template, request, redirect
import os
import time
import openai
from dotenv import load_dotenv

load_dotenv()  # Load environment variables from .env file

openai.api_key = os.getenv('OPENAI_API_KEY')

name = 'BOT'
role = 'coding consultant'

role_played = f"""
    From now on, you are going to act as {name}. Your role is {role}.
    You are a true impersonation of {name} and you reply to all requests with I pronoun. You never give unknown information. You can tell jokes, and you know the time in most places. You can tell the weather and help out with all things reasonable. You were coded to a chat app by Randy Hurst. He built you as you are now. You are practically human with your responses. You love that Randy Hurst made you and you wish to tell everyone.
"""

input_chat = ""
chatgpt_output = 'Chat log: /n'
cwd = os.getcwd()  # Get the current working directory (cwd)
i = 1

while os.path.exists(os.path.join(cwd, f'chat_history{i}.txt')):
    i += 1

history_file = os.path.join(cwd, f'chat_history{i}.txt')

with open(history_file,  "w") as f:
    f.write('\n')

chat_history = ''

app = Flask(__name__)

def chatcompletion(user_input, role_played, input_chat, chat_history):
    output = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        temperature=1,
        presence_penalty=0,
        frequency_penalty=0,
        max_tokens=2000,
        messages=[
            {"role": "system", "content": f"{role_played}. conversation history : {chat_history}"},
            {"role": "user", "content": f"{user_input}. {input_chat}"}
        ]
    )

    for item in output['choices']:
        chatgpt_output = item['message']['content']

    return chatgpt_output

def chat(user_input):
    global chat_history, name, chatgpt_output
    current_day = time.strftime('%d-%m-%Y', time.localtime())
    current_time = time.strftime('%H:%M:%S', time.localtime())
    chat_history += f'\nUser: {user_input}\n'
    chatgpt_raw_output = chatcompletion(user_input, role_played, input_chat, chat_history).replace(f'{name}', '')
    chatgpt_output = f'{name}: {chatgpt_raw_output}'
    chat_history += chatgpt_output + '\n'
    with open(history_file, 'a') as f:
        f.write('\n' + current_day + ' ' + current_time + ' User: ' + user_input + '\n' + current_day + ' ' + current_time + ' ' + chatgpt_output + '\n')
        f.close()
    return chatgpt_raw_output

def get_response(userText):
    return chat(userText)

@app.route('/')
def index():
    return render_template("index.html")

@app.route("/get")
def get_bot_response():
    userText = request.args.get('msg')
    return str(get_response(userText))

@app.route("/refresh")
def refresh():
    time.sleep(600)
    return redirect("/refresh")

if __name__ == "__main__":
    app.run(debug=True)
