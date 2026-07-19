from telethon import TelegramClient
from telethon.tl.functions.messages import RequestWebViewRequest
from telethon.tl.functions.channels import JoinChannelRequest
from loguru import logger
class GetDisposableUrlWithTelegram:
    def __init__(self, api_id, api_hash, session_name):
        self.api_id = api_id
        self.api_hash = api_hash
        self.session_name = session_name
        self.client = TelegramClient(self.session_name, self.api_id, self.api_hash)
        self.is_connected = False


    async def connect_and_auth(self):
        try:
            await self.client.connect()
            if not await self.client.is_user_authorized():
                logger.critical(f"[{self.session_name}] Сессия невалидна или аккаунт разлогинен.")
                return False
            self.is_connected = True
            logger.success(f"[{self.session_name}] успешно запущен!")
            return True
        except Exception as e:
            logger.error(f"[{self.session_name}] Ошибка при запуске клиента: {e}")
            return False

    async def disconnect(self) -> None:
        if self.is_connected:
            await self.client.disconnect()
            self.is_connected = False
            logger.success(f"[{self.session_name} успешно отсоединился!]")
        else:
            logger.debug(f"[{self.session_name}] уже был(а) отсоединин(а)")


    async def get_disposable_url_with_telegram(self, gift_link):
        if self.is_connected:
            result = await self.client(RequestWebViewRequest(
                peer="randombeast_bot",
                bot="randombeast_bot",
                platform="tdesktop",
                url=f"{gift_link}",
                from_bot_menu=False,
                compact=False,
                fullscreen=True
            ))
            logger.success(f"[{self.session_name}] заполучил однорозовую ссылку {result.url}")
            return result.url
        else:
            logger.debug(f"[{self.session_name}] не был(а) соединён(а)")
            return False
