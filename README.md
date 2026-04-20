# Agent Discovery + Usage Platform

A simple FastAPI app for registering agents, searching them, and tracking usage.

---

## How to Run

**1. Install dependencies**
```
pip install -r requirements.txt
```

**2. Start the server**
```
uvicorn main:app --reload
```

**3. Open in browser**
- API docs (Swagger UI): http://127.0.0.1:8000/docs
- Raw API: http://127.0.0.1:8000

---

## API Endpoints

### Register an agent
```
POST /agents
{
  "name": "DocParser",
  "description": "Extracts structured data from PDFs",
  "endpoint": "https://api.example.com/parse"
}
```

### List all agents
```
GET /agents
```

### Search agents (case-insensitive, matches name or description)
```
GET /search?q=pdf
```

### Log usage
```
POST /usage
{
  "caller": "AgentA",
  "target": "DocParser",
  "units": 10,
  "request_id": "abc123"
}
```
Note: If the same request_id is sent twice, it is ignored (idempotent).

### Usage summary
```
GET /usage-summary
```
Returns total units consumed per agent.

---

## Design Questions

### 1. How would you support billing without double charging?

Every usage log entry already has a request_id. Before billing a usage event,
the system checks if that request_id has already been billed (using a 'billed'
flag in the database). If yes, it skips it. A unique constraint on request_id
in the database ensures this holds even under concurrent requests.

### 2. How would you store data if scale increases to 100K agents?

Switch from in-memory to PostgreSQL. Use indexed columns on name and description
for fast lookups. For search specifically, add a full-text search index
(PostgreSQL supports this natively). If search performance becomes a bottleneck
at very high scale, add Elasticsearch just for the search layer while keeping
PostgreSQL as the main data store.
