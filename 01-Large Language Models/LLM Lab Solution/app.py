from helpers import *
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

        # Score the candidate 10 times, drop the highest and lowest
        # scores, and average the rest
        scores = []

        for i in range(10):
            score = score_candidate(candidate, job)
            scores.append(score)
            print(score)

        scores = sorted(scores)[1:-1] # Remove the highest and lowest scores
        final_score = sum(scores) / len(scores) # Average the remaining scores

        # Generate an explanation of the final score
        chunks = explain_score(candidate, job, final_score)

        # Stream the response
        return Response(stream_with_context(generate(final_score, chunks)))

    except Exception as e:
        return Response(stream_with_context("I'm sorry, but something went wrong."))

# Generator for streaming output
def generate(score, chunks):
    yield f'[[[{score:.1f}]]]'

    for chunk in chunks:
        text = chunk.choices[0].delta.content
        if text is not None:
            yield text
