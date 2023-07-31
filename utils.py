import re


def get_json_skeleton(data, root=True):
    if type(data) == dict:
        return {k: get_json_skeleton(v) for k, v in data.items()}
    if type(data) != list:
        return type(data).__name__
    if any(type(item) != type(data[0]) for item in data):
        raise ValueError("List items must be of the same type")

    skeleton = {}
    if type(data[0]) == dict:
        common_keys = set.intersection(
            *[set(k for k in item if not re.match(r"\[.*\]", k)) for item in data]
        )
        optional_keys = set.union(*[set(item.keys()) for item in data]) - common_keys
        if root:
            skeleton["len"] = len(data)
        skeleton["items"] = {}
        skeleton["items"].update(
            {
                k: get_json_skeleton([item[k] for item in data], root=False)
                for k in common_keys
            }
        )
        skeleton["items"].update(
            {
                re.sub(r"\[?([^\[\]]+)\]?", "[\1]", k): get_json_skeleton(
                    [item[k] for item in data], root=False
                )
                for k in optional_keys
            }
        )
        return skeleton
    if type(data[0]) == list:
        lengths = [len(item) for item in data]
        if root:
            skeleton["len"] = len(data)
        skeleton["range"] = (min(lengths), max(lengths))
        skeleton["items"] = get_json_skeleton(
            [x for item in data for x in item], root=False
        )
        return skeleton

    if not root:
        return type(data[0]).__name__
    skeleton["len"] = len(data)
    skeleton["items"] = type(data[0]).__name__
    return skeleton
