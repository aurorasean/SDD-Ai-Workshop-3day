import ollama, re

def score_candidate(candidate, job):
    prompt = f'''
        Determine whether the job candidate described below is or is not a good fit for
        the job described in the job description. Consider factors such as how well the
        candidate's job experience and academic credentials match criteria specified in
        the job description, and whether the candidate's personality would be a good
        cultural fit. Then assign a score from 0.0 to 10.0 quantifying the candidate's
        fitness for the job. Return the numerical score without any other text preceding
        it or following it. For example, "8.5" is a legitimate return value. "8.5 out of
        10.0" is not. Be critical; make it difficult to earn a high score.

        [START DESCRIPTION OF JOB CANDIDATE]
        {candidate}
        [END DESCRIPTION OF JOB CANDIDATE]

        [START JOB DESCRIPTION]
        {job}
        [END JOB DESCRIPTION]
        '''

    messages = [
        {
            'role': 'system',
            'content': 'You are a hiring expert who matches job candidates to job descriptions',
        },
        {
            'role': 'user',
            'content': prompt
        }
    ]

    response = ollama.chat(
        model='llama3.2',
        messages=messages,
        options={ 'temperature': 0.2 }
    )

    result = response['message']['content']

    # Strip extraneous characters (if present) from the output
    # and return the score as a float
    pattern = r'\d+\.\d+'
    matches = re.findall(pattern, result)
    score = float(matches[0]) if matches else None
    return score

def explain_score(candidate, job, score):
    prompt = f'''
        Consider the job candidate described below and the job description that he
        or she is applying for. Explain why on a scale of 0.0 to 10.0, the candidate's
        fitness for the job is {score:.1f}. If appropriate, also suggest ways
        that the candidate could become a better fit for the job.

        [START DESCRIPTION OF JOB CANDIDATE]
        {candidate}
        [END DESCRIPTION OF JOB CANDIDATE]

        [START JOB DESCRIPTION]
        {job}
        [END JOB DESCRIPTION]
        '''

    messages = [
        {
            'role': 'system',
            'content': 'You are a hiring expert who matches job candidates to job descriptions',
        },
        {
            'role': 'user',
            'content': prompt
        }
    ]

    response = ollama.chat(
        model='llama3.2',
        messages=messages,
        stream=True
    )

    return response