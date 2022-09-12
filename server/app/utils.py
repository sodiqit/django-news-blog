def omit(keys: list[str], data: dict) -> dict:
    cloned = data.copy()

    for key in data.keys():
        if key in keys:
            cloned.pop(key, None)

    return cloned