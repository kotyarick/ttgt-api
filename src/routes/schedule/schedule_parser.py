from src.native import parse_schedule
import os
import json

cache = {}
items = {}

if os.isfile("schedule.zip"):
    parse_schedule()

if os.isfile("schedule.json"):
    cache = json.load(open("schedule.json"))

if os.isfile("items.json"):
    items = json.load(open("items.json"))
