"use client";

type ConversationTonePreset = "measured" | "cutting" | "grandiose";

export type ConversationSessionStatus = "listening" | "stopped";

export type ConversationTurnStatus =
  | "queued"
  | "running"
  | "succeeded"
  | "failed"
  | "interrupted"
  | "canceled";

type ConversationTurnCancelState = {
  requested_at: string;
  interrupted_at: string | null;
  canceled_at: string | null;
  reason: string | null;
};

export type ConversationTurnRecord = {
  turn_id: string;
  status: ConversationTurnStatus;
  input_audio_url: string | null;
  user_transcript_text: string | null;
  response_text: string | null;
  playback_url: string | null;
  tone_preset: ConversationTonePreset | null;
  latency_ms: number | null;
  cancel_state: ConversationTurnCancelState | null;
  timing: {
    started_at: string;
    ended_at: string;
    duration_ms: number;
    speech_end_to_transcript_ms: number | null;
    response_text_ms: number | null;
    tts_complete_ms: number | null;
    playback_start_ms: number | null;
  };
};

export type ConversationSessionRecord = {
  session_id: string;
  status: ConversationSessionStatus;
  turns: ConversationTurnRecord[];
  timing: {
    started_at: string;
    ended_at: string;
    duration_ms: number;
  };
};

type ConversationSessionPanelProps = {
  session: ConversationSessionRecord | null;
  statusText: string;
  errorMessage: string | null;
  isStarting: boolean;
  isStopping: boolean;
  canInterruptConversation: boolean;
  isInterruptingConversation: boolean;
  onStartConversation: () => void;
  onStopConversation: () => void;
  onInterruptConversation: () => void;
};

function formatStatusLabel(status: string) {
  return status.charAt(0).toUpperCase() + status.slice(1);
}

function formatLatencyLabel(latencyMs: number | null) {
  return latencyMs === null ? "Pending" : `${(latencyMs / 1000).toFixed(2)} s`;
}

function formatToneLabel(tonePreset: ConversationTonePreset | null) {
  if (!tonePreset) {
    return "Pending";
  }

  return tonePreset.charAt(0).toUpperCase() + tonePreset.slice(1);
}

function ConversationTurnCard({ turn }: { turn: ConversationTurnRecord }) {
  return (
    <article
      className={`attempt-card conversation-turn-card conversation-turn-card--${turn.status}`}
      aria-labelledby={`conversation-turn-${turn.turn_id}`}
    >
      <header className="attempt-card__header">
        <p className="attempt-card__kicker">{formatStatusLabel(turn.status)}</p>
        <div className="conversation-turn-card__header-row">
          <h3 id={`conversation-turn-${turn.turn_id}`}>{turn.turn_id}</h3>
          <div
            className="conversation-turn-card__latency-chip"
            aria-label={`Conversation turn ${turn.turn_id} latency chip`}
          >
            {formatLatencyLabel(turn.latency_ms)}
          </div>
        </div>
      </header>

      <dl className="attempt-card__details">
        <div>
          <dt>Input audio</dt>
          <dd>{turn.input_audio_url ?? "Pending"}</dd>
        </div>
        <div>
          <dt>Transcript</dt>
          <dd>{turn.user_transcript_text ?? "Pending"}</dd>
        </div>
        <div>
          <dt>Response</dt>
          <dd>{turn.response_text ?? "Pending"}</dd>
        </div>
        <div>
          <dt>Tone</dt>
          <dd>{formatToneLabel(turn.tone_preset)}</dd>
        </div>
      </dl>

      {turn.playback_url ? (
        <div className="current-clip-card__player conversation-turn-card__player">
          <audio
            controls
            aria-label={`Conversation turn ${turn.turn_id} playback`}
            preload="metadata"
            src={turn.playback_url}
          />
        </div>
      ) : null}
    </article>
  );
}

export function ConversationSessionPanel({
  session,
  statusText,
  errorMessage,
  isStarting,
  isStopping,
  canInterruptConversation,
  isInterruptingConversation,
  onStartConversation,
  onStopConversation,
  onInterruptConversation,
}: ConversationSessionPanelProps) {
  const turns = session?.turns ?? [];
  const sessionStatusText = session ? formatStatusLabel(session.status) : "Ready to start";
  const sessionIdText = session?.session_id ?? "Not started";

  return (
    <section className="conversation-panel" aria-labelledby="live-conversation-title">
      <header className="generation-card__header" style={{ marginBottom: 0 }}>
        <p className="section-kicker">Live conversation</p>
        <h2 id="live-conversation-title">Live conversation</h2>
        <p className="generation-card__lede">
          Start to arm the mic. Stop to hold the live session in place until
          refresh.
        </p>
      </header>

      <div className="conversation-panel__status-row">
        <div
          className="generation-status"
          role="status"
          aria-label="Live conversation status"
          aria-live="polite"
          aria-atomic="true"
        >
          {statusText}
        </div>
        <div
          className="generation-status"
          aria-label="Conversation session status"
          aria-live="polite"
          aria-atomic="true"
        >
          {sessionStatusText}
        </div>
      </div>

      <dl className="attempt-card__details conversation-panel__details">
        <div>
          <dt>Session ID</dt>
          <dd>{sessionIdText}</dd>
        </div>
        <div>
          <dt>Turns</dt>
          <dd>{turns.length}</dd>
        </div>
        <div>
          <dt>Session timing</dt>
          <dd>{`${session?.timing?.duration_ms ?? 0} ms`}</dd>
        </div>
      </dl>

      <div className="generation-form__footer conversation-panel__footer">
        <button
          type="button"
          className="studio-action"
          disabled={isStarting || session?.status === "listening"}
          aria-busy={isStarting}
          onClick={onStartConversation}
        >
          {isStarting ? "Starting..." : "Start conversation"}
        </button>

        <button
          type="button"
          className="studio-action studio-action--secondary"
          disabled={isStopping || !session || session.status !== "listening"}
          aria-busy={isStopping}
          onClick={onStopConversation}
        >
          {isStopping ? "Stopping..." : "Stop conversation"}
        </button>

        {canInterruptConversation ? (
          <button
            type="button"
            className="studio-action studio-action--secondary studio-action--interrupt"
            disabled={isInterruptingConversation}
            aria-busy={isInterruptingConversation}
            onClick={onInterruptConversation}
          >
            {isInterruptingConversation ? "Interrupting..." : "Interrupt"}
          </button>
        ) : null}
      </div>

      <ol className="attempt-list conversation-turn-list" aria-label="Conversation turns">
        {turns.length === 0 ? (
          <li className="recent-attempts__empty conversation-turn-list__empty">
            No conversation turns yet.
          </li>
        ) : (
          turns.map((turn) => (
            <li key={turn.turn_id}>
              <ConversationTurnCard turn={turn} />
            </li>
          ))
        )}
      </ol>

      {errorMessage ? (
        <p className="generation-state generation-state--error" role="alert">
          {errorMessage}
        </p>
      ) : null}
    </section>
  );
}
