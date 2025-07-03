# Voice Calendar Agent - Project Context

## Project Overview
A voice-enabled web application that allows users to interact with their Google Calendar through natural speech. Built as a learning exercise to master LangChain, VAPI.ai, and modern web development practices.

## Code Quality Principles
**CRITICAL**: Maintain professional, senior-level code quality throughout:

### DRY (Don't Repeat Yourself)
- Extract common logic into reusable functions/components
- Create shared utilities for repeated patterns
- Use configuration objects instead of hardcoded values

### Modularization Guidelines
- **Single Responsibility**: Each module does ONE thing well
- **File Size**: No file should exceed ~100 lines (excluding imports/types)
- **Clear Naming**: File names must immediately convey purpose
  - ✅ `validateCalendarEvent.ts`
  - ❌ `utils.ts` or `helpers.ts`

### Separation of Concerns
```
Backend Example:
├── routers/          # HTTP layer only
├── services/         # Business logic only  
├── repositories/     # Data access only
├── agents/          # AI logic only
└── validators/      # Input validation only

Frontend Example:
├── components/      # UI rendering only
├── hooks/          # React logic only
├── services/       # API calls only
├── stores/         # State management only
└── utils/          # Pure functions only
```

### Code Structure Rules
1. **Functions**: Max 20 lines, single purpose
2. **Classes**: Max 5 methods per class
3. **Imports**: Grouped and ordered (external, internal, types)
4. **Comments**: Only for "why", not "what"
5. **Types**: Separate type files when shared

## Key Learning Objectives
1. Master LangChain/LangGraph for building AI agents
2. Learn VAPI.ai for voice interactions
3. Implement OAuth2 authentication flow
4. Practice Docker containerization
5. Build production-ready TypeScript/Python applications

## Architecture Decisions & Reasoning

### Backend: Python with FastAPI
**Decision**: Python with FastAPI instead of Node.js/Express

**Reasoning**:
- **LangChain First-Class Support**: LangChain was originally built for Python and has the most comprehensive documentation, examples, and community support in Python
- **Better AI Ecosystem**: Python has superior libraries for AI/ML tasks if we need to extend functionality
- **FastAPI Benefits**: 
  - Automatic API documentation (Swagger/OpenAPI)
  - Built-in data validation with Pydantic
  - Async support for handling concurrent requests
  - Type hints provide similar benefits to TypeScript

**Learning Note**: From LangChain docs: "While LangChain has a TypeScript version, the Python version receives updates first and has more extensive examples."

### Frontend: React with TypeScript + Vite
**Decision**: Modern React setup with Vite instead of Create React App

**Reasoning**:
- **Vite Benefits**: 
  - Faster development server (10-100x faster than webpack)
  - Native ESM support (aligns with your ES6 modules requirement)
  - Better TypeScript performance
- **React 19 + TypeScript**: Type safety and latest React features
- **Tailwind 4.0**: Using latest version with new configuration approach

### Voice Integration: Client-Side VAPI
**Decision**: Client-side VAPI integration with webhook callbacks to backend

**Reasoning**:
- **Lowest Latency**: Direct browser-to-VAPI connection eliminates backend round-trip for voice data
- **Real-time Streaming**: Voice streams directly to/from user's browser
- **Architecture**:
  ```
  Browser <--WebRTC--> VAPI <--Webhooks--> FastAPI Backend <---> LangChain Agent
  ```
- **Security**: API keys stay on backend, browser gets temporary session tokens

**VAPI Features to Implement**:
1. **Interruption Handling**: User can interrupt the assistant mid-response
2. **Function Calling**: VAPI calls our backend functions for calendar operations
3. **Session Management**: Temporary voice sessions with backend state

### Learning Priority (Revised Order)
**Decision**: Different order than initially suggested

**Optimal Learning Path**:
1. **VAPI Voice Setup First**
   - Validates the core user experience immediately
   - Helps understand the constraints we're working with
   - Quick dopamine hit seeing voice work

2. **LangChain Agent Architecture**
   - Build the "brain" that processes voice inputs
   - Implement conversation memory
   - Design tool usage for calendar operations

3. **Google Calendar Integration Last**
   - Can mock initially to test voice + agent
   - OAuth2 complexity won't block other learning

**Reasoning**: This order lets us validate the novel parts (voice + AI) before dealing with standard API integration (Google Calendar).

## Technical Stack Summary

### Backend
- **Language**: Python 3.11+
- **Framework**: FastAPI
- **AI Framework**: LangChain (with LangGraph if needed)
- **Database**: PostgreSQL (for session storage)
- **Cache**: Redis (for conversation memory)
- **Testing**: pytest + pytest-asyncio

### Frontend
- **Language**: TypeScript 5.x
- **Framework**: React 19
- **Build Tool**: Vite 6
- **Styling**: Tailwind CSS 4.0
- **State Management**: Zustand (simpler than Redux for our needs)
- **Testing**: Vitest + React Testing Library

### Infrastructure
- **Containerization**: Docker + Docker Compose
- **Environment Management**: .env files with python-dotenv
- **API Documentation**: Automatic via FastAPI
- **Development**: Hot reload in both frontend/backend

