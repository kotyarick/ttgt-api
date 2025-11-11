import traceback
from typing import Dict

import pdfplumber

from . import downloader, overrides_downloader


#  Из строки таблицы получить эти данные:
#  - Информация о подгруппах, если есть
#  - Инициалы преподавателя
#  - Номер кабинета
#  - Индекс пары
#  - Название пары
def parse_lesson(
    row: str, 
    room: str
):
    if row is None: return None
    #  Убираем переход на другую строку
    row = row.replace("\n", " ")

    #  Снятие пары - это замены на ничего
    if row.lower() in ['', 'снят']:
        return None

    #  Разделяем по пробелам
    split = row.split(" ")
    
    if "п/г" not in row:
        #  Если подгруппы нет, то тут всё просто
        
        return dict(
            #  Последние два элемента - это инициалы препода

            #  Убираем инициалы и получаем только название
            name=" ".join(split[:-2]),

            #  Убираем всё кроме инициалов
            teacher=" ".join(split[-2:]),

            room=room
        )

    #  А если подгруппа есть, то капец блин
    #  Каждый раз могут по-разному написать это
    #  хоть п/гр, хоть п/г
    #  могут вообще просто на разных строках подгруппы пихнуть,
    #  без явного обозначения
    name, etc = row.split("п/г")
    name = name.strip()

    return (
        #  Мы разделили строку по "п/г"
        #  Получили что-то вроде ["Призыв демона через мнимые числа 1 ", (тут п/г типа) " Моисеева"]
        #  В первом элементе будет номер подгруппы, его надо убрать
        " ".join(name.split(" ")[:-1]),
        dict(
            #  Если используется п/гр, то надо убрать р
            teacher=etc[1:].strip() if etc.startswith("р") else etc,
            room=room,
            subgroup_index=int(name.split(" ")[-1][-1])
        )
    )

def parse_overrides():
    current_group = None
    out: Dict[str, Overrides] = {}


    #  Парсим этот ужас
    with pdfplumber.open(f"{downloader.dir}zamena.pdf") as pdf:
        rows = []
        #  первые две строки первой страницы
        weeknum, weekday = pdf\
        .pages[0]\
        .extract_text()\
        .split("\n")[:2]

        #  Номер недели - это пятое слово первой строки
        weeknum = int(weeknum.split(" ")[4])-1
        weekday = [
            "понедельник",
            "вторник",
            "среда",
            "четверг",
            "пятница",
            "суббота",
            "воскресенье"
            #  День недели - это четвёртое слово второй строки
        ].index(weekday.split(" ")[3].lower().replace("_", ""))


        for page in pdf.pages:
            for table in page.extract_tables():
                for row in table:

                    #  rows имеют все строки со всех таблиц со всех страниц
                    rows.append(row)

        i = None

        #  Пары с подгруппой, которые должны быть по рассписанию...
        shouldSubgroupedLessons = []
        #  ...и пары, которые состоятся из-за изменений
        willSubgroupedLessons = []

        #  Первая строка не нужна, там только обозначения столбцов
        for row in rows[1:]:
            try:
                #  Если группа указана, сохраняем её
                if row[0] and current_group != row[0]: 
                    current_group = row[0]
                    shouldSubgroupedLessons = []
                    willSubgroupedLessons = []


                #  Если изменения для группы не сохранены, то добавляем их
                if current_group not in out:
                    out[current_group] = dict(
                        overrides = [],
                        weekDay=weekday,
                        weekNum=weeknum
                    )

                #  s - should - по расписанию
                s = parse_lesson(row[2], row[4])
                #  w - will - по замене
                w = parse_lesson(row[3], row[4])

                if type(s) == dict and s.get("subgroups"):
                    shouldSubgroupedLessons.append(s)
                if type(w) == dict and w.get("subgroups"):
                    willSubgroupedLessons.append(w)

                if len(willSubgroupedLessons) > 0:
                    w = dict(
                        name=willSubgroupedLessons[0][0],
                        subgroups=[x[1] for x in willSubgroupedLessons]
                    )

                if len(shouldSubgroupedLessons) > 0:
                    s = dict(
                        name=shouldSubgroupedLessons[0][0],
                        subgroups=[x[1] for x in shouldSubgroupedLessons]
                    )

                i = row[1] or i
                
                if type(s) == tuple:
                    s = dict(
                        name=s[0],
                        subgroups=[s[1]]
                    )

                if type(w) == tuple:
                    w = dict(
                        name=w[0],
                        subgroups=[w[1]]
                    )
                
                out[current_group]["overrides"].append(dict(
                    shouldBe=(
                        None
                        if s is None else
                        { "commonLesson" if type(s) == dict and not s.get("subgroups") else "subgroupedLesson": s }
                    ),

                    willBe=(
                        None
                        if w is None else
                        { "commonLesson" if type(w) == dict and not w.get("subgroups") else "subgroupedLesson": w }
                    ),

                    index=int(i)-1
                ))
            except Exception as error:
                print(traceback.format_exc())
                i = None

                #  Пары с подгруппой, которые должны быть по рассписанию...
                shouldSubgroupedLessons = []
                #  ...и пары, которые состоятся из-за изменений
                willSubgroupedLessons = []
        return out


if __name__ == "__main__":
    overrides_downloader.download("Д-1-1")
