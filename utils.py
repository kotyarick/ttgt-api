import random


def smart_crop(text: str, max_size: int) -> str:
    """
    Обрезает текст по предложениям.

    :param text: Текст, который нужно обрезать
    :param max_size: Максимальный размер результата. Строка на выходе может быть длиннее, если первое предложение длиннее, чем `max_size`
    :return: Обрезанный текст
    """

    split = text.split(". ")
    out = ""

    for index, sentence in enumerate(split):
        out += sentence + ". "

        size = len(out)
        if len(split) < index+1:
            size += len(split[index+1])

        if size >= max_size:
            break

    return out

def regenerate_secret():
    """ Пересоздаёт секрет и делает все токены не валидными """

    with open("secret", "wb") as secret:
        secret.write(random.randbytes(256))
