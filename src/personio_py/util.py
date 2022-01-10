import logging

logger = logging.getLogger('personio_py')
_unique_logs = set()


def log_once(level: int, message: str):
    if hash(message) not in _unique_logs:
        logger.log(level, message)
        _unique_logs.add(hash(message))


class ReadOnlyDict(dict):
    """
    A Python dictionary that only allows read access.

    Raises a RuntimeError whenever a modification is attempted.
    Weird that somethibng like this is not part of the standard library.
    Derived from this SO answer: https://stackoverflow.com/a/31049908
    """
    def __readonly__(self, *args, **kwargs):
        raise RuntimeError("Cannot modify ReadOnlyDict")
    __setitem__ = __readonly__
    __delitem__ = __readonly__
    pop = __readonly__
    popitem = __readonly__
    clear = __readonly__
    update = __readonly__
    setdefault = __readonly__
    del __readonly__
