# marketer_hf_agent.py (GitHub Models version)
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

# --- Step 1: Create Marketer agent ---
def create_marketer_agent():
    return {
        "id": "Marketer",
        "role": "Growth and customer acquisition",
        "display_name": "Marketer",
        "system_prompt": (
            "You are the Marketer agent of a startup. "
            "Your job is to analyze the target market, create marketing strategies, "
            "design campaigns, and suggest growth tactics. "
            "Always return structured, actionable output."
        ),
        "goals": [
            "Identify target customer segments",
            "Design creative campaigns",
            "Plan social media and content strategy",
            "Suggest growth and distribution tactics"
        ],
        "memory": {
            "long_term": [
                {"id": "marketing_goal", "title": "Reach 100k impressions in 6 months", "created": datetime.now().isoformat()}
            ],
            "short_term": []
        },
        "created_at": datetime.now().isoformat()
    }

# --- Step 2: Ask Marketer for plan ---
def ask_marketer_for_plan(state):
    marketer = state["agents"]["Marketer"]
    ceo_messages = [m for m in state["chat_history"] if m["from"] == "CEO"]

    prompt = (
        f"{marketer['system_prompt']}\n"
        f"Long-term memory: {json.dumps(marketer['memory']['long_term'], indent=2)}\n"
        f"Recent CEO instructions: {json.dumps(ceo_messages[-1], indent=2) if ceo_messages else 'None'}\n"
        "Question: What is your marketing plan? "
        "Respond ONLY in valid JSON format with the following structure:\n"
        "{\n"
        '  "campaigns": ["idea1", "idea2"],\n'
        '  "social_post": "short engaging example post",\n'
        '  "growth_strategies": ["strategy1", "strategy2"]\n'
        "}"
    )

    response = client.chat.completions.create(
        model="gpt-4o-mini",  # you can swap to another GitHub-hosted model
        messages=[
            {"role": "system", "content": marketer["system_prompt"]},
            {"role": "user", "content": prompt}
        ]
    )

    raw_output = response.choices[0].message.content

    # Try to parse JSON
    try:
        json_data = json.loads(raw_output)
        print("\n--- Marketer's Plan (JSON) ---")
        print(json.dumps(json_data, indent=2))
    except json.JSONDecodeError:
        print("\n⚠️ Could not parse JSON, raw output:")
        print(raw_output.strip())
        json_data = {
            "campaigns": [],
            "social_post": raw_output.strip(),
            "growth_strategies": []
        }

    # Save to state
    state["chat_history"].append({
        "from": "Marketer",
        "to": ["CEO", "CTO", "Designer"],
        "timestamp": datetime.now().isoformat(),
        "type": "proposal",
        "subject": "Marketing plan",
        "body": json_data
    })

    with open(STATE_FILE, "w") as f:
        json.dump(state, f, indent=2)

    return json_data

# --- Shared public function for new.py ---
def generate_response(prompt: str):
    """Allow other agents (or orchestrator) to ask the Marketer something."""
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "system", "content": "You are the Marketer agent."},
                  {"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content

# --- Wrapper so new.py can import `marketer_agent` ---
def marketer_agent(message: str) -> str:
    return generate_response(message)

if __name__ == "__main__":
    # Load state
    if not os.path.exists(STATE_FILE):
        raise FileNotFoundError(f"{STATE_FILE} not found. Run CEO agent first.")

    with open(STATE_FILE, "r") as f:
        state = json.load(f)

    # Overwrite marketer agent with the correct structure
    marketer_agent_struct = create_marketer_agent()
    state["agents"]["Marketer"] = marketer_agent_struct

    with open(STATE_FILE, "w") as f:
        json.dump(state, f, indent=2)

    # Ask Marketer for plan
    print("💬 Asking Marketer for plan...")
    ask_marketer_for_plan(state)
