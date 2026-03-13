# Shell

<h2>Table of contents</h2>

- [What is a shell](#what-is-a-shell)
  - [Login shell](#login-shell)
  - [`Linux` shell](#linux-shell)
- [Shell variants](#shell-variants)
  - [`bash`](#bash)
  - [`zsh`](#zsh)
  - [`Git Bash` (`Windows`)](#git-bash-windows)
- [Shell profile](#shell-profile)
  - [Reload the shell profile](#reload-the-shell-profile)
- [Shell prompt](#shell-prompt)
- [Shell command](#shell-command)
- [Current working directory](#current-working-directory)
  - [Show the current working directory (full path)](#show-the-current-working-directory-full-path)
  - [Check the current directory is `<directory-name>`](#check-the-current-directory-is-directory-name)
  - [Navigate directories](#navigate-directories)
- [Useful commands](#useful-commands)
  - [Check what shell is running](#check-what-shell-is-running)

## What is a shell

An [operating system](./operating-system.md) shell is a computer program that provides relatively broad and direct access to the system on which it runs.
[[source](https://en.wikipedia.org/wiki/Shell_(computing))]

### Login shell

A login shell is started when a user logs in to the system, for example via [`SSH`](./ssh.md#what-is-ssh).
It reads login-specific configuration files such as `~/.bash_profile` or `~/.profile`.

> [!NOTE]
> A `VS Code` terminal is typically a non-login shell and reads `~/.bashrc` instead.

### `Linux` shell

Used in the docs to refer to a [shell](#shell) opened in [`Linux`](./operating-system.md#linux).

If using [`Windows`](./operating-system.md#windows), [switch to the `Linux` shell](./vs-code.md#windows-only-switch-to-the-linux-shell-for-the-vs-code-terminal).

## Shell variants

<!-- no toc -->
- [`bash`](#bash)
- [`Git Bash` (`Windows`)](#git-bash-windows)
- [`zsh`](#zsh)

### `bash`

`Bash` (short for "Bourne Again SHell") is an interactive command interpreter and scripting language developed for `Unix`-like operating systems (e.g., [`Linux`](./linux.md#what-is-linux)).
[[source](https://en.wikipedia.org/wiki/Bash_(Unix_shell))]

> [!NOTE]
> `Bash` is the default login shell for `Ubuntu`.

`bash` is the most common shell in learning materials and server docs.

> [!NOTE]
> On `Windows`, you must to [open a directory in `WSL`](./vs-code.md#windows-only-open-the-directory-in-wsl) to run `bash`.

See also: [`Bash`](./bash.md).

### `zsh`

`zsh` is the default shell on modern `macOS` and is also common on Linux.
Most `bash` commands in this course work in `zsh` as well.

### `Git Bash` (`Windows`)

`Git Bash` is a terminal shipped with `Git for Windows`.
It provides a `Unix`-like shell environment on `Windows`.

> [!IMPORTANT]
> Don't use it in the `VS Code Terminal`.
>
> The terminal commands in the lab may not work outside of [`bash`](#bash) and [`zsh`](#zsh).
>
> [Switch to the `Linux` shell](./vs-code.md#windows-only-switch-to-the-linux-shell-for-the-vs-code-terminal).

## Shell profile

A shell profile is a configuration file that the shell reads automatically when it starts.
It is used to set environment variables, define aliases, and customize the [shell](#what-is-a-shell) environment.

Common profile files:

- `~/.bashrc` — read by `bash` for every new non-login interactive shell (e.g., a `VS Code` terminal).
- `~/.bash_profile` — read by `bash` for [login shells](#login-shell) (e.g., an [`SSH`](./ssh.md#what-is-ssh) session).
- `~/.zshrc` — read by `zsh` for every new interactive shell.

### Reload the shell profile

1. To reload the shell profile and apply changes to the current session,

   [run in the `VS Code Terminal`](./vs-code.md#run-a-command-in-the-vs-code-terminal):

   ```terminal
   source ~/.bashrc
   ```

## Shell prompt

The shell prompt is the text the shell displays before each command, indicating it is ready to accept input.
It typically shows the current [user](./operating-system.md#user), machine name, and [working directory](#current-working-directory).

A typical `bash` prompt looks like:

```terminal
username@hostname:~/directory$
```

> [!NOTE]
> The `$` at the end indicates a regular user.
> A `#` indicates the [root](./linux.md#the-root-user) (admin) user.

## Shell command

A shell command is text you type at the [shell prompt](#shell-prompt) and execute by pressing `Enter`.
It consists of a command name, optionally followed by arguments and flags.

```terminal
<command> [flags] [arguments]
```

Example:

```terminal
ls -a .
```

Here `ls` is the command, `-a` is a flag (include hidden files), and `.` is the argument (the [current directory](#current-working-directory)).

## Current working directory

The current working directory is the directory where commands run by default.

### Show the current working directory (full path)

1. To show the current working directory,

   [run in the `VS Code Terminal`](./vs-code.md#run-a-command-in-the-vs-code-terminal):

   ```terminal
   pwd
   ```

### Check the current directory is `<directory-name>`

1. [Show the current working directory](#show-the-current-working-directory-full-path).
2. It should end in `<directory-name>`.

### Navigate directories

1. To navigate to a directory,

   [run in the `VS Code Terminal`](./vs-code.md#run-a-command-in-the-vs-code-terminal):

   ```terminal
   cd /
   cd ~
   cd ..
   ```

To list files in the current working directory,

[run in the `VS Code Terminal`](./vs-code.md#run-a-command-in-the-vs-code-terminal):

```terminal
ls
```

When a command fails with "No such file or directory", verify your current directory first using `pwd`.

## Useful commands

These commands run programs:

- `pwd` - show current directory.
- `ls` - list files.
- `cd <dir>` - go to a directory.
- `cat <file-path>` - print the content of a file at the [`<file-path>`](./file-system.md#file-path).

### Check what shell is running

1. To check what shell is running,

   [run in the `VS Code Terminal`](./vs-code.md#run-a-command-in-the-vs-code-terminal):

   ```terminal
   echo "$SHELL"
   ```
