"use client";

import {
  type ChangeEvent,
  type FormEvent,
  useEffect,
  useRef,
  useState,
} from "react";

import { voiceDisplaySeeds } from "@/lib/voice-registry";

type GenerationTonePreset = "measured" | "cutting" | "grandiose";
type GenerationJobStatus = "queued" | "running" | "succeeded" | "failed";
type GenerationPlaybackState = "empty" | GenerationJobStatus;

type GenerationTraceEntry = {
  stage: string;
  provider: string;
  detail: string;
};

type GenerationJobRecord = {
  provider_type: string | null;
  provider_name: string | null;
  job_id: string;
  retry_of_job_id: string | null;
  status: GenerationJobStatus;
  voice_id: string;
  text: string;
  tone_preset: GenerationTonePreset;
  rights_check: {
    status: string;
    approved_for_generation: boolean;
    message: string;
  };
  provider_trace: GenerationTraceEntry[];
  timing: {
    started_at: string;
    ended_at: string;
    duration_ms: number;
  };
  attempt: {
    status: GenerationJobStatus;
    provider_name: string | null;
    mime_type: string | null;
    error_message: string | null;
    audio_duration_ms: number | null;
    started_at: string;
    ended_at: string;
    duration_ms: number;
  };
  playback_url: string | null;
  audio_duration_ms: number | null;
};

type GenerationSubmission = {
  voiceId: string;
  text: string;
  tonePreset: GenerationTonePreset;
};

type GenerationRequestPayload = {
  voice_id: string;
  text: string;
  tone_preset: GenerationTonePreset;
};

type GenerationResponseError = {
  detail?: string;
};

type AudioTurnCaptureSource = "recording" | "upload";
type AudioTurnJobStatus = "queued" | "running" | "succeeded" | "failed";

type AudioTurnAttemptRecord = {
  status: AudioTurnJobStatus;
  provider_name: string | null;
  mime_type: string | null;
  error_message: string | null;
  transcript_text: string | null;
  vad_provider_name: string | null;
  vad_confidence: number | null;
  audio_duration_ms: number | null;
  started_at: string;
  ended_at: string;
  duration_ms: number;
};

type AudioTurnJobRecord = {
  provider_type: string | null;
  provider_name: string | null;
  job_id: string;
  status: AudioTurnJobStatus;
  capture_source: AudioTurnCaptureSource;
  audio_filename: string;
  audio_mime_type: string;
  playback_url: string | null;
  transcript_text: string | null;
  vad_provider_name: string | null;
  vad_confidence: number | null;
  audio_duration_ms: number | null;
  timing: {
    started_at: string;
    ended_at: string;
    duration_ms: number;
  };
  attempt: AudioTurnAttemptRecord;
};

const tonePresetOptions: Array<{
  value: GenerationTonePreset;
  label: string;
  description: string;
}> = [
  {
    value: "measured",
    label: "Measured",
    description: "Cool, precise, and controlled.",
  },
  {
    value: "cutting",
    label: "Cutting",
    description: "Sharper, drier, and a little less patient.",
  },
  {
    value: "grandiose",
    label: "Grandiose",
    description: "Sweeping, theatrical, and elegantly over the top.",
  },
];

const POLL_INTERVAL_MS = 350;

function formatJobStatus(status: GenerationJobStatus) {
  return status.charAt(0).toUpperCase() + status.slice(1);
}

function formatProviderLabel(record: GenerationJobRecord) {
  return record.provider_name ?? record.provider_type ?? "Provider pending";
}

function formatToneLabel(tonePreset: GenerationTonePreset) {
  return (
    tonePresetOptions.find((option) => option.value === tonePreset)?.label ??
    tonePreset
  );
}

function formatAudioTurnSourceLabel(source: AudioTurnCaptureSource) {
  return source === "recording" ? "Recording" : "Upload";
}

function formatRecordingTimer(durationMs: number) {
  const totalSeconds = Math.max(Math.floor(durationMs / 1000), 0);
  const minutes = String(Math.floor(totalSeconds / 60)).padStart(2, "0");
  const seconds = String(totalSeconds % 60).padStart(2, "0");
  return `${minutes}:${seconds}`;
}

function formatDurationLabel(durationMs: number | null) {
  return durationMs === null ? "Pending" : `${durationMs} ms`;
}

