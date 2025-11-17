from src.native import parse_schedule
import os
import json

cache = {}
items = {}

if os.path.isfile("schedule.zip"):
    parse_schedule()

if os.path.isfile("schedule.json"):
    cache = json.load(open("schedule.json"))

if os.path.isfile("items.json"):
    items = json.load(open("items.json"))
