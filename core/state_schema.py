from typing import Optional, Dict, Any
from pydantic import BaseModel, Field

class AgentState(BaseModel):
    user_input: Optional[str] = Field(None)
    tool_name: Optional[str] = Field(None, description="Name of tool called")
    tool_args: Optional[Dict[str, Any]] = Field(default_factory=dict)
    tool_result: Optional[Any] = Field(None)
    final_response: Optional[str] = Field(None)
    params: Optional[Dict[str, Any]] = Field(default_factory=dict)
