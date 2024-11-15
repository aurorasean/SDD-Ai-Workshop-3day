import os, chromadb
from openai import OpenAI
from flask import Flask, render_template, request, Response, stream_with_context
from sentence_transformers import CrossEncoder

app = Flask(__name__)

# Load the vector database
client = chromadb.PersistentClient('chroma')
collection = client.get_collection(name='Electric_Vehicles')

# Load a cross encoder for reranking
reranker = CrossEncoder('jinaai/jina-reranker-v1-turbo-en', trust_remote_code=True)

@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')

@app.route('/answer', methods=['GET'])
def answer_question():
    question = request.args.get('query')

    if question is not None and len(question) > 0:
        # Query the vector store
        results = collection.query(
            query_texts=[question],
            n_results=10
        )

        # Use the cross encoder to identify the 5 best matches
        documents = results['documents'][0]
        ranked_documents = reranker.rank(question, documents, return_documents=True, top_k=5)
        context = '\n\n'.join(x['text'] for x in ranked_documents)        
		
        # Submit the question and the context to an LLM
        client = OpenAI()
		
        content = f'''
            Answer the following question using the provided context, and if the
            answer is not contained within the context, say "I don't know." Explain
            your answer if possible. Do not use markdown formatting in your output,
            and do not mention the context provided to you.
			
            Question:
            {question}

            Context:
            {context}
            '''
		
        messages = [{ 'role': 'user', 'content': content }]

        # Get the response
        response = client.chat.completions.create(
            model='gpt-4o',
            messages=messages,
            stream=True
        )

        return Response(stream_with_context(generate(response)))

def generate(chunks):
    for chunk in chunks:
        content = chunk.choices[0].delta.content
        if content is not None:
            yield content
