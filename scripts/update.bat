@echo off
setlocal

REM Go to the project root (one directory above this script)
cd /d "%~dp0.."

echo ========================================
echo  Updating MMN Max Mode List
echo ========================================

echo.
echo [1/3] Updating leaderboard...
python scripts\leaderboard.py
if errorlevel 1 goto :error

echo.
echo [2/3] Updating countries...
python scripts\countries.py
if errorlevel 1 goto :error

echo.
echo [3/3] Updating beaten modes...
python scripts\beatenmodes.py
if errorlevel 1 goto :error

echo.
echo ========================================
echo  All scripts completed successfully.
echo ========================================

echo.
echo Checking resources\ for changes...

git diff --quiet -- resources
set "DIFF1=%errorlevel%"

git diff --cached --quiet -- resources
set "DIFF2=%errorlevel%"

for /f %%i in ('git ls-files --others --exclude-standard resources') do set "UNTRACKED=1"

if "%DIFF1%"=="0" if "%DIFF2%"=="0" if not defined UNTRACKED (
    echo No changes detected in resources\.
    goto :end
)

echo.
echo Changes detected:
git status --short -- resources

echo.
set /p "answer=Commit and push resources\ changes? [y/N] "

if /i not "%answer%"=="y" (
    echo Changes were not committed.
    goto :end
)

git add resources
git commit -m "Update leaderboard"
if errorlevel 1 goto :error

git push
if errorlevel 1 goto :error

echo.
echo Changes pushed successfully.
goto :end

:error
echo.
echo ========================================
echo  ERROR: Update failed.
echo ========================================
echo No changes were committed.
exit /b 1

:end
echo.
pause
endlocal