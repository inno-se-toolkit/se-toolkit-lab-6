\# Implementation Plan: The Documentation Agent



\*\*Goal:\*\* Extend agent.py with tools to read wiki files.



\*\*Tools:\*\*

\- `list\_files(path)`: returns directory listing (no traversal outside project)

\- `read\_file(path)`: returns file contents (no traversal outside project)



\*\*Agentic loop:\*\*

1\. Send user question + tool definitions to LLM

2\. If tool\_calls → execute, append results, repeat

3\. If no tool\_calls → output final answer with `source` field

4\. Max 10 iterations



\*\*Security:\*\* Use `os.path.abspath` to prevent directory traversal.

