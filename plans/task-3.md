# Task 3 Plan: System Agent

## Provider and LLM model
- Provider: Qwen Code API 
- Model: qwen3-coder-plus
- Reasons for choosing:
- Reliable support for tool calling
- 1000 free requests per day
- Works from Russia 

## Diagram of the `query_api` tool

```json
{
  "name": "query_api",
  "description": "Request to the deployed backend API. Use it for: checking the number of records, HTTP statuses, analytical endpoints, and debugging API errors",
"parameters": {
"type": "object",
"properties": {
"method": {
"type": "string",
"enum": ["GET", "POST", "PUT", "DELETE"],
"description": "HTTP request method"
      },
      "path": {
"type": "string",
"description": "Endpoint path, for example: '/items/', '/analytics/completion-rate'"
      },
      "body": {
        "type": "string",
"description": "Optional request body as a JSON string (for POST/PUT)"
}
    },
    "required": ["method", "path"]
  }
}