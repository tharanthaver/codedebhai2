import anthropic
import os

# Get API key from environment variable
API_KEY = os.getenv('ANTHROPIC_API_KEY')

if not API_KEY:
    raise ValueError("ANTHROPIC_API_KEY environment variable is required")

# Initialize Claude client
client = anthropic.Anthropic(api_key=API_KEY)

def test_claude_3_5():
    prompt = "Write a Python function to check if a number is prime."

    try:
        response = client.messages.create(
            model="claude-3-5-sonnet-20240229",  # official Claude 3.5 model ID
            max_tokens=300,
            temperature=0.2,
            messages=[
                {"role": "user", "content": prompt}
            ]
        )

        print("✅ Claude 3.5 Sonnet Response:")
        print(response.content[0].text.strip())

    except Exception as e:
        print("❌ Error:", str(e))

if __name__ == "__main__":
    test_claude_3_5()
