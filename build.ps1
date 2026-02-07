# Automated Docker build, tag, and push script for Windows PowerShell

$ErrorActionPreference = "Stop"

# Read version
$VERSION = Get-Content "VERSION" -Raw
$VERSION = $VERSION.Trim()
$IMAGE_NAME = "z0r3f/wallbot-docker"

Write-Host "🐳 Building Docker image..." -ForegroundColor Cyan
docker build --tag "${IMAGE_NAME}:latest" --tag "${IMAGE_NAME}:${VERSION}" .

if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ Build complete!" -ForegroundColor Green
    Write-Host "   - ${IMAGE_NAME}:latest"
    Write-Host "   - ${IMAGE_NAME}:${VERSION}"
    Write-Host ""
    
    # Optional: Ask before pushing
    $push = Read-Host "📤 Push to Docker Hub? (y/n)"
    if ($push -eq 'y' -or $push -eq 'Y') {
        Write-Host "Pushing images..." -ForegroundColor Cyan
        docker push "${IMAGE_NAME}:latest"
        docker push "${IMAGE_NAME}:${VERSION}"
        Write-Host "✅ Images pushed successfully!" -ForegroundColor Green
    } else {
        Write-Host "ℹ️  Skipping push to Docker Hub" -ForegroundColor Yellow
    }
} else {
    Write-Host "❌ Build failed!" -ForegroundColor Red
    exit 1
}
