@echo off
REM Automated Docker build, tag, and push script for Windows CMD
setlocal enabledelayedexpansion

echo Building Docker image...

set /p VERSION=<VERSION
set IMAGE_NAME=z0r3f/wallbot-docker

docker build --tag %IMAGE_NAME%:latest --tag %IMAGE_NAME%:%VERSION% .

if %errorlevel% equ 0 (
    echo.
    echo Build complete!
    echo    - %IMAGE_NAME%:latest
    echo    - %IMAGE_NAME%:%VERSION%
    echo.
    
    set /p PUSH="Push to Docker Hub? (y/n): "
    if /i "!PUSH!"=="y" (
        echo Pushing images...
        docker push %IMAGE_NAME%:latest
        docker push %IMAGE_NAME%:%VERSION%
        echo Images pushed successfully!
    ) else (
        echo Skipping push to Docker Hub
    )
) else (
    echo Build failed!
    exit /b 1
)
