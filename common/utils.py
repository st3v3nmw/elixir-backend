import os


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
