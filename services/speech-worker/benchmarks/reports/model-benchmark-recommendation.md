# Model Benchmark Recommendation

## Executive Recommendation
| Workflow | Recommendation |
| --- | --- |
| Studio default | cosyvoice |
| Live conversation | silero-vad |
| Default switch | keep-current-defaults |

Keep cosyvoice as the studio default until an alternate clears the hard gates and provides stronger benchmark evidence. Keep silero-vad as the live conversation default until an alternate clears the hard gates and provides stronger benchmark evidence. End-to-end S2S candidates remain findings-first only. Blocked scan evidence: Moshi: No sanctioned GPU-host execution or package verification has been captured in this workspace.; MiniCPM-o 4.5: The candidate remains findings-only until a capable GPU host produces benchmark evidence.; FlashLabs Chroma: Chroma is too heavy for this workspace and needs a different GPU host before it can be ranked.; Qwen3-Omni: The phase should not absorb a Qwen3-Omni run until larger GPU-host evidence exists.. Phase 6 GPU-host validation is required before any S2S migration is reconsidered.

## Gate Matrix
| Candidate | Provider | Status | License | Safety | Integration |
| --- | --- | --- | --- | --- | --- |
| silero-vad | silero-vad | passed | pass | pass | pass |
| fireredvad | fireredvad | blocked | blocked | pass | blocked |
| silero-vad | silero-vad | passed | pass | pass | pass |
| fireredvad | fireredvad | blocked | blocked | pass | blocked |
| silero-vad | silero-vad | passed | pass | pass | pass |
| fireredvad | fireredvad | blocked | blocked | pass | blocked |
| silero-vad | silero-vad | passed | pass | pass | pass |
| fireredvad | fireredvad | blocked | blocked | pass | blocked |
| cosyvoice | cosyvoice | passed | pass | pass | pass |
| qwen3-tts-12hz-0.6b-customvoice | qwen3-tts | blocked | pass | pass | blocked |
| cosyvoice | cosyvoice | passed | pass | pass | pass |
| qwen3-tts-12hz-0.6b-customvoice | qwen3-tts | blocked | pass | pass | blocked |
| cosyvoice | cosyvoice | passed | pass | pass | pass |
| qwen3-tts-12hz-0.6b-customvoice | qwen3-tts | blocked | pass | pass | blocked |
| moshi | Moshi | blocked | pass | pass | blocked |
| minicpm-o-4.5 | MiniCPM-o 4.5 | blocked | pass | pass | blocked |
| chroma | FlashLabs Chroma | blocked | pass | pass | blocked |
| qwen3-omni | Qwen3-Omni | blocked | pass | pass | blocked |

## VAD Comparison
| Candidate | Provider | Corpus Item | Status | Quality | Total Wall | Runtime Cost | License Fit | Integration Risk |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| silero-vad | silero-vad | audio-clean-short-01 | passed | 2.60 | 22 | cpu fixture path, low memory | pass | low |
| fireredvad | fireredvad | audio-clean-short-01 | blocked | 1.00 | 0 | blocked before runtime | blocked | high |
| silero-vad | silero-vad | audio-clean-long-01 | passed | 2.60 | 28 | cpu fixture path, low memory | pass | low |
| fireredvad | fireredvad | audio-clean-long-01 | blocked | 1.00 | 0 | blocked before runtime | blocked | high |
| silero-vad | silero-vad | audio-noisy-short-01 | passed | 2.60 | 23 | cpu fixture path, low memory | pass | low |
| fireredvad | fireredvad | audio-noisy-short-01 | blocked | 1.00 | 0 | blocked before runtime | blocked | high |
| silero-vad | silero-vad | audio-noisy-expected-failure-01 | passed | 1.80 | 34 | cpu fixture path, low memory | pass | low |
| fireredvad | fireredvad | audio-noisy-expected-failure-01 | blocked | 1.00 | 0 | blocked before runtime | blocked | high |

