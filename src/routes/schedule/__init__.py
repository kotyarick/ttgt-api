import json
import os
from typing import List, Dict

from ...api_tags import SCHEDULE

from fastapi import APIRouter, Response, status
from .overrides_downloader import download_overrides
from .schedule_parser import teachers, groups, cache
from .teacher_overrides import teacher_overrides
from fastapi.responses import FileResponse


os.makedirs("applications", exist_ok=True)

_not_found = Response(status_code=status.HTTP_404_NOT_FOUND)

formats = {
    "android": "apk",
    "ios": "ipa"
}

if not os.path.isfile("applications/updates.json"):
    with open("applications/updates.json", "w") as f:
        f.write("{}")

schedule_router = APIRouter(
    prefix="/schedule",
    tags=[SCHEDULE]
)


@schedule_router.get(
    "/items",
    name="Получить список групп и преподавателей"
)
async def get_items() -> Dict[str, List[str]]:
    return {
        "groups": groups,
        "teachers": teachers
    }


@schedule_router.get(
    "/{item_name:str}/schedule",
    name="Получить расписание"
)
async def get_schedule(item_name: str):
    return cache.get(item_name, _not_found)


@schedule_router.get(
    "/{item_name:str}/overrides",
    name="Получить изменения"    
)
async def get_overrides(item_name: str):
    return download_overrides(item_name) if '-' in item_name else teacher_overrides(item_name)


@schedule_router.get("/{platform:str}/updates")
async def get_updates(platform: str):
    return json.load(open("applications/updates.json")).get(platform, _not_found)

@schedule_router.get("/{platform:str}/download")
async def download_update(platform: str):
    format = formats.get(platform)
    print(platform, formats)

    if format is None:
        return _not_found
        
    return FileResponse(
        f"applications/{platform}.{format}",
        filename=f"{platform}.{format}",
        media_type="application/octet-stream",
        content_disposition_type="attachment"
    )
