from dataclasses import dataclass
from typing import Optional


@dataclass
class VirtualMachine:
    name: str
    token: str
    last_update: float
    ip: Optional[str] = None

