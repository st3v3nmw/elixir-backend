import os
from math import sqrt


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
        if service not in os.environ["SERVER_SERVICES"].split(" "):
            raise Exception(f"{service} not supported on this server.")
        return fn(*args, **kwargs)

    return wrapper


def ci_lower_bound(n_positive, n):
    """
    https://www.evanmiller.org/how-not-to-sort-by-average-rating.html
    https://stackoverflow.com/a/10029645
    """

    if n == 0:
        return 0
    z = 1.96  # 95% confidence level
    phat = 1.0 * n_positive / n
    return (
        phat + z * z / (2 * n) - z * sqrt((phat * (1 - phat) + z * z / (4 * n)) / n)
    ) / (1 + z * z / n)
