import json
import os
from langchain.llms import OpenAI
from langchain.vectorstores import Weaviate
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate
from ddtrace import patch, tracer
from ddtrace.llmobs import LLMObs
import weaviate
from dotenv import load_dotenv

def initialize_observability():
    """
    Enables Datadog observability for LLMs and LangChain using environment variables.
    """
    LLMObs.enable(
        ml_app="rag_chat",
        api_key=os.getenv("DD_API_KEY"),
        site="datadoghq.com",
        agentless_enabled=True,
        integrations_enabled=True
    )

def initialize_weaviate():
    """
    Initializes Weaviate client and sets up the vector store.
    """
    client = weaviate.Client(
        url=os.getenv("WEAVIATE_URL"),
        additional_headers={
            "X-OpenAI-Api-Key": os.getenv("OPENAI_API_KEY")  # Pass the OpenAI API key for embedding
        }
    )
    return Weaviate(client, OpenAIEmbeddings())

def create_retrieval_qa(llm, retriever):
    """
    Creates a Retrieval-QA chain using LangChain.
    """
    prompt_template = """
    Use the context below to answer the question. If the context is not helpful, state "I don't know."

    Context:
    {context}

    Question:
    {question}

    Answer:"""
    prompt = PromptTemplate(template=prompt_template, input_variables=["context", "question"])

    # Create a RetrievalQA chain
    return RetrievalQA.from_chain_type(
        llm=llm,
        retriever=retriever,
        chain_type_kwargs={"prompt": prompt},
    )

def main():
    """
    Main function to handle the multi-turn chat interaction with the LLM.
    """
    # Load the .env file
    load_dotenv()

    # Initialize observability
    initialize_observability()

    # Configure OpenAI LLM
    llm = OpenAI(openai_api_key=os.getenv("OPENAI_API_KEY"), temperature=0.5)

    # Initialize Weaviate
    weaviate_client = initialize_weaviate()

    # Create the Retrieval-QA chain
    qa_chain = create_retrieval_qa(llm, weaviate_client.as_retriever())

    print("Welcome to the Retrieval-Augmented Chat! Type 'exit' to quit.")

    while True:
        user_input = input("You: ")
        if user_input.lower() == "exit":
            print("Goodbye!")
            break

        # Run the question through the chain with observability
        with tracer.trace("langchain.chain.invoke", service="rag_system"):
            response = qa_chain.run(user_input)

        print(f"Assistant: {response}")

if __name__ == "__main__":
    main()