function formatTimingLabel(timing: GenerationJobRecord["timing"]) {
  return `${timing.duration_ms} ms`;
}

function upsertRecord<T extends { job_id: string }>(
  records: T[],
  updatedRecord: T,
) {
  const existingIndex = records.findIndex(
    (record) => record.job_id === updatedRecord.job_id,
  );

  if (existingIndex === -1) {
    return [updatedRecord, ...records];
  }

  return records.map((record) =>
    record.job_id === updatedRecord.job_id ? updatedRecord : record,
  );
}

function getLatestRecord<T>(records: T[]) {
  return records[0] ?? null;
}

function getCurrentClipAttempt(attempts: GenerationJobRecord[]) {
  return attempts.find((attempt) => attempt.status === "succeeded") ?? null;
}

function getPlaybackState(attempts: GenerationJobRecord[]): GenerationPlaybackState {
  const latestAttempt = getLatestRecord(attempts);
  if (!latestAttempt) {
    return "empty";
  }

  return latestAttempt.status;
}

function CurrentClipCard({
  currentClip,
  latestAttempt,
}: {
  currentClip: GenerationJobRecord | null;
  latestAttempt: GenerationJobRecord | null;
}) {
  return (
    <article className="current-clip-card" aria-labelledby="current-clip-title">
      <header className="current-clip-card__header">
        <p className="section-kicker">Current clip</p>
        <h2 id="current-clip-title">Current clip</h2>
        <p className="current-clip-card__lede">
          The latest playable clip stays controlled through the browser and keeps
          the audio URL relative.
        </p>
      </header>

      {currentClip ? (
        <div className="current-clip-card__body">
          <div className="current-clip-card__player">
            <audio
              controls
              aria-label="Current clip playback"
              preload="metadata"
              src={currentClip.playback_url ?? undefined}
            />
          </div>

          <dl className="current-clip-card__details">
            <div>
              <dt>Job ID</dt>
              <dd>{currentClip.job_id}</dd>
            </div>
            <div>
              <dt>Status</dt>
              <dd>{formatJobStatus(currentClip.status)}</dd>
            </div>
            <div>
              <dt>Text</dt>
              <dd>{currentClip.text}</dd>
            </div>
            <div>
              <dt>Voice</dt>
              <dd>{voiceDisplaySeeds[0]?.displayName ?? currentClip.voice_id}</dd>
            </div>
            <div>
              <dt>Tone</dt>
              <dd>{formatToneLabel(currentClip.tone_preset)}</dd>
            </div>
            <div>
              <dt>Provider</dt>
              <dd>{formatProviderLabel(currentClip)}</dd>
            </div>
            <div>
              <dt>Audio duration</dt>
              <dd>{formatDurationLabel(currentClip.audio_duration_ms)}</dd>
            </div>
            <div>
              <dt>Timing</dt>
              <dd>{formatTimingLabel(currentClip.timing)}</dd>
            </div>
            <div>
              <dt>Rights</dt>
              <dd>{currentClip.rights_check.message}</dd>
            </div>
          </dl>
        </div>
      ) : (
        <div className="current-clip-card__empty">
          <p className="current-clip-card__empty-state">No playable clip yet.</p>
          <p className="current-clip-card__empty-note">
            {latestAttempt
              ? latestAttempt.status === "failed"
                ? "The latest attempt failed. Use Recent attempts to retry it."
                : "The latest attempt is still resolving."
              : "Generate a line to hear the current clip here."}
          </p>
        </div>
      )}
    </article>
  );
}

