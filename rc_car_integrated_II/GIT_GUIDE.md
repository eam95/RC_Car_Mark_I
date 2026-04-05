# Git on Linux — Complete Reference Guide

## Table of Contents
- [Installation](#installation)
- [Initial Configuration](#initial-configuration)
- [Creating / Cloning Repositories](#creating--cloning-repositories)
- [Basic Workflow](#basic-workflow)
- [Branching](#branching)
- [Viewing History](#viewing-history)
- [Undoing Changes](#undoing-changes)
- [Remote Repositories](#remote-repositories)
- [Stashing](#stashing)
- [Tags](#tags)
- [.gitignore](#gitignore)
- [SSH Key Setup (for GitHub)](#ssh-key-setup-for-github)
- [Useful Aliases](#useful-aliases)
- [Example: Setting Up an STM32 Project](#example-setting-up-an-stm32-project)

---

## Installation

```bash
# Debian/Ubuntu
sudo apt install git

# Fedora
sudo dnf install git

# Arch
sudo pacman -S git
```

---

## Initial Configuration

```bash
git config --global user.name "Your Name"
git config --global user.email "your.email@example.com"
git config --global core.editor "vim"        # or nano, code, etc.
git config --list                             # verify settings
```

---

## Creating / Cloning Repositories

```bash
# Initialize a new repo in current directory
git init

# Clone an existing remote repo
git clone https://github.com/user/repo.git

# Clone via SSH
git clone git@github.com:user/repo.git
```

---

## Basic Workflow

```bash
# Check status of working directory
git status

# Stage files
git add main.c                  # stage a specific file
git add .                       # stage all changes

# Commit staged changes
git commit -m "Your commit message"

# Push to remote
git push origin main

# Pull latest changes from remote
git pull origin main
```

---

## Branching

```bash
# List branches
git branch

# Create a new branch
git branch feature-branch

# Switch to a branch
git checkout feature-branch
# or (Git 2.23+)
git switch feature-branch

# Create and switch in one step
git checkout -b feature-branch

# Merge a branch into current branch
git merge feature-branch

# Delete a branch
git branch -d feature-branch
```

---

## Viewing History

```bash
# View commit log
git log
git log --oneline --graph --all

# Show changes in a commit
git show <commit-hash>

# Show diff of unstaged changes
git diff

# Show diff of staged changes
git diff --staged
```

---

## Undoing Changes

```bash
# Unstage a file (keep changes)
git restore --staged main.c

# Discard local changes to a file
git restore main.c

# Amend the last commit message
git commit --amend -m "Updated message"

# Revert a commit (creates a new commit that undoes changes)
git revert <commit-hash>

# Reset to a previous commit (destructive — loses commits after that point)
git reset --hard <commit-hash>
```

---

## Remote Repositories

```bash
# List remotes
git remote -v

# Add a remote
git remote add origin https://github.com/user/repo.git

# Change remote URL
git remote set-url origin <new-url>

# Fetch without merging
git fetch origin
```

---

## Stashing

```bash
# Save uncommitted changes temporarily
git stash

# List stashes
git stash list

# Restore most recent stash
git stash pop

# Drop a stash
git stash drop
```

---

## Tags

```bash
# Create a lightweight tag
git tag v1.0

# Create an annotated tag
git tag -a v1.0 -m "Version 1.0 release"

# Push tags to remote
git push origin --tags
```

---

## .gitignore

Create a `.gitignore` file in your repo root to exclude build artifacts.

### Example for STM32CubeIDE / Eclipse Projects

```
# Build output
Debug/
Release/

# Object files
*.o
*.d
*.elf
*.bin
*.hex
*.map
*.list

# Eclipse / STM32CubeIDE settings
.settings/
.metadata/
.cproject
.project

# OS files
.DS_Store
Thumbs.db
```

---

## SSH Key Setup (for GitHub)

```bash
# Generate SSH key
ssh-keygen -t ed25519 -C "your.email@example.com"

# Start ssh-agent and add key
eval "$(ssh-agent -s)"
ssh-add ~/.ssh/id_ed25519

# Copy public key to clipboard (or just cat and copy manually)
cat ~/.ssh/id_ed25519.pub
# Then paste into GitHub → Settings → SSH and GPG keys → New SSH key

# Test connection
ssh -T git@github.com
```

---

## Useful Aliases

```bash
git config --global alias.st status
git config --global alias.co checkout
git config --global alias.br branch
git config --global alias.ci commit
git config --global alias.lg "log --oneline --graph --all"
```

After setting these up you can use shortcuts like:

```bash
git st          # instead of git status
git co main     # instead of git checkout main
git lg          # pretty one-line graph log
```

---

## Example: Setting Up an STM32 Project

```bash
# Navigate to your project
cd ~/STM32CubeIDE/workspace_1.19.0/rc_car_integrated_II

# Initialize git
git init

# Create a .gitignore (see above)
# Then stage and commit
git add .
git commit -m "Initial commit: integrated RC car firmware"

# Add your GitHub remote
git remote add origin git@github.com:your-username/rc_car_integrated_II.git

# Push to GitHub
git push -u origin main
```

> **Note:** If your default branch is called `master` instead of `main`, use `master` in the commands above. You can check with `git branch`.
