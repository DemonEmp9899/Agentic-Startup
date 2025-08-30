from ceo_hf_agent import ceo_agent
from cto_hf_agent import cto_agent
from marketer_hf_agent import marketer_agent
from designer_hf_agent import designer_agent

# Shared conversation state
conversation = []

# Agent registry
agents = {
    "CEO": ceo_agent,
    "CTO": cto_agent,
    "Designer": designer_agent,
    "Marketer": marketer_agent
}

# Order of speaking
agent_order = ["CEO", "CTO", "Designer", "Marketer"]

def send_message(agent_name, message, from_agent="SYSTEM"):
    """Send message to one agent and store reply."""
    agent_fn = agents[agent_name]
    response = agent_fn(f"{from_agent}: {message}")

    conversation.append({
        "from": from_agent,
        "to": agent_name,
        "message": message,
        "response": response
    })

    print(f"\n{agent_name} says:")
    print(response)
    return response

def run_interaction(max_rounds=5):
    print("=== Startup Simulation Begins ===")

    # Kickoff from CEO
    msg = "We need to build an AI-powered personal finance assistant."
    current_speaker = "CEO"
    response = send_message(current_speaker, msg, from_agent="CEO")

    # Conversation loop
    for round_num in range(max_rounds):
        print(f"\n--- Round {round_num+1} ---")

        for i, speaker in enumerate(agent_order):
            # Pick next agent in line
            next_index = (i + 1) % len(agent_order)
            next_agent = agent_order[next_index]

            # Pass the last response forward
            response = send_message(next_agent, response, from_agent=speaker)

            # If someone says "DONE", break out
            if isinstance(response, dict):
                if response.get("status", "").upper() == "DONE":
                    print("\n✅ All agents have completed their tasks.")
                    print("=== Simulation Ends ===")
                    return
            elif isinstance(response, str):
                if "DONE" in response.upper():
                    print("\n✅ Conversation reached conclusion.")
                    print("=== Simulation Ends ===")
                    return

    print("\n⚠️ Max rounds reached, stopping conversation.")
    print("=== Simulation Ends ===")


if __name__ == "__main__":
    run_interaction()
