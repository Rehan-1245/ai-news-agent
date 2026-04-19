import json
import os

FILE = "data/visited.json"

def load():
    if not os.path.exists(FILE):
        return set()
    return set(json.load(open(FILE)))

def save(data):
    json.dump(list(data), open(FILE, "w"))

def is_new(url, visited):
    return url not in visited