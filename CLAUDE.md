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
2. ✅ **VAPI Account**: Created with API keys stored in .env
   - Keys configured in environment variables (VAPI_PUBLIC_KEY, VAPI_PRIVATE_KEY, VAPI_ASSISTANT_ID)
   - All sensitive credentials properly secured in environment variables
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

## Current Status: ✅ FULLY FUNCTIONAL MVP

### What's Working End-to-End:
- **Full Docker Stack**: All services healthy and communicating
- **Frontend UI**: React app with working voice interface
- **VAPI Voice Assistant**: Complete integration with assistant configured via environment variables
- **Google Calendar Integration**: Full OAuth2 flow and real calendar access
- **Voice → Calendar Flow**: Natural speech queries return actual calendar events
- **Backend API**: FastAPI with comprehensive webhook handling
- **Automated Testing**: Puppeteer verification and manual voice testing
- **Version Control**: All working code committed and pushed

### Core Functionality Achieved:
- ✅ **Voice Recognition**: "What do I have today?" → Accurate speech-to-text
- ✅ **Calendar Queries**: Retrieves real events from user's Google Calendar  
- ✅ **Natural Responses**: "You have 10 events: Kai email at 12:00 PM..."
- ✅ **Tool Integration**: VAPI calls backend functions seamlessly
- ✅ **Authentication**: Google OAuth2 with proper token management

## CRITICAL VAPI Integration Learnings

### The toolCallId Discovery 🔍

**PROBLEM**: VAPI was completely ignoring our webhook responses, even though functions executed successfully.

**ROOT CAUSE**: VAPI requires exact `toolCallId` correlation between requests and responses.

#### Broken Response Format:
```json
{
  "result": {
    "success": true,
    "message": "You have 10 events: Kai email at 12:00 PM..."
  }
}
```

#### Working Response Format:
```json
{
  "results": [
    {
      "toolCallId": "call_cETuctAzZtHEJt4iY9t3EH0F",
      "result": "You have 10 events: Kai email at 12:00 PM..."
    }
  ]
}
```

### VAPI Webhook Debugging Methodology

When VAPI integration fails, follow this systematic approach:

1. **Verify Webhook Receipt**: 
   - Add comprehensive logging to see if webhooks arrive
   - Log full request body and headers

2. **Check Function Execution**:
   - Verify functions actually run (not just webhook parsing)
   - Add execution logs in function handlers

3. **Validate Response Format**:
   - Extract `toolCallId` from incoming request
   - Echo it back in response under `results[].toolCallId`
   - Always return HTTP 200, even for errors

4. **Test Response Correlation**:
   - Use curl to test webhook format directly
   - Check VAPI logs for schema validation errors

### Common VAPI Pitfalls

1. **Silent Response Rejection**: VAPI discards responses without `toolCallId` - no error thrown
2. **Assistant Date Confusion**: GPT-4o needs explicit current date in system prompt
3. **OAuth Token Management**: Backend must properly store/retrieve user tokens
4. **Response Content**: Use `result.message` for natural voice responses

### Debugging Prompt That Worked

The breakthrough came from this user prompt:
> "Can you think long and hard... set up debugging... do some research... go step by step through what the software is actually going to be doing... think about all the ways that this could fail... you're being too lazy... research things look things up and then go through step by step in a thought-out process to cover all of the bases"

**Key elements that made it effective**:
- Called out ineffective behavior (making assumptions)
- Explicitly demanded research over guessing  
- Requested systematic step-by-step analysis
- Asked for comprehensive failure mode analysis
- Prescribed methodology: research + debugging + thoroughness

## Future Development Priorities

### Next Features to Implement:
1. **Event Creation**: "Schedule lunch with John tomorrow at noon"
2. **Event Updates**: "Move my 2pm meeting to 4pm" 
3. **Event Deletion**: "Cancel my 3pm meeting"
4. **LangChain Agent**: Add conversation memory and context
5. **Better Date Parsing**: Handle complex natural language dates
6. **Multiple Calendars**: Support work/personal calendar selection

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