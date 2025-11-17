from ..database import Session
from ..models.database import DatabaseSettings
from ..models.api import Settings
from fastapi import Depends, APIRouter, Header
from ..api_tags import SETTINGS

public_settings_router = APIRouter(
    prefix="/settings",
    tags=[SETTINGS]
)

@public_settings_router.get("/")
async def get_settings(names: str):
    names = names.split(" ")
    
    with Session.begin() as session:
        result = session.query(DatabaseSettings).filter(DatabaseSettings.name.in_(names)).all()
        result = [
            Settings.from_database(setting)
            for setting in result
        ]
        result = [
            setting.privatize()
            for setting in result
        ]

    return result
