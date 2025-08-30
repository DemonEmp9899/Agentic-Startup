# backend/app.py
import os
import sys
import json
from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

# load .env in backend (if you create one)
load_dotenv()

# ensure parent dir (where your agent files live) is on path
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.append(ROOT)

# Import the wrapper functions from your agent files
# These should be the wrapper functions you already have:
# ceo_hf_agent.ceo_agent(...), cto_hf_agent.cto_agent(...), etc.
try:
    from ceo_hf_agent import ceo_agent as ceo_fn
    from cto_hf_agent import cto_agent as cto_fn
    from designer_hf_agent import designer_agent as designer_fn
    from marketer_hf_agent import marketer_agent as marketer_fn
except Exception as e:
    raise ImportError(f"Could not import agent wrappers: {e}")

app = FastAPI(title="Agentic-startup API")

# allow local dev from React
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class SimRequest(BaseModel):
    prompt: str = "We need to build an AI-powered personal finance assistant."
    max_rounds: int = 3

@app.post("/simulate")
def simulate(req: SimRequest):
    """
    Run a round-robin simulation:
      CEO -> CTO -> Designer -> Marketer -> CEO -> ...
    Returns the conversation as a list of messages.
    """
    initial = req.prompt
    max_rounds = max(1, int(req.max_rounds))

    agent_order = ["CEO", "CTO", "Designer", "Marketer"]
    agent_fns = {"CEO": ceo_fn, "CTO": cto_fn, "Designer": designer_fn, "Marketer": marketer_fn}

    conversation = []

    # Kickoff: CEO receives the initial prompt
    try:
        response = agent_fns["CEO"](f"CEO: {initial}")
    except Exception as e:
        response = f"ERROR calling CEO agent: {e}"

    conversation.append({"from": "CEO", "to": ["CTO","Designer","Marketer"], "response": response})

    # Run rounds
    for round_idx in range(max_rounds):
        for i, speaker in enumerate(agent_order):
            next_agent = agent_order[(i + 1) % len(agent_order)]

            # turn response into something to send
            if isinstance(response, dict):
                # prefer standard keys if present, else JSON dump
                msg = response.get("decision") or response.get("messages") or response
                try:
                    # convert to compact JSON string
                    msg = json.dumps(response)
                except Exception:
                    msg = str(response)
            else:
                msg = str(response)

            # call next agent
            try:
                response = agent_fns[next_agent](f"{speaker}: {msg}")
            except Exception as e:
                response = f"ERROR calling {next_agent} agent: {e}"

            conversation.append({"from": speaker, "to": next_agent, "response": response})

            # stop early if an agent explicitly signals done
            if isinstance(response, dict) and response.get("status","").upper() == "DONE":
                return {"conversation": conversation, "done": True}
            if isinstance(response, str) and "DONE" in response.upper():
                return {"conversation": conversation, "done": True}

    return {"conversation": conversation, "done": False}
