import torch
import asyncio
from transformers import AutoTokenizer, T5ForConditionalGeneration
from starlette.concurrency import run_in_threadpool

from model_utils import model_cache
from config import settings


class PredictionService:
    def __init__(self):
        self.device = settings.DEVICE or ("cuda" if torch.cuda.is_available() else "cpu")
        self.semaphore = asyncio.Semaphore(1)

    def _predict_one(
        self,
        text: str,
        model_name: str,
        max_source_tokens: int = 600
    ) -> str:
        model, tokenizer, device = model_cache.get(model_name, self.device)

        input_ids = tokenizer(
            text,
            add_special_tokens=True,
            max_length=max_source_tokens,
            padding="max_length",
            truncation=True,
            return_tensors="pt"
        )["input_ids"].to(device)

        with torch.no_grad():
            output_ids = model.generate(
                input_ids=input_ids,
                max_new_tokens=settings.MAX_NEW_TOKENS,
                min_length=settings.MIN_LENGTH,
                no_repeat_ngram_size=settings.NO_REPEAT_NGRAM_SIZE,
                early_stopping=settings.EARLY_STOPPING,
                num_beams=settings.NUM_BEAMS,
                length_penalty=settings.LENGTH_PENALTY
            )

        summary = tokenizer.decode(output_ids[0], skip_special_tokens=True)
        return summary

    async def predict_single(
        self,
        text: str,
        model_name: str,
        max_source_tokens: int = 600
    ) -> str:
        async with self.semaphore:
            return await run_in_threadpool(
                self._predict_one,
                text,
                model_name,
                max_source_tokens
            )
