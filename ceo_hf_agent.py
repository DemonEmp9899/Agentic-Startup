# ceo_hf_agent.py (GitHub Models version)
from openai import OpenAI
import json
from datetime import datetime
import os
from dotenv import load_dotenv
STATE_FILE = "sim_state.json"
STARTUP_NICHE = "AI-powered personal finance assistant"

# Setup OpenAI client (GitHub Models)
client = OpenAI(
    api_key=os.getenv("YOUR_API_KEY_HERE"),
    base_url="https://models.inference.ai.azure.com"
)

# --- Step 1: Create CEO agent ---
def create_ceo_agent(niche: str):
    return {
        "id": "CEO",
        "role": "Vision and strategy leader",
        "display_name": "CEO",
        "system_prompt": f"You are the CEO agent of a startup in the niche: {niche}. "
                         "Define vision, set strategy, and coordinate CTO, Designer, and Marketer. "
                         "Always be concise, strategic, and clear.",
        "goals": [
            "Define startup vision and mission",
            "Coordinate CTO, Designer, and Marketer",
            "Produce business plan and roadmap",
            "Ensure market alignment and feasibility"
        ],
        "memory": {
            "long_term": [
                {"id": "goal_1", "title": "Reach 10k MAU in 12 months", "created": datetime.now().isoformat()},
                {"id": "context_niche", "title": f"Startup niche: {niche}", "created": datetime.now().isoformat()}
            ],
            "short_term": []
        },
        "created_at": datetime.now().isoformat()
    }

# --- Step 2: Initialize sim state ---
def initialize_state(ceo_agent):
    state = {
        "agents": {
            "CEO": ceo_agent,
            "CTO": {"id": "CTO", "role": "Tech strategist", "goals": [], "memory": {"long_term": [], "short_term": []}},
            "Designer": {"id": "Designer", "role": "UX/UI", "goals": [], "memory": {"long_term": [], "short_term": []}},
            "Marketer": {"id": "Marketer", "role": "Growth", "goals": [], "memory": {"long_term": [], "short_term": []}}
        },
        "documents": {
            "business_plan": "",
            "swot_analysis": "",
            "roadmap": "",
            "designs": "",
            "marketing_plan": ""
        },
        "chat_history": [],
        "meta": {"created_at": datetime.now().isoformat(), "niche": STARTUP_NICHE}
    }
    with open(STATE_FILE, "w") as f:
        json.dump(state, f, indent=2)
    return state

# --- Step 3: Ask CEO for first action ---
def ask_ceo_first_action(state):
    ceo = state["agents"]["CEO"]
    prompt = (
        f"{ceo['system_prompt']}\n"
        f"Long-term memory: {json.dumps(ceo['memory']['long_term'], indent=2)}\n"
        "Question: What is your first action as CEO? "
        "Respond ONLY in valid JSON format with the following structure:\n"
        "{\n"
        '  "messages": [],\n'
        '  "artifacts": [],\n'
        '  "decision": "your concise decision here"\n'
        "}"
    )

    response = client.chat.completions.create(
        model="gpt-4o-mini",   # <-- replace with another GitHub model if you want
        messages=[
            {"role": "system", "content": ceo["system_prompt"]},
            {"role": "user", "content": prompt}
        ]
    )

    raw_output = response.choices[0].message.content

    # Try to parse JSON
    try:
        json_start = raw_output.index("{")
        json_end = raw_output.rindex("}") + 1
        json_str = raw_output[json_start:json_end]
        json_data = json.loads(json_str)

        print("\n--- CEO's First Action (JSON) ---")
        print(json.dumps(json_data, indent=2))
    except (ValueError, json.JSONDecodeError):
        print("\n⚠️ Could not parse JSON, raw output:")
        print(raw_output.strip())
        json_data = {"messages": [], "artifacts": [], "decision": raw_output.strip()}

    # Save to state
    state["chat_history"].append({
        "from": "CEO",
        "to": ["CTO", "Designer", "Marketer"],
        "timestamp": datetime.now().isoformat(),
        "type": "proposal",
        "subject": "First action",
        "body": json_data
    })
    with open(STATE_FILE, "w") as f:
        json.dump(state, f, indent=2)

# --- Step 4: Shared function for other agents ---
def generate_response(prompt: str):
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "system", "content": "You are the CEO agent."},
                  {"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content

# --- Step 5: Main execution ---
if __name__ == "__main__":
    ceo_agent = create_ceo_agent(STARTUP_NICHE)
    state = initialize_state(ceo_agent)
    print("✅ CEO agent created and simulation state initialized.")

    print("💬 Asking CEO for first action...")
    ask_ceo_first_action(state)

# --- Step 6: Wrapper for imports ---
def ceo_agent(message: str) -> str:
    """Wrapper to interact with the CEO agent (for imports in new.py)."""
    return generate_response(message)
