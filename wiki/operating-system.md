# Operating system (OS)

<h2>Table of contents</h2>

- [What is an operating system](#what-is-an-operating-system)
- [Operating systems](#operating-systems)
  - [`Linux`](#linux)
  - [`macOS`](#macos)
  - [`Windows`](#windows)
    - [`WSL`](#wsl)
- [Program](#program)
  - [Useful programs](#useful-programs)
- [Process](#process)
  - [Background process](#background-process)
  - [PID](#pid)
- [Service](#service)

## What is an operating system

An operating system (OS) is software that manages computer hardware and software resources, providing a layer between applications and the hardware.

It handles memory allocation, process scheduling, file systems, and device I/O, so that programs can run without directly interacting with hardware.

## Operating systems

### `Linux`

`Linux` is an open-source operating system commonly used for servers and [virtual machines](./vm.md).

See [`Linux`](./linux.md) for more details.

### `macOS`

`macOS` is Apple's proprietary operating system for Mac computers.

It is based on `Unix`, so many command-line tools and workflows that work on `Linux` also work on `macOS`.

### `Windows`

`Windows` is Microsoft's proprietary operating system widely used on personal computers.

It uses a different file system structure and command-line environment from `Linux` and `macOS`.

Students on `Windows` can use [`WSL`](#wsl) (Windows Subsystem for Linux) to run a `Linux` environment.

#### `WSL`

`WSL` (Windows Subsystem for Linux) is a feature of `Windows` that lets you run a `Linux` environment directly on `Windows`, without a virtual machine.

Docs:

- [`WSL` documentation](https://learn.microsoft.com/en-us/windows/wsl/)

> [!TIP]
> To use `WSL` with `VS Code`, see [(`Windows` only) Set up running `VS Code` in `WSL`](./vs-code.md#windows-only-set-up-running-vs-code-in-wsl).

## Program

A program is an executable file containing instructions that can be run by the operating system.

It's a static entity stored on disk that becomes a [process](#process) when executed.

Programs can be compiled binaries, scripts, or other executable files that perform specific tasks when run by a user or system.

### Useful programs

See [Useful programs](./useful-programs.md).

## Process

A process is an instance of a running [program](#program).

When you execute a program, the operating system creates a process that contains the program's code, memory space, variables, and system resources. Each process has a unique process ID (PID) and runs independently of other processes.

Processes can be created, managed, and terminated using various [shell commands](./shell.md#shell-command).

They form the basis of multitasking in the operating system.

### Background process

<!-- TODO -->

### PID

A PID (Process ID) is a unique numerical identifier assigned by the operating system to each running process. PIDs help the operating system to track and manage individual processes.

PIDs are used by various system commands to interact with specific processes, such as terminating them, checking their status, or monitoring their resource usage.

PIDs let the operating system handle multitasking.

## Service

A service is a long-running [process](#process) that performs specific system functions or provides functionality to other processes and applications.

Services typically start automatically during system boot and run in the background without direct user interaction. They can be managed using system service managers like `systemd`, `init`, or service scripts.

Common examples include [web servers](./web-development.md), [database servers](./database.md#database-server) (`MySQL`/`PostgreSQL`), [`SSH` daemons](./ssh.md#ssh-daemon), and network services.

Services often [listen on specific ports](./computer-networks.md#listen-on-a-port) to handle incoming requests.

They form the backbone of system functionality and network communications.
