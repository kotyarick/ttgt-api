import re
import traceback
from typing import Dict
import pdfplumber
from . import downloader, overrides_downloader

weekdays = [
    "понедельник", "вторник", "среда", "четверг", "пятница", "суббота", "воскресенье"
]

months = [
    "января", "февраля", "марта", "апреля", "мая", "инюня",
    "июля", "августа", "сентября", "октября", "ноября", "декабря"
]

TEACHER_PATTERN = re.compile(r'(?P<teacher>[А-ЯЁ][а-яё-]+(?:\-[А-ЯЁ][а-яё-]+)?\s+[А-ЯЁ]\.\s*[А-ЯЁ]?\.?)')

def parse_cell_content(cell_text: str, room_str: str):
    if not cell_text or cell_text.lower() in ['', 'снят', 'нет']:
        return []

    cell_text = cell_text.replace('\xa0', ' ')
    
    raw_lines = cell_text.split('\n')
    lessons = []
    current_name_parts = []
    
    rooms = room_str.split('\n') if room_str else []
    rooms = [r.strip() for r in rooms if r.strip()]

    for line in raw_lines:
        line = line.strip()
        if not line:
            continue
            
        match = TEACHER_PATTERN.search(line)
        
        if match:
            teacher = match.group('teacher')
            name_part = line[:match.start()].strip()
            current_name_parts.append(name_part)
            
            full_name = " ".join(current_name_parts).strip()
            
            subgroup_index = None
            if "п/г" in full_name:
                sg_match = re.search(r'(\d)\s*п/г', full_name)
                if sg_match:
                    subgroup_index = int(sg_match.group(1))
                full_name = re.sub(r'\d?\s*п/г[р]?', '', full_name).strip()

            lessons.append({
                "name": full_name,
                "teacher": teacher,
                "room": room_str, 
                "subgroup_index": subgroup_index
            })
            current_name_parts = []
        else:
            current_name_parts.append(line)

    if current_name_parts:
        full_name = " ".join(current_name_parts).strip()
        lessons.append({
            "name": full_name,
            "teacher": None,
            "room": room_str,
            "subgroup_index": None
        })

    has_teachers = any(l['teacher'] is not None for l in lessons)
    
    if not has_teachers and len(lessons) == 1:
        merged_text = cell_text.replace("\n", " ").strip()
        while "  " in merged_text:
            merged_text = merged_text.replace("  ", " ")
            
        split = merged_text.split(" ")
        
        if len(split) >= 2:
            if len(split) == 2:
                return [{
                    "name": split[0],
                    "teacher": split[1],
                    "room": room_str,
                    "subgroup_index": None
                }]
            else:
                return [{
                    "name": " ".join(split[:-2]),
                    "teacher": " ".join(split[-2:]),
                    "room": room_str,
                    "subgroup_index": None
                }]

    if len(lessons) > 1 and len(rooms) == len(lessons):
        for i, lesson in enumerate(lessons):
            lesson['room'] = rooms[i]
    elif len(lessons) > 0 and len(rooms) == 1:
         for lesson in lessons:
            lesson['room'] = rooms[0]

    if len(lessons) > 1:
        for i, lesson in enumerate(lessons):
            if lesson['subgroup_index'] is None:
                lesson['subgroup_index'] = i + 1

    return lessons

def parse_overrides():
    current_group = None
    out: Dict[str, dict] = {}

    with pdfplumber.open(f"{downloader.dir}zamena.pdf") as pdf:
        rows = []
        try:
            text = pdf.pages[0].extract_text()
            if not text: return {}
            weeknum_line, weekday_line = text.split("\n")[:2]

            day, month_str, year_str = weekday_line.split(" ")[:3]
            day = int(day)
            month = months.index(month_str.lower())
            year = int(year_str[:4])
            
            weeknum = int(weeknum_line.split(" ")[4]) - 1
            weekday = weekdays.index(weekday_line.split(" ")[3].lower().replace("_", ""))
        except Exception:
            return {}

        for page in pdf.pages:
            for table in page.extract_tables():
                for row in table:
                    rows.append(row)

        i = None

        for row in rows[1:]:
            try:
                if not row or len(row) < 5: continue
                
                if row[0] and current_group != row[0]: 
                    current_group = row[0]

                if current_group not in out:
                    out[current_group] = dict(
                        overrides=[],
                        weekDay=weekday,
                        weekNum=weeknum,
                        day=day,
                        month=month,
                        year=year
                    )

                s_list = parse_cell_content(row[2], row[4])
                w_list = parse_cell_content(row[3], row[4])

                should_entry = None
                if s_list:
                    if len(s_list) == 1:
                         should_entry = { "commonLesson": s_list[0] }
                    else:
                        should_entry = { 
                            "subgroupedLesson": {
                                "name": s_list[0]["name"],
                                "subgroups": s_list 
                            }
                        }

                will_entry = None
                if w_list:
                    if len(w_list) == 1:
                         will_entry = { "commonLesson": w_list[0] }
                    else:
                        will_entry = { 
                            "subgroupedLesson": {
                                "name": w_list[0]["name"],
                                "subgroups": w_list 
                            }
                        }

                i = row[1] or i
                
                out[current_group]["overrides"].append(dict(
                    shouldBe=should_entry,
                    willBe=will_entry,
                    index=int(i)-1 if i else 0
                ))
            except Exception:
                print(traceback.format_exc())

        if out:
            print(out[list(out.keys())[0]])
        return out

if __name__ == "__main__":
    overrides_downloader.download("Д-1-1")
