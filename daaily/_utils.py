"""To be populated"""


def refresh_decorator(func):
    def wrap(*args, **kwargs):
        print(func.__name__)
        print("the wrap is running")
        return wrap
