#!/bin/bash

# iteration_tool.sh
#
# This script manages the initial backup and future resets of the repository state.
# It creates an initial backup of the default branch, which can be used to reset
# the repository to its original state when needed.
#
# Usage:
#   ./iteration_tool.sh            # Creates a backup of the current default branch
#   ./iteration_tool.sh --reset    # Resets the repository to the initial backup state
#   ./iteration_tool.sh --help     # Shows usage information

BACKUP_DIR="./backup"
INITIAL_BACKUP_FILE="$BACKUP_DIR/main_backup.tar.gz"

# Function to display usage information
show_usage() {
  cat << EOF
Usage: $0 [--reset | --help]
  --reset    Reset repository to initial backup state.
  --help     Show usage information.
EOF
  exit 0
}

# Function to check if we are in a git repository
check_git_repository() {
  if ! git rev-parse --is-inside-work-tree > /dev/null 2>&1; then
    echo "Error: Not a git repository. Run this script in the root of a git repository."
    exit 1
  fi
}

# Function to detect default branch dynamically
detect_default_branch() {
  DEFAULT_BRANCH=$(git remote show origin | awk '/HEAD branch/ {print $NF}')
  if [ -z "$DEFAULT_BRANCH" ]; then
    echo "Error: Unable to determine the default branch. Ensure that the remote repository is properly configured."
    exit 1
  fi
}

# Function to create an initial backup
create_initial_backup() {
  if mkdir -p "$BACKUP_DIR"; then
    echo "Backup directory created or already exists."
  else
    echo "Error: Failed to create backup directory."
    exit 1
  fi
  
  if [ -f "$INITIAL_BACKUP_FILE" ]; then
    echo "Backup already exists at $INITIAL_BACKUP_FILE. Use '--reset' to revert."
  else
    echo "Creating backup of the current $DEFAULT_BRANCH branch..."
    if git archive --format=tar.gz -o "$INITIAL_BACKUP_FILE" "$DEFAULT_BRANCH"; then
      echo "Backup successfully created at $INITIAL_BACKUP_FILE."
    else
      echo "Error: Failed to create backup."
      exit 1
    fi
  fi
}

# Function to reset the repository to its initial state
reset_to_initial_state() {
  if [ -f "$INITIAL_BACKUP_FILE" ]; then
    read -t 10 -p "Warning: This will reset the repository to the initial state. Uncommitted changes will be lost. Continue? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
      echo "Reset operation cancelled."
      exit 0
    fi
    
    echo "Restoring repository to initial state..."
    # Clean untracked files and directories
    read -p "This will remove all untracked files and directories. Are you sure? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
      if git clean -fdx; then
        echo "Untracked files and directories removed."
      else
        echo "Error: Failed to clean untracked files and directories."
        exit 1
      fi
    else
      echo "Clean operation cancelled."
      exit 0
    fi
    
    # Remove all files except .git and backup directory
    read -p "This will remove all files except for the .git directory and the backup directory. Do you want to proceed? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
      if find . -mindepth 1 -not -path "./.git*" -not -path "$BACKUP_DIR*" -exec rm -rf {} +; then
        echo "Existing repository files removed."
      else
        echo "Error: Failed to remove existing files."
        exit 1
      fi
    else
      echo "File removal operation cancelled."
      exit 0
    fi
    
    # Extract backup
    if tar -xzf "$INITIAL_BACKUP_FILE" -C .; then
      echo "Repository successfully restored to initial state."
    else
      echo "Error: Failed to extract the backup."
      exit 1
    fi
  else
    echo "Error: No backup found. Run without '--reset' to create a backup."
    exit 1
  fi
}

# Main control flow based on provided argument
check_git_repository

detect_default_branch

case "$1" in
  --reset)
    reset_to_initial_state
    ;;
  --help)
    show_usage
    ;;
  "")
    create_initial_backup
    ;;
  *)
    echo "Error: Invalid argument '$1'"
    show_usage
    ;;
esac

