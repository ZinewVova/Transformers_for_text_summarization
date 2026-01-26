import aiohttp
import logging
from typing import Optional

logger = logging.getLogger(__name__)


class FastAPIClient:
    def __init__(self, base_url: str, timeout: int = 60):
        self.base_url = base_url.rstrip('/')
        self.timeout = aiohttp.ClientTimeout(total=timeout)

    async def summarize_text(
        self,
        text: str,
        model_name: Optional[str] = None,
        max_source_tokens: Optional[int] = None
    ) -> dict:
        url = f"{self.base_url}/api/v1/summarize"

        payload = {"text": text}
        if model_name:
            payload["model_name"] = model_name
        if max_source_tokens:
            payload["max_source_tokens"] = max_source_tokens

        try:
            async with aiohttp.ClientSession(timeout=self.timeout) as session:
                async with session.post(url, json=payload) as response:
                    if response.status == 200:
                        result = await response.json()
                        logger.info(f"Successfully summarized text using model: {result.get('model_used')}")
                        return result
                    else:
                        error_text = await response.text()
                        logger.error(f"API error {response.status}: {error_text}")
                        raise Exception(f"API returned status {response.status}: {error_text}")
        except aiohttp.ClientError as e:
            logger.error(f"Network error: {str(e)}")
            raise Exception(f"Failed to connect to summarization service: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error: {str(e)}")
            raise

    async def health_check(self) -> bool:
        url = f"{self.base_url}/health"

        try:
            async with aiohttp.ClientSession(timeout=self.timeout) as session:
                async with session.get(url) as response:
                    if response.status == 200:
                        result = await response.json()
                        return result.get("status") == "healthy"
                    return False
        except Exception as e:
            logger.error(f"Health check failed: {str(e)}")
            return False
