import time as time_


def millis():
    return int(round(time_.time() * 1000))


def match_one(query: str, terms: [str]) -> bool:
    for s in terms:
        if query == s:
            return True
    return False


def match(queries: [str], terms: [str]) -> bool:
    for s in terms:
        if s in queries:
            return True
    return False
