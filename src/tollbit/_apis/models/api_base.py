from pydantic import BaseModel


class TollbitBaseModel(BaseModel):
    model_config = {"populate_by_name": True}
