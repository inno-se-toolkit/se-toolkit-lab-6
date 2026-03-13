# Plan for Task 1

## 1. Choosing an LLM provider and model

**OpenRouter** was chosen as the LLM provider to be independent from VM. Model **anthropic/claude-4.5-sonnet-20250929** was selected since it is presented in OpenRouter docs. I assume it may be changed in the future.

## 2. Implementation strategy

* **No vibecoding** - I hate it and find it useless for learning. I'm not going to use `qwen` agent or similar.

* **Environment variables** - I'm going to use `python-dotenv` to load environment variables from `.env.agent.secret`.

* **User input** - I'm going to use `sys.argv` to get user input from the command line.

* **API calls** - I'm going to use `requests` to make API calls to the LLM provider. I'm going to use official OpenRouter API.

## 3. Implementation steps

 - Load environment variables from `.env.agent.secret`
 - Get user input from the command line
 - Explore official OpenRouter API documentation
 - Make API call to OpenRouter
 - Parse response
 - Print response
 - Write regression test

 ## 4. Testing

 - Run `test_agent.py` to check that `agent.py` works as expected.
