from pydantic import BaseModel

class PlatformBase(BaseModel):
    name: str

class PlatformCreate(PlatformBase):
    pass

class PlatformUpdate(PlatformBase):
    pass

class PlatformOut(PlatformBase):
    id: int

    class Config:
        from_attributes = True  # برای ORM
