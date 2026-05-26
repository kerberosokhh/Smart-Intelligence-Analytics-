from pydantic import BaseModel, Field


class ChatStreamRequest(BaseModel):
    session_id: str = Field(..., min_length=1)
    message: str = Field(..., min_length=1, max_length=4000)


class SchemaTableColumn(BaseModel):
    name: str
    type: str
    nullable: bool = True
    primary_key: bool = False


class SchemaTable(BaseModel):
    columns: list[SchemaTableColumn]


class SchemaResponse(BaseModel):
    tables: dict[str, SchemaTable]
