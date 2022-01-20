import os
from math import sqrt

from scipy import stats


def parametrized(dec):
    """
    https://stackoverflow.com/a/26151604/12938797
    """

    def layer(*args, **kwargs):
        def repl(f):
            return dec(f, *args, **kwargs)

        return repl

    return layer


@parametrized
def require_service(fn, service):
    def wrapper(*args, **kwargs):
        if service not in os.environ["SERVICES"]:
            raise Exception(f"{service} not supported on this server.")
        return fn(*args, **kwargs)

    return wrapper


def ci_lower_bound(pos, n, confidence):
    """
    https://www.evanmiller.org/how-not-to-sort-by-average-rating.html
    https://stackoverflow.com/a/45965534
    """
    
    if n == 0:
        return 0
    z = stats.norm.ppf(1 - (1 - confidence) / 2)
    phat = 1.0 * pos / n
    return (
        phat + z * z / (2 * n) - z * sqrt((phat * (1 - phat) + z * z / (4 * n)) / n)
    ) / (1 + z * z / n)
