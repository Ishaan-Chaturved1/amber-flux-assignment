from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel
import re

app = FastAPI()

# In-memory storage
agents = {}
usage_log = {}
seen_requests = set()


class Agent(BaseModel):
    name: str
    description: str
    endpoint: str


class UsageLog(BaseModel):
    caller: str
    target: str
    units: int
    request_id: str


# ---- REQ 1: Agent Registry ----

@app.post("/agents")
def add_agent(agent: Agent):
    if not agent.name.strip() or not agent.description.strip() or not agent.endpoint.strip():
        raise HTTPException(status_code=400, detail="Missing or empty required fields")

    agents[agent.name] = {
        "name": agent.name,
        "description": agent.description,
        "endpoint": agent.endpoint,
        "tags": extract_tags(agent.description)
    }
    return {"message": f"Agent '{agent.name}' registered successfully"}


@app.get("/agents")
def list_agents():
    return list(agents.values())


@app.get("/search")
def search_agents(q: str = Query(..., description="Search term")):
    q_lower = q.lower()
    results = [
        agent for agent in agents.values()
        if q_lower in agent["name"].lower() or q_lower in agent["description"].lower()
    ]
    return results


# ---- REQ 2: Usage Logging ----

@app.post("/usage")
def log_usage(log: UsageLog):
    if not log.caller.strip() or not log.target.strip() or not log.request_id.strip():
        raise HTTPException(status_code=400, detail="Missing or empty required fields")

    if log.target not in agents:
        raise HTTPException(status_code=404, detail=f"Agent '{log.target}' not found")

    if log.request_id in seen_requests:
        return {"message": "Duplicate request_id — usage not counted again"}

    seen_requests.add(log.request_id)
    usage_log[log.target] = usage_log.get(log.target, 0) + log.units

    return {"message": "Usage logged successfully"}


@app.get("/usage-summary")
def usage_summary():
    return usage_log


# ---- REQ 4 (Bonus): Simple keyword/tag extraction ----

def extract_tags(description: str):
    stop_words = {
        "a", "an", "the", "and", "or", "is", "are", "from",
        "to", "of", "in", "for", "with", "that", "this",
        "it", "as", "on", "by", "into", "at", "be"
    }
    words = re.findall(r'[a-zA-Z]+', description.lower())
    tags = list(set(w for w in words if w not in stop_words and len(w) > 2))
    return tags
