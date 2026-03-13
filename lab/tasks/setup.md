# Lab setup

- [1. Required steps](#1-required-steps)
  - [1.1. (UPD) Find a partner](#11-upd-find-a-partner)
  - [1.2. Start creating a VM](#12-start-creating-a-vm)
  - [1.3. Set up your fork (LOCAL)](#13-set-up-your-fork-local)
    - [1.3.1. Sign in on `GitHub`](#131-sign-in-on-github)
    - [1.3.2. (UPD) Fork the course instructors' repo](#132-upd-fork-the-course-instructors-repo)
    - [1.3.3. (UPD) Go to your fork](#133-upd-go-to-your-fork)
    - [1.3.4. (UPD) Enable issues](#134-upd-enable-issues)
    - [1.3.5. (UPD) Add a classmate as a collaborator](#135-upd-add-a-classmate-as-a-collaborator)
    - [1.3.6. (UPD) Protect your `main` branch](#136-upd-protect-your-main-branch)
  - [1.4. Set up programs (LOCAL)](#14-set-up-programs-local)
    - [1.4.1. (UPD) Set up `VS Code`](#141-upd-set-up-vs-code)
    - [1.4.2. (UPD) Set up `Docker`](#142-upd-set-up-docker)
    - [1.4.3. (UPD) (`Windows` only) Switch to the `Linux` shell for the `VS Code Terminal`](#143-upd-windows-only-switch-to-the-linux-shell-for-the-vs-code-terminal)
    - [1.4.4. (UPD) Clean up `Docker`](#144-upd-clean-up-docker)
    - [1.4.5. Set up `Git`](#145-set-up-git)
  - [1.5. (UPD) Open in `VS Code` the `software-engineering-toolkit` directory (LOCAL)](#15-upd-open-in-vs-code-the-software-engineering-toolkit-directory-local)
  - [1.6. Clone your fork (LOCAL)](#16-clone-your-fork-local)
    - [1.6.1. (UPD) Copy your fork URL](#161-upd-copy-your-fork-url)
    - [1.6.2. (UPD) Clone your fork](#162-upd-clone-your-fork)
  - [1.7. (UPD) Open the cloned repo and set up `VS Code` (LOCAL)](#17-upd-open-the-cloned-repo-and-set-up-vs-code-local)
  - [1.8. Continue creating a VM](#18-continue-creating-a-vm)
  - [1.9. Set up `Python` (LOCAL)](#19-set-up-python-local)
    - [1.9.1. Install `uv`](#191-install-uv)
    - [1.9.2. (UPD) Set up `Python` in `VS Code`](#192-upd-set-up-python-in-vs-code)
  - [1.10. Set up `Node.js` (LOCAL)](#110-set-up-nodejs-local)
    - [1.10.1. Install `Node.js`](#1101-install-nodejs)
    - [1.10.2. (UPD) Install `pnpm`](#1102-upd-install-pnpm)
  - [1.11. (UPD) Set up the `Qwen Code` (LOCAL)](#111-upd-set-up-the-qwen-code-local)
  - [1.12. (UPD) Set up the `Qwen` API (VM)](#112-upd-set-up-the-qwen-api-vm)
  - [1.13. Set up the `Autochecker` bot (`Telegram`)](#113-set-up-the-autochecker-bot-telegram)
  - [1.14. Check the setup using the `Autochecker` bot (`Telegram`)](#114-check-the-setup-using-the-autochecker-bot-telegram)
- [2. Optional steps](#2-optional-steps)
  - [2.1. (UPD) Set up `Nix` (LOCAL)](#21-upd-set-up-nix-local)
  - [2.2. (UPD) Set up `direnv` (LOCAL)](#22-upd-set-up-direnv-local)
  - [2.3. Learn to go back after clicking a link](#23-learn-to-go-back-after-clicking-a-link)
  - [2.4. Set up the shell prompt](#24-set-up-the-shell-prompt)
  - [2.5. Customize the `Source Control`](#25-customize-the-source-control)
  - [2.6. Get familiar with `GitLens`](#26-get-familiar-with-gitlens)
  - [2.7. Create a label for tasks](#27-create-a-label-for-tasks)
  - [2.8. View `Markdown` files in `VS Code`](#28-view-markdown-files-in-vs-code)

## 1. Required steps

> [!IMPORTANT]
> Complete all steps if you haven't completed the full setup in previous labs.
>
> Otherwise, complete just the steps with the `(UPD)` label to get the right setup for this lab.

> [!IMPORTANT]
> Complete the steps with the label:
>
> - `(LOCAL)` - on your local machine (laptop).
>
> - `(VM)` - on your VM.
>
> - `(Telegram)` - in `Telegram`.

> [!NOTE]
> We provide the hardest setup steps before all other tasks
> so that TAs can help you resolve issues during the lab.
>
> Tasks are doable when you have the right setup.

> [!NOTE]
> This lab needs your university email, GitHub alias, and VM IP in the Autochecker bot <https://t.me/auchebot>.
>
> If you haven't registered, do so now.
>
> If you want to change something, contact your TA.

### 1.1. (UPD) Find a partner

1. Find a partner for this lab.
2. Sit next to them.

> [!IMPORTANT]
> You work on tasks independently from your partner.
>
> You and your partner work together when reviewing each other's work.

### 1.2. Start creating a VM

> [!NOTE]
> Skip this step if you can [connect to your VM](../../wiki/vm.md#connect-to-the-vm).

[Create a subscription](../../wiki/vm.md#create-a-subscription) to be able to create a VM.

> [!TIP]
> Subscription approval may take time.
> Continue with the next steps while you wait — you will
> [finish creating the VM](#18-continue-creating-a-vm) later.

### 1.3. Set up your fork (LOCAL)

#### 1.3.1. Sign in on `GitHub`

1. Sign in on [`GitHub`](https://github.com/).
2. [Find `<your-github-username>`](../../wiki/github.md#find-your-github-username).

#### 1.3.2. (UPD) Fork the course instructors' repo

1. [Fork the course instructors' repo](../../wiki/github.md#fork-a-repo).

   The course instructors' repo [URL](../../wiki/computer-networks.md#url) is <https://github.com/inno-se-toolkit/se-toolkit-lab-5>.

#### 1.3.3. (UPD) Go to your fork

1. [Go to your fork](../../wiki/github.md#go-to-your-fork).

   The [URL](../../wiki/computer-networks.md#url) of your fork should look like `https://github.com/<your-github-username>/se-toolkit-lab-5`.

#### 1.3.4. (UPD) Enable issues

1. [Enable issues](../../wiki/github.md#enable-issues).

#### 1.3.5. (UPD) Add a classmate as a collaborator

1. [Add a collaborator](../../wiki/github.md#add-a-collaborator) — your partner.
2. Your partner should add you as a collaborator in their repo.

> [!NOTE]
> It's OK if your collaborator can't change `Settings` in your repo.

#### 1.3.6. (UPD) Protect your `main` branch

> [!NOTE]
> Branch protection prevents accidental pushes directly to `main`.
> This enforces the PR workflow and ensures all changes are reviewed.

1. [Protect the `main` branch](../../wiki/github.md#protect-a-branch).

### 1.4. Set up programs (LOCAL)

#### 1.4.1. (UPD) Set up `VS Code`

1. (Optional) [Read about `VS Code`](../../wiki/vs-code.md#what-is-vs-code).
2. [Set up `VS Code`](../../wiki/vs-code.md#set-up-vs-code).

#### 1.4.2. (UPD) Set up `Docker`

1. (Optional) [Read about `Docker`](../../wiki/docker.md#what-is-docker).
2. [Install `Docker`](../../wiki/docker.md#install-docker) if it's not installed.
3. [Start `Docker`](../../wiki/docker.md#start-docker).

#### 1.4.3. (UPD) (`Windows` only) Switch to the `Linux` shell for the `VS Code Terminal`

1. [Check the current shell in the `VS Code Terminal`](../../wiki/vs-code.md#check-the-current-shell-in-the-vs-code-terminal).
2. If it's not `bash` or `zsh`, [switch to the `Linux` shell for the `VS Code Terminal`](../../wiki/vs-code.md#windows-only-switch-to-the-linux-shell-for-the-vs-code-terminal).
3. [Check the current shell](../../wiki/vs-code.md#check-the-current-shell-in-the-vs-code-terminal) again.

#### 1.4.4. (UPD) Clean up `Docker`

1. [Clean up `Docker`](../../wiki/docker.md#clean-up-docker).

   **Note:** Old containers and volumes from a previous lab version may conflict with the updated services.
   Stop running containers, remove stopped containers, and delete unused volumes so you start with a clean state.

#### 1.4.5. Set up `Git`

1. (Optional) [Read about `Git`](../../wiki/git.md#what-is-git).
2. [Install `Git`](https://git-scm.com/install/) if it's not installed.
3. [Configure `Git`](../../wiki/git.md#configure-git).

### 1.5. (UPD) Open in `VS Code` the `software-engineering-toolkit` directory (LOCAL)

1. Inside the [`Desktop` directory](../../wiki/file-system.md#desktop-directory),
   create the directory `software-engineering-toolkit`.

   Skip this step if this directory exists.

2. [Open in `VS Code` the directory](../../wiki/vs-code.md#open-the-directory):
   `software-engineering-toolkit`.
3. (`Windows` only) [Reopen the directory in `WSL`](../../wiki/vs-code.md#windows-only-reopen-the-directory-in-wsl) if you didn't do that before.

### 1.6. Clone your fork (LOCAL)

#### 1.6.1. (UPD) Copy your fork URL

1. [Go to your fork](#133-upd-go-to-your-fork).
2. Copy [`<your-fork-url>`](../../wiki/github.md#your-fork-url).

   It should look like `https://github.com/<your-github-username>/se-toolkit-lab-5`.

   See [`<your-github-username>`](../../wiki/github.md#your-github-username).

#### 1.6.2. (UPD) Clone your fork

1. [Clone your fork](../../wiki/git-vscode.md#clone-the-repository):

   - Replace `<repo-url>` with [`<your-fork-url>`](../../wiki/github.md#your-fork-url).
   - Replace `<repo-name>` with `se-toolkit-lab-6`.

### 1.7. (UPD) Open the cloned repo and set up `VS Code` (LOCAL)

> [!IMPORTANT]
> Go by the links in the steps below and complete the checks ("You should see ...").
> Otherwise, your setup will be broken.

1. [Open in `VS Code` the directory](../../wiki/vs-code.md#open-the-directory):
   `se-toolkit-lab-6`.
2. [Check the current shell in the `VS Code Terminal`](../../wiki/vs-code.md#check-the-current-shell-in-the-vs-code-terminal).
3. [Install the recommended `VS Code` extensions](../../wiki/vs-code.md#install-the-recommended-vs-code-extensions).

<details><summary><b>Troubleshooting (click to open)</b></summary>

<h4>The terminal shell is not <code>bash</code> or <code>zsh</code></h4>

Go back to [step 1.4.3](#143-upd-windows-only-switch-to-the-linux-shell-for-the-vs-code-terminal) and set the default shell.

<h4>Recommended extensions did not install</h4>

Reload the `VS Code` window: press `Ctrl+Shift+P`, type `Reload Window`, and press `Enter`.

</details>

### 1.8. Continue creating a VM

> [!TIP]
> You don't need to create a new [`SSH` key pair](../../wiki/ssh.md#ssh-key-pair) if the old one exists.
>
> You can use the key pair that you created before for the new VM.

If you can't [connect to your VM](../../wiki/vm.md#connect-to-the-vm), complete these steps:

1. [Set up `SSH`](../../wiki/ssh.md#set-up-ssh).
2. [Create a VM using the subscription](../../wiki/vm.md#create-a-vm-using-the-subscription).

### 1.9. Set up `Python` (LOCAL)

> [!NOTE]
> See [What is `Python`](../../wiki/python.md#what-is-python).

#### 1.9.1. Install `uv`

> [!NOTE]
> See [`uv`](../../wiki/python.md#uv).

1. [Install `uv`](../../wiki/python.md#install-uv).

#### 1.9.2. (UPD) Set up `Python` in `VS Code`

> [!NOTE]
> The dependencies have been updated in this project version.

1. [Set up `Python` in `VS Code`](../../wiki/vscode-python.md#set-up-python-in-vs-code).

### 1.10. Set up `Node.js` (LOCAL)

#### 1.10.1. Install `Node.js`

[Install `Node.js`](../../wiki/nodejs.md#install-nodejs).

#### 1.10.2. (UPD) Install `pnpm`

[Install `pnpm`](../../wiki/nodejs.md#install-pnpm).

### 1.11. (UPD) Set up the `Qwen Code` (LOCAL)

`Qwen Code` is a coding agent that can explain tasks, read wiki, explain concepts, write code, debug.

<div style="display:flex;flex-wrap:wrap;gap:10px">
  <img alt="Qwen request" src="../images/tasks/setup/qwen-request.png" style="width:300px"></img>
  <img alt="Qwen response" src="../images/tasks/setup/qwen-response.png" style="width:300px"></img>
</div>

[Set up the `Qwen Code`](../../wiki/qwen.md#set-up-the-qwen-code-local-machine).

### 1.12. (UPD) Set up the `Qwen` API (VM)

[Set up the `Qwen` API on your VM](../../wiki/qwen.md#set-up-the-qwen-code-api-remote-machine).

### 1.13. Set up the `Autochecker` bot (`Telegram`)

[Set up the `Autochecker`](../../wiki/autochecker.md#set-up-the-autochecker)

### 1.14. Check the setup using the `Autochecker` bot (`Telegram`)

[Check the task](../../wiki/autochecker.md#check-the-task-using-the-autochecker-bot).

---

## 2. Optional steps

These enhancements can make your life easier:

<!-- no toc -->
- [Set up `Nix`](#21-upd-set-up-nix-local)
- [Set up `direnv`](#22-upd-set-up-direnv-local)
- [Learn to go back after clicking a link](#23-learn-to-go-back-after-clicking-a-link)
- [Set up the shell prompt](#24-set-up-the-shell-prompt)
- [Customize the `Source Control`](#25-customize-the-source-control)
- [Get familiar with `GitLens`](#26-get-familiar-with-gitlens)
- [Create a label for tasks](#27-create-a-label-for-tasks)
- [View `Markdown` files in `VS Code`](#28-view-markdown-files-in-vs-code)

### 2.1. (UPD) Set up `Nix` (LOCAL)

1. (Optional) [Read about `Nix`](../../wiki/nix.md#what-is-nix).
2. [Set up `Nix`](../../wiki/nix.md#set-up-nix).

### 2.2. (UPD) Set up `direnv` (LOCAL)

1. (Optional) [Read about `direnv`](../../wiki/direnv.md#what-is-direnv).
2. [Set up `Nix`](#21-upd-set-up-nix-local).
3. [Set up `direnv`](../../wiki/direnv.md#set-up-direnv).

### 2.3. Learn to go back after clicking a link

> [!NOTE]
> Shortcuts for going back after clicking a link:

- `VS Code` — see the [shortcut](../../wiki/vs-code.md#shortcut-go-back).
- `Firefox` — `Alt+ArrowLeft`.
- Other browsers — google.

### 2.4. Set up the shell prompt

`Starship` shows your current `Git` branch, status, and other useful info directly in your [shell prompt](../../wiki/shell.md#shell-prompt) in almost any terminal, including the [`VS Code Terminal`](../../wiki/vs-code.md#vs-code-terminal).

Complete these steps:

1. [Install `Starship`](https://github.com/starship/starship#-installation).
2. [Open the `VS Code Terminal`](../../wiki/vs-code.md#open-the-vs-code-terminal).

   You should see something similar to this:

   <img alt="Starship in the VS Code Terminal" src="../../wiki/images/starship/terminal-prompt.png" style="width:400px"></img>

### 2.5. Customize the `Source Control`

1. [Open the `Source Control`](../../wiki/vs-code.md#open-the-source-control).
2. Click three dots to the right of `SOURCE CONTROL`.
3. Put checkmarks only near `Changes` and `GitLens` to see only these views.

   <img alt="Changes and GitLens" src="../../wiki/images/vs-code/source-control-allowed-views.png" style="width:400px"></img>

### 2.6. Get familiar with `GitLens`

[`GitLens`](../../wiki/gitlens.md#what-is-gitlens) helps you work with `Git` in `VS Code`.

Complete these steps:

1. [See all branches](../../wiki/gitlens.md#see-all-branches).
2. [Look at the commit graph](../../wiki/gitlens.md#look-at-the-commit-graph).
3. [Inspect the current branch](../../wiki/gitlens.md#inspect-the-current-branch).
4. [Inspect the remotes](../../wiki/gitlens.md#inspect-the-remotes).

### 2.7. Create a label for tasks

[Labels](../../wiki/github.md#label) help you filter and organize issues.

With a `task` label, you can see in one view all issues created for lab tasks.

> [!TIP]
> If you create the `task` label before creating issues, your issues will have this label automatically as configured in the [issue form](../../.github/ISSUE_TEMPLATE/01-task.yml).

Complete these steps:

1. [Create](../../wiki/github.md#create-a-label) the `task` label.
2. [Add the label to issues](../../wiki/github.md#add-a-label-to-issues).
3. [See all issues with the label](../../wiki/github.md#see-all-issues-with-a-label).

### 2.8. View `Markdown` files in `VS Code`

If you want to view [`README.md`](../../README.md) and other `Markdown` files in `VS Code` instead of on `GitHub`:

1. [Install the recommended `VS Code` extensions](../../wiki/vs-code.md#install-the-recommended-vs-code-extensions).
2. [Open the file](../../wiki/vs-code.md#open-the-file):
   [`README.md`](../../README.md).
3. [Open the `Markdown` preview](../../wiki/vs-code.md#open-the-markdown-preview).
