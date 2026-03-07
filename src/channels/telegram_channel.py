
import os
import requests

from src.environment_variables.constants import TELEGRAM_API_KEY

from src.channels.provider_types import ProviderTypes
from src.channels.base_channel import BaseChannel
from src.channels.message_types import (OutboundMessage, 
                                        SendResult)

END_POINT = "https://api.telegram.org/bot{api_key}/sendMessage"

class TelegramChannel(BaseChannel):
    def __init__(self, bot_token: str | None = None):
        if bot_token is None:
            bot_token = os.environ[TELEGRAM_API_KEY]
        
        self.bot_token = bot_token
        self.end_point = END_POINT.format(api_key = bot_token)

    def send(self, message: OutboundMessage) -> SendResult:
        
        payload = {
            "chat_id": message.recipient,
            "text": message.text
        }

        response = requests.post(self.end_point, json=payload)
        response.raise_for_status()

        return SendResult(
            provider=ProviderTypes.TELEGRAM.value,
            recipient=message.recipient,
            raw_response=response.json()
        )