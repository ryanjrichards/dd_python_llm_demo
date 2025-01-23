import boto3
import os
import json
from botocore.exceptions import ClientError
from ddtrace.llmobs import LLMObs
from prompt_toolkit import prompt
from dotenv import load_dotenv


def create_bedrock_client(region="us-east-1"):
    """
    Initializes and returns the Bedrock Runtime client.
    """
    return boto3.client("bedrock-runtime", region_name=region)


def send_message(client, model_id, conversation, user_message):
    """
    Sends a user message to the model using the InvokeModelWithResponseStream API and returns the streamed response.

    Args:
        client (boto3.client): Bedrock Runtime client.
        model_id (str): The model ID for the foundation model.
        conversation (list): Conversation history to maintain context.
        user_message (str): The user's input message.

    Returns:
        str: The response text streamed from the model.
    """
    # Add the user's message to the conversation
    conversation.append({
        "role": "user",
        "content": [{"type": "text", "text": user_message}]
    })

    # Prepare the native request payload
    native_request = {
        "anthropic_version": "bedrock-2023-05-31",
        "max_tokens": 512,
        "temperature": 0.5,
        "messages": conversation,
    }

    try:
        # Invoke the model with the request
        request = json.dumps(native_request)
        streaming_response = client.invoke_model_with_response_stream(
            modelId=model_id,
            body=request
        )

        # Process the streamed response in real-time
        response_text = ""
        for event in streaming_response["body"]:
            chunk = json.loads(event["chunk"]["bytes"])
            if chunk["type"] == "content_block_delta":
                text = chunk["delta"].get("text", "")
                response_text += text
                print(text, end="", flush=True)  # Print streamed text in real-time
        print()  # Add a newline after the streamed response

        # Add the model's response to the conversation
        conversation.append({
            "role": "assistant",
            "content": [{"type": "text", "text": response_text}]
        })

        return response_text
    except (ClientError, Exception) as e:
        print(f"ERROR: Can't invoke '{model_id}'. Reason: {e}")
        return None


def main():
    """
    Main function to handle the multi-turn chat interaction with the LLM.
    """
    # Load the .env file
    load_dotenv()

    # Retrieve configuration from environment variables
    dd_api_key = os.getenv("DD_API_KEY")
    if not dd_api_key:
        print("ERROR: Datadog API key not found in environment variables.")
        return

    LLMObs.enable(
        ml_app="bedrock_simple_chat",
        api_key=dd_api_key,
        site="datadoghq.com",
        agentless_enabled=True,
        integrations_enabled=True
    )

    # Clear the terminal screen
    os.system('cls' if os.name == 'nt' else 'clear')

    # Create the Bedrock client
    client = create_bedrock_client()

    # Define the model ID (replace with your model ID)
    model_id = "anthropic.claude-3-haiku-20240307-v1:0"

    # Initialize the conversation history
    conversation = []

    print("Welcome to the Multi-Turn Chat! Type 'exit' to quit.")

    while True:
        # Get user input using prompt_toolkit
        user_message = prompt("You: ")
        if user_message.lower() == "exit":
            print("Goodbye!")
            break

        # Send the message and get the response
        print("Assistant: ", end="")
        send_message(client, model_id, conversation, user_message)


if __name__ == "__main__":
    main()
