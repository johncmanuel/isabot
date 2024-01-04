def safe_nested_get(dct: dict, *keys):
    """https://stackoverflow.com/a/25833661"""
    for key in keys:
        try:
            dct = dct[key]
        except KeyError:
            return None
        except Exception:
            return None
    return dct
