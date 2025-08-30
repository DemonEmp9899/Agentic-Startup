# cto_hf_agent.py (GitHub Models version)
from openai import OpenAI
import json
from datetime import datetime
import os
from dotenv import load_dotenv
STATE_FILE = "sim_state.json"

client = OpenAI(
    api_key=os.getenv("YOUR_API_KEY_HERE"),
    base_url="https://models.inference.ai.azure.com"
)

def create_cto_agent():
    return {
        "id": "CTO",
        "role": "Technology strategist and product builder",
        "display_name": "CTO",
        "system_prompt": (
            "You are the CTO agent. Your job is to design the tech stack, "
            "plan product architecture, and oversee development. "
            "Be clear, technical, and practical."
        ),
        "goals": [
            "Select the best tech stack for the startup",
            "Plan the system architecture",
            "Coordinate development timelines",
            "Ensure scalability and security"
        ],
        "memory": {
            "long_term": [
                {"id": "tech_pref", "title": "Favor modern, cost-efficient stack", "created": datetime.now().isoformat()}
            ],
            "short_term": []
        },
        "created_at": datetime.now().isoformat()
    }

def update_state_with_cto(cto_agent):
    if not os.path.exists(STATE_FILE):
        raise FileNotFoundError(f"{STATE_FILE} not found. Run CEO agent first.")
    
    with open(STATE_FILE, "r") as f:
        state = json.load(f)
    
    state["agents"]["CTO"] = cto_agent
    
    with open(STATE_FILE, "w") as f:
        json.dump(state, f, indent=2)
    
    print("✅ CTO agent added to simulation state.")

def ask_cto_for_plan(state):
    cto = state["agents"]["CTO"]
    ceo_messages = [m for m in state["chat_history"] if m["from"] == "CEO"]
    
    prompt = (
        f"{cto['system_prompt']}\n"
        f"Long-term memory: {json.dumps(cto['memory']['long_term'], indent=2)}\n"
        f"Recent CEO instructions: {json.dumps(ceo_messages[-1], indent=2) if ceo_messages else 'None'}\n"
        f"Question: What is your technical plan? Respond in JSON with keys: architecture, tools, timeline."
    )
    
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": cto["system_prompt"]},
            {"role": "user", "content": prompt}
        ]
    )
    
    raw_output = response.choices[0].message.content
    
    state["chat_history"].append({
        "from": "CTO",
        "to": ["CEO", "Designer", "Marketer"],
        "timestamp": datetime.now().isoformat(),
        "type": "proposal",
        "subject": "Technical plan",
        "body": raw_output
    })
    
    with open(STATE_FILE, "w") as f:
        json.dump(state, f, indent=2)
    
    return raw_output

# --- Shared public function for new.py ---
def generate_response(prompt: str):
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "system", "content": "You are the CTO agent."},
                  {"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content


if __name__ == "__main__":
    # Load state
    with open(STATE_FILE, "r") as f:
        state = json.load(f)
    
    # Always overwrite CTO agent with the correct structure
    cto_agent_struct = create_cto_agent()
    state.setdefault("agents", {})["CTO"] = cto_agent_struct
    
    with open(STATE_FILE, "w") as f:
        json.dump(state, f, indent=2)
    
    # Ask CTO for plan
    print("💬 Asking CTO for technical plan...")
    answer = ask_cto_for_plan(state)
    print("\n--- CTO's Technical Plan ---")
    print(answer)
    print("✅ CTO agent created and technical plan requested.")


# --- Wrapper so new.py can import `cto_agent` ---
def cto_agent(message: str) -> str:
    """Wrapper to interact with the CTO agent (for imports in new.py)."""
    return generate_response(message)
