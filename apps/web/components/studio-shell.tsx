"use client";

import { useState } from "react";

import { voiceDisplaySeeds } from "@/lib/voice-registry";

export function StudioShell() {
  const [selectedVoiceId, setSelectedVoiceId] = useState(
    voiceDisplaySeeds[0]?.id ?? "",
  );

  const selectedVoice =
    voiceDisplaySeeds.find((voice) => voice.id === selectedVoiceId) ??
    voiceDisplaySeeds[0];

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
            <button type="button" className="studio-action">
              Generate stub reading
            </button>
          </aside>
        </div>
      </section>
    </main>
  );
}
