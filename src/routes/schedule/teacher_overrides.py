from typing import List

from . import overrides_downloader


def for_teacher(lesson: dict, teacher: str, group: str) -> dict | None:
    if lesson is None: return None
    if lesson.get("commonLesson"):
        if lesson["commonLesson"]["teacher"] == teacher:
            return dict(
                commonLesson=lesson["commonLesson"],
                group=group
            )
    if lesson.get("subgroupedLesson"):
        for subgroup in lesson["subgroupedLesson"]["subgroups"]:
            if subgroup["teacher"] == teacher:
                return dict(
                    commonLesson=dict(
                        name=lesson["subgroupedLesson"]["name"],
                        teacher=teacher,
                        room=subgroup["room"]
                    ),
                    group=group
                )
    return None

def combine_overrides(first, second):
    return dict(
        shouldBe=first["shouldBe"] or second["shouldBe"],
        willBe=first["willBe"] or second["willBe"],
        index=first["index"]
    )
        

def teacher_overrides(teacher: str):
    overrides_downloader.download_overrides("")
    output: List[dict] = []
    weeknum = weekday = day = month = year = 0

    for group, overrides in overrides_downloader.cache.items():
        weeknum = overrides["weekNum"]
        weekday = overrides["weekDay"]
        
        day = overrides["day"]
        month = overrides["month"]
        year = overrides["year"]

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

    lesson_indexes = [over["index"] for over in output]
    # Индекс пары(over.index): индекс замены(overrides[INDEX])
    inde = {}
    
    for index, lesson in enumerate(lesson_indexes):
        inde[lesson] = inde.get(lesson, [])
        inde[lesson].append(index)

    for i in inde:
        if len(inde[i]) < 2: continue

        res = combine_overrides(output[inde[i][0]], output[inde[i][1]])
        output[inde[i][0]] = res

    remove = [inde[i][1] for i in inde]
    output = [out for index, out in enumerate(output) if index not in remove]
    
    return dict(
        overrides=output,
        weekNum=weeknum,
        weekDay=weekday,
        day = day,
        month = month,
        year = year,
    )
