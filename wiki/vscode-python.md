# `Python` in `VS Code`

<h2>Table of contents</h2>

- [What is `Python` in `VS Code`](#what-is-python-in-vs-code)
- [Set up `Python` in `VS Code`](#set-up-python-in-vs-code)
  - [Install `Python` and dependencies](#install-python-and-dependencies)
  - [Check that `Python` works](#check-that-python-works)
  - [Select the `Python` interpreter](#select-the-python-interpreter)
  - [Check that the language server works](#check-that-the-language-server-works)

## What is `Python` in `VS Code`

`VS Code` can be configured to work with [`Python`](./python.md#what-is-python) using the [`Pylance`](./python.md#pylance) language server for type checking and autocompletion, and [`uv`](./python.md#uv) for virtual environment management.

## Set up `Python` in `VS Code`

Complete these steps:

1. [Install `Python` and dependencies](#install-python-and-dependencies).
2. [Check that `Python` works](#check-that-python-works).
3. [Select the `Python` interpreter](#select-the-python-interpreter).
4. [Check that the language server works](#check-that-the-language-server-works).

### Install `Python` and dependencies

1. [Open in `VS Code` the project directory](./vs-code.md#open-the-directory).

2. To install `Python` and project dependencies,

   [run in the `VS Code Terminal`](./vs-code.md#run-a-command-in-the-vs-code-terminal):

   ```terminal
   uv sync
   ```

   This command automatically downloads the correct `Python` version, creates the `.venv` virtual environment, and installs all dependencies.

3. The output should be similar to this:

   ```terminal
   Using CPython 3.14.2
   Creating virtual environment at: .venv
   Resolved 36 packages in 0.77ms
   Installed 36 packages in 217ms
   ```

> [!NOTE]
> The `.venv` directory contains the virtual environment.
> That is, files and dependencies that are necessary to run the web server and other tools.
>
> This directory is managed by [`uv`](./python.md#uv). You don't need to edit files in this directory manually.

### Check that `Python` works

1. [Open a new `VS Code Terminal`](./vs-code.md#open-a-new-vs-code-terminal).
2. To check the `Python` version,

   [run in the `VS Code Terminal`](./vs-code.md#run-a-command-in-the-vs-code-terminal):

   ```terminal
   uv run python --version
   ```

3. The output should be similar to this:

   ```terminal
   Python 3.14.2
   ```

> [!NOTE]
> The [`Python`](./python.md#what-is-python) version for this project is specified in the [`pyproject.toml`](../pyproject.toml) file using the `requires-python` setting.

### Select the `Python` interpreter

1. [Run using the `Command Palette`](./vs-code.md#run-a-command-using-the-command-palette):
   `Python: Select Interpreter`.
2. Click `Recommended` to select the interpreter in `./.venv/bin/python`.
3. [Check that the language server works](#check-that-the-language-server-works).

### Check that the language server works

> [!NOTE]
> See [`Pylance`](./python.md#pylance).

1. [Open the file](./vs-code.md#open-the-file):
   [`backend/app/main.py`](../backend/app/main.py).
2. Hover over the `add_middleware` method.

   You should see its type:

   <img alt="Type on hover" src="./images/python/type-on-hover.png" style="width:300px">
