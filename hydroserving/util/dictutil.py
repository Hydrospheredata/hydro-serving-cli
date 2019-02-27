def remove_none(obj):
    if isinstance(obj, (list, tuple, set)):
        return type(obj)(remove_none(x) for x in obj if x is not None)
    elif isinstance(obj, dict):
        return dict((remove_none(k), remove_none(v))
                    for k, v in obj.items() if k is not None and v is not None)
    elif hasattr(obj, '__dict__'):
        return remove_none(obj.__dict__)
    return obj


def extract_dict(obj):
    if isinstance(obj, (list, tuple, set)):
        return type(obj)(extract_dict(x) for x in obj if x is not None)
    elif isinstance(obj, dict):
        return dict((extract_dict(k), extract_dict(v))
                    for k, v in obj.items())
    elif hasattr(obj, '__dict__'):
        return extract_dict(obj.__dict__)
    return obj
