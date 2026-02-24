import math
from dataclasses import dataclass


@dataclass
class Netzeinspeisung:
    unq: float
    ik__q: float
    c: float = 1.1
    tr: float = 1.0

    @classmethod
    def kurzschlussmitimpedanz(cls, unq: float, ik__q: float, c: float, tr: float):
        zq = c * unq / math.sqrt(3) * ik__q * tr ** 2
        return zq


def testrechnungen() -> None:
    pass
    # print("Kurzschlussmitimpedanz" = Netzeinspeisung.kurzschlussmitimpedanz(unq: float, ik__q: float))


if __name__ == "__main__":
    testrechnungen()
