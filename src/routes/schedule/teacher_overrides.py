from typing import List

from . import overrides_downloader


def for_teacher(lesson: dict, teacher: str, group: str) -> dict | None:
    if lesson.get("commonLesson"):
        if lesson["commonLesson"].teacher == teacher:
            return dict(
                commonLesson=lesson["commonLesson"],
                group=group
            )
    if lesson.get("subgroupedLesson"):
        for subgroup in lesson["subgroupedLesson"]["subgroups"]:
            if subgroup.teacher == teacher:
                return dict(
                    commonLesson=dict(
                        name=lesson["subgroupedLesson"]["name"],
                        teacher=teacher,
                        room=subgroup["room"]
                    ),
                    group=group
                )
    return None

def teacher_overrides(teacher: str):
    overrides_downloader.download_overrides("")
    output: List[dict] = []
    weeknum, weekday = 0, 0

    for group, overrides in overrides_downloader.cache.items():
        weeknum = overrides["weekNum"]
        weekday = overrides["weekDay"]

        for override in overrides["overrides"]:
            shouldBe = for_teacher(override["shouldBe"], teacher, group)
            willBe = for_teacher(override["willBe"], teacher, group)

            if shouldBe is None and willBe is None:
                continue

            output.append(
                dict(
                    shouldBe=shouldBe,
                    willBe=willBe,
                    index=override["index"]
                )
            )

    return dict(
        overrides=output,
        weekNum=weeknum,
        weekDay=weekday
    )
