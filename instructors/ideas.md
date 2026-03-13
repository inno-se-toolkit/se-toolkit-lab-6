# Ideas

- [Course - TODO](#course---todo)
- [Lab 5 - TODO](#lab-5---todo)
  - [Lab 5 - TODO - Backlog](#lab-5---todo---backlog)
  - [Lab 5 - TODO - Repo](#lab-5---todo---repo)
  - [Lab 5 - TODO - Conventions](#lab-5---todo---conventions)
  - [Lab 5 - TODO - Config](#lab-5---todo---config)
  - [Lab 5 - TODO - Skills](#lab-5---todo---skills)
  - [Lab 5 - TODO - Instructors](#lab-5---todo---instructors)
  - [Lab 5 - TODO - Wiki](#lab-5---todo---wiki)
  - [Lab 5 - TODO - Docs](#lab-5---todo---docs)
  - [Lab 5 - TODO - Contributing](#lab-5---todo---contributing)
  - [Lab 5 - TODO - Git workflow](#lab-5---todo---git-workflow)
  - [Lab 5 - TODO - Autochecker](#lab-5---todo---autochecker)
  - [Lab 5 - TODO - Setup](#lab-5---todo---setup)
  - [Lab 5 - TODO - Task 1](#lab-5---todo---task-1)
  - [Lab 5 - TODO - Task 2](#lab-5---todo---task-2)
  - [Lab 5 - TODO - Task 3](#lab-5---todo---task-3)
  - [Lab 5 - TODO - VM](#lab-5---todo---vm)
  - [Lab 5 - TODO - VS Code](#lab-5---todo---vs-code)
  - [Lab 5 - TODO - Architecture](#lab-5---todo---architecture)
- [Lab 5 - DONE](#lab-5---done)
  - [Lab 5 - DONE - Repository](#lab-5---done---repository)
  - [Lab 5 - DONE - Conventions](#lab-5---done---conventions)
  - [Lab 5 - DONE - Skills](#lab-5---done---skills)
  - [Lab 5 - DONE - Instructors](#lab-5---done---instructors)
- [Lab Observability - TODO](#lab-observability---todo)
  - [Lab Observability - TODO - Backlog](#lab-observability---todo---backlog)
  - [Lab Telegram Bot - TODO - Task 2](#lab-telegram-bot---todo---task-2)
- [Future Lab](#future-lab)
  - [Future Lab - TODO - Backlog](#future-lab---todo---backlog)
  - [Future Lab - VM setup](#future-lab---vm-setup)
  - [Hackathon](#hackathon)

## Course - TODO

- Define outcomes in instructors/course.md

## Lab 5 - TODO

### Lab 5 - TODO - Backlog

### Lab 5 - TODO - Repo

- agents.md
- remember to use .agents
- switch to pnpm

### Lab 5 - TODO - Conventions

- should a section in a sequence of steps assume the previous step?
- "frontend" and "backend" as nouns
- Rename app -> backend
- Rename `APP_` -> `BACK_`
- Add `FRONT_` suffix for front-end variables
- Always provide links to variables from .env.docker.secret
- Consistently use "API token" and "API key" naming
- setup must correspond to the current project state
- it's always "repo", not repository
- new sentence always starts on a new line
- There's always a blank line between list items
- In tasks that require prompt engineering:
  - don't provide a ready prompt first.
  - hint at what to think about when writing a prompt.
  - provide the prompt under a spoiler.
- Where possible in tasks, add tips with prompts:
  "Explain X"
  So that students know what to ask about.
- [?] troubleshooting - block quote
- setup-simple.md - a simpler version of setup.md
  must be in sync
- links should be relative markdown, not just `path/file`
  
  skills: links to conventions
- number sections
  Keep Decision 1
- Remove coverage section
- Specify severity for violations

### Lab 5 - TODO - Config

- .env.docker.secret: update caddy port - should be the biggest
- pyproject: return test-unit
- check setup corresponds to the current project state
- multiple docker compose files
- Fix config after the migration from the older repo
- Move constants with `CONST_` prefix from `.env.docker.example` to `.env.const`

### Lab 5 - TODO - Skills

- skill /fix-adjacent-links
- skill /ideate-lab
  ideate a new lab
  - for a given topic
  - with specified learning outcomes following bloom's taxonomy
  - with three required tasks and one optional task
  - in instructors/lab-plan.md
- skill /issue
- skill: review lab
  - run /review-file in parallel on tasks
  - only sonnet
- skill: review wiki
  - run /review-file in parallel on wiki files
- skill /explain-step
  - select step, then run skill on the selection
  - for students - gives complete instructions on how to do the step
- skill /explain-step-in-russian
  gives the same instructions as explain-step but in Russian
- skill /rewrite-lab <programming-language>
  
### Lab 5 - TODO - Instructors

- add tutorials for skills and devshell tools

### Lab 5 - TODO - Wiki

- [?] use mdsh for tool output
- vm docs: is this true? "# This solution won't work outside the University network."
- [?] vm: describe full vm setup step by step
- vs-code-lsp.md with examples of go to definition
- [?] reference vs-code-lsp.md in the python setup
  where testing that the extension works
- [?] What is X -> About X?
- explain "skills"
- wiki: useful-programs -> programs-used
- Add instructions for qwen by ssh
  Need browser flow for free requests
  Therefore, will have to run on the laptop and connect by ssh
- coding-agents.md - select lines and ask questions
- move to contributing/configuration:
  - dotenv-docker-secret.md and others
  - pyproject-toml.md
- remove "In this project" because they quickly get obsolete
- replace: `<term>` -> `<term>` placeholder
- agents.md - explain based on <https://www.salmanq.com/blog/simplest-agent-loop/>

### Lab 5 - TODO - Docs

- GitHub Pages with good full-text search

### Lab 5 - TODO - Contributing

- github workflows: allow PRs with [CONTRIBUTE] prefix
- github issues: add issue template for bugs in the lab, e.g. [LAB BUG]

### Lab 5 - TODO - Git workflow

- tip: suggest students to use `skill commit`
- update diagram to mention pull from upstream

### Lab 5 - TODO - Autochecker

- autochecker API:
  - clarify the formatting of the password
  - clarify where to get placeholder values when forgot
- autochecker: check the file submission size
  file attached to an issue on GitHub

### Lab 5 - TODO - Setup

- Remove info about the database table and data
  They were loaded from init.sql in the previous lab
  
  but there's no data in this lab.
  
  Can keep the pgadmin step just to check the tables.

- install nodejs and other tools via nix

- setup: set zsh + starship as default
  oh my zsh
  not as login shell because they may uninstall Nix

- Check that you run in WSL
  screenshot WSL - Ubuntu-24.04 in the lower-left corner

- Check that you have syntax highlighting in VS Code

- The instructions aren't guaranteed to work outside of Linux or macOS. This is why we require to use WSL

- install jq via nix

### Lab 5 - TODO - Task 1

- line break after the curl command
- update autochecker API

### Lab 5 - TODO - Task 2

- tasks.test -> tasks.test-unit

### Lab 5 - TODO - Task 3

- Show histogram

### Lab 5 - TODO - VM

- connect by remote ssh - check your ip to understand where you are
- [?] `Remote-SSH: Connect to Host...`
  - can't find ssh config in Linux

### Lab 5 - TODO - VS Code

- Default theme - Monokai

### Lab 5 - TODO - Architecture

- `.env.local.example` - run outside of Docker
  Alternative: enable reload in local development

## Lab 5 - DONE

### Lab 5 - DONE - Repository

- [x] Move ideas to the instructors/ideas.md.

### Lab 5 - DONE - Conventions

- conventions: prohibit agent-specific language in skills
  see contributing/conventions/agents/skills.md
- indented note is a block quote
- meeting report
  
  date and deadline in separate sections
- review which conventions aren't mentioned anywhere or mentioned without a markdown llink
- the autochecker -> `Autochecker`
- review: mark deliverables that are hard to produce without following specific steps.

### Lab 5 - DONE - Skills

- [x] fix /fix-file-by-conventions skill: write title instead of cross-out in the task report.
  Solution: cross-out, then use a skill for clearing

- [x] lab-prompts.md? - prompts for agents
  - bundle all instructions for task 1 in a readable doc
  
  Solution: We'll add a skill that explains a particular step.

### Lab 5 - DONE - Instructors

- Rename instructors/lab-design to instructors/meetings
- Use instructors/meetings just for storing meeting notes, not for the lab design.
- Check qwen works on a VM.
  it does if you copy the credentials

## Lab Observability - TODO

### Lab Observability - TODO - Backlog

- enable logging
- Implement a Status page like <https://status.claude.com/>
   Must be a separate service that checks health. Grafana?
- test front
- caddy https
- include logging
- script for database backup
- deploy via github actions
- use pnpm
- setup: install everything via nix
- grafana later when we have multiple apps

### Lab Telegram Bot - TODO - Task 2

- telegram bot task - create an issue from a group chat.

## Future Lab

### Future Lab - TODO - Backlog

- Multiple backends (Go, Haskell, TypeScript, Java)

### Future Lab - VM setup

- use [system-manager](https://github.com/numtide/system-manager)
- Migrate relevant parts of inno-se/the-guide (environments)

### Hackathon

- Teach to make meeting notes after a discussion using AI
- provide a prompt for discussing with an AI
- set up voice mode in the agent
