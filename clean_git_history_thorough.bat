@echo off
echo Thorough Git history cleanup - removes ALL commit history
echo WARNING: This will create a completely new Git history!
echo.

echo Step 1: Creating backup branch...
git branch backup-before-cleanup

echo Step 2: Adding all current changes...
git add .
git commit -m "Final commit before history cleanup"

echo Step 3: Creating new orphan branch...
git checkout --orphan new-main

echo Step 4: Adding all files to new branch...
git add .
git commit -m "Initial commit with secrets removed"

echo Step 5: Replacing main branch...
git branch -D main
git branch -m main

echo Step 6: Force pushing new history...
echo WARNING: This will completely replace the remote repository!
set /p confirm="Are you sure you want to continue? This cannot be undone! (y/N): "
if /i "%confirm%"=="y" (
    git push --force origin main
    echo.
    echo Git history completely cleaned!
    echo All previous commits and secrets have been removed.
    echo Backup branch 'backup-before-cleanup' is available if needed.
) else (
    echo Operation cancelled.
    git checkout main
    git branch -D new-main
)

pause