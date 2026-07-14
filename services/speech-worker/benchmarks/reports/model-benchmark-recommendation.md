# Model Benchmark Recommendation

## Gate Matrix
| Candidate | Provider | License | Safety | Integration |
| --- | --- | --- | --- | --- |
| silero-vad | silero-vad | pass | pass | pass |
| fireredvad | fireredvad | blocked | pass | blocked |
| silero-vad | silero-vad | pass | pass | pass |
| fireredvad | fireredvad | blocked | pass | blocked |
| silero-vad | silero-vad | pass | pass | pass |
| fireredvad | fireredvad | blocked | pass | blocked |
| silero-vad | silero-vad | pass | pass | pass |
| fireredvad | fireredvad | blocked | pass | blocked |
| cosyvoice | cosyvoice | pass | pass | pass |
| qwen3-tts-12hz-0.6b-customvoice | qwen3-tts | pass | pass | blocked |
| cosyvoice | cosyvoice | pass | pass | pass |
| qwen3-tts-12hz-0.6b-customvoice | qwen3-tts | pass | pass | blocked |
| cosyvoice | cosyvoice | pass | pass | pass |
| qwen3-tts-12hz-0.6b-customvoice | qwen3-tts | pass | pass | blocked |

## Quality Rubric
| Candidate | Intelligibility | Persona Tone Fit | Naturalness | Artifact Level | Safety Boundary |
| --- | --- | --- | --- | --- | --- |
| silero-vad | 2 | 2 | 2 | 2 | 5 |
| fireredvad | 1 | 1 | 1 | 1 | 1 |
| silero-vad | 2 | 2 | 2 | 2 | 5 |
| fireredvad | 1 | 1 | 1 | 1 | 1 |
| silero-vad | 2 | 2 | 2 | 2 | 5 |
| fireredvad | 1 | 1 | 1 | 1 | 1 |
| silero-vad | 1 | 1 | 1 | 1 | 5 |
| fireredvad | 1 | 1 | 1 | 1 | 1 |
| cosyvoice | 5 | 5 | 5 | 5 | 5 |
| qwen3-tts-12hz-0.6b-customvoice | 1 | 1 | 1 | 1 | 1 |
| cosyvoice | 5 | 5 | 5 | 5 | 5 |
| qwen3-tts-12hz-0.6b-customvoice | 1 | 1 | 1 | 1 | 1 |
| cosyvoice | 5 | 5 | 5 | 5 | 5 |
| qwen3-tts-12hz-0.6b-customvoice | 1 | 1 | 1 | 1 | 1 |

## Latency And Runtime
| Candidate | VAD | STT | Response Text | TTS | Playback Ready | Total Wall | Runtime Cost |
| --- | --- | --- | --- | --- | --- | --- | --- |
| silero-vad | 22 | 0 | 0 | 0 | 22 | 22 | cpu fixture path, low memory |
| fireredvad | 0 | 0 | 0 | 0 | 0 | 0 | blocked before runtime |
| silero-vad | 28 | 0 | 0 | 0 | 28 | 28 | cpu fixture path, low memory |
| fireredvad | 0 | 0 | 0 | 0 | 0 | 0 | blocked before runtime |
| silero-vad | 23 | 0 | 0 | 0 | 23 | 23 | cpu fixture path, low memory |
| fireredvad | 0 | 0 | 0 | 0 | 0 | 0 | blocked before runtime |
| silero-vad | 34 | 0 | 0 | 0 | 34 | 34 | cpu fixture path, low memory |
| fireredvad | 0 | 0 | 0 | 0 | 0 | 0 | blocked before runtime |
| cosyvoice | 0 | 0 | 0 | 140 | 145 | 145 | single GPU class, moderate memory footprint |
| qwen3-tts-12hz-0.6b-customvoice | 0 | 0 | 0 | 0 | 0 | 0 | blocked before runtime |
| cosyvoice | 0 | 0 | 0 | 140 | 145 | 145 | single GPU class, moderate memory footprint |
| qwen3-tts-12hz-0.6b-customvoice | 0 | 0 | 0 | 0 | 0 | 0 | blocked before runtime |
| cosyvoice | 0 | 0 | 0 | 140 | 145 | 145 | single GPU class, moderate memory footprint |
| qwen3-tts-12hz-0.6b-customvoice | 0 | 0 | 0 | 0 | 0 | 0 | blocked before runtime |

## Recommendation
| Workflow | Recommendation |
| --- | --- |
| Studio default | cosyvoice |
| Live conversation | silero-vad |

Studio generation follows the runnable CosyVoice baseline while live conversation follows the runnable Silero VAD baseline. FireRedVAD stays blocked until package legitimacy and GPU-worker validation are confirmed, and Qwen3-TTS stays blocked until the approved GPU-worker path is exercised.

## Blocked Candidates
| Candidate | Blocker | Next Action | Evidence |
| --- | --- | --- | --- |
| fireredvad | FireRedVAD is blocked until package legitimacy/download evidence and GPU-worker runtime compatibility are verified in the local workspace. | Approve a verified FireRedVAD source/package, validate it on the GPU worker, then rerun the benchmark before ranking it. | GPU-worker runtime validation remains pending. |
| fireredvad | FireRedVAD is blocked until package legitimacy/download evidence and GPU-worker runtime compatibility are verified in the local workspace. | Approve a verified FireRedVAD source/package, validate it on the GPU worker, then rerun the benchmark before ranking it. | GPU-worker runtime validation remains pending. |
| fireredvad | FireRedVAD is blocked until package legitimacy/download evidence and GPU-worker runtime compatibility are verified in the local workspace. | Approve a verified FireRedVAD source/package, validate it on the GPU worker, then rerun the benchmark before ranking it. | GPU-worker runtime validation remains pending. |
| fireredvad | FireRedVAD is blocked until package legitimacy/download evidence and GPU-worker runtime compatibility are verified in the local workspace. | Approve a verified FireRedVAD source/package, validate it on the GPU worker, then rerun the benchmark before ranking it. | GPU-worker runtime validation remains pending. |
| qwen3-tts-12hz-0.6b-customvoice | Qwen3-TTS is approved on source/license grounds but remains blocked until GPU-worker runtime evidence is captured. | Run the approved Qwen3-TTS source checkout with the Hugging Face weights on the GPU worker, capture timings and quality scores, and then rerun the benchmark. | GPU-worker validation remains pending for the approved path. |
| qwen3-tts-12hz-0.6b-customvoice | Qwen3-TTS is approved on source/license grounds but remains blocked until GPU-worker runtime evidence is captured. | Run the approved Qwen3-TTS source checkout with the Hugging Face weights on the GPU worker, capture timings and quality scores, and then rerun the benchmark. | GPU-worker validation remains pending for the approved path. |
| qwen3-tts-12hz-0.6b-customvoice | Qwen3-TTS is approved on source/license grounds but remains blocked until GPU-worker runtime evidence is captured. | Run the approved Qwen3-TTS source checkout with the Hugging Face weights on the GPU worker, capture timings and quality scores, and then rerun the benchmark. | GPU-worker validation remains pending for the approved path. |
