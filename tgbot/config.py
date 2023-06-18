from dataclasses import dataclass
from typing import Optional

from environs import Env


@dataclass
class TgBot:
    token: str
    admin_ids: list[int]
    use_redis: bool


@dataclass
class RedisConfig:
    redis_pass: Optional[str]
    redis_port: Optional[int]
    redis_host: Optional[str]

    def dsn(self) -> str:
        if self.redis_pass:
            return f"redis://:{self.redis_pass}@{self.redis_host}:{self.redis_port}/0"
        else:
            return f"redis://{self.redis_host}:{self.redis_port}/0"


@dataclass
class Miscellaneous:
    openai_api_key: str


@dataclass
class Config:
    tg_bot: TgBot
    misc: Miscellaneous
    redis: RedisConfig = None


def load_config(path: str = None) -> Config:
    env = Env()
    env.read_env(path)

    return Config(
        tg_bot=TgBot(
            token=env.str("BOT_TOKEN"),
            admin_ids=list(map(int, env.list("ADMINS"))),
            use_redis=env.bool("USE_REDIS")
        ),

        # redis=RedisConfig(
        #     redis_pass=env.str("REDIS_PASSWORD"),
        #     redis_port=env.int("REDIS_PORT"),
        #     redis_host=env.str("REDIS_HOST"),
        # ),

        misc=Miscellaneous(
            openai_api_key=env.str("OPENAI_API_KEY"),
        )
    )
