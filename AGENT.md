# Lab Agent

A CLI tool that connects to an LLM and answers questions using tools. The agent can read files and list directories to find accurate information from the project wiki.

## Architecture

### Task 1: Basic LLM Chat

```
┌─────────────┐     ┌──────────────┐     ┌─────────────────┐
│   User CLI  │────▶│   agent.py   │────▶│  LLM Provider   │
│  (question) │     │  (OpenAI SDK)│     │ (Qwen Code API) │
└─────────────┘     └──────────────┘     └─────────────────┘
                           │
                           ▼
                    ┌──────────────┐
                    │ .env.agent.  │
                    │   secret     │
                    └──────────────┘
```

### Task 2+: Agentic Loop with Tools

```
┌─────────────┐     ┌──────────────┐     ┌─────────────────┐
│   User CLI  │────▶│   agent.py   │────▶│  LLM Provider   │
│  (question) │     │  (Agentic    │     │ (Qwen Code API) │
└─────────────┘     │   Loop)      │     └─────────────────┘
                    │      │               │
                    │      ▼               │
                    │  ┌──────────┐        │
                    │  │ Tools:   │◀───────┘
                    │  │ - read   │
                    │  │ - list   │
                    │  └──────────┘
                    │      │
                    │      ▼
                    │  Project Files
                    │  (wiki/, etc.)
                    ▼
             JSON Output
```

## LLM Provider

**Provider**: Qwen Code API (OpenAI-compatible endpoint)

**Model**: `qwen3-coder-plus`

**Why Qwen Code API**:
- 1000 free requests per day
- Works from Russia
- No credit card required
- OpenAI-compatible API (easy to switch providers)

**Alternative**: OpenRouter (free tier: 50 requests/day)

## Configuration

The agent reads configuration from `.env.agent.secret` (gitignored):

```bash
# LLM API key
LLM_API_KEY=your-api-key-here

# API base URL (OpenAI-compatible endpoint)
LLM_API_BASE=http://<vm-ip>:<port>/v1

# Model name
LLM_MODEL=qwen3-coder-plus
```

### Setup

1. Copy the example file:
   ```bash
   cp .env.agent.example .env.agent.secret
   ```

2. Edit `.env.agent.secret` with your credentials:
   - `LLM_API_KEY`: Your API key from Qwen Code API or OpenRouter
   - `LLM_API_BASE`: The API endpoint URL
   - `LLM_MODEL`: The model name to use

## Usage

### Run the agent

```bash
uv run agent.py "What does REST stand for?"
```

### Output

The agent outputs a single JSON object to stdout:

```json
{
  "answer": "Representational State Transfer.",
  "source": "wiki/rest-api.md#what-is-rest",
  "tool_calls": [
    {"tool": "list_files", "args": {"path": "wiki"}, "result": "rest-api.md\n..."},
    {"tool": "read_file", "args": {"path": "wiki/rest-api.md"}, "result": "..."}
  ]
}
```

- `answer`: The LLM's text response
- `source`: The wiki section that answers the question (format: `wiki/filename.md#section`)
- `tool_calls`: Array of all tool calls made during execution, each with:
  - `tool`: Tool name (`read_file` or `list_files`)
  - `args`: Arguments passed to the tool
  - `result`: The tool's return value

**Important**: Only valid JSON goes to stdout. All debug/log output goes to stderr.

## How It Works

### Task 1: Basic Flow

1. **Parse CLI argument**: The question is passed as the first command-line argument
2. **Load configuration**: Environment variables are loaded from `.env.agent.secret`
3. **Initialize OpenAI client**: The client is configured with `api_key` and `base_url`
4. **Send request**: POST to `<LLM_API_BASE>/v1/chat/completions` with the prompt
5. **Parse response**: Extract `choices[0].message.content` from the LLM response
6. **Format output**: Wrap answer in JSON with empty `tool_calls` array
7. **Print result**: Output JSON to stdout

### Task 2+: Agentic Loop

1. **Initialize messages**: System prompt + user question
2. **Call LLM with tools**: Send message with tool schemas attached
3. **Check response**:
   - If `tool_calls` present: execute each tool, append results, repeat from step 2
   - If text answer: extract answer + source, return JSON
4. **Max iterations**: Loop runs at most 10 times to prevent infinite loops
5. **Output**: JSON with answer, source, and all tool calls made

## Tools

The agent has access to two tools for navigating the project:

### `read_file`

Read the contents of a file from the project repository.

**Parameters:**
- `path` (string, required): Relative path from project root (e.g., `wiki/git-workflow.md`)

**Returns:**
- File contents as a string
- Error message if file doesn't exist or path is invalid

**Security:**
- Rejects paths containing `..` (directory traversal)
- Rejects absolute paths starting with `/`
- Validates resolved path is within project directory

**Example:**
```python
read_file("wiki/git-workflow.md")
# Returns: "# Git Workflow\n\n## Resolving Merge Conflicts\n..."
```

### `list_files`

List files and directories at a given path.

**Parameters:**
- `path` (string, required): Relative directory path from project root (e.g., `wiki`)

**Returns:**
- Newline-separated list of entries
- Directories are marked with trailing `/`
- Error message if directory doesn't exist or path is invalid

**Security:**
- Same path validation as `read_file`
- Skips hidden files (except `.qwen`) and `__pycache__`

**Example:**
```python
list_files("wiki")
# Returns: "git-workflow.md\nrest-api.md\nssh.md\n..."
```

## System Prompt Strategy

The system prompt guides the LLM to:

1. **Use tools effectively**: Always use `list_files` to discover wiki structure, then `read_file` to find specific information
2. **Base answers on evidence**: Answer from actual file contents, not assumptions
3. **Include source references**: Format as `wiki/filename.md#section-anchor`
4. **Be concise**: Provide clear, direct answers

Example system prompt excerpt:
```
You are a documentation assistant for a software engineering lab.
You have access to tools to read files and list directories in the project.

When answering questions:
1. Use list_files to discover what files exist in the wiki/ directory
2. Use read_file to read the contents of relevant files
3. Find the specific section that answers the question
4. Provide a clear answer based on the file contents
5. Include the source as: wiki/filename.md#section-anchor
```

## Error Handling

- **Missing environment variables**: Raises `ValueError` with helpful message
- **LLM API errors**: Caught and returned in the JSON `answer` field, exit code 1
- **No CLI argument**: Prints usage to stderr, exit code 1

## Testing

Run the regression test:

```bash
uv run pytest backend/tests/unit/test_agent.py -v
```

The test:
1. Runs `agent.py` as a subprocess
2. Parses the JSON output
3. Verifies `answer` and `tool_calls` fields are present

## Development

### Dependencies

- `openai`: OpenAI Python SDK (supports OpenAI-compatible APIs)
- `python-dotenv`: Load environment variables from `.env` files

### Add new features

In Task 2, you will:
- Add tools (file system, API queries, etc.)
- Implement the agentic loop
- Populate `tool_calls` with tool invocations

In Task 3, you will:
- Add domain knowledge (wiki articles)
- Expand the system prompt
- Improve tool selection

## Troubleshooting

### "LLM_API_KEY not found"

Make sure `.env.agent.secret` exists and contains `LLM_API_KEY=...`

### Connection refused

Check that `LLM_API_BASE` points to a running API endpoint. For Qwen Code API on your VM, ensure the proxy is running:

```bash
# On your VM, in ~/qwen-code-oai-proxy
docker compose ps
```

### 401 Unauthorized

Your `LLM_API_KEY` is incorrect or expired.

### Rate limit errors

Free-tier models have daily limits. Wait 24 hours or switch to a different provider.
