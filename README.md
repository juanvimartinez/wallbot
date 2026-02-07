<!-- Docker Badges -->
[![Docker Image Size (latest by date)](https://img.shields.io/docker/image-size/z0r3f/wallbot-docker)](https://hub.docker.com/r/z0r3f/wallbot-docker)
[![Docker pulls](https://img.shields.io/docker/pulls/z0r3f/wallbot-docker?style=flat-square)](https://hub.docker.com/r/z0r3f/wallbot-docker)
[![Docker Image Version (latest by date)](https://img.shields.io/docker/v/z0r3f/wallbot-docker)](https://hub.docker.com/r/z0r3f/wallbot-docker)

<!-- GitHub Actions Badges -->
[![Docker Release](https://github.com/z0r3f/wallbot/actions/workflows/docker-release.yml/badge.svg)](https://github.com/z0r3f/wallbot/actions/workflows/docker-release.yml)
[![Build Status](https://github.com/z0r3f/wallbot/actions/workflows/main.yml/badge.svg)](https://github.com/z0r3f/wallbot/actions/workflows/main.yml)

[//]: # ([![Codecov]&#40;https://codecov.io/gh/z0r3f/wallbot/branch/main/graph/badge.svg&#41;]&#40;https://codecov.io/gh/z0r3f/wallbot&#41;)

<!-- Proyecto y actividad -->
[![commit_freq](https://img.shields.io/github/commit-activity/m/z0r3f/wallbot?style=flat-square)](https://github.com/z0r3f/wallbot/commits)
[![last_commit](https://img.shields.io/github/last-commit/z0r3f/wallbot?style=flat-square)](https://github.com/z0r3f/wallbot/commits)
[![Python Version](https://img.shields.io/pypi/pyversions/wallbot-docker)](https://github.com/z0r3f/wallbot)

<!-- Licencia -->
![GitHub](https://img.shields.io/github/license/z0r3f/wallbot)

# Wallbot

Wallapop search bot

Bot de Telegram para gestionar búsquedas sobre Wallapop

- Notifica cuando encuentra alguna búsqueda
- Avisa cuando algún ítem baja de precio
- Avisa cuando algún ítem es reservado
- Permite gestionar tu lista de ítems

## Development Setup

### Prerequisites

- Python 3.x
- pip3

### Installation

1. Clone the repository
2. Create and activate a virtual environment:
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On macOS/Linux
   # or
   venv\Scripts\activate     # On Windows
   ```

3. Install dependencies:
   ```bash
   pip3 install -r requirements.txt
   ```

### Running Locally

To run the application in development mode:

```bash
# Set the PROFILE environment variable for development
export PROFILE=dev

# Run the application
python -m src.wallbot
```

Or run with inline environment variable:
```bash
PROFILE=dev python -m src.wallbot
```

### Environment Variables

| Variable          | Required | Default | Description                                                                         |
|-------------------|----------|---------|-------------------------------------------------------------------------------------|
| `BOT_TOKEN`       | Yes      | -       | Your Telegram bot token                                                             |
| `PROFILE`         | No       | -       | Set to any value for development mode. When set, uses local paths and debug logging |
| `SEARCH_INTERVAL` | No       | 300     | Search interval in seconds                                                          |

### Development vs Production Mode

The `PROFILE` environment variable controls the application mode:

**Development Mode** (PROFILE is set):
- Database: `db.sqlite` (project root)
- Logs: `wallbot.log` (project root)
- Log Level: `DEBUG`

**Production Mode** (PROFILE not set):
- Database: `/data/db.sqlite` (bind mount: `./data/` directory)
- Logs: `/logs/wallbot.log` (bind mount: `./logs/` directory)
- Log Level: `INFO`

# Docker

## Quick Start with Docker Compose (Recommended)

### Prerequisites
- Docker and Docker Compose installed
- Telegram Bot Token (get it from [@BotFather](https://t.me/botfather))

### Steps

1. **Clone the repository**
   ```bash
   git clone https://github.com/z0r3f/wallbot.git
   cd wallbot
   ```

2. **Create environment file**
   ```bash
   cp .env.example .env
   ```

3. **Edit `.env` and add your bot token**
   ```env
   BOT_TOKEN=your_telegram_bot_token_here
   SEARCH_INTERVAL=300
   ```

4. **Build the Docker image**
   ```bash
   # Linux/macOS
   chmod +x build.sh
   ./build.sh

   # Windows (PowerShell)
   .\build.ps1

   # Windows (CMD)
   build.bat
   ```

5. **Start the bot**
   ```bash
   docker-compose up -d
   ```

6. **View logs**
   ```bash
   docker-compose logs -f wallbot
   ```

7. **Stop the bot**
   ```bash
   docker-compose down
   ```

### Managing Data

Data and logs are stored in local directories for easy access:
- Database: `./data/db.sqlite`
- Logs: `./logs/wallbot.log`

**Backup database:**
```bash
cp ./data/db.sqlite ./backup.sqlite
```

**Restore database:**
```bash
cp ./backup.sqlite ./data/db.sqlite
docker-compose restart wallbot
```

**Direct access to data:**
```bash
# View database
sqlite3 ./data/db.sqlite

# View logs
tail -f ./logs/wallbot.log
```

---

## Building Docker Image

### Automated Build (Recommended)

Use the provided scripts to automatically build, tag, and optionally push the Docker image:

**Linux/macOS:**
```bash
chmod +x build.sh
./build.sh
```

**Windows (PowerShell):**
```powershell
.\build.ps1
```

**Windows (CMD):**
```batch
build.bat
```

The scripts will:
- ✅ Read version from `VERSION` file
- ✅ Build image with both `latest` and version tags
- ✅ Optionally push to Docker Hub (asks for confirmation)

### Manual Build (Advanced)

If you prefer manual control:

**Linux/macOS:**
```bash
# Build image
docker build --tag z0r3f/wallbot-docker:latest .

# Tag with version
VERSION=$(cat VERSION)
docker tag z0r3f/wallbot-docker:latest z0r3f/wallbot-docker:$VERSION

# Push to Docker Hub
docker push z0r3f/wallbot-docker:latest
docker push z0r3f/wallbot-docker:$VERSION
```

**Windows (PowerShell):**
```powershell
# Build image
docker build --tag z0r3f/wallbot-docker:latest .

# Tag with version
$VERSION = Get-Content "VERSION"
docker tag z0r3f/wallbot-docker:latest z0r3f/wallbot-docker:$VERSION

# Push to Docker Hub
docker push z0r3f/wallbot-docker:latest
docker push z0r3f/wallbot-docker:$VERSION
```

---

## Development with Docker Compose

For development with live code reloading:

```bash
docker-compose -f docker-compose.dev.yml up
```

This mounts the `src/` directory into the container and enables development mode.

---

## Running without Docker Compose

If you prefer using `docker run` directly:

```bash
docker run -d \
  --name wallbot \
  --restart unless-stopped \
  -e BOT_TOKEN=your_token_here \
  -e SEARCH_INTERVAL=300 \
  -v wallbot-data:/data \
  -v wallbot-logs:/logs \
  z0r3f/wallbot-docker:latest
```

**View logs:**
```bash
docker logs -f wallbot
```

**Stop container:**
```bash
docker stop wallbot
docker rm wallbot
```

---

## Other Docker Commands

**See images:**
```bash
docker images
```

**Export image:**
```bash
docker save -o wallbot-docker.tar z0r3f/wallbot-docker:latest
```

**Import image:**
```bash
docker load -i wallbot-docker.tar
```

## Target Project Structure

```
wallapop_bot/
├── __init__.py
├── main.py                    # Punto de entrada principal
├── config/
│   ├── __init__.py
│   ├── settings.py           # Configuración general
│   └── constants.py          # Constantes (emojis, URLs)
├── database/
│   ├── __init__.py
│   ├── db_helper.py          # Tu DBHelper actual
│   ├── models.py             # Clases ChatSearch, Item
│   └── migrations.py         # Migraciones de BD
├── telegram/
│   ├── __init__.py
│   ├── bot.py                # Configuración del bot
│   ├── handlers.py           # Manejadores de comandos
│   └── notifications.py      # Función notel y similares
├── wallapop/
│   ├── __init__.py
│   ├── api_client.py         # Cliente API Wallapop
│   ├── search.py             # Lógica de búsqueda
│   └── item_processor.py     # Procesamiento de items
├── utils/
│   ├── __init__.py
│   ├── logger.py             # Configuración de logging
│   ├── currency.py           # Utilidades de moneda
│   └── exceptions.py         # Excepciones personalizadas
└── requirements.txt
```
