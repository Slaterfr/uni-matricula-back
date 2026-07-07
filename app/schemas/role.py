import uuid
from typing import Optional
from pydantic import BaseModel

class RoleBase(BaseModel):
    name: str
    description: Optional[str] = None

class RoleCreate(RoleBase):
    pass

class RoleUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None

class RoleRead(RoleBase):
    id: uuid.UUID

    model_config = {
        "from_attributes": True
    }
