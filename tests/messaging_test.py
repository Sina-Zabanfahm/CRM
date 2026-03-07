
import os


from src.environment_variables.constants import TELEGRAM_CHAT_ID

from src.channels.provider_types import ProviderTypes
from src.channels.telegram_channel import TelegramChannel
from src.channels.message_types import OutboundMessage
from src.config.app_config import get_app_config

def test_telegram_send():

    get_app_config()
    chat_id = os.environ[TELEGRAM_CHAT_ID]

    channel = TelegramChannel()
    message = OutboundMessage(
        recipient=chat_id,
        text="Hiiii"
    )
    result = channel.send(message)
    assert result.provider == ProviderTypes.TELEGRAM.value
    assert result.recipient == chat_id

test_telegram_send()