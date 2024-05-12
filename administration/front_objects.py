from pydantic import BaseModel


class Card(BaseModel):
    title: str
    subtitle: str
    content: str
    bootstrap_class: str
    style: str
