import os
import glob
from git import Repo
from weaviate import Client
import weaviate
from weaviate.util import generate_uuid5
from dotenv import load_dotenv
from langchain.text_splitter import RecursiveCharacterTextSplitter
import frontmatter
import re

def clone_repo(repo_url, clone_path):
    """
    Clone a GitHub repository to a local directory.

    Args:
        repo_url (str): URL of the GitHub repository.
        clone_path (str): Local path to clone the repository.

    Returns:
        str: Path to the cloned repository.
    """
    if os.path.exists(clone_path):
        print(f"Repository already exists at {clone_path}. Pulling latest changes...")
        repo = Repo(clone_path)
        repo.remote().pull()
    else:
        print(f"Cloning repository from {repo_url} to {clone_path}...")
        Repo.clone_from(repo_url, clone_path)
    return clone_path

def load_documents_from_repo(repo_path):
    """
    Load all .md files from the specified repository path.

    Args:
        repo_path (str): Path to the local cloned repository.

    Returns:
        list: A list of tuples containing document content and filenames.
    """
    print(f"Loading documents from repository path: {repo_path}")
    documents = []
    for file_path in glob.glob(os.path.join(repo_path, "**", "*.md"), recursive=True):
        with open(file_path, "r", encoding="utf-8") as file:
            content = file.read()
            documents.append((content, os.path.basename(file_path)))
    print(f"Loaded {len(documents)} documents.")
    return documents

def parse_documents(documents):
    """
    Parse a list of markdown documents to extract title, description, and content.

    Args:
        documents (list): List of tuples containing document content and filenames.

    Returns:
        list: A list of dictionaries with extracted fields including title, description, and content.
    """
    print("Parsing documents...")
    parsed_documents = []
    for content, filename in documents:
        try:
            # Parse the frontmatter and content using `frontmatter.loads()`
            post = frontmatter.loads(content)
            
            # Extract title from frontmatter
            title = post.get("title", "Untitled")
            
            # Extract description (Overview section or first few lines)
            description_match = re.search(r"## Overview\n\n(.+?)(?:\n\n|$)", post.content, re.DOTALL)
            description = description_match.group(1).strip() if description_match else post.content[:200]  # Fallback to the first 200 chars
            
            parsed_documents.append({
                "title": title,
                "description": description,
                "content": post.content,
                "filename": filename
            })
        
        except Exception as e:
            print(f"Failed to parse document {filename}: {e}")
            continue

    print(f"Parsed {len(parsed_documents)} documents.")
    return parsed_documents



def main():
    """
    Main function to process documents and load them into Weaviate.
    """
    print("Loading environment variables...")
    load_dotenv()

    # Get the current script's directory
    script_dir = os.path.dirname(os.path.abspath(__file__))

    # Configuration
    repo_url = "https://github.com/DataDog/documentation.git"
    clone_path = os.path.join(script_dir, "documentation")
    specific_path = os.path.join(clone_path, "content/en")
    weaviate_url = os.getenv("WEAVIATE_URL")
    
    # Clone the repository and load documents
    clone_repo(repo_url, clone_path)
    documents = load_documents_from_repo(specific_path)
    parsed_documents = parse_documents(documents)

    # Example usage
    print("Example parsed document:")
    print(parsed_documents[0])

    print("Connecting to Weaviate...")
    client = weaviate.connect_to_local()

    try:
        # Work with the client here - e.g.:
        assert client.is_live()
        print("Connected to Weaviate.")
        pass

    finally:  # This will always be executed, even if an exception is raised
        client.close()  # Close the connection & release resources
        print("Closed connection to Weaviate.")

    # Optional: Delete cloned repository
    #shutil.rmtree(clone_path, ignore_errors=True)
    #print(f"Deleted local repository at {clone_path}.")

if __name__ == "__main__":
    main()
