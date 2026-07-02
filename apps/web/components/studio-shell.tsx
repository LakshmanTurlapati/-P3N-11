"use client";

import { type FormEvent, useState } from "react";

import { voiceDisplaySeeds } from "@/lib/voice-registry";

type GenerationTonePreset = "measured" | "cutting" | "grandiose";

type GenerationTraceEntry = {
  stage: string;
  provider: string;
  detail: string;
};

type GenerationResult = {
  provider_type: string;
  job_id: string;
  status: "queued" | "running" | "succeeded" | "failed";
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

function formatJobStatus(status: GenerationResult["status"]) {
  return status.charAt(0).toUpperCase() + status.slice(1);
}

function formatProviderType(providerType: string) {
  if (providerType.includes("prototype")) {
    return "Prototype baseline stub";
  }

  return providerType;
}

export function StudioShell() {
  const [selectedVoiceId, setSelectedVoiceId] = useState(
    voiceDisplaySeeds[0]?.id ?? "",
  );
  const [generationText, setGenerationText] = useState("");
  const [selectedTonePreset, setSelectedTonePreset] =
    useState<GenerationTonePreset>("measured");
  const [isGenerating, setIsGenerating] = useState(false);
  const [generationError, setGenerationError] = useState<string | null>(null);
  const [generationResult, setGenerationResult] = useState<GenerationResult | null>(null);

  const selectedVoice =
    voiceDisplaySeeds.find((voice) => voice.id === selectedVoiceId) ??
    voiceDisplaySeeds[0];

  const generationStatusText = generationResult
    ? formatJobStatus(generationResult.status)
    : isGenerating
      ? "Generating..."
      : "Ready to generate";

  async function handleGenerate(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();

    const trimmedText = generationText.trim();
    if (!trimmedText) {
      setGenerationError("Generation text is required.");
      setGenerationResult(null);
      return;
    }

    setIsGenerating(true);
    setGenerationError(null);

    try {
      const response = await fetch("/generate", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          voice_id: selectedVoiceId,
          text: trimmedText,
          tone_preset: selectedTonePreset,
        }),
      });

      const payload = (await response.json()) as GenerationResult & {
        detail?: string;
      };

      if (!response.ok) {
        throw new Error(
          typeof payload.detail === "string"
            ? payload.detail
            : "Generation request failed.",
        );
      }

      setGenerationResult(payload);
    } catch (error) {
      setGenerationResult(null);
      setGenerationError(
        error instanceof Error ? error.message : "Generation request failed.",
      );
    } finally {
      setIsGenerating(false);
    }
  }

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
                  disabled={isGenerating || generationText.trim().length === 0}
                  aria-busy={isGenerating}
                >
                  {isGenerating ? "Generating..." : "Generate voice"}
                </button>
              </div>
            </form>

            {generationError ? (
              <p className="generation-state generation-state--error" role="alert">
                {generationError}
              </p>
            ) : null}

            {generationResult ? (
              <article className="generation-card" aria-labelledby="generation-job-title">
                <header className="generation-card__header">
                  <p className="generation-card__kicker">Prototype baseline audition</p>
                  <h2 id="generation-job-title">Generation job</h2>
                  <p className="generation-card__lede">
                    The server returned a queued prototype job and kept the rights gate
                    ahead of generation work.
                  </p>
                </header>

                <div className="generation-card__grid">
                  <dl className="generation-card__details">
                    <div>
                      <dt>Job ID</dt>
                      <dd>{generationResult.job_id}</dd>
                    </div>
                    <div>
                      <dt>Status</dt>
                      <dd>{formatJobStatus(generationResult.status)}</dd>
                    </div>
                    <div>
                      <dt>Voice</dt>
                      <dd>{selectedVoice.displayName}</dd>
                    </div>
                    <div>
                      <dt>Text</dt>
                      <dd>{generationResult.text}</dd>
                    </div>
                    <div>
                      <dt>Tone</dt>
                      <dd>
                        {
                          tonePresetOptions.find(
                            (option) => option.value === generationResult.tone_preset,
                          )?.label
                        }
                      </dd>
                    </div>
                    <div>
                      <dt>Rights check</dt>
                      <dd>
                        {generationResult.rights_check.status}
                        {" - "}
                        {generationResult.rights_check.message}
                      </dd>
                    </div>
                    <div>
                      <dt>Provider</dt>
                      <dd>{formatProviderType(generationResult.provider_type)}</dd>
                    </div>
                    <div>
                      <dt>Timing</dt>
                      <dd>
                        {generationResult.timing.started_at} -{" "}
                        {generationResult.timing.ended_at} (
                        {generationResult.timing.duration_ms} ms)
                      </dd>
                    </div>
                  </dl>

                  <section className="generation-card__trace" aria-label="Provider trace">
                    <p className="generation-card__trace-label">Provider trace</p>
                    <ul>
                      {generationResult.provider_trace.map((entry) => (
                        <li key={`${entry.stage}-${entry.provider}`}>
                          <strong>{entry.stage}</strong>
                          <span>{entry.provider}</span>
                          <p>{entry.detail}</p>
                        </li>
                      ))}
                    </ul>
                  </section>
                </div>
              </article>
            ) : null}
          </section>

          <aside className="mission-panel" aria-label="Studio posture">
            <p className="mission-panel__label">Studio posture</p>
            <p>
              The first pass stays text-only, tone-locked, and rights-gated. Playback
              and live conversation come later.
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
