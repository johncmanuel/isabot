def safe_nested_get(
    dct: dict,
    *keys,
    default=None,
):
    """https://stackoverflow.com/a/25833661"""
    for key in keys:
        try:
            dct = dct[key]
        except KeyError:
            return default
        except Exception:
            return default
    return dct
