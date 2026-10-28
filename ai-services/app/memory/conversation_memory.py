"""Conversation memory management."""
from typing import List, Dict

def format_history(messages: List[Dict], max_turns: int = 5) -> str:
    """Format conversation history for prompt injection."""
    if not messages:
        return "No previous conversation."
    recent = messages[-max_turns * 2:]
    lines = []
    for msg in recent:
        role = msg.get("role", "user").upper()
        content = msg.get("content", "")[:500]  # Truncate long messages
        lines.append(f"{role}: {content}")
    return "\n".join(lines)
