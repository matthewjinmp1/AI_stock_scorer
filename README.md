# Grok LLM API Client

A Python program that integrates with xAI's Grok language model API, providing an easy-to-use interface for querying Grok models.

## Features

- Simple query interface for quick questions
- Conversational chat support with context
- Interactive mode for real-time conversations
- Support for multiple Grok models (grok-4-latest, grok-3-latest, grok-2-latest)
- Error handling for common API issues
- Environment variable configuration for security

## Prerequisites

- Python 3.7 or higher
- xAI API key (get one from [https://console.x.ai/](https://console.x.ai/))

## Installation

1. Clone or download this repository
2. Install the required dependencies:

```bash
pip install -r requirements.txt
```

## Configuration

### Option 1: Environment Variable (Recommended)

Set your xAI API key as an environment variable:

**On Windows:**
```cmd
set XAI_API_KEY=your_api_key_here
```

**On macOS/Linux:**
```bash
export XAI_API_KEY=your_api_key_here
```

### Option 2: Direct Configuration

You can also pass the API key directly when initializing the client:

```python
from grok_client import GrokClient

grok = GrokClient(api_key="your_api_key_here")
```

## Usage

### Basic Usage

Run the demo program:

```bash
python grok_client.py
```

This will run through several examples and then enter interactive mode.

### Programmatic Usage

```python
from grok_client import GrokClient

# Initialize the client
grok = GrokClient()

# Simple query
response = grok.simple_query("What is artificial intelligence?")
print(response)

# Conversational chat
conversation = [
    {"role": "user", "content": "Tell me about Python programming."},
    {"role": "assistant", "content": "Python is a high-level programming language..."}
]

response = grok.conversational_chat(
    conversation, 
    "What are its main advantages?"
)
print(response)

# Custom chat completion
messages = [
    {"role": "system", "content": "You are a helpful coding assistant."},
    {"role": "user", "content": "How do I create a Python class?"}
]

response = grok.chat_completion(
    messages=messages,
    model="grok-4-latest",
    temperature=0.7,
    max_tokens=500
)
print(response)
```

## Available Models

- `grok-4-latest` - Latest Grok-4 model (recommended)
- `grok-3-latest` - Latest Grok-3 model
- `grok-2-latest` - Latest Grok-2 model

## API Parameters

The `chat_completion` method supports various parameters:

- `messages`: List of message dictionaries
- `model`: Grok model to use (default: "grok-4-latest")
- `temperature`: Controls randomness (0.0 to 1.0, default: 0.7)
- `max_tokens`: Maximum tokens to generate (default: 1000)
- Additional OpenAI-compatible parameters

## Error Handling

The client includes comprehensive error handling for:

- Missing API key
- Invalid API key (401 error)
- Rate limiting (429 error)
- General API errors
- Network issues

## Examples

### Example 1: Simple Query
```python
grok = GrokClient()
response = grok.simple_query("Explain quantum computing in simple terms")
print(response)
```

### Example 2: Multi-turn Conversation
```python
grok = GrokClient()

# Start a conversation
conversation = [
    {"role": "system", "content": "You are a helpful science tutor."},
    {"role": "user", "content": "What is photosynthesis?"},
    {"role": "assistant", "content": "Photosynthesis is the process by which plants..."}
]

# Continue the conversation
response = grok.conversational_chat(
    conversation, 
    "What are the main components needed for photosynthesis?"
)
print(response)
```

### Example 3: Custom Configuration
```python
grok = GrokClient()

messages = [
    {"role": "system", "content": "You are a creative writing assistant."},
    {"role": "user", "content": "Write a short story about a robot learning to paint."}
]

response = grok.chat_completion(
    messages=messages,
    model="grok-4-latest",
    temperature=0.9,  # More creative
    max_tokens=800
)
print(response)
```

## Troubleshooting

### Common Issues

1. **"API key is required" error**
   - Make sure you've set the `XAI_API_KEY` environment variable
   - Verify your API key is correct

2. **"Rate limit exceeded" error**
   - Wait a moment before making another request
   - Consider implementing exponential backoff for production use

3. **"Invalid API key" error**
   - Check that your API key is valid and active
   - Ensure you're using the correct API key format

4. **Import errors**
   - Make sure you've installed the requirements: `pip install -r requirements.txt`
   - Verify you're using Python 3.7 or higher

## License

This project is open source and available under the MIT License.

## Contributing

Feel free to submit issues, feature requests, or pull requests to improve this client.

## Support

For issues related to the Grok API itself, please refer to the [xAI documentation](https://docs.x.ai/) or contact xAI support.
