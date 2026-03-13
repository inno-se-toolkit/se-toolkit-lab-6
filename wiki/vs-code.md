# `VS Code`

<h2>Table of contents</h2>

- [What is `VS Code`](#what-is-vs-code)
- [`Basic Layout`](#basic-layout)
- [`Custom Layout`](#custom-layout)
  - [Move the `Primary Sidebar` to the right](#move-the-primary-sidebar-to-the-right)
- [`Editor`](#editor)
- [`Activity Bar`](#activity-bar)
- [`Primary Sidebar`](#primary-sidebar)
  - [Open the `Primary Sidebar`](#open-the-primary-sidebar)
  - [Switch between `Primary Sidebar` views](#switch-between-primary-sidebar-views)
- [`Status Bar`](#status-bar)
- [`Editor Toolbar`](#editor-toolbar)
- [`Command Palette`](#command-palette)
  - [Open the `Command Palette`](#open-the-command-palette)
  - [Run a command using the `Command Palette`](#run-a-command-using-the-command-palette)
  - [Select an option from a list](#select-an-option-from-a-list)
- [`Panel Toolbar`](#panel-toolbar)
- [`VS Code Terminal`](#vs-code-terminal)
  - [Open the `VS Code Terminal`](#open-the-vs-code-terminal)
  - [Close the `VS Code Terminal`](#close-the-vs-code-terminal)
  - [Open a new `VS Code Terminal`](#open-a-new-vs-code-terminal)
  - [Switch to another `VS Code Terminal`](#switch-to-another-vs-code-terminal)
  - [Delete a `VS Code Terminal`](#delete-a-vs-code-terminal)
  - [Copy text inside the `VS Code Terminal`](#copy-text-inside-the-vs-code-terminal)
  - [Paste text inside the `VS Code Terminal`](#paste-text-inside-the-vs-code-terminal)
  - [Look at the open `VS Code Terminal`s](#look-at-the-open-vs-code-terminals)
  - [Look at the current `VS Code Terminal`](#look-at-the-current-vs-code-terminal)
  - [Check the current shell in the `VS Code Terminal`](#check-the-current-shell-in-the-vs-code-terminal)
  - [Expand the sidebar with open `VS Code Terminal`s](#expand-the-sidebar-with-open-vs-code-terminals)
  - [(`Windows` only) Switch to the `Linux` shell for the `VS Code Terminal`](#windows-only-switch-to-the-linux-shell-for-the-vs-code-terminal)
  - [Run a command in the `VS Code Terminal`](#run-a-command-in-the-vs-code-terminal)
- [`VS Code Explorer`](#vs-code-explorer)
  - [Open the `VS Code Explorer`](#open-the-vs-code-explorer)
  - [Open the local file using the `VS Code Explorer`](#open-the-local-file-using-the-vs-code-explorer)
- [`Source Control`](#source-control)
  - [Open the `Source Control`](#open-the-source-control)
  - [Close the `Source Control`](#close-the-source-control)
- [`Extensions`](#extensions)
  - [Open the `Extensions`](#open-the-extensions)
  - [Install the `VS Code` extension](#install-the-vs-code-extension)
  - [Filter the `VS Code` extensions](#filter-the-vs-code-extensions)
  - [Install the recommended `VS Code` extensions](#install-the-recommended-vs-code-extensions)
- [Keyboard shortcuts](#keyboard-shortcuts)
  - [Frequently used shortcuts](#frequently-used-shortcuts)
    - [Shortcut: `Go back`](#shortcut-go-back)
    - [Shortcut: Switch to the previous editor](#shortcut-switch-to-the-previous-editor)
    - [Shortcut: Search in the current editor](#shortcut-search-in-the-current-editor)
    - [Shortcut: Search in all files](#shortcut-search-in-all-files)
    - [Shortcut: Toggle line comment](#shortcut-toggle-line-comment)
  - [Set a shortcut](#set-a-shortcut)
- [Workspace settings](#workspace-settings)
  - [Change the workspace settings](#change-the-workspace-settings)
- [Common actions](#common-actions)
  - [Open the directory](#open-the-directory)
    - [(`Windows` only) Open the directory in `WSL`](#windows-only-open-the-directory-in-wsl)
    - [(`Windows` only) Reopen the directory in `WSL`](#windows-only-reopen-the-directory-in-wsl)
  - [Open the file](#open-the-file)
    - [Open the file using `Quick Open`](#open-the-file-using-quick-open)
    - [Open the file using `code`](#open-the-file-using-code)
    - [Open the file using a context menu](#open-the-file-using-a-context-menu)
  - [Open the `Markdown` preview](#open-the-markdown-preview)
- [Language server](#language-server)
  - [Type on hover](#type-on-hover)
  - [Docs on hover](#docs-on-hover)
  - [Go to the definition](#go-to-the-definition)
  - [Rename a symbol](#rename-a-symbol)
- [Set up `VS Code`](#set-up-vs-code)
  - [Install `VS Code`](#install-vs-code)
  - [(`Windows` only) Set up running `VS Code` in `WSL`](#windows-only-set-up-running-vs-code-in-wsl)
  - [(`macOS` only) Add `VS Code` to `PATH`](#macos-only-add-vs-code-to-path)

> [!IMPORTANT]
> The first [keyboard shortcut](#keyboard-shortcuts) is always for `Linux`.
> It usually coincides with the shortcut for `Windows`.
>
> You can check shortcuts for your platform in the [reference](https://code.visualstudio.com/docs/configure/keybindings#_keyboard-shortcuts-reference).

## What is `VS Code`

`VS Code` (`Visual Studio Code`) is a free, open-source code editor made by `Microsoft`. It provides features like syntax highlighting, a built-in [terminal](#vs-code-terminal), [extensions](#extensions), and [`Git`](./git.md) integration.

Docs:

- [Visual Studio Code documentation](https://code.visualstudio.com/docs)
- [`VS Code` on `GitHub`](https://github.com/microsoft/vscode)

## `Basic Layout`

Default user interface (UI).

Docs:

- [Basic layout](https://code.visualstudio.com/docs/getstarted/userinterface#_basic-layout)
- [Visual Studio Code tips and tricks](https://code.visualstudio.com/docs/getstarted/tips-and-tricks)
- [UX Guidelines](https://code.visualstudio.com/api/ux-guidelines/overview)

Schema that we use in docs:

<img alt="Basic Layout schema" src="./images/vs-code/vs-code-ui.drawio.svg" style="width:100%"></img>

## `Custom Layout`

Custom UI appearance.

Docs:

- [Customizing VS Code's UI for Productivity](https://www.youtube.com/watch?v=nORT3-kONgA)
- [Custom Layout](https://code.visualstudio.com/docs/configure/custom-layout)

Actions:

- [Move the `Primary Sidebar` to the right](#move-the-primary-sidebar-to-the-right)

### Move the `Primary Sidebar` to the right

[Move](https://code.visualstudio.com/docs/configure/custom-layout#_primary-side-bar) the [`Primary Sidebar`](#primary-sidebar) to the right so that it doesn't move your code whenever the `Primary Sidebar` opens.

[Change the workspace settings](#change-the-workspace-settings) if you don't like that the `Primary Sidebar` on the right side.

## `Editor`

Space where you can edit files.

Location: see [`Basic Layout`](#basic-layout).

Docs:

- [Basic editing](https://code.visualstudio.com/docs/editing/codebasics)

## `Activity Bar`

Menus of extensions on a side of the [`Editor`](#editor).

Location: see [`Basic Layout`](#basic-layout).

## `Primary Sidebar`

Views on a side of the [`Editor`](#editor). See [`Basic Layout`](#basic-layout).

Docs:

- [Primary Side Bar](https://code.visualstudio.com/docs/configure/custom-layout#_primary-side-bar)

Actions:

- [Open the `Primary Sidebar`](#open-the-primary-sidebar)
- [Switch between `Primary Sidebar` views](#switch-between-primary-sidebar-views)

### Open the `Primary Sidebar`

For example, [open the `Source Control`](#open-the-source-control).

### Switch between `Primary Sidebar` views

Click icons in the [`Activity Bar`](#activity-bar).

## `Status Bar`

Statuses and menus of extensions at the bottom of the `VS Code` window.

- [docs](https://code.visualstudio.com/docs/getstarted/userinterface#_basic-layout)

<img alt="Status Bar (left)" src="./images/vs-code/status-bar-left.png" style="width:400px"></img>

<img alt="Status Bar (right)" src="./images/vs-code/status-bar-right.png" style="width:400px"></img>

## `Editor Toolbar`

Quick actions buttons located above the [`Editor`](#editor).

- [docs](https://code.visualstudio.com/api/ux-guidelines/overview#editor-toolbar)

<img alt="Editor Toolbar" src="./images/vs-code/editor-toolbar.png" style="width:400px"></img>

## `Command Palette`

Run editor commands in `VS Code`.

Docs:

- [Command Palette](https://code.visualstudio.com/docs/getstarted/userinterface#_command-palette)
- [Access commands with the Command Palette](https://code.visualstudio.com/docs/getstarted/getting-started#_access-commands-with-the-command-palette)

Actions:

- [Open the `Command Palette`](#open-the-command-palette)
- [Run a command using the `Command Palette`](#run-a-command-using-the-command-palette)

### Open the `Command Palette`

1. Press `Ctrl+Shift+P` (`Cmd+Shift+P` on `macOS`).

### Run a command using the `Command Palette`

1. [Open the `Command Palette`](#open-the-command-palette).
2. Start typing a command.
3. [Select](#select-an-option-from-a-list) the necessary command.

### Select an option from a list

Method 1:

1. Click the option.

Method 2:

1. Change the highlighted option using `UpArrow` and `DownArrow` on your keyboard.
2. Press `Enter` to confirm the option.

## `Panel Toolbar`

Switch between panels.

Location: see [`Basic Layout`](#basic-layout).

Left side with tabs:

<img alt="Panel Toolbar Left" src="./images/vs-code/panel-toolbar-left.png" style="width:400px"></img>

Right side (depends on the current tab; this one is for the `VS Code Terminal`):

<img alt="Panel Toolbar Right" src="./images/vs-code/panel-toolbar-left.png" style="width:400px"></img>

## `VS Code Terminal`

Run terminal commands inside `VS Code`.

Docs:

- [Getting started with the terminal](https://code.visualstudio.com/docs/terminal/getting-started)

Actions:

- [Open the `VS Code Terminal`](#open-the-vs-code-terminal)
- [Close the `VS Code Terminal`](#close-the-vs-code-terminal)
- [Open a new `VS Code Terminal`](#open-a-new-vs-code-terminal)
- [Switch to another `VS Code Terminal`](#switch-to-another-vs-code-terminal)
- [Copy text inside the `VS Code Terminal`](#copy-text-inside-the-vs-code-terminal)
- [Paste text inside the `VS Code Terminal`](#paste-text-inside-the-vs-code-terminal)
- [Run a command in the `VS Code Terminal`](#run-a-command-in-the-vs-code-terminal)

### Open the `VS Code Terminal`

Press ```Ctrl+` ``` (```Cmd+` ``` on `macOS`)

### Close the `VS Code Terminal`

Press ```Ctrl+` ``` (```Cmd+` ``` on `macOS`)

### Open a new `VS Code Terminal`

Method 1:

1. Press ```Ctrl+Shift+` ``` (```Cmd+Shift+` ``` on `macOS`).

Method 2:

1. [Open the `VS Code Terminal`](#open-the-vs-code-terminal).
2. Click the `+` icon.

   <img alt="New Terminal" src="./images/vs-code/terminal-new-plus.png" style="width:400px"></img>

### Switch to another `VS Code Terminal`

Method 1:

1. [Open the `VS Code Terminal`](#open-the-vs-code-terminal).
2. Click a terminal tab in the terminal panel.

    <img alt="Switch Terminal" src="./images/vs-code/terminal-panel-switch.png" style="width:400px"></img>

Method 2:

1. [Open the `VS Code Terminal`](#open-the-vs-code-terminal).
1. Press `Ctrl+PageDown` / `Ctrl+PageUp` (`Cmd+Shift+]` / `Cmd+Shift+[` on `macOS`).

### Delete a `VS Code Terminal`

1. [Open the `VS Code Terminal`](#open-the-vs-code-terminal).
2. [Look at the open `VS Code Terminal`s](#look-at-the-open-vs-code-terminals).
3. Go to the `VS Code Terminal` that should be deleted.
4. Delete the terminal.

   <img alt="Terminal - Delete Terminal" src="./images/vs-code/terminal-delete-terminal.png" style="width:200px"></img>

### Copy text inside the `VS Code Terminal`

1. Select text.
2. Press `Ctrl+Shift+C` (`Cmd+C` on `macOS`).

### Paste text inside the `VS Code Terminal`

`Ctrl+Shift+V` (`Cmd+V` on `macOS`, `Ctrl+V` on `Windows`)

### Look at the open `VS Code Terminal`s

1. [Open the `VS Code Terminal`](#open-the-vs-code-terminal).
2. Look at the sidebar with a list of `VS Code Terminal`s.

   <img alt="Open Terminals" src="./images/vs-code/terminal-current-terminal.png" style="width:300px"></img>

   <img alt="Open Terminals - Narrow" src="./images/vs-code/terminal-open-terminals-narrow.png" style="width:300px"></img>

   If you don't see a list of `VS Code Terminal`s on the right, you have only one `VS Code Terminal` open.
3. (Optional) [Expand the sidebar with open `VS Code Terminal`s](#expand-the-sidebar-with-open-vs-code-terminals).

### Look at the current `VS Code Terminal`

1. [Open the `VS Code Terminal`](#open-the-vs-code-terminal).
2. Look at one of these:
   - The [`Panel Toolbar`](#panel-toolbar):

      <img alt="Current Terminal Shell" src="./images/vs-code/terminal-single-current-shell-bash.png" style="width:300px"></img>

   - Current (highlighted) `VS Code Terminal`:

      <img alt="Terminals" src="./images/vs-code/terminal-current-terminal.png" style="width:300px"></img>

### Check the current shell in the `VS Code Terminal`

1. [Look at the current `VS Code Terminal`](#look-at-the-current-vs-code-terminal).

   You should see on:

   - `Windows`: `bash`

      If you see something else, you're not using [`VS Code`](#what-is-vs-code) in [`Linux`](./linux.md#what-is-linux).

      [Switch to the `Linux` shell for the `VS Code Terminal`](#windows-only-switch-to-the-linux-shell-for-the-vs-code-terminal).

   - `macOS`, `Linux`: [`zsh`](./shell.md#zsh), [`bash`](./shell.md#bash), or another [shell](./shell.md#shell-variants) name

### Expand the sidebar with open `VS Code Terminal`s

1. [Open the `VS Code Terminal`](#open-the-vs-code-terminal).
2. Hover, click, and move the mouse:

   <img alt="Terminal - Expand Open Terminals" src="./images/vs-code/terminal-expand-open-terminals.png" style="width:300px"></img>

### (`Windows` only) Switch to the `Linux` shell for the `VS Code Terminal`

> [!NOTE]
> See [`Linux` shell](./shell.md#linux-shell).

1. Make sure you can [run `VS Code` in `WSL`](#windows-only-set-up-running-vs-code-in-wsl).
2. [Reopen the directory in `WSL`](#windows-only-reopen-the-directory-in-wsl)
3. [Run using the `Command Palette`](#run-a-command-using-the-command-palette):
   `Terminal: Select Default Profile`.
4. There can be the following cases.

   - Case 1 (bad): You don't have the recommended extensions installed.

     <img alt="Terminal Default Profile - Bad Options" src="./images/vs-code/command-palette-default-terminal-profile-bad-options.png" style="width:400px"></img>

     Return to the first step and make sure you can [run `VS Code` in `WSL`](#windows-only-set-up-running-vs-code-in-wsl).

   - Case 2 (good): You're running `VS Code` outside `WSL`.

     <img alt="Terminal Default Profile - Outside WSL" src="./images/vs-code/command-palette-default-terminal-profile-outside-wsl-wsl.png" style="width:400px"></img>

     [Switch to the `Linux` shell for the `VS Code Terminal`](#windows-only-switch-to-the-linux-shell-for-the-vs-code-terminal) again.

   - Case 3 (the best): You're running `VS Code` inside `WSL`.
     You've probably [opened the directory inside `WSL`](#windows-only-open-the-directory-in-wsl).
     This is the best case.

     <img alt="Terminal Default Profile - Bash" src="./images/vs-code/command-palette-default-terminal-profile-bash.png" style="width:400px"></img>

     [Select](#select-an-option-from-a-list) `bash`.
5. [Open the `VS Code Terminal`](#open-the-vs-code-terminal).
6. [Delete all `VS Code Terminal`s](#delete-a-vs-code-terminal).
7. [Open a new `VS Code Terminal`](#open-a-new-vs-code-terminal).

### Run a command in the `VS Code Terminal`

1. [Open the `VS Code Terminal`](#open-the-vs-code-terminal).
2. [Check the current shell in the `VS Code Terminal`](#check-the-current-shell-in-the-vs-code-terminal).
3. [Check whether you run in the `SSH` shell](./ssh.md#check-whether-you-run-an-ssh-shell) and decide whether you need to run an [SSH shell](./ssh.md#ssh-shell).
4. Write or [paste](#paste-text-inside-the-vs-code-terminal) a [command](./shell.md#shell-command) or commands.
5. Press `Enter`.

## `VS Code Explorer`

View the file tree.

Location: [`Activity Bar`](#activity-bar).

Docs:

- [Explorer view](https://code.visualstudio.com/docs/getstarted/userinterface#_explorer-view)

Actions:

- [Open the `VS Code Explorer`](#open-the-vs-code-explorer)
- [Open the local file using the `VS Code Explorer`](#open-the-local-file-using-the-vs-code-explorer)

### Open the `VS Code Explorer`

1. Go to the [`Activity Bar`](#activity-bar).
2. Click the `Explorer` icon.

   <img alt="Explorer" src="./images/vs-code/activity-bar-explorer.png" style="width:100px"></img>

### Open the local file using the `VS Code Explorer`

1. [Open the `Explorer`](#open-the-vs-code-explorer).
2. Search for the file in the file tree.
3. Click it.

## `Source Control`

Interact with `Git` via `VS Code` UI.

Docs:

- [Source Control in VS Code](https://code.visualstudio.com/docs/sourcecontrol/overview)

Actions:

- [Open the `Source Control`](#open-the-source-control)
- [Close the `Source Control`](#close-the-source-control)

### Open the `Source Control`

Method 1:

1. Go to the [`Activity Bar`](#activity-bar).
2. Click `Source Control`.

   <img alt="Activity Bar - Source Control" src="./images/vs-code/activity-bar-source-control.png" style="width:100px"></img>
3. Click `CHANGES` to uncollapse the view.

   <img alt="Source Control - Changes" src="./images/vs-code/source-control-changes.png" style="width:100px"></img>
  
Method 2:

1. Press `Ctrl+Shift+G G` (`Ctrl+Shift+G` on `macOS`)
2. Click `CHANGES` to uncollapse the view.

### Close the `Source Control`

Method 1:

1. Go to the [`Activity Bar`](#activity-bar)
2. Click `Source Control`.

   <img alt="Explorer" src="./images/vs-code/activity-bar-source-control.png" style="width:100px"></img>

Method 2:

1. Click outside of the [`Editor`](#editor).
2. Press `Ctrl+B` (`Cmd+B` on `macOS`).

## `Extensions`

Install extensions for `VS Code` from [`VS Code Marketplace`](https://marketplace.visualstudio.com/vscode) to enable new functionality.

Docs:

- [Extension Marketplace](https://code.visualstudio.com/docs/configure/extensions/extension-marketplace)

Actions:

- [Open the `Extensions`](#open-the-extensions)
- [Filter the `VS Code` extensions](#filter-the-vs-code-extensions)
- [Install the recommended `VS Code` extensions](#install-the-recommended-vs-code-extensions)

### Open the `Extensions`

Method 1:

1. Go to the [`Activity Bar`](#activity-bar).
2. Click the icon `Extensions`.

Method 2:

1. Press `Ctrl+Shift+X` (`Cmd+Shift+X` on `macOS`).

### Install the `VS Code` extension

1. [Open the `Extensions`](#open-the-extensions).
2. Write:
   - Option 1: the extension name

      Example: `GitHub Copilot Chat`
   - Option 2: the extension identifier

      Format: `<extension-publisher>.<extension-name>`

      Example: `github.copilot-chat`.
3. Click the extension.
4. Click `Install`.

### Filter the `VS Code` extensions

1. [Open the `Extensions`](#open-the-extensions).
2. Click the icon `Filter Extensions...`.

   <img alt="Filter Extensions" src="./images/vs-code/extensions-filter.png" style="width:400px"></img>
3. A menu will open.
4. Select a filter in the menu and click it to apply the filter.

### Install the recommended `VS Code` extensions

> [!NOTE]
> Recommended extensions are listed in [`.vscode/extensions.json`](../.vscode/extensions.json).

1. [Open in `VS Code` the directory](#open-the-directory) that contains `.vscode/extensions.json`.
2. [Filter the `VS Code` extensions](#filter-the-vs-code-extensions).
3. Click `Recommended` in the menu.
4. Click `WORKSPACE RECOMMENDATIONS` to uncollapse this view.
5. Click the icon `Install Workspace Recommended extensions`.

   <img alt="Install Workspace Recommended Extensions" src="./images/vs-code/extensions-install-workspace-recommended.png" style="width:400px"></img>

**Tip:** (`Windows` only) If you want these extensions to be available when you open `VS Code` not in `WSL`, complete these steps again without first opening the directory in `WSL` .

## Keyboard shortcuts

Keyboard shortcuts for various commands.

Docs:

- [Keyboard Shortcuts reference](https://code.visualstudio.com/docs/configure/keybindings#_keyboard-shortcuts-reference)
- [Keyboard Shortcuts editor](https://code.visualstudio.com/docs/configure/keybindings#_keyboard-shortcuts-editor)

### Frequently used shortcuts

- [Go back](#shortcut-go-back)
- [Switch to the previous editor](#shortcut-switch-to-the-previous-editor)
- [Search in the current editor](#shortcut-search-in-the-current-editor)
- [Search in all files](#shortcut-search-in-all-files)
- [Toggle line comment](#shortcut-toggle-line-comment)

#### Shortcut: `Go back`

`Ctrl+Alt+-` (`Ctrl+-` on `macOS`)

You can [set another shortcut](#set-a-shortcut):

- `<command-name>` is `Go Back`;
- Get the `Alt+-` shortcut by typing `Alt`, then `-`.

#### Shortcut: Switch to the previous editor

`Ctrl+Tab`

#### Shortcut: Search in the current editor

`Ctrl+F` (`Cmd+F` on `macOS`)

#### Shortcut: Search in all files

`Ctrl+Shift+F` (`Cmd+Shift+F` on `macOS`)

#### Shortcut: Toggle line comment

1. Select a line or place cursor at that line.
2. Press `Ctrl+/` (`Cmd+/` on `macOS`)

> [!TIP]
> This shortcut also works for a sequence of lines:
>
> 1. Select lines.
> 2. Press the shortcut.

### Set a shortcut

1. [Run using the `Command Palette`](#run-a-command-using-the-command-palette):
   `Preferences: Open Keyboard Shortcuts`.
2. Write the keybinding name.
3. In the `Command column`, find the `<command-name>`.
4. Double-click the row with that command.
5. Type the shortcut.
6. (Optional) Press `Esc` to reset the input.
7. Press `Enter` to save the shortcut.

## Workspace settings

`VS Code` settings for the workspace.

Docs:

- [What is a VS Code workspace?](https://code.visualstudio.com/docs/editing/workspaces/workspaces)
- [Workspace settings](https://code.visualstudio.com/docs/configure/settings#_workspace-settings)
- [Settings JSON file](https://code.visualstudio.com/docs/configure/settings#_settings-json-file)

Settings for this workspace are in [`.vscode/settings.json`](../.vscode/settings.json).

### Change the workspace settings

Here are some [workspace settings](#workspace-settings) that you can change:

- [`files.autoSave`](https://code.visualstudio.com/docs/editing/codebasics#_save-auto-save) - Enabled to save your work if VS Code closes;
- [`editor.formatOnSave`](https://code.visualstudio.com/docs/editing/codebasics#_formatting) - Enabled to run formatters when you press `Ctrl+S` (or `Cmd+S` on `macOS`) to save code.
- `Markdown` editor and preview [synchronization settings](https://code.visualstudio.com/docs/languages/markdown#_editor-and-preview-synchronization) - Disabled for smoother scrolling of the editor and the preview.

## Common actions

### Open the directory

> [!NOTE]
> The `<directory-name>` is the name of a directory (without `<` and `>`) that you want to open.
>
> Example: `software-engineering-toolkit`

1. [Run using the `Command Palette`](./vs-code.md#command-palette):
   `File: Open Folder...`
2. Find the directory `<directory-name>`.
3. Open this directory.

   `VS Code` should now open in that directory.
4. [Open the `Explorer`](./vs-code.md#open-the-vs-code-explorer).

   You should see `<DIRECTORY-NAME>` there.

   Example: `SOFTWARE-ENGINEERING-TOOLKIT`
5. (`Windows` only) [Reopen the directory in `WSL`](#windows-only-reopen-the-directory-in-wsl)
   to use the [file system](./file-system.md#what-is-a-file-system) of [`Linux`](./linux.md#what-is-linux).

#### (`Windows` only) Open the directory in `WSL`

1. [Run using the `Command Palette`](#command-palette):
   `WSL: Open Folder in WSL...`
2. Click `Show Local`.
3. Select the directory.
4. [Check the current shell in the `VS Code Terminal`](#check-the-current-shell-in-the-vs-code-terminal).

#### (`Windows` only) Reopen the directory in `WSL`

1. [Run using the `Command Palette`](./vs-code.md#run-a-command-using-the-command-palette):
   `WSL: Reopen Folder in WSL`.
2. Choose `Ubuntu 24.04`.
3. If you don't see such an option, [set up running `VS Code` in `WSL`](#windows-only-set-up-running-vs-code-in-wsl)

### Open the file

<!-- no toc -->
- Method 1: [Open the local file using `VS Code Explorer`](#open-the-local-file-using-the-vs-code-explorer)
- Method 2: [Open the file using `Quick Open`](#open-the-file-using-quick-open)
- Method 3: [Open the file using `code`](#open-the-file-using-code)
- Method 4: [Open the file using a context menu](#open-the-file-using-a-context-menu)

#### Open the file using `Quick Open`

1. Press `Ctrl+P` (`Cmd+P` on `macOS`).
2. Start typing the name of the file.
3. [Select](#select-an-option-from-a-list) the file.

#### Open the file using `code`

1. [Open a new `VS Code Terminal`](#open-a-new-vs-code-terminal) if something is running in your current `VS Code Terminal`.
2. To open a file from the terminal,

   [run in the `VS Code Terminal`](#run-a-command-in-the-vs-code-terminal):

   ```terminal
   code <file-path>
   ```

   See [`<file-path>`](./file-system.md#file-path).

   **Note:** the file will be created if it doesn't yet exist.

   <details><summary><b>Troubleshooting (click to open)</b></summary>

   <h4>(<code>macOS</code> only) <code>command code doesn't exist</code></h4>

   [Add `VS Code` to `PATH`](#macos-only-add-vs-code-to-path).

   </details>

#### Open the file using a context menu

1. Right-click a file.
2. Find `Open with...` or similar.
3. Choose `VS Code`.

### Open the `Markdown` preview

> [!NOTE]
> See [`Markdown`](./file-formats.md#markdown).

Method 1:

1. Go to the [`Editor Toolbar`](#editor-toolbar).
2. Click `Open Preview to the Side`.

Method 2:

1. [Run using the `Command Palette`](#run-a-command-using-the-command-palette):

  `Markdown: Open Preview to the Side`

## Language server

A language server provides smart features for a programming language: type information, documentation, navigation, and refactoring.

`VS Code` uses the [Language Server Protocol](https://microsoft.github.io/language-server-protocol/) to communicate with language servers.

Docs:

- [Language Server Protocol](https://code.visualstudio.com/api/language-extensions/language-server-extension-guide)

Actions:

- [Type on hover](#type-on-hover)
- [Docs on hover](#docs-on-hover)
- [Go to the definition](#go-to-the-definition)
- [Rename a symbol](#rename-a-symbol)

### Type on hover

1. Hover over a variable, function, or other symbol.
2. A tooltip will show the type information.

### Docs on hover

1. Hover over a variable, function, or other symbol.
2. A tooltip will show the documentation (if available).

### Go to the definition

Method 1:

1. Hold `Ctrl`/`Alt` (`Cmd` on `macOS`).
2. Click the symbol.

Method 2:

1. Right-click the symbol.
2. Click `Go to Definition`.

Method 3:

1. Place the cursor on the symbol.
2. Press `F12`.

### Rename a symbol

Method 1:

1. Right-click the symbol.
2. Click `Rename Symbol`.
3. Type the new name.
4. Press `Enter`.

Method 2:

1. Place the cursor on the symbol.
2. Press `F2`.
3. Type the new name.
4. Press `Enter`.

## Set up `VS Code`

1. [Install `VS Code`](#install-vs-code)
2. [(`Windows` only) Set up running `VS Code` in `WSL`](#windows-only-set-up-running-vs-code-in-wsl).
3. [(`macOS` only) Add `VS Code` to `PATH`](#macos-only-add-vs-code-to-path).

### Install `VS Code`

Follow the installation instructions for your platform:

- [`Linux`](https://code.visualstudio.com/docs/setup/linux#_install-vs-code-on-linux)
- [`macOS`](https://code.visualstudio.com/docs/setup/mac#_install-vs-code-on-macos)
- [`Windows`](https://code.visualstudio.com/docs/setup/windows#_install-vs-code-on-windows)

### (`Windows` only) Set up running `VS Code` in `WSL`

<img alt="VS Code and WSL" src="./images/vs-code/vs-code-wsl.png" style="width:400px"></img>

[image source](https://code.visualstudio.com/docs/remote/wsl)

Complete these steps:

1. [Enable `WSL`](https://code.visualstudio.com/docs/remote/wsl-tutorial#_enable-wsl).
2. Open a terminal (not the `VS Code Terminal`).
3. To install `Ubuntu` in `WSL`,

   [run in the `VS Code Terminal`](#run-a-command-in-the-vs-code-terminal):

   ```terminal
   wsl --install -d Ubuntu-24.04
   ```

   **Note:** [`Ubuntu`](./linux-distros.md#ubuntu) is a [`Linux` distro](./linux-distros.md#what-is-a-linux-distro).

4. Open [`VS Code`](#what-is-vs-code).
5. [Install the extension](./vs-code.md#install-the-vs-code-extension) with the identifier `ms-vscode-remote.remote-wsl`.

   This extension lets you use `VS Code` in [`WSL`](./operating-system.md#wsl).

### (`macOS` only) Add `VS Code` to `PATH`

1. [Add `VS Code` to `PATH`](https://code.visualstudio.com/docs/setup/mac#_configure-the-path-with-vs-code).

   See [`PATH` environment variable](./environments.md#path-environment-variable).
2. [Open a new `VS Code Terminal`](#open-a-new-vs-code-terminal).
3. To check that the `code` command is available,

   [run in the `VS Code Terminal`](#run-a-command-in-the-vs-code-terminal):

   ```terminal
   code --version
   ```

   The output should be similar to this text:

   ```terminal
   1.109.0
   bdd88df003631aaa0bcbe057cb0a940b80a476fa
   x64
   ```
