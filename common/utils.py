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
def require_server(fn, site_type):
    def wrapper(*args, **kwargs):
        if os.environ["SITE_TYPE"] != site_type:
            raise Exception(
                f"This service is not supported on this site ({os.environ['SITE_TYPE']})."
            )
        return fn(*args, **kwargs)

    return wrapper
