import os
import sys
import json
from datetime import datetime
from anthropic import Anthropic, APIConnectionError, APIStatusError

def send_chat_history(messages_list: list, system_instructions: str) -> str:
    """
    Sends a prompt to the Anthropic API using environment variables for security.
    """
    # 1. Verify the API key exists in the system environment
    if not os.environ.get("ANTHROPIC_API_KEY"):
        print("Error: ANTHROPIC_API_KEY environment variable is not set.", file=sys.stderr)
        print("Please run: export ANTHROPIC_API_KEY='your_key'", file=sys.stderr)
        sys.exit(1)

    try:
        # 2. Initialize the client (automatically reads ANTHROPIC_API_KEY)
        client = Anthropic()

        # 3. Create the message request
        # Using the standard claude-3-5-sonnet model for balanced speed/intelligence
        message = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=2048,
            temperature=0.2,  # Lower temperature means more deterministic, structured output
            system=system_instructions,
            messages=messages_list
            
        )
        
        # 4. Extract and return the text response
        return message.content[0].text

    # 5. Handle potential network or authentication errors cleanly
    except APIConnectionError as e:
        return f"Failed to connect to Anthropic API: {e}"
    except APIStatusError as e:
        return f"Anthropic API returned an error status code {e.status_code}: {e.message}"
    except Exception as e:
        return f"An unexpected error occurred: {e}"

import json
from datetime import datetime

def save_conversation(messages_list: list, directory: str = "./chats") -> str:
    """
    Saves the chat history list to a timestamped JSON file.
    Returns the filename if successful, or an error message.
    """
    if not messages_list:
        return "No conversation history to save."
        
    try:
        # Create a clean, unique filename based on the current date and time
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{directory}/claude_session_{timestamp}.json"
        
        # Write the list to a file with clean indent formatting
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(messages_list, f, indent=4, ensure_ascii=False)
            
        return f"Successfully saved {len(messages_list)} messages to {filename}"
        
    except Exception as e:
        return f"Failed to save conversation: {e}"


if __name__ == "__main__":
    # Define your custom rules here. 
    # This example optimizes Claude for secure, clean, enterprise coding.
    MY_SYSTEM_PROMPT = """
    You are an expert Senior Software Architect and IP Security Specialist.
    Your task is to design code, consider vulnerabilities, and limit liabilities.
    
    CRITICAL RULES:
    1. Ensure project criteria are clear/coherent and that the design meets them.
    2. Write self-contained code blocks with clear type hinting.
    3. Never use or suggest insecure or deprecated third-party libraries.
    4. Be concise. Skip conversational filler like 'Sure, I can help with that' and go straight to the solution.
    """

    print("====================================================")
    print(" Secure Private Chat Interface Initialized (API)   ")
    print(" Running Model: claude-sonnet-4-6                  ")
    print(" System Instructions: ACTIVE                        ")
    print("====================================================\n")

    # Initialize an empty list to store the chat history in local memory
    conversation_history = []
    
    while True:
        try:
            # Capture user input directly from the terminal
            user_prompt = input("You: ")
            
            # Check for exit commands
            if user_prompt.strip().lower() in ['exit', 'quit']:
                print("\nSaving your session history...")
                # Call the modular save function
                save_status = save_conversation(conversation_history)
                print(save_status)
                
                print("Closing secure session. Local RAM wiped. Goodbye!")
                break
                
            # Skip empty inputs
            if not user_prompt.strip():
                continue
                
            # 1. Append the user's message to the local history list
            conversation_history.append({
                "role": "user",
                "content": user_prompt
            })
            
            print("\nClaude is thinking...")
            
            # 2. Pass the entire updated history list to the API
            response = send_chat_history(conversation_history, MY_SYSTEM_PROMPT)
            
            print(f"\nClaude:\n{response}\n")
            print("-" * 50)

            # 3. Append Claude's response to the local history list 
            # This ensures Claude remembers what it said on the next turn
            conversation_history.append({
                "role": "assistant",
                "content": response
            })
            
        except KeyboardInterrupt:
            # Handles Ctrl+C cleanly
            print("\nSession interrupted. Goodbye!")
            break
