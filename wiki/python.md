# `Python`

<h2>Table of contents</h2>

- [What is `Python`](#what-is-python)
- [Syntax](#syntax)
  - [Code blocks](#code-blocks)
  - [Documentation](#documentation)
  - [Docstring](#docstring)
- [Package managers](#package-managers)
  - [`uv`](#uv)
    - [Install `uv`](#install-uv)
- [Quality assurance tools](#quality-assurance-tools)
  - [Dynamic analysis tools](#dynamic-analysis-tools)
    - [The `assert` statement](#the-assert-statement)
    - [`pytest`](#pytest)
  - [Static analysis tools](#static-analysis-tools)
    - [`Pylance`](#pylance)
    - [`ruff` (linter)](#ruff-linter)
  - [Code transformation tools](#code-transformation-tools)
    - [`ruff` (formatter)](#ruff-formatter)

## What is `Python`

`Python` is a general-purpose programming language. In this project, it is used to build the backend web server with [`FastAPI`](https://fastapi.tiangolo.com/).

Docs:

- [Python documentation](https://docs.python.org/3/)
- [Learn Python in Y minutes](https://learnxinyminutes.com/python/)

## Syntax

### Code blocks

`Python` uses indentation (spaces) to define code blocks instead of curly braces `{}`.

### Documentation

`Python` supports writing inline documentation as [docstrings](#docstring) embedded directly in source code.

### Docstring

A docstring is a string literal that appears as the first statement in a function, class, or module. It describes what the code does.

Docs:

- [PEP 257 – Docstring Conventions](https://peps.python.org/pep-0257/)

Example:

```python
def greet(name):
    """Return a greeting message for the given name."""
    return f"Hello, {name}!"
```

## Package managers

- [`uv`](#uv)

Docs:

- [Package manager](./package-manager.md#what-is-a-package-manager)

### `uv`

`uv` is a modern [package manager](./package-manager.md#what-is-a-package-manager) for [`Python`](#what-is-python).

#### Install `uv`

1. [Check the current shell in the `VS Code Terminal`](./vs-code.md#check-the-current-shell-in-the-vs-code-terminal).

   ([`Windows`](./operating-system.md#linux) only) Now you use a `Linux` shell.

2. Follow the [installation instructions](https://docs.astral.sh/uv/getting-started/installation/) for [`macOS`](./operating-system.md#macos) and [`Linux`](./operating-system.md#linux), even if you use `Windows`.

3. To check that `uv` is installed,

   [run in the `VS Code Terminal`](./vs-code.md#run-a-command-in-the-vs-code-terminal):

   ```terminal
   uv --version
   ```

4. The output should be similar to this:

   ```terminal
   uv 0.10.4
   ```

## Quality assurance tools

See [Quality assurance](./quality-assurance.md#what-is-quality-assurance).

Tools:

- [Dynamic analysis tools](#dynamic-analysis-tools)
- [Static analysis tools](#static-analysis-tools)
- [Code transformation tools](#code-transformation-tools)

### Dynamic analysis tools

- [The `assert` statement](#the-assert-statement)
- [`pytest`](#pytest)

Docs:

- [testing](./quality-assurance.md#testing).

#### The `assert` statement

The `assert` statement checks that a condition is true (see [Assertion](./quality-assurance.md#assertion)).
If the condition is false, the test fails with an `AssertionError`.

```python
assert result == expected
```

Docs:

- [`assert` statement](https://docs.python.org/3/reference/simple_stmts.html#the-assert-statement)

#### `pytest`

`pytest` is a testing framework for `Python`. It discovers and runs test functions automatically.

Docs:

- [`pytest` documentation](https://docs.pytest.org/)

### Static analysis tools

- [`Pylance`](#pylance)
- [`ruff` (linter)](#ruff-linter)

#### `Pylance`

A [language server](./vs-code.md#language-server) for `Python` that provides static analysis features such as type checking and detection of undefined variables.

#### `ruff` (linter)

A fast [linter](./quality-assurance.md#linting) for `Python`.

Docs:

- [`ruff` documentation](https://docs.astral.sh/ruff/)

### Code transformation tools

- [`ruff` (formatter)]

Docs:

- [Code transformation](./quality-assurance.md#code-transformation)

#### `ruff` (formatter)

`ruff` checks code for errors and style violations and automatically rewrites files to enforce a consistent style (see [Code transformation](./quality-assurance.md#code-transformation)).
