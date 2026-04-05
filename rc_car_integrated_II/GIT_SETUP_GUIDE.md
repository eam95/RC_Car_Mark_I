# RC Car Integrated II — Git Setup & Daily Workflow

## After Restarting Your Computer

### 1. Open a terminal and navigate to your repo

```bash
cd ~/Desktop/STM32_Workspace/rc_car_integrated_II
```

### 2. Check you're in the right place

```bash
git status
```

### 3. Check which branch you're on

```bash
git branch
```

You should see something like:

```
  feature/rf_timing
* main
```

The `*` shows your current branch.

### 4. Switch to the branch you want to work on

```bash
git checkout feature/rf_timing
```

---

## Daily Workflow — Saving Your Work

### Step 1: See what you changed

```bash
git status
```

### Step 2: See the actual line changes (optional)

```bash
git diff
```

### Step 3: Stage your changes

```bash
# Stage everything
git add .

# Or stage specific files
git add Core/Src/main.c
git add Core/Inc/NRF24.h
```

### Step 4: Commit with a message describing what you did

```bash
git commit -m "Short description of what you changed"
```

Good commit message examples:

```bash
git commit -m "Added forward and reverse motor control"
git commit -m "Fixed NRF24 timing issue in RX mode"
git commit -m "Added LIS3DH accelerometer data to TX payload"
```

### Step 5: Push to GitHub

```bash
git push origin feature/rf_timing
```

---

## When You're Done with a Feature — Merge to Main

```bash
# Switch to main
git checkout main

# Pull latest main from GitHub (in case of remote changes)
git pull origin main

# Merge your feature branch into main
git merge feature/rf_timing

# Push updated main to GitHub
git push origin main

# Switch back to your feature branch to keep working
git checkout feature/rf_timing
```

---

## Quick Command Cheat Sheet

| What you want to do                  | Command                                      |
|--------------------------------------|----------------------------------------------|
| Go to your repo                      | `cd ~/Desktop/STM32_Workspace/rc_car_integrated_II` |
| Check status                         | `git status`                                 |
| See which branch you're on           | `git branch`                                 |
| Switch branch                        | `git checkout feature/rf_timing`             |
| Stage all changes                    | `git add .`                                  |
| Commit changes                       | `git commit -m "your message"`               |
| Push to GitHub                       | `git push origin feature/rf_timing`          |
| Pull latest from GitHub              | `git pull origin feature/rf_timing`          |
| See last 5 commits                   | `git log --oneline -5`                       |
| See what files changed               | `git diff --name-only`                       |
| Merge feature into main              | `git checkout main && git merge feature/rf_timing` |
| Push main to GitHub                  | `git push origin main`                       |

---

## Typical Session Example

```bash
# 1. Open terminal
cd ~/Desktop/STM32_Workspace/rc_car_integrated_II

# 2. Check where you left off
git status
git branch

# 3. Switch to your working branch
git checkout feature/rf_timing

# 4. Do your work in STM32CubeIDE...

# 5. When you're ready to save
git add .
git commit -m "Updated comm state machine for RX/TX switching"
git push origin feature/rf_timing
```

---

## Your Repo Info

- **GitHub URL:** https://github.com/eam95/rc_car_II
- **Branches:** `main`, `feature/rf_timing`
- **Board:** STM32H723ZG (Nucleo-H723ZG)
- **IDE:** STM32CubeIDE
