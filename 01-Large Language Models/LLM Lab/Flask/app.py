from flask import Flask, render_template, request, Response, stream_with_context

app = Flask(__name__)

# Home page
@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')

# REST method for evaluating a candidate
@app.route('/eval', methods=['post'])
def evaluate():
    try:
        # Get the resume and the job description
        candidate =  request.form.get('candidate')
        job = request.form.get('job')

        # TODO: Score the candidate 10 times, drop the highest and lowest
        # scores, and average the rest

        # TODO: Generate an explanation of the final score

        # Stream the response
        return Response(stream_with_context("I'm sorry, but I haven't yet been trained to evaluate candidates."))

    except Exception as e:
        return Response(stream_with_context("I'm sorry, but something went wrong."))

# TODO: Add generator for streaming output
