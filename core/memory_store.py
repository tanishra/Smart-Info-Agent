import json
import os
from datetime import datetime
from typing import Any, Dict, List


class MemoryStore:
    """
    Persistent conversation memory for Smart Info Agent (Tool-Based Workflow).
    Compatible with LangGraph's message-based agent interface.
    """

    def __init__(self, filename: str = "data/memory.json"):
        self.filename = filename
        self.data: Dict[str, Any] = {"messages": []}
        self._ensure_directory()
        self._load_from_file()

    # Conversation Management
    def append(self, user_input: str, assistant_output: str) -> None:
        """
        Append a new conversation turn (user + assistant) to memory.
        """
        self.data.setdefault("messages", [])
        self.data["messages"].extend([
            {"role": "user", "content": user_input, "timestamp": datetime.now().isoformat()},
            {"role": "assistant", "content": assistant_output, "timestamp": datetime.now().isoformat()},
        ])
        self._save_to_file()

    def get_messages(self) -> List[Dict[str, str]]:
        """
        Retrieve conversation history formatted for LangGraph agent context.
        """
        return self.data.get("messages", [])

    def clear(self) -> None:
        """Clear the entire conversation memory."""
        self.data = {"messages": []}
        self._save_to_file()

    def get_history(self) -> str:
        """
        Return a readable string summary of conversation history.
        """
        logs = self.data.get("messages", [])
        formatted = []
        for msg in logs:
            timestamp = msg.get("timestamp", "")
            role = msg.get("role", "").capitalize()
            content = msg.get("content", "")
            formatted.append(f"[{timestamp}] {role}: {content}")
        return "\n".join(formatted) if formatted else "No conversation history."

    # Generic Key-Value Storage 
    def save(self, key: str, value: Any) -> None:
        """Save an arbitrary key-value pair to memory."""
        self.data[key] = value
        self._save_to_file()

    def load(self, key: str) -> Any:
        """Retrieve a value by key."""
        return self.data.get(key)

    def dump(self) -> Dict[str, Any]:
        """Return full memory contents."""
        return dict(self.data)

    # Internal Helpers
    def _ensure_directory(self) -> None:
        """Ensure the memory file’s directory exists."""
        directory = os.path.dirname(self.filename)
        if directory and not os.path.exists(directory):
            os.makedirs(directory, exist_ok=True)

    def _save_to_file(self) -> None:
        """Persist memory data to disk."""
        try:
            with open(self.filename, "w", encoding="utf-8") as f:
                json.dump(self.data, f, indent=4, ensure_ascii=False)
        except Exception as e:
            print(f"[MemoryStore] Failed to save memory: {e}")

    def _load_from_file(self) -> None:
        """Load memory from disk (if available)."""
        try:
            if os.path.exists(self.filename):
                with open(self.filename, "r", encoding="utf-8") as f:
                    self.data = json.load(f)
            else:
                self.data = {"messages": []}
        except (FileNotFoundError, json.JSONDecodeError):
            print("[MemoryStore] No valid memory file found — starting fresh.")
            self.data = {"messages": []}

