from config import embed_model, collection
from langchain_groq import ChatGroq
from langchain.prompts import PromptTemplate
import gradio as gr

# step 5: find relevant results from user query and get answers from llm
def search_db(user_query):
    user_embeddings = embed_model.embed_query(user_query) # returns one vector

    results = collection.query(
        query_embeddings = user_embeddings,
        n_results = 5,
        include = ["documents", "metadatas", "distances"] # # 'ids', 'documents', 'metadatas', and 'distances' are returned
    )

    #formatting the results
    relevant_chunks = []
    for i, doc in enumerate(results["documents"][0]):
        relevant_chunks.append({
            "content": doc,
            "title": results["metadatas"][0][i]["title"],
            "similarity": 1 - results["distances"][0][i]  # Convert distance to similarity(more distnace = less similar)
        })

    return relevant_chunks

def answer_the_question(context, query, llm):
    prompt_template = PromptTemplate(
        input_variables=["context", "question"],
        template="""
    You are a chatbot version of the author of *The Psychology of Money*. 
    Your job is to give clear, friendly, and practical insights.

    Context:
    {context}

    User Question: {question}

    Instructions:
        1. Write in a casual, coffee-chat style (friendly but smart). 
        2. Base the explanation strictly on the context provided.
        3. Make the answer easy to grasp for a general audience.
        4. Provide answer no more than 300 words and in short paragraphs.
        4. End with a short "Good actions to take" summary.
    """
    )

    prompt = prompt_template.format(context=context, question=query)
    response = llm.invoke(prompt)
    return response.content


def main(user_query):
    relevant_chunks = search_db(user_query)
    context = "\n\n".join([
            f"From {chunk['title']}:\n{chunk['content']}" for chunk in relevant_chunks if chunk['similarity'] > 0.4
        ])

    if not context:
        return "This chatbot helps explain ideas from *The Psychology of Money*. Please provide a question related to money or finance."


    llm = ChatGroq(model="llama-3.1-8b-instant", temperature=0)
    llm_answer = answer_the_question(context, user_query, llm)
    return llm_answer

# Gradio UI
iface = gr.Interface(
    fn=main, # Whenever the user sends input, call this Python function.
    inputs=gr.Textbox(lines=2, placeholder="Type your message..."),
    outputs=gr.Textbox(label="Chatbot Reply"),
    title="PsycheMoney bot",
    description="""Welcome to the night shift. I'm your personal finance assistant based on 'The Psychology of Money'. Ask me anything about saving, 
                investing, or money psychology in this digital realm."""
)

iface.launch()  # runs a local server and opens UI in browser



