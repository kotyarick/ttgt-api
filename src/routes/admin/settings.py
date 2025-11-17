import json
from fastapi import APIRouter
from typing import List

from ...api_tags import SETTINGS
from ...models.api import Settings
from ...models.database import DatabaseSettings
from ...database import Session

admin_settings_router = APIRouter(prefix="/settings", tags=[SETTINGS])

@admin_settings_router.get("/")
async def get_settings(names: str):
    names = names.split(" ")
    
    with Session.begin() as session:
        result = session.query(DatabaseSettings).filter(DatabaseSettings.name.in_(names)).all()
        result = [
            Settings.from_database(setting)
            for setting in result
        ]
    
    return result

@admin_settings_router.patch("/", status_code=204)
async def edit_settings(settings: List[Settings]):
    for setting in settings:
        with Session.begin() as session:
            result = session.query(DatabaseSettings).filter(
                DatabaseSettings.name == setting.name
            ).one_or_none()
            
            if result:
                result.value = json.dumps(setting.value)
                result.name = setting.name

                session.commit()
            else:
                session.add(DatabaseSettings(
                    name=setting.name,
                    value=json.dumps(setting.value),
                    enabled=setting.enabled
                ))
