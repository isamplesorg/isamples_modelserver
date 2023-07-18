from enum import Enum


class _NoValue(Enum):
    """Enum subclass indicating the value is unimportant (https://docs.python.org/3/library/enum.html)"""

    def __repr__(self):
        return "<%s.%s>" % (self.__class__.__name__, self.name)


class ISBModelType(_NoValue):
    """The conceptual type of data in the ML model"""

    MATERIAL = "material"
    SAMPLE = "sample"
    CONTEXT = "context"