from enum import Enum
from typing import Optional

from pydantic import BaseModel


class RoleName(str, Enum):
    admin = "admin"
    vendor = "vendor"
    procurement = "procurement"


class RoleBase(BaseModel):
    name: RoleName
    description: Optional[str] = None


class RoleCreate(RoleBase):
    """Schema for creating a new role."""

    pass


class RoleUpdate(BaseModel):
    """Schema for updating an existing role."""

    description: Optional[str] = None


class RoleRead(RoleBase):
    """Schema returned when reading a role."""

    id: int

    class Config:
        orm_mode = True


