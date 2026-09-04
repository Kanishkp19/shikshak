export type MotionGraphicElementType =
  | "text"
  | "arrow"
  | "badge"
  | "icon"
  | "highlight"
  | "card"
  | "metric";

export interface MotionGraphicElement {
  id?: string;
  type: MotionGraphicElementType;
  content: string;
  subtitle?: string;
  icon?: string;
  color?: string;
}

export type MotionTemplateType =
  | "step_by_step_flow"
  | "animated_title"
  | "concept_highlight"
  | "text_reveal"
  | "comparison"
  | "timeline"
  | "diagram_build";

export interface MotionSceneProps {
  template: MotionTemplateType;
  title: string;
  subtitle?: string;
  steps?: string[];
  elements?: MotionGraphicElement[];
  keyTakeaway?: string;
  accentColor?: string;
  badge?: string;
  narrationText?: string;
  durationSeconds?: number;
}
