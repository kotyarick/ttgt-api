import os
from datetime import datetime

from .downloader import download_file
from .overrides_parser import parse_overrides

"""
    Ключ: ID группы

    Значение: Изменения
"""
cache = {}

#  Когда последний раз получали изменения
last_time_retrieved = None

def download_overrides(group_id: str):
    global last_time_retrieved, cache

    now = datetime.now()

    #  Если изменения не были полученны...
    if (last_time_retrieved is None)\
        or (
            #  или они были полученны сегодня, 
            last_time_retrieved.day == now.day \
            #  но сейчас >=15 часов, поэтому новые изменения были выставленны
            and now.hour >= 15\
            #  и мы их ещё не видели...
            and last_time_retrieved.hour < 15\
        ) or (
        #  или изменения были полученны вчера или ранее
        last_time_retrieved.day != now.day):
            #  ...то нам надо получить изменения
            filename = download_file("https://ttgt.org/images/pdf/zamena.pdf")
            cache = parse_overrides()
            os.system(f"rm {filename}")
            last_time_retrieved = now

    #  Берём первое попавшееся изменение,
    #  чтобы получить номер и день недели
    c = cache[list(cache.keys())[0]]

    return cache.get(group_id) or dict(
        overrides=[],
        weekDay=c["weekDay"],
        weekNum = c["weekNum"]
    )

