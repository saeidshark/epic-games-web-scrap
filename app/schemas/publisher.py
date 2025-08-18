from pydantic import BaseModel

class PublisherBase(BaseModel):
    name: str
    website: str | None = None

class PublisherCreate(PublisherBase):
    pass

class PublisherUpdate(PublisherBase):
    pass

class PublisherOut(PublisherBase):
    id: int

    class Config:
        from_attributes = True

