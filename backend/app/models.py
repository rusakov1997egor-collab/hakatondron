from pydantic import BaseModel
from typing import Optional, Dict, Any, List

class GestureAction(BaseModel):
    action: str

class OrderMessage(BaseModel):
    type: str
    order: Optional[Dict[str, Any]] = None
    action: Optional[str] = None # Для команд вроде START_DELIVERY