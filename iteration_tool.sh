#!/bin/bash

# iteration_tool.sh

# This script backs up the current main branch of the FountainAI-Mock repository
# and resets the main branch to a fresh initial state as per the development plan.
# It serves as a numbered iteration branching strategic tool.

# Usage:
#   ./iteration_tool.sh

# Requirements:
# - gh CLI tool (https://cli.github.com/)
# - Git

# Exit immediately if a command exits with a non-zero status
set -e

# Variables
REPO_URL="https://github.com/Contexter/FountainAI-Mock.git"
REPO_NAME="FountainAI-Mock"
TIMESTAMP=$(date +%Y%m%d%H%M%S)
BACKUP_BRANCH_NAME="backup/main-$TIMESTAMP"
MAIN_BRANCH_NAME="main"
TEMP_BRANCH_NAME="temp-main"

# Function to check if gh CLI is installed
check_gh_cli() {
    if ! command -v gh &> /dev/null
    then
        echo "Error: gh CLI is not installed. Please install it from https://cli.github.com/."
        exit 1
    fi
}

# Function to clone the repository
clone_repository() {
    echo "Cloning the repository..."
    # Checking if the repository directory already exists helps to avoid redundant cloning, saving time and system resources by not repeating this operation unnecessarily.
    if [ -d "$REPO_NAME" ]; then
        echo "Repository already exists locally. Do you want to delete it and re-clone? (y/n)"
        read -r response
        if [[ "$response" != "y" ]]; then
            echo "Aborting script."
            exit 1
        fi
        echo "Deleting the existing repository to avoid redundant cloning..."
        rm -rf "$REPO_NAME"
    fi
    git clone "$REPO_URL"
    cd "$REPO_NAME"
}

# Function to create a backup branch from main
create_backup_branch() {
    echo "Checking out main branch..."
    if ! git checkout "$MAIN_BRANCH_NAME"; then
        echo "Error: Failed to checkout main branch."
        exit 1
    fi
    
    echo "Pulling latest changes..."
    if ! git pull origin "$MAIN_BRANCH_NAME"; then
        echo "Error: Failed to pull latest changes from main branch."
        exit 1
    fi
    
    echo "Creating a backup branch '$BACKUP_BRANCH_NAME' from '$MAIN_BRANCH_NAME'..."
    if ! git checkout -b "$BACKUP_BRANCH_NAME"; then
        echo "Error: Failed to create backup branch."
        exit 1
    fi
    
    echo "Pushing backup branch to origin..."
    if ! git push origin "$BACKUP_BRANCH_NAME"; then
        echo "Error: Failed to push backup branch to origin."
        exit 1
    fi
}

# Function to reset main branch to initial state
reset_main_branch() {
    echo "Resetting '$MAIN_BRANCH_NAME' branch to a fresh initial state..."
    
    echo "Creating an orphan branch '$TEMP_BRANCH_NAME' with no history..."
    # Creating an orphan branch ensures no commit history is carried over, providing a clean slate for the new main branch.
    if ! git checkout --orphan "$TEMP_BRANCH_NAME"; then
        echo "Error: Failed to create orphan branch."
        exit 1
    fi
    
    echo "Removing all files from the index..."
    if ! git rm -rf .; then
        echo "Error: Failed to remove files from index."
        exit 1
    fi
    
    echo "Setting up initial directory structure as per the development plan..."
    mkdir -p service/openapi
    mkdir -p service/scripts
    # Copying the existing README ensures that documentation is not lost and remains consistent between iterations.
    cp README.md service/README.md
    touch service/openapi/.gitkeep
    touch service/scripts/.gitkeep
    
    # Move relevant files to the /service directory
    echo "Moving requirements.txt and Dockerfile to the /service directory..."
    # Ensure that `requirements.txt` is moved to the correct directory to make dependencies easily accessible for Docker builds and other processes.
    mv service/openapi/requirements.txt service/
    mv service/openapi/Dockerfile service/
    
    # Optionally, add the merge_openapi.py script if available
    cp merge_openapi.py service/
    
    echo "Creating a new initial commit..."
    if ! git add . || ! git commit -m "Initial commit for FountainAI Mock Server development plan"; then
        echo "Error: Failed to create initial commit."
        exit 1
    fi
    
    echo "Deleting the old '$MAIN_BRANCH_NAME' branch..."
    if ! git branch -D "$MAIN_BRANCH_NAME"; then
        echo "Error: Failed to delete old main branch."
        exit 1
    fi
    
    echo "Renaming '$TEMP_BRANCH_NAME' to '$MAIN_BRANCH_NAME'..."
    if ! git branch -m "$MAIN_BRANCH_NAME"; then
        echo "Error: Failed to rename temporary branch to main."
        exit 1
    fi
    
    echo "Force pushing the new '$MAIN_BRANCH_NAME' branch to origin..."
    echo "Warning: Force pushing can overwrite important history. Make sure all collaborators are informed before proceeding to avoid accidental data loss."
    if ! git push -f origin "$MAIN_BRANCH_NAME"; then
        echo "Error: Failed to force push new main branch to origin."
        exit 1
    fi
}

# Function to display completion message
display_completion_message() {
    echo "Backup and reset completed successfully."
    echo "The '$MAIN_BRANCH_NAME' branch has been reset to a fresh initial state."
    echo "The original main branch has been backed up as '$BACKUP_BRANCH_NAME'."
}

# Main execution flow
main() {
    check_gh_cli
    clone_repository
    create_backup_branch
    reset_main_branch
    display_completion_message
}

# Execute the main function
main

