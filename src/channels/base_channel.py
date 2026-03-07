
from abc import ABC, abstractmethod
from src.channels.message_types import (OutboundMessage, 
                                        SendResult)


class BaseChannel(ABC):

    @abstractmethod
    def send(self, message:OutboundMessage) -> SendResult:
        raise NotImplementedError("")
