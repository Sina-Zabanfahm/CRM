
from enum import Enum

class StatusType(Enum, str):
    WAITING = "WAITING"
    EXPIRED = "EXPIRED"
    FINISHED = "FINISHED"