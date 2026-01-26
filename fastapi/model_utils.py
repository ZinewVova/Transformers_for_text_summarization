import torch
from transformers import AutoTokenizer, T5ForConditionalGeneration
from typing import Tuple, Optional


def get_device(preferred_device: Optional[str] = None) -> str:
    if preferred_device:
        return preferred_device
    return "cuda" if torch.cuda.is_available() else "cpu"


def load_model_and_tokenizer(
    model_name: str,
    device: Optional[str] = None
) -> Tuple[T5ForConditionalGeneration, AutoTokenizer, str]:
    device = get_device(device)
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = T5ForConditionalGeneration.from_pretrained(model_name).to(device)
    return model, tokenizer, device


class ModelCache:
    def __init__(self):
        self._cache = {}

    def get(self, model_name: str, device: Optional[str] = None):
        cache_key = f"{model_name}_{device}"
        if cache_key not in self._cache:
            self._cache[cache_key] = load_model_and_tokenizer(model_name, device)
        return self._cache[cache_key]

    def clear(self):
        self._cache.clear()


model_cache = ModelCache()