function RecentAttemptList({
  attempts,
  onRetryCurrentGeneration,
}: {
  attempts: GenerationJobRecord[];
  onRetryCurrentGeneration: () => void;
}) {
  return (
    <section className="recent-attempts" aria-labelledby="recent-attempts-title">
      <header className="recent-attempts__header">
        <p className="section-kicker">Recent attempts</p>
        <h2 id="recent-attempts-title">Recent attempts</h2>
        <p className="recent-attempts__lede">
          Keep the current session visible. Failed attempts remain listed here so
          retry can reuse the last submitted inputs.
        </p>
      </header>

      <ol className="attempt-list" aria-label="Recent attempts">
        {attempts.length === 0 ? (
          <li className="recent-attempts__empty">No attempts yet.</li>
        ) : (
          attempts.map((attempt, index) => {
            const isLatestAttempt = index === 0;

            return (
              <li key={attempt.job_id}>
                <article
                  className={`attempt-card attempt-card--${attempt.status}`}
                  aria-labelledby={`attempt-${attempt.job_id}`}
                >
                  <header className="attempt-card__header">
                    <p className="attempt-card__kicker">
                      {formatJobStatus(attempt.status)}
                    </p>
                    <h3 id={`attempt-${attempt.job_id}`}>{attempt.job_id}</h3>
                  </header>

                  <dl className="attempt-card__details">
                    <div>
                      <dt>Voice</dt>
                      <dd>{voiceDisplaySeeds[0]?.displayName ?? attempt.voice_id}</dd>
                    </div>
                    <div>
                      <dt>Tone</dt>
                      <dd>{formatToneLabel(attempt.tone_preset)}</dd>
                    </div>
                    <div>
                      <dt>Text</dt>
                      <dd>{attempt.text}</dd>
                    </div>
                    <div>
                      <dt>Provider</dt>
                      <dd>{formatProviderLabel(attempt)}</dd>
                    </div>
                    <div>
                      <dt>Timing</dt>
                      <dd>{formatTimingLabel(attempt.timing)}</dd>
                    </div>
                    <div>
                      <dt>Audio duration</dt>
                      <dd>{formatDurationLabel(attempt.audio_duration_ms)}</dd>
                    </div>
                  </dl>

                  {attempt.status === "failed" && isLatestAttempt ? (
                    <button
                      type="button"
                      className="studio-action studio-action--secondary"
                      onClick={onRetryCurrentGeneration}
                    >
                      Retry current generation
                    </button>
                  ) : null}
                </article>
              </li>
            );
          })
        )}
      </ol>
    </section>
  );
}

function SpokenTurnList({ turns }: { turns: AudioTurnJobRecord[] }) {
  return (
    <section className="recent-attempts" aria-labelledby="spoken-turns-title">
      <header className="recent-attempts__header">
        <p className="section-kicker">Spoken turns</p>
        <h2 id="spoken-turns-title">Spoken turns</h2>
        <p className="recent-attempts__lede">
          Keep spoken capture separate from generation attempts. Each turn stays
          in the current session until the page refreshes.
        </p>
      </header>

      <ol className="attempt-list" aria-label="Spoken turns">
        {turns.length === 0 ? (
          <li className="recent-attempts__empty">No spoken turns yet</li>
        ) : (
          turns.map((turn) => (
            <li key={turn.job_id}>
              <article
                className={`attempt-card attempt-card--${turn.status}`}
                aria-labelledby={`spoken-turn-${turn.job_id}`}
              >
                <header className="attempt-card__header">
                  <p className="attempt-card__kicker">{formatJobStatus(turn.status)}</p>
                  <h3 id={`spoken-turn-${turn.job_id}`}>{turn.job_id}</h3>
                </header>

                <dl className="attempt-card__details">
                  <div>
                    <dt>Source</dt>
                    <dd>{formatAudioTurnSourceLabel(turn.capture_source)}</dd>
                  </div>
                  <div>
                    <dt>File</dt>
                    <dd>{turn.audio_filename}</dd>
                  </div>
                  <div>
                    <dt>MIME</dt>
                    <dd>{turn.audio_mime_type}</dd>
                  </div>
                  <div>
                    <dt>Status</dt>
                    <dd>{formatJobStatus(turn.status)}</dd>
                  </div>
                </dl>
              </article>
            </li>
          ))
        )}
      </ol>
    </section>
  );
}

