import hashlib
import hmac
from src.core.settings import TELEGRAM_BOT_TOKEN


def check_hash(data: dict) -> bool:
    token_hash = hashlib.sha256(TELEGRAM_BOT_TOKEN.encode()).digest()
    check_string = "\n".join(f"{key}={data[key]}" for key in sorted(data.keys()) if key != "hash")
    secret_key = hashlib.sha256(TELEGRAM_BOT_TOKEN.encode()).digest()
    hmac_result = hmac.new(secret_key, check_string.encode(), hashlib.sha256).hexdigest()
    return hmac_result == data["hash"]
