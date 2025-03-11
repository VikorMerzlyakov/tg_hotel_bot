import os
from dotenv import  load_dotenv
from pydantic import SecretStr, StrictStr,  BaseSettings

load_dotenv()


class SiteSetting(BaseSettings):
    api_key: SecretStr = os.getenv("SITE_API", None)
    host_api: StrictStr = os.getenv("HOST_API", None)