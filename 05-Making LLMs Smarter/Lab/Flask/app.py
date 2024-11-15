from helpers import *
from flask import Flask, render_template, request

app = Flask(__name__)

# Home page
@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')

# REST method for invoking an LLM
@app.route('/assistant', methods=['get'])
def ask_assistant():
    try:
        input = request.args.get('input')
        messages = chat(input) # Call the LLM
        return messages[-1]['content']

    except Exception as e:
        return "I'm sorry, but something went wrong."
