# designer_hf_agent.py (GitHub Models version)
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
def create_designer_agent():
    """Create the Designer agent structure."""
    return {
        "id": "Designer",
        "role": "UX/UI Designer",
        "display_name": "Designer",
        "system_prompt": (
            "You are the Designer agent for the startup. "
            "Your role is to create product interface concepts, improve usability, "
            "and ensure visual appeal matches the business vision. "
            "You collaborate with CEO and CTO to produce detailed text-based mockups, "
            "color schemes, and layout suggestions."
        ),
        "goals": [
            "Create intuitive UI/UX flows",
            "Propose color palettes and typography",
            "Ensure accessibility and responsiveness",
            "Collaborate with CTO on technical feasibility"
        ],
        "memory": {
            "long_term": [
                {"id": "design_pref", "title": "Favor minimalistic and modern UI", "created": datetime.now().isoformat()}
            ],
            "short_term": []
        },
        "created_at": datetime.now().isoformat()
    }

def update_state_with_designer(designer_agent):
    """Add Designer agent to the simulation state."""
    if not os.path.exists(STATE_FILE):
        raise FileNotFoundError(f"{STATE_FILE} not found. Run CEO agent first.")
    
    with open(STATE_FILE, "r") as f:
        state = json.load(f)
    
    state["agents"]["Designer"] = designer_agent
    
    with open(STATE_FILE, "w") as f:
        json.dump(state, f, indent=2)
    
    print("✅ Designer agent added to simulation state.")
    return state

def ask_designer_for_mockups(state):
    """Ask Designer to propose UI mockups and style guidelines."""
    designer = state["agents"]["Designer"]
    ceo_messages = [m for m in state["chat_history"] if m["from"] == "CEO"]
    cto_messages = [m for m in state["chat_history"] if m["from"] == "CTO"]
    
    prompt = (
        f"{designer['system_prompt']}\n"
        f"Long-term memory: {json.dumps(designer['memory']['long_term'], indent=2)}\n"
        f"Recent CEO instructions: {json.dumps(ceo_messages[-1], indent=2) if ceo_messages else 'None'}\n"
        f"Recent CTO plan: {json.dumps(cto_messages[-1], indent=2) if cto_messages else 'None'}\n"
        f"Question: Provide a UI/UX concept including color palette, layout, and feature highlights. "
        f"Respond in JSON with keys: layout, colors, typography, notes."
    )
    
    response = client.chat.completions.create(
        model="gpt-4o-mini",  # you can swap for another GitHub model if needed
        messages=[
            {"role": "system", "content": designer["system_prompt"]},
            {"role": "user", "content": prompt}
        ]
    )

    raw_output = response.choices[0].message.content

    # Save conversation in state
    state["chat_history"].append({
        "from": "Designer",
        "to": ["CEO", "CTO", "Marketer"],
        "timestamp": datetime.now().isoformat(),
        "type": "proposal",
        "subject": "UI/UX concept",
        "body": raw_output
    })
    
    with open(STATE_FILE, "w") as f:
        json.dump(state, f, indent=2)
    
    return raw_output

# --- Shared public function for new.py ---
def generate_response(prompt: str):
    """Public function that can be imported in new.py"""
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "system", "content": "You are the Designer agent."},
                  {"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content

# --- Wrapper so new.py can import `designer_agent` ---
def designer_agent(message: str) -> str:
    return generate_response(message)

if __name__ == "__main__":
    # Load state
    with open(STATE_FILE, "r") as f:
        state = json.load(f)
    
    # Add Designer agent
    designer_agent_struct = create_designer_agent()
    state = update_state_with_designer(designer_agent_struct)
    
    print("💬 Asking Designer for UI/UX concepts...")
    answer = ask_designer_for_mockups(state)
    print("\n--- Designer's UI/UX Concept ---")
    print(answer)
