# Qwen Code

<h2>Table of contents</h2>

- [What is `Qwen Code`](#what-is-qwen-code)
- [Set up the `Qwen Code` (local machine)](#set-up-the-qwen-code-local-machine)
  - [Set up the `Qwen Code` CLI (local machine)](#set-up-the-qwen-code-cli-local-machine)
  - [Set up the `Qwen Code Companion` extension for `VS Code`](#set-up-the-qwen-code-companion-extension-for-vs-code)
  - [Set up the `GitHub Copilot Chat` extension for `VS Code`](#set-up-the-github-copilot-chat-extension-for-vs-code)
- [Check the `Qwen Code` credentials file](#check-the-qwen-code-credentials-file)
  - [Check the `Qwen Code` credentials file in the `VS Code Terminal`](#check-the-qwen-code-credentials-file-in-the-vs-code-terminal)
  - [Check the `Qwen Code` credentials file in the `VS Code Editor`](#check-the-qwen-code-credentials-file-in-the-vs-code-editor)
- [Set up the `Qwen Code` (remote machine)](#set-up-the-qwen-code-remote-machine)
  - [Set up the `Qwen Code` CLI (remote machine)](#set-up-the-qwen-code-cli-remote-machine)
  - [Set up the `Qwen Code` API (remote machine)](#set-up-the-qwen-code-api-remote-machine)
- [Open a chat with `Qwen Code`](#open-a-chat-with-qwen-code)
  - [Open a chat with `Qwen Code` using the CLI](#open-a-chat-with-qwen-code-using-the-cli)
  - [Open a chat with `Qwen Code` using the `Qwen Code Companion` extension for `VS Code`](#open-a-chat-with-qwen-code-using-the-qwen-code-companion-extension-for-vs-code)
  - [Open a chat with `Qwen Code` using the `GitHub Copilot Chat` extension for `VS Code`](#open-a-chat-with-qwen-code-using-the-github-copilot-chat-extension-for-vs-code)
- [Chat with `Qwen Code`](#chat-with-qwen-code)
  - [Refer to a file](#refer-to-a-file)
  - [Use a skill](#use-a-skill)
- [Lab instructions for `Qwen Code`](#lab-instructions-for-qwen-code)

## What is `Qwen Code`

[`Qwen Code`](https://github.com/QwenLM/qwen-code) is a [coding agent](./coding-agents.md#what-is-a-coding-agent) that:

- [provides 1000 free requests per day](https://github.com/QwenLM/qwen-code#why-qwen-code) to the [`Qwen3-Coder`](https://github.com/QwenLM/Qwen3-Coder) model (see [Model](./llm.md#model)).
- is available in Russia.

See:

- [Set up the `Qwen Code` (local machine)](#set-up-the-qwen-code-local-machine).
- [Set up the `Qwen Code` (remote machine)](#set-up-the-qwen-code-remote-machine).

## Set up the `Qwen Code` (local machine)

<!-- no toc -->
- Method 1: [Set up the `Qwen Code` CLI (local machine)](#set-up-the-qwen-code-cli-local-machine).
- Method 2: [Set up the `Qwen Code Companion` extension for `VS Code`](#set-up-the-qwen-code-companion-extension-for-vs-code).
- Method 3: [Set up the `GitHub Copilot Chat` extension for `VS Code`](#set-up-the-github-copilot-chat-extension-for-vs-code).

### Set up the `Qwen Code` CLI (local machine)

> [!NOTE]
> See [CLI](./cli.md#what-is-a-cli)

1. [Install `Node.js`](./nodejs.md#install-nodejs).

2. Copy the single-line [shell command](./shell.md#shell-command) from the [installation instructions](https://github.com/QwenLM/qwen-code#installation) for [`Qwen Code`](#what-is-qwen-code).

   <!-- TODO use pnpm -->

3. [Open a chat with `Qwen Code` using the CLI](#open-a-chat-with-qwen-code-using-the-cli).

4. Write `/auth` in the chat to [authenticate via Qwen OAuth](https://github.com/QwenLM/qwen-code?tab=readme-ov-file#authentication).

5. [Check the `Qwen Code` credentials file](#check-the-qwen-code-credentials-file).

### Set up the `Qwen Code Companion` extension for `VS Code`

1. [Install the `VS Code` extension](./vs-code.md#install-the-vs-code-extension):
   `qwenlm.qwen-code-vscode-ide-companion`.

2. [Open a chat with `Qwen Code` using the `Qwen Code Companion` extension for `VS Code`](#open-a-chat-with-qwen-code-using-the-qwen-code-companion-extension-for-vs-code).

3. Write `/login` in the chat to [authenticate via Qwen OAuth](https://github.com/QwenLM/qwen-code?tab=readme-ov-file#authentication).

4. Complete the authentication procedure.

5. [Check the `Qwen Code` credentials file](#check-the-qwen-code-credentials-file).

### Set up the `GitHub Copilot Chat` extension for `VS Code`

> [!NOTE]
> `Copilot Chat` is not officially available for users in Russia (see [this discussion](https://github.com/orgs/community/discussions/182386)).

1. [Install](https://code.visualstudio.com/docs/configure/extensions/extension-marketplace#_browse-for-extensions) the `github.copilot-chat` and `denizhandaklr.vscode-qwen-copilot` extensions.

2. [Run using the `Command Palette`](./vs-code.md#run-a-command-using-the-command-palette):
   `Qwen Copilot: Authenticate` to [authenticate via Qwen OAuth](https://github.com/QwenLM/qwen-code?tab=readme-ov-file#authentication).

3. [Check the `Qwen Code` credentials file](#check-the-qwen-code-credentials-file).

4. [Run using the `Command Palette`](./vs-code.md#run-a-command-using-the-command-palette):
   `Chat: Manage Language Models`.

5. Click `Add Models`.

6. Click `Qwen Code`.

7. Double click `Qwen 3 Coder Plus` to make the model visible.

8. [Open a chat with `Qwen Code` using the `GitHub Copilot Chat` extension for `VS Code`](#open-a-chat-with-qwen-code-using-the-github-copilot-chat-extension-for-vs-code).

## Check the `Qwen Code` credentials file

- Method 1: [Check the `Qwen Code` credentials file in the `VS Code Terminal`](#check-the-qwen-code-credentials-file-in-the-vs-code-editor).
- Method 2: [Check the `Qwen Code` credentials file in the `VS Code Editor`](#check-the-qwen-code-credentials-file-in-the-vs-code-editor).

### Check the `Qwen Code` credentials file in the `VS Code Terminal`

To print the content of the credentials file,

[run in the `VS Code Terminal`](./vs-code.md#run-a-command-in-the-vs-code-terminal):

```terminal
cat ~/.qwen/oauth_creds.json | jq .
```

### Check the `Qwen Code` credentials file in the `VS Code Editor`

[Open in `VS Code` the file](./vs-code.md#open-the-file):
`~/.qwen/oauth_creds.json`.

This file contains the `Qwen Code` authentication credentials.

The file must be non-empty.

## Set up the `Qwen Code` (remote machine)

- Method 1: [Set up the `Qwen Code` CLI (remote machine)](#set-up-the-qwen-code-cli-remote-machine).
- Method 2: [Set up the `Qwen Code` API (remote machine)](#set-up-the-qwen-code-api-remote-machine).

### Set up the `Qwen Code` CLI (remote machine)

1. [Connect to the VM](./ssh.md#connect-to-the-vm).

2. [Install `pnpm`](./nodejs.md#install-pnpm).

3. To install [`Qwen Code`](#what-is-qwen-code),

   [run in the `VS Code Terminal`](./vs-code.md#run-a-command-in-the-vs-code-terminal):

   ```terminal
   pnpm add -g @qwen-code/qwen-code
   ```

4. [Open a chat with `Qwen Code` using the CLI](#open-a-chat-with-qwen-code-using-the-cli).

5. Write `/auth` in the chat to [authenticate via Qwen OAuth](https://github.com/QwenLM/qwen-code?tab=readme-ov-file#authentication).

6. Open the link in a browser to complete the authentication procedure.

### Set up the `Qwen Code` API (remote machine)

> [`qwen-code-oai-proxy`](https://github.com/inno-se-toolkit/qwen-code-oai-proxy) exposes [`Qwen Code`](#what-is-qwen-code) through an [OpenAI-compatible API](./llm.md#openai-compatible-api) so that other tools can use it as an [LLM](./llm.md#what-is-an-llm).

1. [Set up the `Qwen Code` CLI (remote machine)](#set-up-the-qwen-code-cli-remote-machine).

   Keep working in the opened `VS Code Terminal`.
   You complete the following steps on your VM.

2. To [clone using the `VS Code Terminal` the repo](./git-vscode.md#clone-the-repo-using-the-vs-code-terminal)

   <https://github.com/inno-se-toolkit/qwen-code-oai-proxy>,

   [run in the `VS Code Terminal`](./vs-code.md#run-a-command-in-the-vs-code-terminal):

   ```terminal
   git clone https://github.com/inno-se-toolkit/qwen-code-oai-proxy ~/qwen-code-oai-proxy
   ```

3. To enter the repository directory,

   [run in the `VS Code Terminal`](./vs-code.md#run-a-command-in-the-vs-code-terminal):

   ```terminal
   cd ~/qwen-code-oai-proxy
   ```

4. To create the [environment](./environments.md#what-is-an-environment) file,

   [run in the `VS Code Terminal`](./vs-code.md#run-a-command-in-the-vs-code-terminal):

   ```terminal
   cp .env.example .env
   ```

5. To open `.env` in `nano`,

   [run in the `VS Code Terminal`](./vs-code.md#run-a-command-in-the-vs-code-terminal):

   ```terminal
   nano .env
   ```

6. Write the value of `QWEN_API_KEY`.

   You'll use it in requests to the API.

7. Save the file (`Ctrl + O`).

8. To start the `Qwen` API,

   [run in the `VS Code Terminal`](./vs-code.md#run-a-command-in-the-vs-code-terminal):

   ```terminal
   docker compose up --build -d
   ```

9. To get the value of `HOST_PORT` in `.env`,

   [run in the `VS Code Terminal`](./vs-code.md#run-a-command-in-the-vs-code-terminal):

   ```terminal
   cat .env | grep HOST_PORT
   ```

10. The API is available at `http://localhost:<qwen-api-port>/v1`.

    Replace `<qwen-api-port>` with the value of `HOST_PORT` (without `<` and `>`) that you got.

    Example: `http://localhost:42005/v1`

11. To check that the `Qwen` API works,

    [run in the `VS Code Terminal`](./vs-code.md#run-a-command-in-the-vs-code-terminal):

    ```terminal
    curl -s http://127.0.0.1:<qwen-api-port>/v1/chat/completions \
      -H "Content-Type: application/json" \
      -H "Authorization: Bearer <qwen-api-key>" \
      -d '{"model":"qwen3-coder-plus","messages":[{"role":"user","content":"What is 2+2?"}]}' \
      | jq .
    ```

    Replace:

    - `<qwen-api-port>`
    - `<qwen-api-key>` with the value of `QWEN_API_KEY` in `.env`.
    - (Optional) `qwen3-coder-plus` in `"model": "qwen3-coder-plus"` with one of the available models:

      - `coder-model` — `Qwen 3.5 Plus` (recommended).
      - `qwen3-coder-plus` — `Qwen 3 Coder Plus`.
      - `qwen3-coder-flash` — `Qwen 3 Coder Flash` (faster).

    The output should be similar to this:

    ```terminal
    {
      "created": 1773379590,
      "usage": {
         "completion_tokens": 8,
         "prompt_tokens": 15,
         "prompt_tokens_details": {
            "cached_tokens": 0
         },
         "total_tokens": 23
      },
      "model": "qwen3-coder-plus",
      "id": "chatcmpl-9c04fd89-7d16-469f-af7b-8e64a9418bb3",
      "choices": [
         {
            "finish_reason": "stop",
            "index": 0,
            "message": {
            "role": "assistant",
            "content": "2 + 2 = 4."
            }
         }
      ],
      "object": "chat.completion"
    }
    ```

12. To check that you can access the deployed `Qwen` API from your local machine:
  
    1. Open a new `VS Code Terminal`.
    2. To query the `Qwen` API,

       [run in the `VS Code Terminal`](./vs-code.md#run-a-command-in-the-vs-code-terminal):

       ```terminal
       curl -s http://<your-vm-ip-address>:<qwen-api-port>/v1/chat/completions \
         -H "Content-Type: application/json" \
         -H "Authorization: Bearer <qwen-api-key>" \
         -d '{"model":"qwen3-coder-plus","messages":[{"role":"user","content":"What is 2+2?"}]}' \
         | jq .
       ```

       Replace
       - `<your-vm-ip-address>`
       - `<qwen-api-port>`
       - `<qwen-api-key>`

<!-- TODO create own sections for querying the API -->

## Open a chat with `Qwen Code`

<!-- no toc -->
- Method 1: [Open a chat with `Qwen Code` using the CLI](#open-a-chat-with-qwen-code-using-the-cli)
- Method 2: [Open a chat with `Qwen Code` using the `Qwen Code Companion` extension for `VS Code`](#open-a-chat-with-qwen-code-using-the-qwen-code-companion-extension-for-vs-code)
- Method 3: [Open a chat with `Qwen Code` using the `GitHub Copilot Chat` extension for `VS Code`](#open-a-chat-with-qwen-code-using-the-github-copilot-chat-extension-for-vs-code)

### Open a chat with `Qwen Code` using the CLI

> [!NOTE]
> See [CLI](./cli.md#what-is-a-cli).

1. [Run in the `VS Code Terminal`](./vs-code.md#run-a-command-in-the-vs-code-terminal):

   ```terminal
   qwen
   ```

2. If you want to exit the chat:

   1. Write `/quit` in the chat.
   2. Press `Enter`.

### Open a chat with `Qwen Code` using the `Qwen Code Companion` extension for `VS Code`

Method 1:

1. Go to the [`Editor Toolbar`](./vs-code.md#editor-toolbar).
2. Click the `Qwen Code: Open` icon.

   <img alt="Icon Qwen Code: Open" src="./images/qwen-code/qwen-code-open.png" style="width:300px"></img>

Method 2:

1. [Run using the `Command Palette`](./vs-code.md#run-a-command-using-the-command-palette):
   `Qwen Code: Open`.

### Open a chat with `Qwen Code` using the `GitHub Copilot Chat` extension for `VS Code`

1. [Run using the `Command Palette`](./vs-code.md#run-a-command-using-the-command-palette):
   `Chat: Open Chat`
2. The `CHAT` panel will open.
3. Go to `CHAT`.
4. Click `Auto` (`Pick Model`).
5. Click `Qwen 3 Coder Plus`.

## Chat with `Qwen Code`

Actions:

<!-- no toc -->
- [Refer to a file](#refer-to-a-file)
- [Use a skill](#use-a-skill)

### Refer to a file

Write `@<file-path>` (without `<` and `>`) to refer to the file at the [`<file-path>`](./file-system.md#file-path).

Example: `@main.py`.

### Use a skill

1. [Open a chat with `Qwen Code`](#open-a-chat-with-qwen-code).
2. Write `skills`.
3. Press `Enter`.
4. To use the skill, write the [skill name](./coding-agents.md#skill-name) and the [skill arguments](./coding-agents.md#skill-arguments).

   Example: `commit @main.py`.

   See [Refer to a file](#refer-to-a-file).
5. Press `Enter`.

## Lab instructions for `Qwen Code`

[`Qwen Code`](#what-is-qwen-code) automatically reads [`AGENTS.md`](../AGENTS.md) in the project root. This file contains instructions that guide the agent to help you learn — not just generate code. The agent will ask you questions, help you plan, and encourage you to write code yourself.
