from fastapi import APIRouter

from app.db.sqlite import get_business_schema
from app.schemas.chat import SchemaResponse, SchemaTable, SchemaTableColumn

router = APIRouter(prefix="/api", tags=["schema"])


@router.get("/schema", response_model=SchemaResponse)
def get_schema() -> SchemaResponse:
    raw = get_business_schema()
    tables = {
        name: SchemaTable(
            columns=[SchemaTableColumn(**col) for col in table["columns"]]
        )
        for name, table in raw["tables"].items()
    }
    return SchemaResponse(tables=tables)
