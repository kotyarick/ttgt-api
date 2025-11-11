import os.path

import requests

dir = "/tmp/kotyarick/schedule-parser/"


#  Скачивает файл в оперативку
#  по заданному URL.
#  Возвращает полный путь к файлу
def download_file(url):
    if not os.path.isdir(dir):
        os.makedirs(dir)
    local_filename = dir + url.split('/')[-1]

    #  Если файл уже скачан, используем его
    if os.path.isfile(local_filename):
        return local_filename

    #  Скачиваем файл по 8192 байта (128 килобайт)
    with requests.get(url, stream=True) as r:
        r.raise_for_status()
        with open(local_filename, 'wb') as f:
            for chunk in r.iter_content(chunk_size=8192):
                f.write(chunk)

    return local_filename
