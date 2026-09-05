/**
 * Stage + agent metadata for the /how-it-works demo.
 * Grounded in apps/api/orchestrator/execution_plan.py and agent docstrings.
 */

export type StageId =
  | "ingest"
  | "plan"
  | "personalize"
  | "produce"
  | "teach"
  | "adapt";

export interface AgentNode {
  id: string;
  label: string;
  responsibility: string;
  inputs: string[];
  outputs: string[];
  stageIds: StageId[];
}

export interface ThinkingLog {
  agent: string;
  message: string;
  delayMs: number;
}

export interface FlowStage {
  id: StageId;
  number: number;
  title: string;
  subtitle: string;
  studentSees: string;
  backendDoes: string;
  diagramNodes: { id: string; label: string; detail: string }[];
  thinking: ThinkingLog[];
}

export const STAGES: FlowStage[] = [
  {
    id: "ingest",
    number: 1,
    title: "Ingest",
    subtitle: "PDF becomes structured knowledge",
    studentSees: "Upload a textbook PDF, notes, or syllabus — or just type a topic.",
    backendDoes:
      "Content Ingestion parses pages, chunks text, embeds vectors into pgvector, and extracts headings, sections, and formulas so the curriculum mirrors the document’s own structure.",
    diagramNodes: [
      { id: "pdf", label: "PDF Upload", detail: "storage_path + file_type" },
      { id: "parse", label: "Parse Pages", detail: "pdf_parsing / docx / pptx" },
      { id: "chunk", label: "Chunk + Embed", detail: "chunking_embedding → document_chunks" },
      { id: "struct", label: "Structure Extract", detail: "headings · sections · formulas" },
    ],
    thinking: [
      { agent: "content_ingestion", message: "Opened NCERT Chemistry Ch.1 — 24 pages detected", delayMs: 0 },
      { agent: "content_ingestion", message: "Chunked into 47 semantic blocks with section labels", delayMs: 600 },
      { agent: "content_ingestion", message: "Embedded chunks → pgvector (document_chunks)", delayMs: 1200 },
      { agent: "content_ingestion", message: "Structure: 5 sections, 8 formulas, 3 worked examples", delayMs: 1800 },
      { agent: "orchestrator", message: "Status → ready · duration_ms: 1840", delayMs: 2400 },
    ],
  },
  {
    id: "plan",
    number: 2,
    title: "Plan",
    subtitle: "Curriculum from document structure",
    studentSees: "A 3–6 segment lesson outline tailored to the chapter — not a generic dump.",
    backendDoes:
      "Knowledge Retrieval pulls relevant chunks; Lesson Planning builds a curriculum from pdf_structure (or topic), producing ordered segments with depth, visual type, and checkpoint flags.",
    diagramNodes: [
      { id: "retrieve", label: "Knowledge Retrieval", detail: "semantic search over chunks" },
      { id: "lp", label: "Lesson Planning", detail: "3–6 segments from structure" },
      { id: "seg", label: "Segments", detail: "concept · depth · checkpoint?" },
      { id: "curr", label: "Curriculum Graph", detail: "prerequisites + sequence" },
    ],
    thinking: [
      { agent: "knowledge_retrieval", message: "Query: chemical reactions & balancing", delayMs: 0 },
      { agent: "knowledge_retrieval", message: "Retrieved 12 grounded chunks (document_id scoped)", delayMs: 700 },
      { agent: "lesson_planning", message: "Building plan from 5 PDF sections…", delayMs: 1400 },
      { agent: "lesson_planning", message: "Segment 1: What is a chemical reaction?", delayMs: 2000 },
      { agent: "lesson_planning", message: "Segment 2: Balancing equations · has_checkpoint=true", delayMs: 2600 },
      { agent: "lesson_planning", message: "Plan ready: 5 segments · language=en · level=beginner", delayMs: 3200 },
    ],
  },
  {
    id: "personalize",
    number: 3,
    title: "Personalize",
    subtitle: "Prior weakness shapes this lesson",
    studentSees: "Choose level, language, and time budget — the lesson adapts around you.",
    backendDoes:
      "Learner Profile injects prior weak_concepts; Personalization rewrites segment depths and prepends remediation; Time Budgeting truncates to fit minutes; Language rewrites if needed.",
    diagramNodes: [
      { id: "profile", label: "Learner Profile", detail: "weak / strong concepts" },
      { id: "pers", label: "Personalization", detail: "depth + remediation segments" },
      { id: "time", label: "Time Budgeting", detail: "fit to N minutes" },
      { id: "lang", label: "Language", detail: "optional non-English rewrite" },
    ],
    thinking: [
      { agent: "learner_profile", message: "Loaded profile: weak=[physical vs chemical change]", delayMs: 0 },
      { agent: "personalization", message: "Prepending remediation: Recap: physical vs chemical change", delayMs: 800 },
      { agent: "personalization", message: "Normalized all segment depths → beginner", delayMs: 1400 },
      { agent: "time_budgeting", message: "Budget 15 min → kept 4 of 6 segments", delayMs: 2100 },
      { agent: "orchestrator", message: "Personalized plan locked for session", delayMs: 2700 },
    ],
  },
  {
    id: "produce",
    number: 4,
    title: "Produce",
    subtitle: "Deterministic visuals, not hallucinations",
    studentSees: "An animated lesson with chalkboard derivations, accurate diagrams, and a teacher avatar.",
    backendDoes:
      "Per segment: Explanation scripts narration; Scene Planning decomposes into scenes; Visual Selection routes to RDKit / IEC circuits / biology / math / Motion Canvas; QA Grounding Guard checks textbook fidelity; FFmpeg composites.",
    diagramNodes: [
      { id: "expl", label: "Explanation", detail: "narration scripts" },
      { id: "scene", label: "Scene Planning", detail: "2–5 scenes / segment" },
      { id: "router", label: "Visual Router", detail: "RDKit · circuits · Motion" },
      { id: "comp", label: "Composite", detail: "voice + avatar + FFmpeg" },
    ],
    thinking: [
      { agent: "explanation", message: "Scripted Seg 2: conservation of mass intuition", delayMs: 0 },
      { agent: "scene_planning", message: "3 scenes: unbalanced → coefficients → verify atoms", delayMs: 800 },
      { agent: "visual_selection", message: "Route: chemistry_kit (RDKit molecules)", delayMs: 1500 },
      { agent: "qa_grounding_guard", message: "Grounding check PASSED against source chunks", delayMs: 2200 },
      { agent: "video_compositing", message: "Rendered 42s H.264 · perfect A/V sync", delayMs: 2900 },
    ],
  },
  {
    id: "teach",
    number: 5,
    title: "Teach",
    subtitle: "Socratic checkpoints mid-lesson",
    studentSees: "Video pauses with conceptual MCQs. Wrong answers trigger a fresh explanation — not a scold.",
    backendDoes:
      "Interaction Agent generates diagnostic checkpoints; Answer Evaluation scores; Misconception Detection picks a reteach strategy from the attempt ladder and produces a new analogy.",
    diagramNodes: [
      { id: "play", label: "Interactive Player", detail: "segments + timeline" },
      { id: "cp", label: "Checkpoint", detail: "MCQ with distractors" },
      { id: "eval", label: "Evaluate Answer", detail: "correct / misconception" },
      { id: "reteach", label: "Reteach Ladder", detail: "simplify → example → atomic" },
    ],
    thinking: [
      { agent: "interaction", message: "Checkpoint: Why did the solution turn cloudy?", delayMs: 0 },
      { agent: "answer_evaluation", message: "Student chose: Temperature increased — INCORRECT", delayMs: 900 },
      { agent: "misconception_detection", message: "Diagnosed: confusing physical vs chemical change", delayMs: 1600 },
      { agent: "misconception_detection", message: "Strategy attempt#1 → simplify (zero jargon)", delayMs: 2300 },
      { agent: "misconception_detection", message: "Injecting 30s remediation scene + new analogy", delayMs: 3000 },
    ],
  },
  {
    id: "adapt",
    number: 6,
    title: "Adapt",
    subtitle: "The system learns the student",
    studentSees: "End-of-lesson report: strong areas, weak areas, and what to practice next.",
    backendDoes:
      "Assessment writes the report; Learner Profile merges strong/weak concepts and updates average_score; next session’s Personalization agent reads those weak concepts and remediates first.",
    diagramNodes: [
      { id: "assess", label: "Assessment", detail: "score + area bands" },
      { id: "mastery", label: "Concept Mastery", detail: "strong / weak status" },
      { id: "writeback", label: "Profile Writeback", detail: "learner_profiles upsert" },
      { id: "next", label: "Smarter Next Lesson", detail: "remediation on entry" },
    ],
    thinking: [
      { agent: "assessment", message: "Score 72% · strong=[balancing] · weak=[phys vs chem]", delayMs: 0 },
      { agent: "learner_profile", message: "Merging weak_concepts += physical vs chemical change", delayMs: 800 },
      { agent: "learner_profile", message: "average_score updated → 0.74", delayMs: 1500 },
      { agent: "orchestrator", message: "Session closed · learning path hint queued", delayMs: 2200 },
      { agent: "personalization", message: "Next session will open with Recap: phys vs chem", delayMs: 2900 },
    ],
  },
];

