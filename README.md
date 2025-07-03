# Voice Calendar Assistant

A voice-enabled web application that allows natural language interaction with Google Calendar, built with LangChain, VAPI.ai, and modern web technologies.

## Features

- 🎤 Voice-controlled calendar management
- 📅 Full CRUD operations on Google Calendar events
- 🧠 Intelligent conversation memory within sessions
- 🔐 Secure OAuth2 authentication
- 🚀 Low-latency voice processing
- 🐳 Fully containerized with Docker

## Quick Start

```bash
# Clone the repository
git clone [repository-url]
cd voice-calendar-assistant

# Copy environment variables
cp .env.example .env
# Edit .env with your API keys

# Start all services
docker-compose up

# Access the application
# Frontend: http://localhost:5173
# Backend API: http://localhost:8000
# API Docs: http://localhost:8000/docs
```

## Prerequisites

- Docker and Docker Compose
- VAPI.ai account
- Google Cloud Console project with Calendar API enabled
- Modern web browser with microphone access

## Architecture

- **Frontend**: React + TypeScript + Vite + Tailwind CSS 4.0
- **Backend**: Python + FastAPI + LangChain
- **Voice**: VAPI.ai (client-side WebRTC)
- **Database**: PostgreSQL + Redis
- **Containerization**: Docker

## Documentation

- [Architecture Overview](docs/architecture.md)
- [API Reference](docs/api-reference.md)
- [Deployment Guide](docs/deployment.md)

## Development

See [CLAUDE.md](CLAUDE.md) for detailed project context and development guidelines.

## License

MIT