import os
import json

def load_json(file_path):
    with open(file_path) as j:
        d = json.load(j)
        j.close()
        return d