## TTS And Voice-Cloning Comparison
| Candidate | Provider | Corpus Item | Status | Quality | Total Wall | Runtime Cost | License Fit | Integration Risk |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| cosyvoice | cosyvoice | text-measured-01 | passed | 5.00 | 145 | single GPU class, moderate memory footprint | pass | low |
| qwen3-tts-12hz-0.6b-customvoice | qwen3-tts | text-measured-01 | blocked | 1.00 | 0 | blocked before runtime | pass | high |
| cosyvoice | cosyvoice | text-cutting-01 | passed | 5.00 | 145 | single GPU class, moderate memory footprint | pass | low |
| qwen3-tts-12hz-0.6b-customvoice | qwen3-tts | text-cutting-01 | blocked | 1.00 | 0 | blocked before runtime | pass | high |
| cosyvoice | cosyvoice | text-grandiose-01 | passed | 5.00 | 145 | single GPU class, moderate memory footprint | pass | low |
| qwen3-tts-12hz-0.6b-customvoice | qwen3-tts | text-grandiose-01 | blocked | 1.00 | 0 | blocked before runtime | pass | high |

## End-to-End Speech Findings
| Candidate | Status | License Summary | Hardware / Runtime | Streaming / Latency | Voice Control Fit | Integration Risk | Attempted Setup Evidence | Blocker | Next Action |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Moshi | blocked | Repo docs indicate a promising open stack, but the model/runtime path has not been validated in the local benchmark workspace. | Capable GPU host with streaming/full-duplex speech runtime and low-latency transport. | Best first scan target because the docs describe clear streaming/full-duplex behavior. | Strong conversational fit if external execution proves stable and interruptible. | medium | Research notes cite clear streaming/full-duplex docs, but \`.venv\` lacks torch, ffmpeg, and GPU access. | No sanctioned GPU-host execution or package verification has been captured in this workspace. | Run a sanctioned GPU-host scan and attach the external evidence reference before ranking Moshi. |
| MiniCPM-o 4.5 | blocked | Repo docs and model notes are available, but no external GPU-host benchmark evidence has been captured. | GPU host with a bounded runtime envelope for full-duplex multimodal speech. | Clear streaming/full-duplex documentation, but the local workspace cannot validate it. | Good candidate for live turn-taking if the external host keeps latency bounded. | medium | Research notes describe clear streaming/full-duplex docs and a bounded runtime story, but no GPU-host run is captured. | The candidate remains findings-only until a capable GPU host produces benchmark evidence. | Capture an external evidence reference from a capable GPU host or keep MiniCPM-o blocked. |
| FlashLabs Chroma | blocked | The repo is visible, but the heavier runtime and CUDA dependency story makes it a late-scan candidate. | CUDA 12.6 GPU host with a heavier inference envelope than the baseline slice. | Interesting speech-to-speech profile, but too much runtime friction for the local benchmark host. | Moderate conversational fit once the CUDA 12.6 runtime can be exercised on the correct worker. | high | Phase research flags CUDA 12.6 and the local workspace lacks GPU access for a real run. | Chroma is too heavy for this workspace and needs a different GPU host before it can be ranked. | Defer until a CUDA 12.6 worker is available and the benchmark slice can absorb the run. |
| Qwen3-Omni | blocked | Official repo/docs are available, but the 30B-A3B-class stack needs a much larger runtime envelope. | Large GPU host with substantial memory headroom and streaming support. | Open streaming issues keep it as a late-scan candidate rather than a local benchmark target. | Potentially strong multimodal fit, but still unproven in this benchmark slice. | high | Research notes call out the 30B-A3B class and open streaming issues; the local host has no GPU runtime. | The phase should not absorb a Qwen3-Omni run until larger GPU-host evidence exists. | Revisit only after smaller S2S candidates or a Phase 6 GPU host make the runtime plausible. |

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
| moshi | 3 | 3 | 3 | 3 | 4 |
| minicpm-o-4.5 | 3 | 3 | 3 | 2 | 4 |
| chroma | 2 | 2 | 2 | 2 | 4 |
| qwen3-omni | 2 | 2 | 2 | 1 | 4 |

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
| moshi | 0 | 0 | 0 | 0 | 0 | 0 | gpu host, bounded streaming runtime |
| minicpm-o-4.5 | 0 | 0 | 0 | 0 | 0 | 0 | gpu host, moderate memory footprint |
| chroma | 0 | 0 | 0 | 0 | 0 | 0 | cuda 12.6 GPU host, heavier memory footprint |
| qwen3-omni | 0 | 0 | 0 | 0 | 0 | 0 | 30B-A3B-class GPU host, high memory footprint |

## Blocked Candidates
| Candidate | Provider | Blocker | Attempted Setup | Next Action |
| --- | --- | --- | --- | --- |
| fireredvad | vad | FireRedVAD is blocked until package legitimacy/download evidence and GPU-worker runtime compatibility are verified in the local workspace. | https://github.com/FireRedTeam/FireRedVAD | Approve a verified FireRedVAD source/package, validate it on the GPU worker, then rerun the benchmark before ranking it. |
| fireredvad | vad | FireRedVAD is blocked until package legitimacy/download evidence and GPU-worker runtime compatibility are verified in the local workspace. | https://github.com/FireRedTeam/FireRedVAD | Approve a verified FireRedVAD source/package, validate it on the GPU worker, then rerun the benchmark before ranking it. |
| fireredvad | vad | FireRedVAD is blocked until package legitimacy/download evidence and GPU-worker runtime compatibility are verified in the local workspace. | https://github.com/FireRedTeam/FireRedVAD | Approve a verified FireRedVAD source/package, validate it on the GPU worker, then rerun the benchmark before ranking it. |
| fireredvad | vad | FireRedVAD is blocked until package legitimacy/download evidence and GPU-worker runtime compatibility are verified in the local workspace. | https://github.com/FireRedTeam/FireRedVAD | Approve a verified FireRedVAD source/package, validate it on the GPU worker, then rerun the benchmark before ranking it. |
| qwen3-tts-12hz-0.6b-customvoice | tts | Qwen3-TTS is approved on source/license grounds but remains blocked until GPU-worker runtime evidence is captured. | https://github.com/QwenLM/Qwen3-TTS \| https://huggingface.co/Qwen/Qwen3-TTS-12Hz-0.6B-CustomVoice | Run the approved Qwen3-TTS source checkout with the Hugging Face weights on the GPU worker, capture timings and quality scores, and then rerun the benchmark. |
| qwen3-tts-12hz-0.6b-customvoice | tts | Qwen3-TTS is approved on source/license grounds but remains blocked until GPU-worker runtime evidence is captured. | https://github.com/QwenLM/Qwen3-TTS \| https://huggingface.co/Qwen/Qwen3-TTS-12Hz-0.6B-CustomVoice | Run the approved Qwen3-TTS source checkout with the Hugging Face weights on the GPU worker, capture timings and quality scores, and then rerun the benchmark. |
| qwen3-tts-12hz-0.6b-customvoice | tts | Qwen3-TTS is approved on source/license grounds but remains blocked until GPU-worker runtime evidence is captured. | https://github.com/QwenLM/Qwen3-TTS \| https://huggingface.co/Qwen/Qwen3-TTS-12Hz-0.6B-CustomVoice | Run the approved Qwen3-TTS source checkout with the Hugging Face weights on the GPU worker, capture timings and quality scores, and then rerun the benchmark. |
| moshi | s2s | No sanctioned GPU-host execution or package verification has been captured in this workspace. | Research notes cite clear streaming/full-duplex docs, but \`.venv\` lacks torch, ffmpeg, and GPU access. | Run a sanctioned GPU-host scan and attach the external evidence reference before ranking Moshi. |
| minicpm-o-4.5 | s2s | The candidate remains findings-only until a capable GPU host produces benchmark evidence. | Research notes describe clear streaming/full-duplex docs and a bounded runtime story, but no GPU-host run is captured. | Capture an external evidence reference from a capable GPU host or keep MiniCPM-o blocked. |
| chroma | s2s | Chroma is too heavy for this workspace and needs a different GPU host before it can be ranked. | Phase research flags CUDA 12.6 and the local workspace lacks GPU access for a real run. | Defer until a CUDA 12.6 worker is available and the benchmark slice can absorb the run. |
| qwen3-omni | s2s | The phase should not absorb a Qwen3-Omni run until larger GPU-host evidence exists. | Research notes call out the 30B-A3B class and open streaming issues; the local host has no GPU runtime. | Revisit only after smaller S2S candidates or a Phase 6 GPU host make the runtime plausible. |

## Default Switch Decision
| Decision | Reason | Next Step |
| --- | --- | --- |
| keep-current-defaults | No alternate candidate cleared the hard gates and evidence thresholds; keep the current studio and live conversation defaults until Phase 6 GPU-host validation. | Phase 6 GPU-host validation or an approved external evidence run is required before any default switch is considered. |
