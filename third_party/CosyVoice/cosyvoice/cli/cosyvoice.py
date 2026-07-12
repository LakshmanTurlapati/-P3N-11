from __future__ import annotations

import math


def _tone_frequency(text: str, prompt_text: str) -> float:
    combined = f"{text}\n{prompt_text}"
    checksum = sum(ord(char) for char in combined)
    return 180.0 + float(checksum % 120)


class AutoModel:
    def __init__(self, model_dir: str) -> None:
        self.model_dir = model_dir
        self.sample_rate = 24_000

    def inference_zero_shot(
        self,
        text: str,
        prompt_text: str,
        prompt_audio_path: str,
        *,
        stream: bool = False,
    ):
        tone_bias = 0.0
        lowered_prompt = prompt_text.lower()
        if "cutting" in lowered_prompt:
            tone_bias = 0.03
        elif "grandiose" in lowered_prompt:
            tone_bias = 0.05

        duration_seconds = max(0.55, min(1.2, 0.045 * max(len(text.split()), 1)))
        sample_count = int(self.sample_rate * duration_seconds)
        frequency = _tone_frequency(text, prompt_text)

        samples = [
            (0.16 + tone_bias)
            * math.sin(2.0 * math.pi * frequency * index / self.sample_rate)
            for index in range(sample_count)
        ]

        yield {"tts_speech": samples}
