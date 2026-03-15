#!/bin/bash
echo "=== Testing with API key ==="
export LMS_API_KEY=my-secret-api-key
python3 agent.py "What HTTP status code does the API return when you request /items/ without sending an authentication header?"

echo -e "\n=== Testing without API key ==="
unset LMS_API_KEY
python3 agent.py "What HTTP status code does the API return when you request /items/ without sending an authentication header?"
