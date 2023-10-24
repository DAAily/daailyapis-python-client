import datetime


class NewDatetime(datetime.datetime):
    """
    In order to mock datetime.datetime.utcnow()
    Inspiration was taken from this thread: https://stackoverflow.com/a/4482067/14527713
    """

    @classmethod
    def utcnow(cls):
        return cls(2010, 1, 1)


datetime.datetime = NewDatetime
