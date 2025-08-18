from pydantic import BaseModel

class DeveloperBase(BaseModel):
    name: str

class DeveloperCreate(DeveloperBase):
    pass

class DeveloperUpdate(DeveloperBase):
    pass

class DeveloperOut(DeveloperBase):
    id: int

    class Config:
       from_attributes = True
