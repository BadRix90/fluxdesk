# Flux Project Structure Setup
# Run: .\Setup-Flux-Structure.ps1

Write-Host "Creating Flux project structure..." -ForegroundColor Cyan

# Backend Directories
$backendDirs = @(
    "backend/apps/tickets/models",
    "backend/apps/tickets/api",
    "backend/apps/tickets/services",
    "backend/apps/tickets/tests",
    "backend/apps/users/models",
    "backend/apps/users/api",
    "backend/apps/users/tests",
    "backend/apps/core",
    "backend/config"
)

# Frontend Directories
$frontendDirs = @(
    "frontend/src/app/features/tickets/components",
    "frontend/src/app/features/tickets/services",
    "frontend/src/app/features/tickets/models",
    "frontend/src/app/features/auth/components",
    "frontend/src/app/features/auth/services",
    "frontend/src/app/shared/components",
    "frontend/src/app/shared/services",
    "frontend/src/app/core/guards",
    "frontend/src/app/core/interceptors",
    "frontend/src/assets",
    "frontend/src/environments"
)

# Other Directories
$otherDirs = @(
    "docker",
    "scripts",
    "docs/assets"
)

# Create all directories
$allDirs = $backendDirs + $frontendDirs + $otherDirs
foreach ($dir in $allDirs) {
    New-Item -ItemType Directory -Force -Path $dir | Out-Null
    Write-Host "  Created: $dir" -ForegroundColor Green
}

# Create __init__.py files for Python packages
$pythonPackages = @(
    "backend/apps/__init__.py",
    "backend/apps/tickets/__init__.py",
    "backend/apps/tickets/models/__init__.py",
    "backend/apps/tickets/api/__init__.py",
    "backend/apps/tickets/services/__init__.py",
    "backend/apps/tickets/tests/__init__.py",
    "backend/apps/users/__init__.py",
    "backend/apps/users/models/__init__.py",
    "backend/apps/users/api/__init__.py",
    "backend/apps/users/tests/__init__.py",
    "backend/apps/core/__init__.py",
    "backend/config/__init__.py"
)

foreach ($file in $pythonPackages) {
    New-Item -ItemType File -Force -Path $file | Out-Null
}

Write-Host ""
Write-Host "Flux project structure created!" -ForegroundColor Cyan
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Yellow
Write-Host "  1. Copy config files to their locations"
Write-Host "  2. Copy .env.example to .env"
Write-Host "  3. Run: docker-compose up -d"
