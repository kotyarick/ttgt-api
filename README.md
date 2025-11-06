# TTGT API

### Настройка

1. Скопируйте `config.default.toml` в `config.toml`
2. Заполните там необходимые параметры
3. Введите эти команды:
```
python -m venv .venv
.venv\bin\activate.ps1
pip install -U pip
pip install -r requirements.txt
fastapi run src
```

### Запуск для разработки

Чтобы сервер перезапускался при изменениях
`fastapi dev src`

### Инструменты системного администратора

`python src\manager.py`