export const AGENTS: AgentNode[] = [
  {
    id: "content_ingestion",
    label: "Content Ingestion",
    responsibility:
      "Parse uploaded PDF/DOCX/PPTX, chunk pages, embed vectors, and extract PDF structure (headings, sections, formulas).",
    inputs: ["document_id", "storage_path", "file_type"],
    outputs: ["chunk_count", "page_count", "pdf_structure", "status=ready"],
    stageIds: ["ingest"],
  },
  {
    id: "knowledge_retrieval",
    label: "Knowledge Retrieval",
    responsibility:
      "Semantic search over document_chunks (pgvector) scoped to the student’s document or topic query.",
    inputs: ["query", "document_id?"],
    outputs: ["retrieved_chunks[]"],
    stageIds: ["plan"],
  },
  {
    id: "lesson_planning",
    label: "Lesson Planning",
    responsibility:
      "Build a 3–6 segment curriculum from topic + pdf_structure, with depth, visual_type, and checkpoint flags.",
    inputs: ["topic", "level", "time_budget", "pdf_structure", "weak_concepts"],
    outputs: ["plan.segments[]"],
    stageIds: ["plan"],
  },
  {
    id: "personalization",
    label: "Personalization",
    responsibility:
      "Rewrite segment depths to student level; prepend up to 2 remediation segments for prior weak concepts.",
    inputs: ["plan", "level", "weak_concepts"],
    outputs: ["personalized plan"],
    stageIds: ["personalize"],
  },
  {
    id: "time_budgeting",
    label: "Time Budgeting",
    responsibility: "Truncate or compress segments so the lesson fits the student’s time budget.",
    inputs: ["plan", "time_budget_minutes"],
    outputs: ["budgeted plan"],
    stageIds: ["personalize"],
  },
  {
    id: "visual_selection",
    label: "Visual Selection",
    responsibility:
      "Route each segment to the right deterministic visual kit (chemistry, physics, biology, math, Motion Canvas).",
    inputs: ["segments"],
    outputs: ["visual_type per segment"],
    stageIds: ["produce"],
  },
  {
    id: "explanation",
    label: "Explanation",
    responsibility: "Write narration scripts grounded in retrieved chunks for each segment.",
    inputs: ["segment", "chunks"],
    outputs: ["narration_script"],
    stageIds: ["produce"],
  },
  {
    id: "scene_planning",
    label: "Scene Planning",
    responsibility: "Decompose a segment into 2–5 timed scenes with learning objectives and visual specs.",
    inputs: ["segment", "narration"],
    outputs: ["scenes[]"],
    stageIds: ["produce"],
  },
  {
    id: "qa_grounding_guard",
    label: "QA Grounding Guard",
    responsibility: "Validate that generated content stays faithful to the source document chunks.",
    inputs: ["segment content", "source chunks"],
    outputs: ["pass / repair"],
    stageIds: ["produce"],
  },
  {
    id: "interaction",
    label: "Interaction",
    responsibility: "Generate mid-lesson MCQ checkpoints with diagnostic distractors.",
    inputs: ["segment concept"],
    outputs: ["question_checkpoint"],
    stageIds: ["teach"],
  },
  {
    id: "misconception_detection",
    label: "Misconception Detection",
    responsibility:
      "On wrong answers, diagnose the misconception and escalate: simplify → concrete_example → atomic_steps.",
    inputs: ["student_answer", "attempt_number", "prior_analogies"],
    outputs: ["ReteachContent"],
    stageIds: ["teach", "adapt"],
  },
  {
    id: "assessment",
    label: "Assessment",
    responsibility: "Produce end-of-session report with score, strong areas, and weak areas.",
    inputs: ["session checkpoints"],
    outputs: ["assessment_report"],
    stageIds: ["adapt"],
  },
  {
    id: "learner_profile",
    label: "Learner Profile",
    responsibility:
      "Read weak/strong concepts at session start; write them back at session end so the next lesson remediates first.",
    inputs: ["student_id", "report"],
    outputs: ["learner_profiles row"],
    stageIds: ["personalize", "adapt"],
  },
];

/** DAG edges matching execution_plan.py order */
export const DAG_EDGES: [string, string][] = [
  ["content_ingestion", "knowledge_retrieval"],
  ["knowledge_retrieval", "lesson_planning"],
  ["lesson_planning", "personalization"],
  ["personalization", "time_budgeting"],
  ["time_budgeting", "visual_selection"],
  ["visual_selection", "explanation"],
  ["explanation", "scene_planning"],
  ["scene_planning", "qa_grounding_guard"],
  ["qa_grounding_guard", "interaction"],
  ["interaction", "misconception_detection"],
  ["misconception_detection", "assessment"],
  ["assessment", "learner_profile"],
];

export const STAGE_DURATION_MS = 5000;

export function stageIndex(id: StageId): number {
  return STAGES.findIndex((s) => s.id === id);
}
