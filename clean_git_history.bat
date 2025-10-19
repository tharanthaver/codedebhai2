@echo off
echo Cleaning Git history to remove secrets...
echo.

echo Step 1: Adding all changes to staging area...
git add .

echo Step 2: Amending the last commit to remove secrets from history...
git commit --amend --all -m "Remove hardcoded API keys and secrets, use environment variables"

echo Step 3: Force pushing to overwrite remote history...
echo WARNING: This will overwrite the remote repository history!
set /p confirm="Are you sure you want to continue? (y/N): "
if /i "%confirm%"=="y" (
    git push --force-with-lease origin main
    echo.
    echo Git history cleaned successfully!
    echo All secrets should now be removed from the repository history.
) else (
    echo Operation cancelled.
)

pause