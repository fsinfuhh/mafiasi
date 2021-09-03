import json
import re


def parse(string):
    # To make the data json, the headers have to be quoted and the angle brackets have to be removed
    # i.e. {key, <<"value">>} to {"key": "value"}
    quoted_headers = re.sub(r"\{(\w+),", r'{"\1":', string)
    no_angle_brackets = re.sub(r'<<("[^"]+")>>', r'\1', quoted_headers)
    data = json.loads(no_angle_brackets)
    # Now, the data is available in Python, but it is a list of one-element dictionaries
    # These dictionaries are merged here.
    result = dict()
    for item in data:
        result.update(item)
    return result


def dump(object):
    # First, the merged dictionary has to be split in a list of one-element dictionaries
    data = [{k: v} for k, v in object.items()]
    # Then, the data is stringified and the transformations from before (header quotes, angle brackets) are reverted
    string = json.dumps(data)
    no_quoted_headers = re.sub(r'\{"(\w+)":', r'{\1,', string)
    angle_brackets = re.sub(r'("[^"]+")', r'<<\1>>', no_quoted_headers)
    return angle_brackets
