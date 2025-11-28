import json
import random
def message(path):
    try:
        with open(path) as f:
                    messages = json.load(f)
                    msg = random.choice(messages)
                    return msg
    except:
        return "error :(("