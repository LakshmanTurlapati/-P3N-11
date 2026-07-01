"use client";

import { useState } from "react";

import { voiceDisplaySeeds } from "@/lib/voice-registry";

type GenerationTraceEntry = {
  stage: string;
  provider: string;
  detail: string;
};

type GenerationResult = {
  provider_type: string;
  voice_id: string;
  rights_check: {
    status: string;
    approved_for_generation: boolean;
    message: string;
  };
  result_metadata: {
    status: string;
    summary: string;
    artifact_label: string;
    provider_note: string;
  };
  provider_trace: GenerationTraceEntry[];
  timing: {
    started_at: string;
    ended_at: string;
    duration_ms: number;
  };
};

export function StudioShell() {
  const [selectedVoiceId, setSelectedVoiceId] = useState(
    voiceDisplaySeeds[0]?.id ?? "",
  );
  const [isGenerating, setIsGenerating] = useState(false);
  const [generationError, setGenerationError] = useState<string | null>(null);
  const [generationResult, setGenerationResult] = useState<GenerationResult | null>(null);

  const selectedVoice =
    voiceDisplaySeeds.find((voice) => voice.id === selectedVoiceId) ??
    voiceDisplaySeeds[0];

  async function handleGenerate() {
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

              <div className="approval-badge" role="status">
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
          </section>

          <aside className="mission-panel" aria-label="Studio posture">
            <p className="mission-panel__label">Studio posture</p>
            <p>
              The shell stays restrained, direct, and free of the later generation
              controls.
            </p>
            <button
              type="button"
              className="studio-action"
              onClick={handleGenerate}
              disabled={isGenerating}
              aria-busy={isGenerating}
            >
              {isGenerating ? "Generating..." : "Generate stub reading"}
            </button>
          </aside>
        </div>

        {generationError ? (
          <p className="generation-state generation-state--error" role="alert">
            {generationError}
          </p>
        ) : null}

        {generationResult ? (
          <article className="generation-card" aria-labelledby="generation-card-title">
            <header className="generation-card__header">
              <p className="generation-card__kicker">Structured metadata result</p>
              <h2 id="generation-card-title">Generation result</h2>
              <p className="generation-card__lede">
                The stub path returns a compact result card and no playback surface.
              </p>
            </header>

            <div className="generation-card__grid">
              <dl className="generation-card__details">
                <div>
                  <dt>Provider type</dt>
                  <dd>{generationResult.provider_type}</dd>
                </div>
                <div>
                  <dt>Voice id</dt>
                  <dd>{generationResult.voice_id}</dd>
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
                  <dt>Result metadata</dt>
                  <dd>
                    {generationResult.result_metadata.artifact_label}
                    {" - "}
                    {generationResult.result_metadata.summary}
                    <br />
                    {generationResult.result_metadata.provider_note}
                  </dd>
                </div>
                <div>
                  <dt>Timing</dt>
                  <dd>
                    {generationResult.timing.started_at} -{" "}
                    {generationResult.timing.ended_at} ({generationResult.timing.duration_ms}{" "}
                    ms)
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
    </main>
  );
}
