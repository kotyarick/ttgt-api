import os
import json
import zipfile
from typing import Dict, List

import alive_progress
from bs4 import BeautifulSoup
import concurrent.futures

_archive = zipfile.ZipFile('database/fixed_files/schedule.zip', 'r')
_namelist = _archive.namelist()


cache: Dict[str, dict] = {}
filenames: Dict[str, str] = {}
items: Dict[str, List[str]] = {
    "groups": [],
    "teachers": []
}

TEACHER = 0
STUDENT = 1

def get_html(target):
    if not target in filenames: return

    return _archive.read(filenames[target]).decode("windows-1251").replace("windows-1251", "utf-8")

def process_file(file):
    if not file.endswith(".html"):
        return
        
    schedule = dict(weeks=[])

    soup = BeautifulSoup(_archive.read(file).decode("windows-1251"), 'html.parser')

    target = soup.find('font', {'face': 'Times New Roman', 'size': '6', 'color': '#ff00ff'}).children.__next__().text.strip()

    if target.lower() in [".", "вакансия"]:
        return

    target_type: int = -1

    print(target, "." in target, "-" in target)

    if "." in target:
        if target in items["teachers"]:
            return

        items["teachers"].append(target)
        target_type = TEACHER

    elif "-" in target:
        if target in items["groups"]:
            return

        items["groups"].append(target)
        target_type = STUDENT
    else:
        return

    filenames[target] = file

    for table in soup.find_all("table"):
        week = dict(days=[])

        #  Первые две строки таблицы - это номера пар и время
        for row_index, row in enumerate(table.find_all("tr")[2:]):
            day = dict(lessons=[])

            #  Первая ячейка - это день недели
            for cell_index, cell in enumerate(row.find_all("td")[1:]):
                childs = list(cell.find("font").find("p").stripped_strings)
                text = [text.strip() for text in childs if text.strip()]

                if not text or text[0] in "-_":
                    day["lessons"].append(None)
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

                        day["lessons"].append(dict(
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
                        day["lessons"].append(lesson)

            week["days"].append(day)

        schedule["weeks"].append(week)

    cache[target] = schedule


def update(force: bool = False):
    global items, cache, filenames
    
    if force or not all([os.path.exists(file) for file in ("items.json", "schedule.json", "filenames.json")]):
        with alive_progress.alive_bar(len(_namelist)) as bar:
            for file in _namelist:
                process_file(file)
                bar()


        items["teachers"].sort()
        items["groups"].sort()


        with open("filenames.json", "w") as f: json.dump(filenames, f)
        with open("schedule.json", "w") as f: json.dump(cache, f)
        with open("items.json", "w") as f: json.dump(items, f)
    else:
        print(items)
        items = json.load(open("items.json"))
        cache = json.load(open("schedule.json"))
        filenames = json.load(open("filenames.json"))
        print(items)