export function StudioShell() {
  const [selectedVoiceId, setSelectedVoiceId] = useState(
    voiceDisplaySeeds[0]?.id ?? "",
  );
  const [generationText, setGenerationText] = useState("");
  const [selectedTonePreset, setSelectedTonePreset] =
    useState<GenerationTonePreset>("measured");
  const [attempts, setAttempts] = useState<GenerationJobRecord[]>([]);
  const [generationError, setGenerationError] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [activeJobId, setActiveJobId] = useState<string | null>(null);
  const [lastSubmission, setLastSubmission] = useState<GenerationSubmission | null>(
    null,
  );
  const [spokenTurns, setSpokenTurns] = useState<AudioTurnJobRecord[]>([]);
  const [captureMessage, setCaptureMessage] = useState("Ready to record");
  const [captureError, setCaptureError] = useState<string | null>(null);
  const [isRecording, setIsRecording] = useState(false);
  const [recordingStartedAt, setRecordingStartedAt] = useState<number | null>(null);
  const [recordingElapsedMs, setRecordingElapsedMs] = useState(0);
  const audioUploadInputRef = useRef<HTMLInputElement | null>(null);
  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const mediaStreamRef = useRef<MediaStream | null>(null);
  const recordingChunksRef = useRef<Blob[]>([]);
  const recordingTimerRef = useRef<number | null>(null);
  const pollTimerRef = useRef<number | null>(null);

  const selectedVoice =
    voiceDisplaySeeds.find((voice) => voice.id === selectedVoiceId) ??
    voiceDisplaySeeds[0];
  const latestAttempt = getLatestRecord(attempts);
  const currentClip = getCurrentClipAttempt(attempts);
  const playbackState = getPlaybackState(attempts);

  const generationStatusText = isSubmitting
    ? "Generating..."
    : playbackState === "queued"
      ? "Queued"
      : playbackState === "running"
        ? "Running"
        : playbackState === "failed"
          ? "Failed"
          : playbackState === "succeeded"
            ? "Succeeded"
            : "Ready to generate";

  const recordingStatusText = captureError ?? captureMessage;
  const recordingTimerText = formatRecordingTimer(recordingElapsedMs);

  async function submitGeneration(submission: GenerationSubmission) {
    setIsSubmitting(true);
    setGenerationError(null);

    try {
      const response = await fetch("/generate", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          voice_id: submission.voiceId,
          text: submission.text,
          tone_preset: submission.tonePreset,
        } satisfies GenerationRequestPayload),
      });

      const payload = (await response.json()) as
        | GenerationJobRecord
        | (GenerationResponseError & Partial<GenerationJobRecord>);
      const responseError = payload as GenerationResponseError;

      if (!response.ok) {
        throw new Error(
          typeof responseError.detail === "string"
            ? responseError.detail
            : "Generation request failed.",
        );
      }

      const generationRecord = payload as GenerationJobRecord;
      setLastSubmission(submission);
      setAttempts((currentAttempts) =>
        upsertRecord(currentAttempts, generationRecord),
      );
      setActiveJobId(generationRecord.job_id);
    } catch (error) {
      setGenerationError(
        error instanceof Error ? error.message : "Generation request failed.",
      );
    } finally {
      setIsSubmitting(false);
    }
  }

  async function submitAudioTurn(
    audioBlob: Blob,
    captureSource: AudioTurnCaptureSource,
    audioFilename: string,
  ) {
    const mimeType = audioBlob.type || "audio/webm";
    try {
      const response = await fetch("/audio-turns", {
        method: "POST",
        headers: {
          "Content-Type": mimeType,
          "X-Audio-Capture-Source": captureSource,
          "X-Audio-Filename": audioFilename,
        },
        body: audioBlob,
      });

      const payload = (await response.json()) as
        | AudioTurnJobRecord
        | { detail?: string };
      const responseError = payload as { detail?: string };

      if (!response.ok) {
        throw new Error(
          typeof responseError.detail === "string"
            ? responseError.detail
            : "Audio turn request failed.",
        );
      }

      const audioTurnRecord = payload as AudioTurnJobRecord;
      setSpokenTurns((currentTurns) => upsertRecord(currentTurns, audioTurnRecord));
      setCaptureMessage("Queued");
      setCaptureError(null);
      return audioTurnRecord;
    } catch (error) {
      const message =
        error instanceof Error ? error.message : "Audio turn request failed.";
      setCaptureMessage(message);
      setCaptureError(message);
      throw error;
    }
  }

  async function startRecording() {
    setCaptureError(null);

    if (!navigator.mediaDevices?.getUserMedia) {
      const message =
        "Mic access is blocked. Allow microphone access in the browser or upload audio instead.";
      setCaptureMessage(message);
      setCaptureError(message);
      return;
    }

    if (typeof MediaRecorder === "undefined") {
      const message =
        "Recording is not supported in this browser. Upload audio instead.";
      setCaptureMessage(message);
      setCaptureError(message);
      return;
    }

    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      const preferredMimeType =
        typeof MediaRecorder.isTypeSupported === "function" &&
        MediaRecorder.isTypeSupported("audio/webm;codecs=opus")
          ? "audio/webm;codecs=opus"
          : "audio/webm";
      const recorder = new MediaRecorder(stream, { mimeType: preferredMimeType });

      recordingChunksRef.current = [];
      recorder.ondataavailable = (event) => {
        if (event.data.size > 0) {
          recordingChunksRef.current.push(event.data);
        }
      };
      recorder.onstop = () => {
        const recordingBlob = new Blob(recordingChunksRef.current, {
          type: recorder.mimeType || preferredMimeType,
        });
        recordingChunksRef.current = [];
        mediaRecorderRef.current = null;
        mediaStreamRef.current?.getTracks().forEach((track) => track.stop());
        mediaStreamRef.current = null;
        setIsRecording(false);
        setRecordingStartedAt(null);
        setRecordingElapsedMs(0);
        void submitAudioTurn(
          recordingBlob,
          "recording",
          "spoken-turn.webm",
        ).catch(() => undefined);
      };

      recorder.start();
      mediaRecorderRef.current = recorder;
      mediaStreamRef.current = stream;
      setIsRecording(true);
      setRecordingStartedAt(Date.now());
      setRecordingElapsedMs(0);
      setCaptureMessage("Recording...");
      setCaptureError(null);
    } catch (error) {
      const message =
        error instanceof DOMException &&
        (error.name === "NotAllowedError" || error.name === "NotFoundError")
          ? "Mic access is blocked. Allow microphone access in the browser or upload audio instead."
          : error instanceof Error
            ? error.message
            : "Mic access is blocked. Allow microphone access in the browser or upload audio instead.";
      setCaptureMessage(message);
      setCaptureError(message);
      setIsRecording(false);
      setRecordingStartedAt(null);
      setRecordingElapsedMs(0);
    }
  }

  function stopRecording() {
    const recorder = mediaRecorderRef.current;
    if (!recorder || recorder.state === "inactive") {
      return;
    }

    recorder.stop();
  }

  function handleAudioButtonClick() {
    if (isRecording) {
      stopRecording();
      return;
    }

    void startRecording();
  }

  async function handleAudioUploadChange(event: ChangeEvent<HTMLInputElement>) {
    const file = event.currentTarget.files?.[0];
    event.currentTarget.value = "";

    if (!file) {
      return;
    }

    const isSupportedAudio =
      file.type.startsWith("audio/") ||
      /\.(wav|webm|mp3|m4a|ogg|flac)$/i.test(file.name);

    if (!isSupportedAudio) {
      const message =
        "That file is not supported. Upload a valid audio file and try again.";
      setCaptureMessage(message);
      setCaptureError(message);
      return;
    }

    setCaptureMessage("Queued");
    setCaptureError(null);
    await submitAudioTurn(file, "upload", file.name || "spoken-turn.audio").catch(
      () => undefined,
    );
  }

  function triggerAudioUpload() {
    audioUploadInputRef.current?.click();
  }

  async function handleGenerate(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();

    const trimmedText = generationText.trim();
    if (!trimmedText) {
      setGenerationError("Generation text is required.");
      return;
    }

    await submitGeneration({
      voiceId: selectedVoiceId,
      text: trimmedText,
      tonePreset: selectedTonePreset,
    });
  }

  async function retryCurrentGeneration() {
    if (!lastSubmission) {
      return;
    }

    await submitGeneration(lastSubmission);
  }

  useEffect(() => {
    if (!isRecording || recordingStartedAt === null) {
      if (recordingTimerRef.current !== null) {
        window.clearInterval(recordingTimerRef.current);
        recordingTimerRef.current = null;
      }
      return undefined;
    }

    recordingTimerRef.current = window.setInterval(() => {
      setRecordingElapsedMs(Date.now() - recordingStartedAt);
    }, 250);

    return () => {
      if (recordingTimerRef.current !== null) {
        window.clearInterval(recordingTimerRef.current);
        recordingTimerRef.current = null;
      }
    };
  }, [isRecording, recordingStartedAt]);

  useEffect(() => {
    if (!activeJobId) {
      return undefined;
    }

    let cancelled = false;

    const pollGeneration = async () => {
      try {
        const response = await fetch(`/generations/${activeJobId}`);
        const payload = (await response.json()) as GenerationJobRecord & {
          detail?: string;
        };
        const responseError = payload as GenerationResponseError;

        if (!response.ok) {
          throw new Error(
            typeof responseError.detail === "string"
              ? responseError.detail
              : "Failed to poll generation status.",
          );
        }

        if (cancelled) {
          return;
        }

        setAttempts((currentAttempts) => upsertRecord(currentAttempts, payload));

        if (payload.status === "queued" || payload.status === "running") {
          pollTimerRef.current = window.setTimeout(() => {
            void pollGeneration();
          }, POLL_INTERVAL_MS);
          return;
        }

        setActiveJobId(null);
        if (payload.status === "failed") {
          setGenerationError(
            payload.attempt.error_message ?? "Generation failed after job polling.",
          );
        } else {
          setGenerationError(null);
        }
      } catch (error) {
        if (cancelled) {
          return;
        }

        setGenerationError(
          error instanceof Error ? error.message : "Failed to poll generation status.",
        );
        setActiveJobId(null);
      }
    };

    pollTimerRef.current = window.setTimeout(() => {
      void pollGeneration();
    }, POLL_INTERVAL_MS);

    return () => {
      cancelled = true;
      if (pollTimerRef.current !== null) {
        window.clearTimeout(pollTimerRef.current);
        pollTimerRef.current = null;
      }
    };
  }, [activeJobId]);

  useEffect(
    () => () => {
      if (recordingTimerRef.current !== null) {
        window.clearInterval(recordingTimerRef.current);
        recordingTimerRef.current = null;
      }

      mediaStreamRef.current?.getTracks().forEach((track) => track.stop());
    },
    [],
  );

  return (
    <main className="studio-shell">
      <div className="studio-shell__glow studio-shell__glow--left" aria-hidden="true" />
      <div className="studio-shell__glow studio-shell__glow--right" aria-hidden="true" />

      <section className="studio-panel" aria-labelledby="studio-title">
        <header className="studio-panel__header">
          <p className="eyebrow">No-login studio</p>
          <h1 className="studio-panel__title" id="studio-title">
            Theatrical Voice Studio
          </h1>
          <p className="lede">
            Open the studio directly, keep the first surface voice-first, and let
            Vesper Glass define the tone of the room.
          </p>
        </header>

        <div className="studio-panel__grid">
          <section className="studio-panel__primary" aria-label="Voice surface">
            <div className="control-row">
              <div className="field-group">
                <label htmlFor="voice-selector">Voice selector</label>
                <select
                  id="voice-selector"
                  name="voice-selector"
                  value={selectedVoiceId}
                  onChange={(event) => setSelectedVoiceId(event.target.value)}
                >
                  {voiceDisplaySeeds.map((voice) => (
                    <option key={voice.id} value={voice.id}>
                      {voice.selectorLabel}
                    </option>
                  ))}
                </select>
              </div>

              <div className="approval-badge" role="status" aria-label="Voice rights status">
                {selectedVoice.approvalBadgeLabel}
              </div>
            </div>

            <article className="voice-card" aria-labelledby="voice-card-title">
              <p className="voice-card__kicker">Bundled original voice</p>
              <h2 id="voice-card-title">{selectedVoice.displayName}</h2>
              <p className="voice-card__summary">{selectedVoice.stageSummary}</p>

              <dl className="voice-card__details">
                <div>
                  <dt>Rights</dt>
                  <dd>{selectedVoice.rightsSummary}</dd>
                </div>
                <div>
                  <dt>Source note</dt>
                  <dd>{selectedVoice.sourceNote}</dd>
                </div>
                <div>
                  <dt>Boundary</dt>
                  <dd>{selectedVoice.boundaryNote}</dd>
                </div>
              </dl>

              <ul className="trait-list" aria-label="Voice traits">
                {selectedVoice.styleTraits.map((trait) => (
                  <li key={trait}>{trait}</li>
                ))}
              </ul>
            </article>

            <div
              style={{
                display: "grid",
                gap: "1rem",
                gridTemplateColumns: "repeat(auto-fit, minmax(20rem, 1fr))",
                alignItems: "start",
              }}
            >
              <section className="generation-form" aria-labelledby="spoken-input-title">
                <header className="generation-card__header" style={{ marginBottom: 0 }}>
                  <p className="section-kicker">Spoken input</p>
                  <h2 id="spoken-input-title">Record or upload audio</h2>
                  <p className="generation-card__lede">
                    Record a line or upload audio beside the composer to create a
                    queued spoken turn.
                  </p>
                </header>

                <div
                  style={{
                    display: "flex",
                    flexWrap: "wrap",
                    gap: "0.75rem",
                    alignItems: "center",
                  }}
                >
                  <div className="generation-status" role="status" aria-label="Recording status">
                    {recordingStatusText}
                  </div>
                  <div
                    className="generation-status"
                    aria-label="Recording timer"
                    aria-live="polite"
                    aria-atomic="true"
                  >
                    {recordingTimerText}
                  </div>
                </div>

                <div className="generation-form__footer">
                  <button
                    type="button"
                    className="studio-action"
                    onClick={handleAudioButtonClick}
                  >
                    {isRecording ? "Stop recording" : "Record turn"}
                  </button>

                  <button
                    type="button"
                    className="studio-action studio-action--secondary"
                    onClick={triggerAudioUpload}
                  >
                    Upload audio
                  </button>
                </div>

                <input
                  ref={audioUploadInputRef}
                  type="file"
                  accept="audio/*"
                  aria-label="Audio file input"
                  onChange={handleAudioUploadChange}
                  style={{
                    position: "absolute",
                    width: "1px",
                    height: "1px",
                    padding: 0,
                    margin: "-1px",
                    overflow: "hidden",
                    clip: "rect(0, 0, 0, 0)",
                    whiteSpace: "nowrap",
                    border: 0,
                  }}
                />

                {captureError ? (
                  <p className="generation-state generation-state--error" role="alert">
                    {captureError}
                  </p>
                ) : null}
              </section>

              <form className="generation-form" onSubmit={handleGenerate}>
                <div className="field-group field-group--wide">
                  <label htmlFor="generation-text">Generation text</label>
                  <textarea
                    id="generation-text"
                    name="generation-text"
                    value={generationText}
                    onChange={(event) => setGenerationText(event.target.value)}
                    placeholder="Write the line to audition in Vesper Glass's voice."
                    rows={5}
                  />
                </div>

                <fieldset className="tone-selector">
                  <legend>Tone preset</legend>
                  <div className="tone-selector__chips">
                    {tonePresetOptions.map((option) => {
                      const isSelected = selectedTonePreset === option.value;

                      return (
                        <button
                          key={option.value}
                          type="button"
                          className={`tone-chip${isSelected ? " tone-chip--selected" : ""}`}
                          aria-pressed={isSelected}
                          onClick={() => setSelectedTonePreset(option.value)}
                        >
                          <span>{option.label}</span>
                          <small>{option.description}</small>
                        </button>
                      );
                    })}
                  </div>
                </fieldset>

                <div className="generation-form__footer">
                  <div className="generation-status" role="status" aria-label="Generation status">
                    {generationStatusText}
                  </div>

                  <button
                    type="submit"
                    className="studio-action"
                    disabled={isSubmitting || generationText.trim().length === 0}
                    aria-busy={isSubmitting}
                  >
                    {isSubmitting ? "Generating..." : "Generate voice"}
                  </button>
                </div>
              </form>
            </div>

            {generationError ? (
              <p className="generation-state generation-state--error" role="alert">
                {generationError}
              </p>
            ) : null}

            <SpokenTurnList turns={spokenTurns} />

            <CurrentClipCard currentClip={currentClip} latestAttempt={latestAttempt} />

            <RecentAttemptList
              attempts={attempts}
              onRetryCurrentGeneration={retryCurrentGeneration}
            />
          </section>

          <aside className="mission-panel" aria-label="Studio posture">
            <p className="mission-panel__label">Studio posture</p>
            <p>
              Text generation and spoken capture now share the same no-login studio
              surface while staying in separate session lists.
            </p>
            <p>
              Playback remains controlled through same-origin API URLs, retry still
              reuses the last submitted generation inputs, and refresh clears session
              history.
            </p>
            <p>
              The spoken-input path stays capture-first so future VAD and STT work can
              extend the same job seam without adding a separate page.
            </p>
          </aside>
        </div>
      </section>
    </main>
  );
}
