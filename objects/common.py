import json

__config = None

def config():
    """This function loads the parameters in ./objects/config.json."""
    global __config
    if not __config:
        with open('./objects/config.json') as f:
            __config = json.load(f)

    return __config
