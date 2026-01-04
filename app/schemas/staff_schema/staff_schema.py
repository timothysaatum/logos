import re
from typing import Optional
from uuid import UUID
from datetime import datetime
from pydantic import ( # type: ignore
    BaseModel, 
    Field, 
    field_validator, 
    EmailStr,
    HttpUrl,
    ConfigDict,
    model_validator
)


class DepartmentBase(BaseModel):

    id: int
    name: str
    code: Optional[str]
    description: Optional[str] = None
    
    model_config = ConfigDict(from_attributes=True)


class SpecializationBase(BaseModel):

    id: int
    name: str
    code: Optional[str]
    description: Optional[str] = None
    
    model_config = ConfigDict(from_attributes=True)


class StaffBase(BaseModel):
    
    username: str = Field(..., min_length=3, max_length=50)
    full_name: str = Field(..., min_length=1, max_length=150)
    telephone: str = Field(..., max_length=20)
    email: EmailStr = Field(..., max_length=255)
    
    # Foreign key IDs
    department_id: int = Field(..., description="Department ID")
    specialization_id: int = Field(..., description="Specialization ID")
    
    # Optional fields
    staff_id: Optional[str] = Field(None, max_length=50)
    bio: Optional[str] = Field(None, max_length=500)
    residential_address: Optional[str] = Field(None, max_length=255)
    linkedin_profile: Optional[HttpUrl] = None
    website: Optional[HttpUrl] = None

    @field_validator("staff_id")
    @classmethod
    def validate_staff_id(cls, v: str) -> str:
        v = v.strip().upper()
        if not re.fullmatch(r"STF-[A-Z0-9]{6}", v):
            raise ValueError("staff_id must be in format STF-XXXXXX")
        return v



class StaffCreate(StaffBase):

    password: str = Field(..., min_length=8, max_length=100)
    password_confirm: str  = Field(..., min_length=8, max_length=100)
    
    @field_validator("password")
    @classmethod
    def validate_password(cls, v: str) -> str:
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters')
        has_upper = any(c.isupper() for c in v)
        has_lower = any(c.islower() for c in v)
        has_digit = any(c.isdigit() for c in v)
        if not (has_upper and has_lower and has_digit):
            raise ValueError('Password must contain uppercase, lowercase, and digit')
        return v


    @model_validator(mode="after")
    def validate_passwords_match(self) -> "StaffCreate":
        """Validate that password and password_confirm match."""
        if self.password != self.password_confirm:
            raise ValueError("Passwords do not match")
        return self


class StaffUpdate(BaseModel):

    username: Optional[str] = Field(None, min_length=3, max_length=50)
    full_name: Optional[str] = Field(None, min_length=1, max_length=150)
    telephone: Optional[str] = Field(None, max_length=20)
    email: Optional[EmailStr] = Field(None, max_length=255)
    staff_id: Optional[str] = Field(None, max_length=50)
    bio: Optional[str] = Field(None, max_length=500)
    department_id: Optional[int] = None
    specialization_id: Optional[int] = None
    residential_address: Optional[str] = Field(None, max_length=255)
    linkedin_profile: Optional[HttpUrl] = None
    website: Optional[HttpUrl] = None
    password: Optional[str] = Field(None, min_length=8)


class StaffResponse(StaffBase):

    id: UUID
    is_active: bool
    is_verified: bool
    created_at: datetime
    updated_at: datetime
    
    # Nested relationships
    department: DepartmentBase
    specialization: SpecializationBase
    
    model_config = ConfigDict(
        from_attributes=True,
        json_encoders={HttpUrl: lambda v: str(v) if v else None}
    )


class StaffLogin(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=8, max_length=100)


class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    data: StaffResponse