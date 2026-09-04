/**
 * Shikshak AI — typed fetch wrapper around the FastAPI backend.
 *
 * Every endpoint in 05-BACKEND-SCHEMA.md "Full API contract" has a method here.
 * React Query is used by the calling components for caching, retry and
 * loading/empty/error state transitions.
 */
import type {
  AgentError,
  AssessmentReport,
  CreateSessionRequest,
  DocumentOut,
  LearnerProfile,
  LearningPath,
  Session,
  SubmitAnswerResponse,
} from "./types";

const API_BASE =
  process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000";

export class ApiError extends Error {
  status: number;
  payload: AgentError | null;

  constructor(message: string, status: number, payload: AgentError | null) {
    super(message);
    this.status = status;
    this.payload = payload;
  }
}

async function call<T>(
  path: string,
  init?: RequestInit & { json?: unknown },
): Promise<T> {
  const headers: Record<string, string> = {
    ...(init?.headers as Record<string, string> | undefined),
  };
  let body: BodyInit | null | undefined = init?.body;
  if (init?.json !== undefined) {
    headers["Content-Type"] = "application/json";
    body = JSON.stringify(init.json);
  }
  const res = await fetch(`${API_BASE}${path}`, {
    ...init,
    headers,
    body,
  });
  if (!res.ok) {
    let payload: AgentError | null = null;
    try {
      payload = (await res.json()) as AgentError;
    } catch {
      // not JSON
    }
    throw new ApiError(
      payload?.error ?? `HTTP ${res.status}`,
      res.status,
      payload,
    );
  }
  if (res.status === 204) return undefined as T;
  return (await res.json()) as T;
}

export const api = {
  // Documents
  uploadDocument: (file: File, ownerId: string) => {
    const fd = new FormData();
    fd.append("file", file);
    return call<DocumentOut>(`/api/v1/documents?owner_id=${encodeURIComponent(ownerId)}`, {
      method: "POST",
      body: fd,
    });
  },
  getDocument: (id: string) =>
    call<DocumentOut>(`/api/v1/documents/${id}`),

  // Sessions
  createSession: (body: CreateSessionRequest, studentId: string) =>
    call<{ sessionId: string; status: string }>(
      `/api/v1/sessions?student_id=${encodeURIComponent(studentId)}`,
      { method: "POST", json: body },
    ),
  listSessions: (studentId: string) =>
    call<Session[]>(`/api/v1/sessions?student_id=${encodeURIComponent(studentId)}`),
  getSession: (id: string) => call<Session>(`/api/v1/sessions/${id}`),
  deleteSession: (id: string) =>
    call<{ ok: boolean; sessionId: string; message: string }>(
      `/api/v1/sessions/${id}`,
      { method: "DELETE" },
    ),
  getSessionStatus: (id: string) =>
    call<{ status: string }>(`/api/v1/sessions/${id}/status`),
  switchLanguage: (id: string, language: string) =>
    call<{ status: string; language: string }>(
      `/api/v1/sessions/${id}/language`,
      { method: "POST", json: { language } },
    ),


  // Segments
  getSegmentStatus: (sessionId: string, segmentId: string) =>
    call<{ status: string; videoUrl: string | null }>(
      `/api/v1/sessions/${sessionId}/segments/${segmentId}/status`,
    ),
  renderSegment: (sessionId: string, segmentId: string) =>
    call<{ status: string; videoUrl: string; provider: string }>(
      `/api/v1/sessions/${sessionId}/segments/${segmentId}/render`,
      { method: "POST" },
    ),

  // Checkpoints
  submitAnswer: (sessionId: string, checkpointId: string, answer: string) =>
    call<SubmitAnswerResponse>(
      `/api/v1/sessions/${sessionId}/answer`,
      { method: "POST", json: { checkpointId, answer } },
    ),

  // Assessment
  getReport: (sessionId: string) =>
    call<AssessmentReport>(`/api/v1/sessions/${sessionId}/report`),

  // Learner profile
  getLearnerProfile: (studentId: string) =>
    call<LearnerProfile>(`/api/v1/learner-profile/${studentId}`),
  patchLearnerProfile: (
    studentId: string,
    patch: { defaultLevel?: string; defaultLanguage?: string },
  ) =>
    call<LearnerProfile>(`/api/v1/learner-profile/${studentId}`, {
      method: "PATCH",
      json: patch,
    }),

  // Learning paths
  createLearningPath: (studentId: string, broadTopic: string) =>
    call<LearningPath>(`/api/v1/learning-paths`, {
      method: "POST",
      json: { studentId, broadTopic },
    }),
  getLearningPath: (id: string) =>
    call<LearningPath>(`/api/v1/learning-paths/${id}`),

  // Deep Dive / Related Concepts
  generateNextSegment: (
    sessionId: string,
    currentSegmentId: string,
    selectedConcept?: string,
  ) =>
    call<any>(`/api/v1/sessions/${sessionId}/next-segment`, {
      method: "POST",
      json: {
        current_segment_id: currentSegmentId,
        selected_concept: selectedConcept ?? null,
      },
    }),
  getRelatedConcepts: (sessionId: string, segmentId: string) =>
    call<{
      related: Array<{
        concept: string;
        brief: string;
        prerequisite: boolean;
        difficulty: string;
      }>;
    }>(`/api/v1/sessions/${sessionId}/segments/${segmentId}/related-concepts`),
};