## Project Structure
```
voice-calendar-agent/
├── docker-compose.yml          # Orchestrates all services
├── .env.example               # Template for environment variables
├── CLAUDE.md                  # This file - project context
├── README.md                  # User-facing documentation
│
├── backend/
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── app/
│   │   ├── main.py           # FastAPI application
│   │   ├── agents/           # LangChain agents
│   │   ├── routers/          # API endpoints
│   │   ├── services/         # Business logic
│   │   ├── models/           # Pydantic models
│   │   └── utils/            # Helper functions
│   └── tests/
│
├── frontend/
│   ├── Dockerfile
│   ├── package.json
│   ├── vite.config.ts
│   ├── tailwind.config.ts    # Tailwind 4.0 config
│   ├── src/
│   │   ├── main.tsx
│   │   ├── App.tsx
│   │   ├── components/       # React components
│   │   ├── hooks/            # Custom React hooks
│   │   ├── services/         # API client code
│   │   └── types/            # TypeScript types
│   └── tests/
│
└── docs/                      # Additional documentation
    ├── architecture.md        # Detailed architecture
    ├── api-reference.md       # API documentation
    └── deployment.md          # Deployment guide
```

## Key Design Patterns

### 1. Repository Pattern for Data Access
- Abstracts database operations
- Makes testing easier with mock repositories

### 2. Dependency Injection in FastAPI
- Clean separation of concerns
- Easy to test components in isolation

### 3. Custom React Hooks for Business Logic
- `useVoiceSession`: Manages VAPI connection
- `useCalendarAgent`: Interfaces with backend agent
- `useGoogleAuth`: Handles OAuth flow

### 4. LangChain Agent as a Service
- Agent instance per user session
- Conversation memory stored in Redis
- Tools for each calendar operation

## Security Considerations

1. **API Keys**: All sensitive keys in backend only
2. **OAuth Tokens**: Encrypted in database, never exposed to frontend
3. **Session Management**: JWT tokens with expiration
4. **CORS**: Properly configured for production
5. **Input Validation**: Pydantic models validate all inputs

## Development Workflow

1. **Local Development**: Docker Compose spins up all services
2. **Hot Reload**: Both frontend and backend auto-reload on changes
3. **Testing**: Separate test databases, mocked external services
4. **Git Workflow**: Feature branches, PR reviews
5. **Documentation**: Update docs with each feature

## Progress Completed ✅

### Phase 1: Project Setup & Infrastructure (COMPLETED)
1. ✅ **GitHub Repository**: Created at https://github.com/alexanderjuxoncobb/voice-calendar-agent
2. ✅ **VAPI Account**: Created with API keys configured
   - Public Key: ef9bdcbe-fad6-4fbe-b912-d43fb0bed0e1
   - Private Key: 38598c97-dfb9-497b-a63b-c4e50c23d48f
   - Free tier: 10 minutes/month, $0.08/minute after
3. ✅ **Docker Environment**: All services running
   - Backend (FastAPI): http://localhost:8000
   - Frontend (React): http://localhost:5173
   - PostgreSQL: port 5432
   - Redis: port 6379
4. ✅ **Tailwind CSS v4**: Successfully configured with @tailwindcss/vite plugin
5. ✅ **Puppeteer Testing**: Automated frontend verification working

### Phase 2: Frontend & Backend Foundation (COMPLETED)
1. ✅ **Modular Backend Structure**: Clean FastAPI architecture
   - Health, Auth, VAPI, Calendar routers implemented (stubs)
   - Configuration management with Pydantic
   - Type-safe API endpoints
2. ✅ **React Frontend**: Working UI with Tailwind v4
   - Voice interface component created
   - VAPI store setup with Zustand
   - TypeScript configuration
3. ✅ **Code Quality Standards**: Senior-level patterns
   - DRY principles enforced
   - Single responsibility modules
   - ES6 modules throughout
   - Files < 100 lines each

## Current Status

### What's Working Right Now:
- **Full Docker Stack**: All services healthy
- **Frontend UI**: "Voice Calendar Agent" with blue "Start Recording" button
- **Backend API**: FastAPI with auto-documentation at /docs
- **Automated Testing**: Puppeteer captures screenshots and verifies functionality
- **Version Control**: Git repo with clean commit history

### What's NOT Working Yet:
- **VAPI Assistant**: Need to create assistant on VAPI dashboard
- **Voice Functionality**: Button exists but no actual voice processing
- **LangChain Agent**: Not implemented yet
- **Google Calendar**: OAuth and API integration pending
- **End-to-End Flow**: Voice → AI → Calendar not connected

## Next Phase: Voice Integration & AI Agent

### IMMEDIATE NEXT STEPS:
1. **Create VAPI Assistant** on dashboard (most critical)
2. **Get Assistant ID** and update frontend VAPI configuration
3. **Test basic voice functionality** (speech-to-text working)
4. **Implement LangChain agent** for calendar command processing
5. **Set up Google Calendar OAuth2** integration

### Technical Debt to Address:
- Update .env with real Assistant ID once created
- Implement actual webhook handlers in backend
- Add session management for voice calls
- Create calendar event processing logic

## Important Notes

- This is a learning project - we prioritize understanding over speed
- Each implementation will include explanations and documentation references
- We'll commit after each working feature
- Tests will be written alongside features
- MCP tools can be integrated for enhanced development workflow

## Questions to Resolve

1. VAPI.ai pricing model - free tier limitations?
2. Google Calendar API quotas for development
3. Preferred Docker registry for deployment?
4. Domain name for production deployment?

---

This document will be continuously updated as we make progress and learn more about each technology.