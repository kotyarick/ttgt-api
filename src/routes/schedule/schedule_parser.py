import os
import zipfile
from typing import Dict, List

import alive_progress
from bs4 import BeautifulSoup


_archive = zipfile.ZipFile('schedule.zip', 'r')
_namelist = _archive.namelist()


cache: Dict[str, dict] = {}

teachers: List[str] = []
groups: List[str] = []

TEACHER = 0
STUDENT = 1


with alive_progress.alive_bar(len(_namelist)) as bar:
    for file in _namelist:
        if not file.endswith(".html"):
            bar()
            continue

        schedule = dict(weeks=[])

        soup = BeautifulSoup(_archive.read(file).decode("windows-1251"), 'html.parser')

        target = soup.find('font', {'face': 'Times New Roman', 'size': '6', 'color': '#ff00ff'}).children.__next__().text.strip()

        if target == '.':
            bar()
            continue

        target_type: int = -1

        if file.startswith("teacher/"):
            if target in teachers:
                print(file)
                continue

            teachers.append(target)
            target_type = TEACHER

        elif file.startswith("student/"):
            if target in groups:
                print(file)
                continue

            groups.append(target)
            target_type = STUDENT
        else:
            bar()
            continue

        for table in soup.find_all("table"):
            week = dict(days=[])

            #  Первые две строки таблицы - это номера пар и время
            for row_index, row in enumerate(table.find_all("tr")[2:]):
                day = dict(lesson=[])

                #  Первая ячейка - это день недели
                for cell_index, cell in enumerate(row.find_all("td")[1:]):
                    childs = list(cell.find("font").find("p").stripped_strings)
                    text = [text.strip() for text in childs if text.strip()]

                    if not text or text[0] in "-_":
                        day["lesson"].append(None)
                        continue

                    match target_type:
                        case 0:
                            match len(text):
                                case 3:
                                    group, name, room = text
                                case 2:
                                    group_and_name, room = text

                                    group = name = ""
                                    num = False

                                    for i in group_and_name:
                                        if i == '-' or i.isdigit():
                                            num = True
                                        if num and not (i == '-' or i.isdigit()):
                                            break
                                        group += i

                                    name = group_and_name[len(group):]

                            day["lesson"].append(dict(
                                group=group,
                                commonLesson=dict(
                                    name=name,
                                    room=room,
                                    teacher=target
                                )
                            ))
                        case 1:
                            if len(text) == 2:
                                name = text[0]
                                teacher, room = text[1].rsplit(" ", 1)

                                lesson = dict(
                                    commonLesson=dict(
                                        name=name,
                                        teacher=teacher,
                                        room=room
                                    ),
                                    group=target
                                )
                            elif len(text) == 3:
                                name = text[0]
                                subgroups = [
                                    dict(
                                        teacher=string[6:].rsplit(" ", 1)[0],
                                        room=string[6:].rsplit(" ", 1)[1],
                                        subgroup_index=index+1
                                    )
                                    for index, string in enumerate(text[1:])
                                ]
                                """
                                [
                                    'Иностранный язык', 
                                    '1 п/г Предеина Е.И. 201', 
                                    '2 п/г Акиева Н.В. 236'
                                ]
                                """

                                lesson = dict(
                                    subgroupedLesson=dict(
                                        name=name,
                                        subgroups=subgroups
                                    ),
                                    group=target
                                )
                            day["lesson"].append(lesson)

                week["days"].append(day)

            schedule["weeks"].append(week)

        cache[target] = schedule
        bar()
