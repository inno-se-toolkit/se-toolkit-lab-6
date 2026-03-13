# Quality assurance

<h2>Table of contents</h2>

- [What is quality assurance](#what-is-quality-assurance)
- [Static analysis](#static-analysis)
  - [Linting](#linting)
  - [Type checking](#type-checking)
  - [Model checking](#model-checking)
- [Dynamic analysis](#dynamic-analysis)
  - [Testing](#testing)
    - [Assertion](#assertion)
    - [Unit test](#unit-test)
    - [End-to-end test](#end-to-end-test)
    - [Boundary value analysis](#boundary-value-analysis)
  - [Profiling](#profiling)
  - [Fuzzing](#fuzzing)
- [Code transformation](#code-transformation)
  - [Formatting](#formatting)

## What is quality assurance

<!-- TODO it's not only verification and not only about software but also about processes -->

Quality assurance is the practice of ensuring that the software works as intended.

It combines two approaches to identify problems with the code:

- [Static analysis](#static-analysis), which inspects code without running it
- [Dynamic analysis](#dynamic-analysis), which executes code with specific inputs and checks the outputs

The identified problems are fixed via:

- [Code transformation](#code-transformation)

Together, these techniques catch bugs early, prevent regressions when code changes, and document the intended behavior of a program.

## Static analysis

Static analysis checks code for errors without running it. It can detect type errors, undefined variables, and style issues.

Common methods:

- [Linting](#linting)
- [Type checking](#type-checking)

### Linting

Linting analyzes code for potential errors, bad practices, and style violations beyond what [formatting](#formatting) covers. A linter reports problems but does not rewrite code.

Examples:

- [`poe lint`](./pyproject-toml.md#poe-lint) — check [`Python`](./python.md#what-is-python) code for lint errors using `ruff`.

### Type checking

Type checking verifies that values are used consistently with their declared types — for example, that a function expecting a string is not called with an integer. A type checker reports mismatches without running the code.

Examples:

- [`poe typecheck`](./pyproject-toml.md#poe-typecheck) — run `pyright` and `ty` in sequence.
- [`Pylance`](./python.md#pylance) — provides real-time type checking in the editor.

### Model checking

Model checking verifies that a system satisfies a formal specification by systematically exploring all possible states. It is used in safety-critical domains such as hardware design and protocol verification.

## Dynamic analysis

Dynamic analysis checks code behavior by executing it. Errors are only detected when the relevant code path actually runs.

Common methods:

- [Testing](#testing)
- [Profiling](#profiling)
- [Fuzzing](#fuzzing)

### Testing

Testing verifies that code produces expected outputs for given inputs. Each test typically calls a function or sends a request, then uses [assertions](#assertion) to check the result.

Tests are usually grouped by scope — how much of the system each test exercises. Narrower tests run faster and pinpoint failures precisely; broader tests verify that components work together.

Common methods:

- [Unit testing](#unit-test)
- [End-to-end testing](#end-to-end-test)
- [Boundary value analysis](#boundary-value-analysis)

#### Assertion

An assertion is a statement that checks whether a given condition is true. If the condition is false, the assertion fails and raises an error, stopping the test immediately.

Assertions are the primary mechanism for verifying expected behavior in tests — each test typically ends with one or more assertions that confirm the code produced the right result.

Examples:

- [The `assert` statement in `Python`](./python.md#the-assert-statement)

#### Unit test

A unit test verifies that an individual function or module works correctly in isolation. Unit tests are fast because they don't depend on external services like databases or network connections.

#### End-to-end test

An end-to-end (E2E) test verifies that the full system works correctly by sending real [`HTTP` requests](./http.md#http-request) to the deployed application and checking the responses. E2E tests are slower than [unit tests](#unit-test) because they depend on running services.

In this project, E2E tests are located in `backend/tests/e2e/` and run with [`poe test-e2e`](./pyproject-toml.md#poe-test-e2e).

#### Boundary value analysis

Boundary value analysis is a testing technique that focuses on the edges of input ranges — values like `0`, `1`, an empty list, or the maximum allowed size. Bugs often occur at these boundaries because of off-by-one errors, missing edge-case handling, or incorrect comparison operators.

When writing tests, check both sides of each boundary: the value just inside the valid range and the value just outside it.

### Profiling

Profiling measures how much time or memory each part of a program uses while it runs. It helps identify performance bottlenecks — functions that run too often or take too long.

### Fuzzing

Fuzzing feeds random or malformed inputs to a program to find crashes, hangs, or unexpected behavior. It is effective at discovering edge cases that manual [testing](#testing) might miss.

## Code transformation

After problems are found, the code must be transformed.

- [Formatting](#formatting)

### Formatting

Formatting automatically adjusts code style — indentation, spacing, line length — to enforce a consistent appearance across the codebase.
A formatter rewrites files in place without changing behavior.
