import os
from dataclasses import dataclass
from dotenv import load_dotenv

load_dotenv()


@dataclass(frozen=True)
class Settings:
    api_key: str
    api_secret: str
    base_url: str
    testnet: bool = True

    @property
    def is_configured(self) -> bool:
        return bool(self.api_key and self.api_secret)


def get_settings() -> Settings:
    return Settings(
        api_key=os.getenv("API_KEY", "").strip(),
        api_secret=os.getenv("API_SECRET", "").strip(),
        base_url=os.getenv("BASE_URL", "https://testnet.binancefuture.com").strip(),
    )


SUPPORTED_SYMBOLS = ["BTCUSDT", "ETHUSDT", "BNBUSDT", "SOLUSDT", "XRPUSDT"]
SUPPORTED_SIDES = ["BUY", "SELL"]
SUPPORTED_TYPES = ["MARKET", "LIMIT", "STOP"]
