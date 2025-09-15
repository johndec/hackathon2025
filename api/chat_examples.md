# Request Body Examples for /chat Endpoint
# Hackathon 2025 OpenAI API

Below are various request body examples for the POST /chat endpoint.

## Basic Request (Minimum Required)

```json
{
  "message": "Hello! How can you help me today?"
}
```

## Simple Chat with Custom Temperature

```json
{
  "message": "What are some good programming languages for beginners?",
  "temperature": 0.5,
  "max_tokens": 200
}
```

## Chat with System Prompt (Recommended)

```json
{
  "message": "How do I optimize a Python function for better performance?",
  "system_prompt": "You are a senior Python developer with expertise in performance optimization.",
  "max_tokens": 300,
  "temperature": 0.7
}
```

## Hackathon Project Ideas

```json
{
  "message": "I need innovative project ideas for a 48-hour hackathon. What would you suggest?",
  "system_prompt": "You are a creative technology consultant who specializes in hackathon projects and emerging tech trends.",
  "max_tokens": 400,
  "temperature": 0.8
}
```

## Technical Problem Solving

```json
{
  "message": "I'm getting a 'ModuleNotFoundError' in Python. How can I debug this?",
  "system_prompt": "You are a debugging expert who provides step-by-step solutions to programming problems.",
  "max_tokens": 250,
  "temperature": 0.3
}
```

## Creative Writing

```json
{
  "message": "Write a short story about an AI that learns to paint",
  "system_prompt": "You are a creative writer who specializes in science fiction and AI-themed stories.",
  "max_tokens": 500,
  "temperature": 0.9
}
```

## Code Review Request

```json
{
  "message": "Can you review this Python function and suggest improvements?\n\ndef calculate_average(numbers):\n    total = 0\n    for num in numbers:\n        total = total + num\n    return total / len(numbers)",
  "system_prompt": "You are a code reviewer who provides constructive feedback and suggestions for improvement.",
  "max_tokens": 300,
  "temperature": 0.4
}
```

## Business Strategy

```json
{
  "message": "What are the key considerations when building a SaaS product for small businesses?",
  "system_prompt": "You are a business strategist with experience in SaaS products and small business markets.",
  "max_tokens": 350,
  "temperature": 0.6
}
```

## Learning Assistant

```json
{
  "message": "Explain machine learning in simple terms that a beginner can understand",
  "system_prompt": "You are a patient teacher who excels at explaining complex technical concepts in simple, easy-to-understand language.",
  "max_tokens": 300,
  "temperature": 0.5
}
```

## API Documentation Help

```json
{
  "message": "How should I structure the documentation for my REST API?",
  "system_prompt": "You are a technical writer who specializes in API documentation and developer experience.",
  "max_tokens": 400,
  "temperature": 0.6
}
```

## Maximum Customization Example

```json
{
  "message": "Design a comprehensive testing strategy for a Flask API that integrates with Azure OpenAI",
  "system_prompt": "You are a senior QA engineer with expertise in API testing, Flask applications, and cloud services. Provide detailed, actionable advice.",
  "max_tokens": 500,
  "temperature": 0.7
}
```

## Parameter Descriptions

- **message** (required): The user's input/question
- **system_prompt** (optional): Defines the AI's role and behavior
  - Default: "You are a helpful AI agent that answers questions when asked."
- **max_tokens** (optional): Maximum tokens in the response
  - Default: 500
  - Range: 1-4000 (depending on model)
- **temperature** (optional): Controls randomness/creativity
  - Default: 0.7
  - Range: 0.0 (deterministic) to 1.0 (very creative)

## Temperature Guide

- **0.0-0.3**: Factual, precise, consistent responses
- **0.4-0.6**: Balanced creativity and accuracy
- **0.7-0.9**: Creative, varied responses
- **1.0**: Maximum creativity and randomness

## Expected Response Format

```json
{
  "response": "AI generated response text...",
  "model": "jay-hackathon-deployment",
  "usage": {
    "prompt_tokens": 45,
    "completion_tokens": 123,
    "total_tokens": 168
  }
}
```

## Error Response Examples

### Missing Message
```json
{
  "error": "Missing 'message' in request body"
}
```

### API Configuration Error
```json
{
  "error": "Configuration error: AZURE_OPENAI_API_KEY environment variable is not set"
}
```

### OpenAI API Error
```json
{
  "error": "Failed to generate response: [specific error message]"
}
```