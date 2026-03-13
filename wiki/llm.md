# LLM

<h2>Table of contents</h2>

- [What is an LLM](#what-is-an-llm)
- [Model](#model)
  - [Choose a model](#choose-a-model)
  - [Local inference](#local-inference)
- [LLM provider](#llm-provider)
  - [`OpenRouter`](#openrouter)
- [Free models](#free-models)
- [LLM provider API](#llm-provider-api)
  - [`OpenAI`-compatible API](#openai-compatible-api)
  - [Request to LLM provider API](#request-to-llm-provider-api)
- [Token](#token)
- [Context](#context)
  - [Context window](#context-window)
- [Context engineering](#context-engineering)
- [Prompt](#prompt)
- [Prompt engineering](#prompt-engineering)

## What is an LLM

An LLM (Large Language Model) is a type of AI model trained on large amounts of text data that can understand and generate human-readable text, including code.

LLMs power [coding agents](./coding-agents.md#what-is-a-coding-agent) that help you complete tasks in this course.

Docs:

- [What is a large language model?](https://aws.amazon.com/what-is/large-language-model/)

## Model

A model is a specific trained version of an [LLM](#llm), identified by a name (e.g., `Qwen3-Coder`, `claude-sonnet-4-6`).

Different models vary in capability, speed, and cost. [Coding agents](./coding-agents.md#choose-and-use-a-coding-agent) let you choose which model to use.

### Choose a model

Choose a model for the task at hand.

### Local inference

Docs:

- [What Can I Run?](https://apxml.com/models)

## LLM provider

### `OpenRouter`

## Free models

- [`OpenRouter`](https://openrouter.ai/) provides [free models](https://openrouter.ai/collections/free-models).

## LLM provider API

An LLM provider API is an [HTTP API](./web-api.md#http-api) exposed by an LLM provider (e.g., `OpenAI`, `Anthropic`, [`OpenRouter`](#openrouter)) that allows applications and tools to send requests to their [LLMs](#what-is-an-llm) programmatically.

[Coding agents](./coding-agents.md#what-is-a-coding-agent) use an LLM provider API to send [prompts](#prompt) and receive generated responses, authenticating each [request](#request-to-llm-provider-api) with an API key.

<!-- TODO links - authentication, api key, responses -->

Docs:

- [OpenAI API reference](https://developers.openai.com/api/reference/overview)
- [OpenRouter API reference](https://openrouter.ai/docs/api-reference/overview)

### `OpenAI`-compatible API

An `OpenAI`-compatible API follows the same request and response format as the `OpenAI` API, allowing the same client code to work with different [LLM providers](#llm-provider-api) by changing only the base URL and API key.

Most [coding agents](./coding-agents.md#what-is-a-coding-agent) support `OpenAI`-compatible APIs, which lets you point them at providers like [`OpenRouter`](#openrouter) instead of `OpenAI` directly.

Docs:

- [OpenRouter: OpenAI compatibility](https://openrouter.ai/docs/community/frameworks)

### Request to LLM provider API

A request to an LLM provider API is an [`HTTP` POST request](./http.md#http-request) that includes the [model](#model) name and a list of messages, each with a role and text content.

The three message roles are:

- `system` — instructions that set the behavior of the LLM (e.g., "You are a helpful assistant.").
- `user` — the input from the user.
- `assistant` — a previous response from the LLM, included to provide conversation history.

The request is authenticated using an API key in the [`Authorization` header](./http-auth.md#http-authentication).

Example request body:

```json
{
  "model": "gpt-4o-mini",
  "messages": [
    { "role": "system", "content": "You are a helpful assistant." },
    { "role": "user", "content": "What is an LLM?" }
  ]
}
```

Docs:

- [OpenAI: Chat completions](https://platform.openai.com/docs/guides/chat-completions)

## Token

A token is a unit of text that an [LLM](#llm) processes — roughly a word or a few characters.

LLMs read and generate text token by token. The number of tokens in a message affects how much of the [context window](#context-window) it uses.

## Context

The context is the information available to the [LLM](#llm) during an interaction — your messages, the conversation history, and any files or instructions you provide.

### Context window

The context window is the maximum amount of text (measured in [tokens](#token)) that an [LLM](#llm) can process in a single interaction — including the conversation history, files, and the current message.

When the context window is full, earlier parts of the conversation are dropped. To avoid this, keep conversations focused and start a new conversation when switching tasks.

## Context engineering

Context engineering is the practice of deliberately choosing what information to include in the context to get better results from an LLM.

When using a [coding agent](./coding-agents.md#what-is-a-coding-agent), you control the [context](#context) by referencing specific files, pasting error messages, and providing acceptance criteria. The more relevant the context, the more useful the response.

## Prompt

A prompt is the input text you send to an LLM to guide its response. The quality of the prompt directly affects the quality of the output.

See [Prompt engineering](#prompt-engineering).

## Prompt engineering

Prompt engineering is the practice of writing prompts that produce accurate, relevant, and useful responses.
