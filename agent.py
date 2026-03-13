import requests
import dotenv
import sys
import os
import json

global LLM_API_KEY
global LLM_API_BASE
global LLM_MODEL
global LLM_TEMPERATURE

# get prompt from command line
def get_user_input():
    prompt = sys.argv[1]
    if not len(sys.argv):
        raise Exception("No user input")
    return prompt

# load environment variables
def get_env():

    dotenv.load_dotenv(".env.agent.secret")

    global LLM_API_KEY
    global LLM_API_BASE
    global LLM_MODEL
    global LLM_TEMPERATURE

    LLM_API_KEY = os.getenv("LLM_API_KEY")
    LLM_API_BASE = os.getenv("LLM_API_BASE")
    LLM_MODEL = os.getenv("LLM_MODEL")
    LLM_TEMPERATURE = os.getenv("LLM_TEMPERATURE")

    if not LLM_API_KEY:
        raise Exception("LLM_API_KEY is not set")
    if not LLM_API_BASE:
        raise Exception("LLM_API_BASE is not set")
    if not LLM_MODEL:
        raise Exception("LLM_MODEL is not set")
    if not LLM_TEMPERATURE:
        raise Exception("LLM_TEMPERATURE is not set")

# send request to the LLM API
def send_request(prompt):
    global LLM_API_KEY
    global LLM_API_BASE
    global LLM_MODEL
    global LLM_TEMPERATURE

    response = requests.post(
        f"{LLM_API_BASE}/messages",
        headers={
            "Authorization": f"Bearer {LLM_API_KEY}",
            "Content-Type": "application/json"
        },
        json={
            "model": LLM_MODEL,
            "messages": [
            {
                "role": "user",
                "content": prompt
            }
            ],
            "max_tokens": 1024,
            "temperature": float(LLM_TEMPERATURE),
        },
    )

    if not response.ok:
        raise Exception(f"LLM API error: {response.status_code}")

    answer = response.json()['content'][-1]['text']
    tool_calls = []

    if not answer:
        raise Exception("Failed to parse LLM response")

    return json.dumps({"answer": answer, "tool_calls": tool_calls})

if __name__ == "__main__":
    try:
        get_env()
        prompt = get_user_input()
        print(send_request(prompt))
        exit(0)
    except Exception as e:
        print(f"Error: {e}")
        exit(1)