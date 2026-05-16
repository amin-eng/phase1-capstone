#!/bin/bash
# check_env.sh - Verify the dev environment is ready for the capstone project.
# Exits with code 0 if everything is fine, 1 if anything is missing.

# Stop the script immediately if any unhandled command fails.
set -e

# A counter for problems found. Starts at 0.
problems=0

echo "=========================================="
echo "  Phase 1 Capstone — Environment Check"
echo "=========================================="
echo

# ---------- Check 1: Python ----------
echo "[1/3] Checking Python..."
if command -v python3 >/dev/null 2>&1; then
    py_version=$(python3 --version | awk '{print $2}')
    echo "      Found Python $py_version"

    # Pull out major and minor numbers (e.g. 3.10.12 -> 3 and 10)
    py_major=$(echo "$py_version" | cut -d. -f1)
    py_minor=$(echo "$py_version" | cut -d. -f2)

    if [ "$py_major" -ge 3 ] && [ "$py_minor" -ge 10 ]; then
        echo "      ✅ Python version OK (>= 3.10)"
    else
        echo "      ❌ Python is too old. Need 3.10 or higher."
        problems=$((problems + 1))
    fi
else
    echo "      ❌ Python3 is not installed."
    problems=$((problems + 1))
fi
echo

# ---------- Check 2: Docker ----------
echo "[2/3] Checking Docker..."
if command -v docker >/dev/null 2>&1; then
    echo "      Docker CLI found: $(docker --version)"

    # 'docker info' only works if the Docker engine is actually running.
    if docker info >/dev/null 2>&1; then
        echo "      ✅ Docker engine is running"
    else
        echo "      ❌ Docker is installed but the engine isn't running."
        echo "         Open Docker Desktop on Windows and try again."
        problems=$((problems + 1))
    fi
else
    echo "      ❌ Docker is not installed."
    problems=$((problems + 1))
fi
echo

# ---------- Check 3: Git ----------
echo "[3/3] Checking Git..."
if command -v git >/dev/null 2>&1; then
    echo "      Git found: $(git --version)"

    git_name=$(git config --global user.name || echo "")
    git_email=$(git config --global user.email || echo "")

    if [ -n "$git_name" ] && [ -n "$git_email" ]; then
        echo "      ✅ Git configured as: $git_name <$git_email>"
    else
        echo "      ❌ Git user.name or user.email is not set."
        problems=$((problems + 1))
    fi
else
    echo "      ❌ Git is not installed."
    problems=$((problems + 1))
fi
echo

# ---------- Final verdict ----------
echo "=========================================="
if [ "$problems" -eq 0 ]; then
    echo "  ✅ All checks passed. Environment ready."
    echo "=========================================="
    exit 0
else
    echo "  ❌ $problems problem(s) found. Fix them and re-run."
    echo "=========================================="
    exit 1
fi
