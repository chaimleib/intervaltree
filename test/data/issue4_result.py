"""
Result tree data from test/issue4.py.
"""
from os import path
import json

memo = None
def load():
    global memo
    if memo is not None:
        return memo
    dir = path.dirname(__file__)
    fpath = path.join(dir, 'issue4_result.json')
    with open(fpath, 'r') as f:
        memo = json.load(f)
        return memo
