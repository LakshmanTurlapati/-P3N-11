export type VoiceDisplaySeed = {
  id: string;
  displayName: string;
  selectorLabel: string;
  approvalBadgeLabel: string;
  rightsSummary: string;
  sourceNote: string;
  boundaryNote: string;
  stageSummary: string;
  styleTraits: readonly string[];
};

export const vesperGlassDisplaySeed = {
  id: "vesper-glass",
  displayName: "Vesper Glass",
  selectorLabel: "Vesper Glass",
  approvalBadgeLabel: "Approved for generation",
  rightsSummary: "Original theatrical voice profile",
  sourceNote:
    "Render-only display seed for the Phase 1 studio shell; canonical rights records land in the backend slice.",
  boundaryNote:
    "Original voice profile. Not a clone of any actor or protected character.",
  stageSummary:
    "Measured theatrical delivery with cool charm, philosophical cynicism, and honey-edged sarcasm.",
  styleTraits: [
    "Measured theatrical delivery",
    "Cool charm",
    "Philosophical cynicism",
    "Honey-edged sarcasm",
  ],
} satisfies VoiceDisplaySeed;

export const voiceDisplaySeeds = [vesperGlassDisplaySeed] as const;

