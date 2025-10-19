import anthropic
import os

# Get API key from environment variable
API_KEY = os.getenv('ANTHROPIC_API_KEY')

if not API_KEY:
    raise ValueError("ANTHROPIC_API_KEY environment variable is required")

def test_claude_api():
    # Initialize the client
    client = anthropic.Anthropic(api_key=API_KEY)
    
    try:
        # Make a request to Claude 3.5 Sonnet
        response = client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=1000,
            messages=[
                {
                    "role": "user",
                    "content": "give the code for factorial of 5 with no explanation"
                }
            ]
        )
        
        print("Claude's response:")
        print(response.content[0].text)
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_claude_api()
