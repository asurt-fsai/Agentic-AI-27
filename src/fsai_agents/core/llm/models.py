# The one place that creates model clients. Nothing else should build one.
import os

from dotenv import load_dotenv
from langchain_ollama import ChatOllama
from langchain_openrouter import ChatOpenRouter
from openrouter.utils import BackoffStrategy, RetryConfig
from pydantic import SecretStr

load_dotenv()

API_TIMEOUT = float(os.getenv("MODEL_API_TIMEOUT", "60"))
LOCAL_TIMEOUT = float(os.getenv("MODEL_LOCAL_TIMEOUT", "120"))  

API_MODEL = os.getenv("MODEL_OPENROUTER_NAME", "nvidia/nemotron-3.5-lightning:free")
LOCAL_MODEL = os.getenv("MODEL_LOCAL_NAME", "qwen3.5:0.8b")
OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434")

ROUTES = ("api", "local", "openrouter")
class ChatOpenRouterNoRetry(ChatOpenRouter):
    """ChatOpenRouter where max_retries=0 really means no SDK retries."""

    def _build_client(self):
        client = super()._build_client()
        if self.max_retries == 0:
            client.sdk_configuration.retry_config = RetryConfig(
                strategy="backoff",
                backoff=BackoffStrategy(
                    initial_interval=1,
                    max_interval=1,
                    exponent=1.0,
                    max_elapsed_time=1,
                ),
                retry_connection_errors=False,
            )
        return client

def get_model(route: str = "api"):
    """Return a chat model for the given route: 'api' (main) or 'local' (backup)."""
    if route == "api":
        return ChatOpenRouter(
            model=API_MODEL,
            api_key=SecretStr(os.environ["OPENROUTER_API_KEY"]),
            timeout= max(1, int(API_TIMEOUT * 1000)),
            max_retries=0,  
        )
    if route == "local":
        return ChatOllama(
            model=LOCAL_MODEL,
            base_url=OLLAMA_URL,
            client_kwargs={"timeout": LOCAL_TIMEOUT},
        )
    if route == "openrouter":
        return ChatOpenRouterNoRetry(
            model=API_MODEL,
            api_key=SecretStr(os.environ["OPENROUTER_API_KEY"]),
            timeout= max(1, int(API_TIMEOUT * 1000)),
            max_retries=0,  
        )
    
    raise ValueError(f"unknown route: {route!r}, expected one of {ROUTES}")