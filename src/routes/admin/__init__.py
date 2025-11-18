from typing import Annotated, TypeAlias, Optional
from collections.abc import Callable

from fastapi import Depends, APIRouter, Header

from ...api_tags import ADMIN_ONLY
from ...models.api import Admin, AdminType
from ...routes.auth import extract_jwt


def admin_login(
        admin_type: Optional[int]
) -> Callable[[Annotated[str, Header()]], Admin]:
    def inner(x_authorization: Annotated[str, Header()]) -> Admin:
        return extract_jwt(x_authorization, admin_type)
    return inner


adminDependency = Depends(admin_login(None))
""" Depends, который требует токен любого админа """

siteAdminDependency = Depends(admin_login(AdminType.Site))
""" Depends, который требует токен админа сайта """

scheduleAdminDependency = Depends(admin_login(AdminType.Schedule))
""" Depends, который требует токен ответственного за расписание """

coursesAdminDependency = Depends(admin_login(AdminType.Courses))
""" Depends, который требует токен ответственного за курсы """


AdminRequired: TypeAlias = Annotated["Admin", adminDependency]
""" Тип, который требует токен любого админа """

SiteAdminRequired: TypeAlias = Annotated["Admin", siteAdminDependency]
""" Тип, который требует токен админа сайта """

ScheduleAdminRequired: TypeAlias = Annotated["Admin", scheduleAdminDependency]
""" Тип, который требует токен ответственного за расписание """

CourseAdminRequired: TypeAlias = Annotated["Admin", coursesAdminDependency]
""" Тип, который требует токен ответственного за курсы """



admin_router = APIRouter(prefix="/admin", tags=[ADMIN_ONLY])

from .fixed_files import fixed_files_router
from .posts import posts_router
from .settings import admin_settings_router
from .teachers import teachers_router
from .vacancies import vacancies_router

admin_router.include_router(fixed_files_router)
admin_router.include_router(posts_router)
admin_router.include_router(admin_settings_router)
admin_router.include_router(teachers_router)
admin_router.include_router(vacancies_router)
