# Gemini API Integration Setup

This project now supports both Ollama (local) and Google Gemini API as LLM providers. You can easily switch between them using environment variables.

## Configuration

### Using Ollama (Default)
```bash
# Set in your .env file
LLM_PROVIDER=ollama
OLLAMA_URL=http://localhost:11434
OLLAMA_MODEL=gpt-oss:latest
```

### Using Gemini API
```bash
# Set in your .env file
LLM_PROVIDER=gemini
GEMINI_API_KEY=your_actual_gemini_api_key_here
GEMINI_MODEL=gemini-pro
```

## Getting a Gemini API Key

1. Go to [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Sign in with your Google account
3. Click "Create API Key"
4. Copy the generated API key
5. Add it to your `.env` file as `GEMINI_API_KEY=your_key_here`

## Installation

1. Install the additional dependency:
```bash
pip install google-generativeai==0.3.2
```

2. Update your `.env` file with the appropriate configuration

3. Restart your Django development server

## Testing

Run the test script to verify both providers work:
```bash
python test_llm_providers.py
```

This will test:
- Connection to the LLM provider
- SQL query generation
- Natural language response generation

## Usage

The application will automatically use the provider specified in `LLM_PROVIDER`. No code changes are needed - just update the environment variable and restart the server.

## Available Models

### Ollama
- Any model you have installed locally (e.g., `llama3.2`, `gpt-oss:latest`)

### Gemini
- `gemini-pro` (recommended)
- `gemini-pro-vision` (for multimodal tasks)

## Benefits of Each Provider

### Ollama
- ✅ Free to use
- ✅ Runs locally (privacy)
- ✅ No API limits
- ❌ Requires local setup and resources

### Gemini
- ✅ No local setup required
- ✅ Fast response times
- ✅ High-quality outputs
- ❌ Requires API key and has usage limits
- ❌ Data sent to Google

## Switching Providers

To switch from Ollama to Gemini:
1. Set `LLM_PROVIDER=gemini` in your `.env` file
2. Add your `GEMINI_API_KEY`
3. Restart the Django server

To switch back to Ollama:
1. Set `LLM_PROVIDER=ollama` in your `.env` file
2. Ensure Ollama is running locally
3. Restart the Django server

## Troubleshooting

### Gemini API Key Issues
- Ensure your API key is valid and active
- Check that you have remaining quota
- Verify the key has the correct permissions

### Ollama Connection Issues
- Ensure Ollama is running: `ollama serve`
- Check the OLLAMA_URL is correct
- Verify the model is installed: `ollama list`

### General Issues
- Check Django logs for detailed error messages
- Run the test script to isolate the issue
- Ensure all environment variables are set correctly