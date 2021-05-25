import json

__config = None

def config():
    global __config
    if not __config:
        with open('./objects/config.json') as f:
            __config = json.load(f)

    return __config