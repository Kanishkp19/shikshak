/**
 * Shikshak AI — Semantic Animation Intermediate Representation (IR).
 * TypeScript interfaces mirroring the Python AnimationSceneSpec.
 *
 * Guaranteed Coordinate-Free:
 * LLMs and scene planners provide semantic educational intent only.
 * Motion Canvas resolves all geometry, layout, camera transforms, and timing.
 */

export interface SemanticObject {
  id: string;
  type: string; // "atom" | "molecule" | "bond" | "particle" | "wire" | "switch" | "resistor" | "membrane" | "organelle" | "equation" | "term" | string
  source?: string; // "rdkit" | "iec" | "bio_icons" | "latex" | "system"
  semanticRole: string; // e.g. "reactant_iron", "current_drift", "chlorophyll_hub"
  pedagogicalPurpose: string; // e.g. "count reactant iron atoms", "show electron flow"
  importance?: number; // 0.0 - 1.0
  label?: string;
  formula?: string;
  count?: number;
  properties?: Record<string, unknown>;
}

export type SemanticAction =
  | "introduce"
  | "reveal"
  | "highlight"
  | "focus"
  | "dim"
  | "emphasize"
  | "pulse"
  | "trace"
  | "draw"
  | "move"
  | "transform"
  | "morph"
  | "duplicate"
  | "split"
  | "merge"
  | "count"
  | "compare"
  | "follow"
  | "zoom"
  | "pan"
  | "camera_focus"
  | "camera_pullback"
  | "group"
  | "fade"
  | "equation_transform"
  | "coefficient_insert"
  | "object_compare"
  | "flow_particle"
  | "process_step"
  | "cause_effect"
  | "progressive_build"
  | "remove"
  | "reorder";

export interface SemanticBeat {
  at: number; // Start time in seconds relative to scene start
  duration?: number;
  action: SemanticAction | string;
  target?: string[]; // Target semantic object IDs
  semanticValue?: unknown;
  narrativeCue?: string;
  easing?: "linear" | "ease_in" | "ease_out" | "ease_in_out";
}

export type CameraAction =
  | "establish"
  | "focus"
  | "follow"
  | "zoom_in"
  | "zoom_out"
  | "pan"
  | "pullback";

export interface SemanticCameraKeyframe {
  at: number;
  action: CameraAction;
  target?: string[];
  zoomFactor?: number;
  transitionDuration?: number;
}

export interface NarrativeMarker {
  timeSeconds: number;
  wordCue: string;
}

export interface AnimationSceneSpec {
  sceneId: string;
  domain: "chemistry" | "physics" | "biology" | "mathematics" | "general";
  duration: number;
  fps?: number;
  width?: number;
  height?: number;
  objects: SemanticObject[];
  beats: SemanticBeat[];
  camera?: SemanticCameraKeyframe[];
  narrativeSync?: NarrativeMarker[];
  metadata?: Record<string, unknown>;
}
