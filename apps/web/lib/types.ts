/**
 * Shikshak AI — shared TypeScript types.
 * Mirrors the Pydantic models in apps/api/models/__init__.py exactly — every
 * field name and type is identical (camelCase on the wire).
 */

export type Level = "beginner" | "intermediate" | "advanced";
export type VisualType = "diagram" | "equation" | "code" | "animation" | "none";
export type SourceType = "document" | "topic";
export type SessionStatus =
  | "planning"
  | "in_progress"
  | "completed"
  | "failed";
export type SegmentStatus = "pending" | "rendering" | "ready" | "failed";
export type QuestionType = "mcq" | "short_answer" | "conceptual";

export interface LessonSegment {
  id: string;
  order: number;
  concept: string;
  depth: Level;
  visualType: VisualType;
  narrationScript: string;
  videoUrl: string | null;
  hasCheckpoint: boolean;
  relatedConcepts?: string[];
}

export interface Session {
  id: string;
  studentId: string;
  sourceType: SourceType;
  documentId: string | null;
  topic: string | null;
  level: Level;
  language: string;
  timeBudgetMinutes: number;
  status: SessionStatus;
  segments: LessonSegment[];
  createdAt: string;
}

export interface QuestionCheckpoint {
  id: string;
  segmentId: string;
  type: QuestionType;
  prompt: string;
  options: string[] | null;
  studentAnswer: string | null;
  isCorrect: boolean | null;
  misconception: string | null;
}

export interface AssessmentReport {
  sessionId: string;
  score: number;
  strongAreas: string[];
  weakAreas: string[];
  recommendation: string;
}

export interface LearnerProfile {
  studentId: string;
  topicsStudied: string[];
  weakConcepts: string[];
  strongConcepts: string[];
  averageScore: number;
  defaultLevel?: Level;
  defaultLanguage?: string;
}

export interface LearningPathItem {
  id: string;
  itemOrder: number;
  subTopic: string;
  status: "locked" | "unlocked" | "completed";
  relatedSessionId: string | null;
}

export interface LearningPath {
  id: string;
  broadTopic: string;
  items: LearningPathItem[];
}

export interface DocumentOut {
  id: string;
  fileName: string;
  fileType: "pdf" | "docx" | "pptx";
  pageCount: number | null;
  status: "processing" | "ready" | "failed";
}

export interface CreateSessionRequest {
  sourceType: SourceType;
  documentId?: string;
  topic?: string;
  level: Level;
  language: string;
  timeBudgetMinutes: number;
}

export interface SubmitAnswerResponse {
  isCorrect: boolean;
  misconception: string | null;
  nextSegmentId: string | null;
}

export interface AgentError {
  error: string;
  agent: string;
  retryable: boolean;
}
