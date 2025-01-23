## Overview
The rag_chat folder contains scripts and configurations for setting up and running a Retrieval-Augmented Generation (RAG) chat application. This application leverages Weaviate for vector storage and retrieval, and integrates with Datadog for observability.

## Folder Structure
weaviate_vector_db/: Contains scripts for setting up and interacting with the Weaviate vector database.
chunk_and_load.py: Script to clone a repository, parse documents, chunk them, and load them into Weaviate.
.env: Environment variables configuration file.

## Prerequisites
Python 3.12 or higher
Weaviate instance running locally or remotely
Datadog account and API key
OpenAI API key

## Usage
1. Run the chunk_and_load.py script

This script clones the Datadog documentation repository, parses the documents, chunks them, and loads them into Weaviate.

2. Run the rag_chat.py script


## Observability
The application integrates with Datadog for observability. Ensure that the DD_API_KEY environment variable is set in the .env file.

## Contact

For any questions or inquiries, please contact Ryan Richards at ryan.richards95@gmail.com
