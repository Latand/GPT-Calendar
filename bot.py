import asyncio
import json
import logging

import betterlogging as bl
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.fsm.storage.redis import RedisStorage, DefaultKeyBuilder
from gcsa.google_calendar import GoogleCalendar

from infrastructure.openai_api.api import OpenAIAPIClient
from tgbot.config import load_config
from tgbot.handlers import routers_list
from tgbot.middlewares.config import ConfigMiddleware
from tgbot.services import broadcaster

logger = logging.getLogger(__name__)
log_level = logging.INFO
bl.basic_colorized_config(level=log_level)


async def on_startup(bot: Bot, admin_ids: list[int]):
    await broadcaster.broadcast(bot, admin_ids, "Бот був запущений")


def register_global_middlewares(dp: Dispatcher, config, session_pool=None):
    dp.message.outer_middleware(ConfigMiddleware(config))
    dp.callback_query.outer_middleware(ConfigMiddleware(config))


async def main():
    logger.info("Starting bot")
    config = load_config(".env")
    if config.tg_bot.use_redis:
        storage = RedisStorage.from_url(
            config.redis.dsn(),
            key_builder=DefaultKeyBuilder(with_bot_id=True, with_destiny=True),
        )
    else:
        storage = MemoryStorage()
    bot = Bot(token=config.tg_bot.token, parse_mode="HTML")
    dp = Dispatcher(storage=storage)

    openai = OpenAIAPIClient(config.misc.openai_api_key)
    calendar_service = GoogleCalendar(
        credentials_path="./infrastructure/function_services/creds/config.json",
        token_path="./infrastructure/function_services/creds/token.pickle",
    )

    with open("./infrastructure/function_services/definitions.json", "r") as f:
        function_definitions = json.load(f)

    dp.include_routers(*routers_list)

    register_global_middlewares(
        dp,
        config,
    )
    dp.workflow_data.update(
        openai=openai,
        calendar_service=calendar_service,
        function_definitions=function_definitions,
    )

    await on_startup(bot, config.tg_bot.admin_ids)
    await dp.start_polling(bot)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.error("Бот був вимкнений!")
