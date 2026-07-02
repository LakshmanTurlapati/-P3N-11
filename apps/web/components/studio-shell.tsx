"use client";

import { type FormEvent, useEffect, useRef, useState } from "react";

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

function formatDurationLabel(durationMs: number | null) {
  return durationMs === null ? "Pending" : `${durationMs} ms`;
}

function formatTimingLabel(timing: GenerationJobRecord["timing"]) {
  return `${timing.duration_ms} ms`;
}

function upsertAttempt(
  attempts: GenerationJobRecord[],
  updatedAttempt: GenerationJobRecord,
) {
  const existingIndex = attempts.findIndex(
    (attempt) => attempt.job_id === updatedAttempt.job_id,
  );

  if (existingIndex === -1) {
    return [updatedAttempt, ...attempts];
  }

  return attempts.map((attempt) =>
    attempt.job_id === updatedAttempt.job_id ? updatedAttempt : attempt,
  );
}

function getLatestAttempt(attempts: GenerationJobRecord[]) {
  return attempts[0] ?? null;
}

function getCurrentClipAttempt(attempts: GenerationJobRecord[]) {
  return attempts.find((attempt) => attempt.status === "succeeded") ?? null;
}

function getPlaybackState(attempts: GenerationJobRecord[]): GenerationPlaybackState {
  const latestAttempt = getLatestAttempt(attempts);
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
  const pollTimerRef = useRef<number | null>(null);

  const selectedVoice =
    voiceDisplaySeeds.find((voice) => voice.id === selectedVoiceId) ??
    voiceDisplaySeeds[0];
  const latestAttempt = getLatestAttempt(attempts);
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
        upsertAttempt(currentAttempts, generationRecord),
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

        setAttempts((currentAttempts) => upsertAttempt(currentAttempts, payload));

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

            {generationError ? (
              <p className="generation-state generation-state--error" role="alert">
                {generationError}
              </p>
            ) : null}

            <CurrentClipCard currentClip={currentClip} latestAttempt={latestAttempt} />

            <RecentAttemptList
              attempts={attempts}
              onRetryCurrentGeneration={retryCurrentGeneration}
            />
          </section>

          <aside className="mission-panel" aria-label="Studio posture">
            <p className="mission-panel__label">Studio posture</p>
            <p>
              The first pass stays text-only, tone-locked, and rights-gated while
              the browser keeps the current session visible.
            </p>
            <p>
              Playback is controlled through the API URL, retry reuses the last
              submitted inputs, and refresh clears session history.
            </p>
            <p>
              Prototype baseline output is acceptable here, but the voice copy must
              stay clearly original and never drift toward protected-character
              imitation.
            </p>
          </aside>
        </div>
      </section>
    </main>
  );
}
