# Shikshak AI — Visual Architecture & System Guide

> **A comprehensive, visual, and architectural guide to how Shikshak AI transforms topics and textbook documents into interactive, animated, and Socratic video lessons.**

![Shikshak AI Architecture Overview](./docs/assets/shikshak_architecture_overview.jpg)

---

## 1. Executive Mental Model (The 30-Second Overview)

Traditional "AI video" platforms use generative video diffusion models (e.g., Sora, Runway, Kling). While visually impressive, generative models suffer from **five fundamental pedagogical failures**:
1. **Scientific Hallucination:** Chemical bonds, circuit symbols, and mathematical steps are distorted or physically impossible.
2. **Text Illegibility:** On-screen text warps, blends, or becomes unreadable gibberish.
3. **Audio-Visual Drift:** The voice narration describes concept $A$ while the video depicts concept $B$.
4. **Massive Latency & Cost:** Rendering a 3-minute video takes 3–10 minutes of GPU cluster compute.
5. **Zero Interactivity:** The output is a static video file with no way to pause for quizzes or remediate misconceptions.

**Shikshak AI solves this with a Scene-First, Deterministic Multi-Agent Architecture:**

```
┌─────────────────────────────────────────────────────────────────────────────────────────────┐
│                                   THE SHIKSHAK TRIAD                                        │
├───────────────────────────────┬───────────────────────────────┬─────────────────────────────┤
│   1. MULTI-AGENT REASONING    │  2. DETERMINISTIC RENDERING   │   3. SOCRATIC INTERACTION   │
│                               │                               │                             │
│ • Breaks curricula into       │ • Zero LLM calls at render    │ • Interactive video player  │
│   pedagogical segments        │ • Algorithmic DAG layout      │ • Mid-lesson checkpoints    │
│ • Generates simultaneous      │ • Textbook-grade science kits │ • Misconception detection   │
│   Narration + Diagram specs   │   (RDKit, IEC circuits, Bio)  │ • On-the-fly remediation    │
│ • Enforces strict schema gates│ • 1280x720 HD @ 24fps in <2s  │   segment splicing          │
└───────────────────────────────┴───────────────────────────────┴─────────────────────────────┘
```

---

## 2. Complete End-to-End System Architecture

The following diagram details how data flows across all 7 layers of Shikshak AI — from student input to video playback:

```mermaid
graph TD
    classDef client fill:#38bdf8,stroke:#0284c7,stroke-width:2px,color:#0f172a;
    classDef gateway fill:#818cf8,stroke:#4f46e5,stroke-width:2px,color:#ffffff;
    classDef agent fill:#34d399,stroke:#059669,stroke-width:2px,color:#0f172a;
    classDef llm fill:#a78bfa,stroke:#7c3aed,stroke-width:2px,color:#ffffff;
    classDef render fill:#fbbf24,stroke:#d97706,stroke-width:2px,color:#0f172a;
    classDef engine fill:#f97316,stroke:#ea580c,stroke-width:2px,color:#ffffff;
    classDef storage fill:#f472b6,stroke:#db2777,stroke-width:2px,color:#0f172a;

    subgraph LAYER1 ["1. CLIENT EXPERIENCE (Next.js 14 App Router)"]
        UI_Input["Student Input<br/>(Topic / PDF Upload)"]:::client
        UI_Player["Interactive Lesson Player<br/>(Synced Video + Captions)"]:::client
        UI_Quiz["Socratic Checkpoint Modal<br/>(MCQ / Diagnostic Distractors)"]:::client
        UI_Graph["Concept Deep-Dive Graph<br/>(Curriculum Exploration)"]:::client
    end

    subgraph LAYER2 ["2. GATEWAY & ORCHESTRATION (FastAPI & Celery)"]
        API["FastAPI Gateway<br/>/api/v1/sessions"]:::gateway
        Router["DAG Orchestration Router<br/>orchestrator/router.py"]:::gateway
        CeleryWorker["Async Worker Queue<br/>(Celery + Redis)"]:::gateway
    end

    subgraph LAYER3 ["3. MULTI-AGENT INTELLIGENCE PIPELINE"]
        AG_Ingest["Content Ingestion<br/>(PDF Structure & Chunking)"]:::agent
        AG_Retrieve["Knowledge Retrieval<br/>(Per-concept Vector Search)"]:::agent
        AG_Plan["Lesson Planning<br/>(Segment Breakdown & Remediation)"]:::agent
        AG_Pers["Personalization & Profile<br/>(Difficulty & Pace Adaptation)"]:::agent
        AG_Time["Time Budgeting<br/>(Word counts & Durations)"]:::agent
        AG_Visual["Visual Selection<br/>(Diagram / Chemistry / Circuit)"]:::agent
        AG_Explain["Content Scriptwriter<br/>(Unified ContentBlueprint)"]:::agent
        AG_Scene["Scene Planning Agent<br/>(3-5 Visual Scenes per Segment)"]:::agent
        AG_Quality["Quality Gate Skill<br/>(Auto-repair & Schema Check)"]:::agent
        AG_QA["QA Grounding Guard<br/>(Factual Verification vs Source)"]:::agent
        AG_Interact["Interaction Agent<br/>(Diagnostic Checkpoints)"]:::agent
    end

    subgraph LAYER4 ["4. DUAL-LLM ROUTING SHIELD"]
        Groq["Groq Cloud Llama-3.3-70B<br/>⚡ 300+ tok/s (Primary Content & Schema)"]:::llm
        Gemini["Google Gemini Flash<br/>🎨 Creative Visual Fallback & High Quota"]:::llm
        FallbackShield["Adaptive Routing Shield<br/>(Auto-retry, Rate-limit failover)"]:::llm
    end

    subgraph LAYER5 ["5. SCIENCE VISUAL KITS & DETERMINISTIC LAYOUT"]
        LayoutEngine["NetworkX Sugiyama DAG Layout<br/>(Collision-free Coordinates)"]:::engine
        FontEngine["Pillow Font Measurement<br/>(Guaranteed No Text Truncation)"]:::engine
        RDKit["RDKit Chemistry Kit<br/>(2D Molecules + Bond Glow)"]:::engine
        CircuitKit["IEC 60617 Circuit Kit<br/>(Textbook Physics Schematics)"]:::engine
        BioKit["BioIcons Biology Kit<br/>(Cellular & Organ Diagrams)"]:::engine
    end

    subgraph LAYER6 ["6. THREE-TRACK DETERMINISTIC MEDIA SYNTHESIS"]
        TTS["Track 1: Audio Track<br/>(Microsoft Edge-TTS / XTTS-v2)"]:::render
        Cairo["Track 2: Visual Frames<br/>(CairoSVG Renderer @ 24fps)"]:::render
        Avatar["Track 3: Presenter Rail<br/>(Teacher Talking Head Video)"]:::render
        FFmpeg["Compositor Engine<br/>(FFmpeg H.264 + FastStart MP4)"]:::render
    end

    subgraph LAYER7 ["7. PERSISTENCE & DATA LAYER (Supabase)"]
        DB_Sessions[("sessions<br/>(Topic, Student ID, Status)")]:::storage
        DB_Segments[("lesson_segments<br/>(Blueprint, Narration, Video URL)")]:::storage
        DB_Scenes[("scenes<br/>(Visual Mode, Payload, Timing)")]:::storage
        DB_Checkpoints[("question_checkpoints<br/>(Distractors, Misconceptions)")]:::storage
    end

    %% Flow Connections
    UI_Input -->|"1. Submit topic/PDF"| API
    API -->|"2. Initialize Session"| Router
    Router -->|"3. Build Execution DAG"| CeleryWorker

    CeleryWorker --> AG_Ingest
    AG_Ingest --> AG_Retrieve
    AG_Retrieve --> AG_Plan
    AG_Plan --> AG_Pers
    AG_Pers --> AG_Time
    AG_Time --> AG_Visual
    AG_Visual --> AG_Explain
    AG_Explain --> AG_Scene
    AG_Scene --> AG_Quality
    AG_Quality --> AG_QA
    AG_QA --> AG_Interact

    AG_Plan <--> FallbackShield
    AG_Explain <--> FallbackShield
    AG_Scene <--> FallbackShield
    FallbackShield --> Groq
    FallbackShield -.->|Quota/Error Fallback| Gemini

    AG_Interact -->|"Save Lesson Structure"| DB_Segments
    AG_Interact -->|"Save Scenes"| DB_Scenes
    AG_Interact -->|"Save Checkpoints"| DB_Checkpoints

    API -->|"4. Trigger Segment Render"| TTS
    API -->|"4. Trigger Visual Layout"| LayoutEngine

    LayoutEngine --> FontEngine
    FontEngine --> Cairo
    RDKit -.-> Cairo
    CircuitKit -.-> Cairo
    BioKit -.-> Cairo

    TTS -->|"Audio (.wav)"| FFmpeg
    Cairo -->|"Visual Frames (.png)"| FFmpeg
    Avatar -->|"Presenter Video (.mp4)"| FFmpeg

    FFmpeg -->|"5. Final Lesson Video (.mp4)"| DB_Segments
    DB_Segments -->|"6. Stream to Player"| UI_Player
    DB_Checkpoints -->|"7. Trigger Checkpoint Pause"| UI_Quiz
    UI_Quiz -->|"8. Wrong Answer: Trigger Reteach"| Router
```

---

## 3. The End-to-End Life of a Lesson (Step-by-Step)

Here is exactly what happens when a student requests a lesson on **"Photosynthesis and Cellular Respiration"**:

```
[ PHASE 1: INGESTION & CURRICULUM PLANNING ]
  1. Student enters "Photosynthesis" or uploads an NCERT Biology chapter PDF.
  2. Content Ingestion Agent parses the document structure (sections, headings, formulas).
  3. Lesson Planning Agent reads the student's learning profile (prior weak concepts, level).
  4. Output: A 3-segment lesson plan:
       • Segment 1: Light Reactions (Visual: Chloroplast Flowchart)
       • Segment 2: The Calvin Cycle (Visual: Cycle Diagram + Checkpoint Quiz)
       • Segment 3: ATP Synthesis (Visual: Molecular/Energy Diagram)

[ PHASE 2: UNIFIED CONTENT SCRIPTWRITING (Groq Llama-3.3-70B) ]
  5. For each segment, the Content Scriptwriter generates a SINGLE `ContentBlueprint`:
     ┌─────────────────────────────────────────────────────────────────────────────┐
     │ Narration: "Inside the thylakoid membrane, sunlight energizes chlorophyll   │
     │            electrons, splitting water into oxygen and hydrogen ions..."     │
     ├─────────────────────────────────────────────────────────────────────────────┤
     │ Diagram Spec:                                                               │
     │   • Nodes: [Sunlight, Chlorophyll, Water, Oxygen, H+ Ions, ATP]             │
     │   • Edges: Sunlight -> Chlorophyll -> Water -> [Oxygen + H+ Ions] -> ATP    │
     │   • Layout: "flowchart" | Color Tokens: locked textbook palette             │
     └─────────────────────────────────────────────────────────────────────────────┘

[ PHASE 3: SCENE PLANNING & QUALITY GATE AUDIT ]
  6. Scene Planning Agent decomposes the segment into 3-4 granular visual scenes:
       • Scene 1: Sunlight photons striking the chlorophyll complex.
       • Scene 2: Water molecule splitting ($2H_2O \rightarrow 4H^+ + O_2 + 4e^-$).
       • Scene 3: Proton gradient driving ATP synthase.
  7. Quality Gate Skill audits the scene payload:
       • Validates JSON schemas and visual modes.
       • Checks on-screen text length (<= 28 chars per label) to avoid clipping.
       • Ensures mathematical/chemical equations are formatted correctly.

[ PHASE 4: DETERMINISTIC 3-TRACK MEDIA SYNTHESIS (Zero Render-Time LLM Calls) ]
  8. Audio Track: Microsoft Edge-TTS synthesizes natural teacher voice in parallel.
  9. Visual Track:
       • NetworkX computes Sugiyama-layered DAG coordinates for all nodes.
       • Pillow measures pixel length of every label for precise container padding.
       • CairoSVG renders 24 frames/sec with smooth opacity fades and active node pulses.
 10. Presenter Track: Teacher avatar rail is generated or pulled from cached profile assets.
 11. Assembly: FFmpeg composites all three tracks into a 1280x720 HD MP4 with `+faststart`.

[ PHASE 5: PLAYBACK & THE SOCRATIC INTERACTION LOOP ]
 12. Student watches Segment 1; video smoothly transitions into Segment 2.
 13. At 01:45, the video pauses: Checkpoint question appears on screen.
 14. If Student answers correctly: Celebratory feedback plays, and Segment 3 resumes.
 15. If Student picks a diagnostic distractor:
       • Misconception Detection Agent identifies the exact confusion.
       • Orchestrator generates a targeted 30-second remediation segment with a fresh analogy.
       • The remediation segment is spliced directly into the video playlist dynamically!
```

---

## 4. Multi-Agent Directory & Responsibilities Matrix

The orchestrator coordinates 12 specialized agents and skills across the session lifecycle:

| Agent / Skill | Responsibility | Primary Input | Output | Primary Model / Engine |
| :--- | :--- | :--- | :--- | :--- |
| **Content Ingestion** | Extracts hierarchical sections, tables, and text from PDFs/DOCXs | Raw PDF / PPTX file | Document chunk hierarchy | PyPDF / pdfplumber |
| **Knowledge Retrieval** | Semantic retrieval of top-$k$ relevant source chunks per concept | Concept name + Document ID | Grounding text chunks | pgvector / embeddings |
| **Lesson Planning** | Builds pedagogical segment curriculum tailored to student level | Topic + Weak concepts | Ordered segment list | Groq Llama-3.3-70B |
| **Personalization** | Adjusts terminology depth, pacing, and real-world analogies | Learner profile + Plan | Personalized segment spec | Groq Llama-3.3-70B |
| **Time Budgeting** | Allocates exact duration and target word counts to each segment | Session budget (e.g. 5 min) | Per-segment word & second budgets | Deterministic Math |
| **Visual Selection** | Chooses optimal visual presentation mode for each concept | Segment concept & domain | Visual mode tag (circuit, bio, etc.) | Rule-based / Groq |
| **Content Scriptwriter** | Simultaneously outputs spoken narration and diagram graph spec | Grounding chunks + Concept | `ContentBlueprint` (Audio + Visual) | Groq Llama-3.3-70B |
| **Scene Planning** | Decomposes segments into 3–5 timed visual scenes | Narration script + Visual mode | Ordered `ScenePlanRaw` list | Groq Llama-3.3-70B |
| **Quality Gate** | Validates scene payloads, sanitizes text lengths, auto-repairs | Scene plans | Validated & repaired scenes | Pure Python Rule Engine |
| **QA Grounding Guard** | Verifies narration facts against source chunks to prevent hallucination | Narration + Source text | Audited & verified narration | Groq / Gemini Flash |
| **Interaction Agent** | Generates conceptual checkpoint questions with diagnostic distractors | Segment concept + Depth | Checkpoint MCQ + Explanations | Groq Llama-3.3-70B |
| **Misconception Detection** | Diagnoses student errors and drafts remediation scripts | Student wrong answer + Target | Remediation script + Analogy | Groq Llama-3.3-70B |

---

## 5. Scene-First Video Generation & Rendering Architecture

Shikshak AI implements a **Scene-First Deterministic Video Pipeline**. Rather than generating a single monolithic diagram or relying on generative AI video APIs (which hallucinate formulas, drift out of sync, and take minutes to render), the system decomposes each lesson segment into **discrete, timed pedagogical scenes** rendered by specialized deterministic vector engines and motion templates, then stitched into a final stream via FFmpeg.

### High-Level Video Generation Architecture

```
                                 SHIKSHAK
                                    │
                              Lesson Planner
                                    │
                             ContentBlueprint
                                    │
                              Semantic Scene
                                    │
                               Quality Gate
                                    │
                              Motion Director
                           (Flick Scene Planner)
                                    │
                          Visual Renderer Router
                                    │
        ┌──────────────┬────────────┼────────────┬──────────────┬──────────────┐
        │              │            │            │              │              │
        ▼              ▼            ▼            ▼              ▼              ▼
    Chemistry       Physics      Biology        Math          Motion        Generic
    Renderer       Renderer     Renderer      Renderer       Renderer       Fallback
        │              │            │            │              │              │
      RDKit        IEC 60617    BioIcons    LaTeX/Algebra     Flick         CairoSVG
   Reaction Lab     Circuits    Cellular     Number Line     Remotion      Explainer
        │              │            │            │              │              │
        └──────────────┴────────────┼────────────┴──────────────┴──────────────┘
                                    │
                                    ▼
                              Scene Timeline
                         (Per-Scene 1280x720 MP4s)
                                    │
                                    ▼
                               Composition
                        (Scene Video + Audio + PIP)
                                    │
                                    ▼
                                  FFmpeg
                                    │
                                    ▼
                              Final Video
```

### Detailed Video Generation Pipeline Flowchart

```mermaid
flowchart TD
    classDef input fill:#f8fafc,stroke:#64748b,stroke-width:2px,color:#0f172a;
    classDef agent fill:#6366f1,stroke:#4f46e5,stroke-width:2px,color:#ffffff;
    classDef gate fill:#f59e0b,stroke:#d97706,stroke-width:2px,color:#ffffff;
    classDef router fill:#0284c7,stroke:#0369a1,stroke-width:2px,color:#ffffff;
    classDef engine fill:#0ea5e9,stroke:#0284c7,stroke-width:2px,color:#ffffff;
    classDef flick fill:#ec4899,stroke:#db2777,stroke-width:2px,color:#ffffff;
    classDef comp fill:#10b981,stroke:#059669,stroke-width:2px,color:#ffffff;
    classDef output fill:#8b5cf6,stroke:#7c3aed,stroke-width:2px,color:#ffffff;

    subgraph PLANNING["1. AI Motion Planning & Quality Gate"]
        Blueprint["ContentBlueprint<br/>(Narration Script + Concept Depth)"]:::input --> ScenePlanner["Scene Planning Agent<br/>(Flick Universal AI Motion Director)"]:::agent
        ScenePlanner -->|"3 to 5 Discrete Scenes<br/>(Semantic Pydantic Schemas)"| QGate["Quality Gate<br/>(Schema Audit & Auto-Repair)"]:::gate
    end

    subgraph ROUTING["2. Deterministic Visual Routing"]
        QGate -->|"Audited Scene Plans"| CentralRouter{"Central Visual Router<br/>(router.py)"}:::router
    end

    subgraph RENDERING["3. Parallel Specialized Render Backends"]
        CentralRouter -->|"Chemistry Pack"| RDKitEng["RDKit & Reaction Lab<br/>(Precipitation, Beakers, Formulas)"]:::engine
        CentralRouter -->|"Physics Pack"| CircuitEng["IEC 60617 Circuits & Optics<br/>(Resistors, Rays, Mechanics)"]:::engine
        CentralRouter -->|"Biology Pack"| BioEng["BioIcons Cellular Engine<br/>(Organelles, Membranes, Anatomy)"]:::engine
        CentralRouter -->|"Mathematics Pack"| MathEng["Coordinate Geometry & LaTeX<br/>(Number Lines, Derivations)"]:::engine
        CentralRouter -->|"Motion Graphics Pack"| FlickEng["Flick Remotion Motion Engine<br/>(StepFlow, Title, Highlight, Timeline)"]:::flick
        CentralRouter -->|"Universal Fallback"| CairoEng["CairoSVG Generic Explainer<br/>(Vector Cards & Equations)"]:::engine

        FlickEng <-->|"SHA-256 Hash"| DiskCache[("Disk Cache<br/>/tmp/shikshak_cache/")]:::gate
    end

    subgraph COMPOSITING["4. Multi-Track Video Assembly & Stitching"]
        RDKitEng --> Collector["Scene Video Collector<br/>(1280x720 24fps H.264 MP4s)"]:::input
        CircuitEng --> Collector
        BioEng --> Collector
        MathEng --> Collector
        FlickEng --> Collector
        CairoEng --> Collector

        Collector --> ConcatScenes["concat_segments()<br/>(Concatenates Scene MP4s)"]:::comp

        AudioTTS["Edge-TTS Synthesis<br/>(High-fidelity Voice Track)"]:::engine --> Compositor["FFmpeg Compositor<br/>(stitch_segment)"]:::comp
        TeacherAvatar["Teacher Avatar Track<br/>(Speaking PIP Overlay)"]:::input --> Compositor
        ConcatScenes --> Compositor

        Compositor --> FinalMP4["Final Lesson Segment Video<br/>(1280x720 H.264 MP4 Stream)"]:::output
    end
```

---

### Architectural Tenet: The Coordinate Invariant
> [!IMPORTANT]
> **No LLM in Shikshak AI is ever allowed to output `x`, `y`, `width`, or `height` coordinates, CSS styles, or arbitrary React/Canvas code.**
> The LLM provides high-level semantic intent via `AnimationSceneSpec` (`SemanticObject`, `SemanticBeat`, `SemanticCameraKeyframe`). The rendering engines algorithmically calculate layout geometry based on true domain topology, font metrics, and kinetic camera choreography.

```
OLD WAY (Flawed):
LLM ──(hallucinates)──► [Node A: x=120, y=340] + [Node B: x=140, y=350] ──► Overlapping Boxes & Cutoff Text!

SHIKSHAK WAY (Deterministic):
LLM ──(semantic intent only)──► AnimationSceneSpec { objects: [...], beats: [...], camera: [...] }
                                            │
                                            ▼
                                [ Central Visual Router ]
                                Resolves visual_mode to Motion Canvas / Scientific Adapters
                                            │
                                            ▼
                           [ Headless Motion Canvas Engine ]
                           Deterministic 1280x720 HD @ 30fps streaming directly to FFmpeg
```

---

### The Science & Motion Visual Kits

For domain-specific concepts, the visual pipeline routes to dedicated vector rendering engines, Motion Canvas adapters, and legacy Remotion fallback templates:

```mermaid
graph LR
    classDef kit fill:#0ea5e9,stroke:#0284c7,stroke-width:2px,color:#ffffff;
    classDef motion fill:#ec4899,stroke:#db2777,stroke-width:2px,color:#ffffff;
    classDef core fill:#6366f1,stroke:#4f46e5,stroke-width:2px,color:#ffffff;

    VSelection["Central Visual Router<br/>(router.py)"]:::core

    VSelection -->|"Chemistry"| KitChem["Molecular Structure Kit<br/>(Motion Canvas + RDKit 2D)"]:::kit
    VSelection -->|"Physics"| KitPhys["Circuit Symbol Kit<br/>(Motion Canvas + IEC 60617)"]:::kit
    VSelection -->|"Biology"| KitBio["BioIcons Illustration Kit<br/>(Motion Canvas + BioIcons)"]:::kit
    VSelection -->|"Mathematics"| KitMath["Math Diagram Engine<br/>(Motion Canvas + LaTeX Solvers)"]:::kit
    VSelection -->|"Primary Motion"| KitMC["Motion Canvas Engine<br/>(Headless 30fps Canvas + Camera)"]:::motion
    VSelection -->|"Legacy Fallback"| KitFlick["Flick Remotion Engine<br/>(7 Reusable Pedagogical Templates)"]:::motion
```

1. **Molecular Structure Kit (Chemistry):** Uses **Motion Canvas** and **RDKit** for equation balancing ($Fe + H_2O \to Fe_3O_4 + H_2$), atom inventory verification (strictly NO seesaw / balance scale metaphors), and reaction kinetics.
2. **Circuit Symbol Kit (Physics):** Uses **Motion Canvas** with **IEC 60617** vector symbols, animated switch closure, directional electron drift, and resistor voltage drop.
3. **BioIcons Kit (Biology):** Realizes cellular processes (photosynthesis thylakoid light reactions, photolysis, proton gradients, and ATP synthase rotor dynamics).
4. **Math Diagram Engine (Mathematics):** Realizes step-by-step algebraic equation transformations and quadratic formula derivations with term continuity.
5. **Motion Canvas Core Engine (Primary Educational Motion):** Headless 30fps canvas rendering pipeline with semantic camera choreography (`establish`, `focus`, `pullback`) streaming frame buffers to FFmpeg with SHA-256 caching.
6. **MuseTalk v1.5 Apple Silicon Presenter:** Fast local talking-head generation running on Metal Performance Shaders (MPS) with female educator profile (`female_teacher_v1`). Composited dynamically (`TEACHER_EXPLAIN` PIP, `TEACHER_INTRO`, `TEACHER_OFF_SCREEN`) replacing the fixed 300px sidebar.

---

## 6. The Dual-LLM Routing Shield

To prevent API rate limits (HTTP 429) from interrupting lessons, Shikshak AI operates a resilient routing shield:

```mermaid
flowchart TD
    classDef req fill:#f1f5f9,stroke:#94a3b8,stroke-width:2px,color:#0f172a;
    classDef groq fill:#f97316,stroke:#ea580c,stroke-width:2px,color:#ffffff;
    classDef gemini fill:#8b5cf6,stroke:#6d28d9,stroke-width:2px,color:#ffffff;
    classDef check fill:#38bdf8,stroke:#0284c7,stroke-width:2px,color:#0f172a;

    Task["Incoming Agent Task"]:::req --> Router{"Task Type?"}:::check

    Router -->|"Content / Logic / Schema"| GroqTry["Groq Cloud Llama-3.3-70B<br/>⚡ Blazing Fast (300+ tok/s)"]:::groq
    Router -->|"Visual Styling / Fallback"| GeminiTry["Google Gemini Flash<br/>🎨 High Quota & Creative Specs"]:::gemini

    GroqTry -->|"HTTP 429 or Timeout"| GeminiFallback["Failover to Gemini Flash"]:::gemini
    GeminiTry -->|"HTTP 429 or Timeout"| GroqFallback["Failover to Groq"]:::groq

    GroqTry -->|"Success"| Output["Validated Pydantic Contract"]:::req
    GeminiTry -->|"Success"| Output
    GeminiFallback --> Output
    GroqFallback --> Output
```

### Why This Dual Strategy Works:
- **Groq Llama-3.3-70B** provides near-instantaneous JSON schema responses (sub-second generation of complete blueprints).
- **Gemini Flash** acts as an expansive visual-reasoning fallback with generous rate limits.
- If either provider experiences downtime or regional rate caps, the orchestrator automatically swaps models transparently with zero disruption to the student.

---

## 7. The Socratic Feedback & Remediation Loop

When a student reaches an embedded question checkpoint, the player enters an interactive diagnostic mode:

```mermaid
sequenceDiagram
    autonumber
    actor Student
    participant Player as Next.js Video Player
    participant Gateway as FastAPI Gateway
    participant Evaluator as Answer Evaluation Agent
    participant Misconception as Misconception Agent
    participant Orchestrator as DAG Orchestrator
    participant Render as Media Render Engine

    Student->>Player: Watches lesson to checkpoint timestamp
    Player->>Player: Pauses video, presents interactive MCQ
    Student->>Player: Selects Option B (Diagnostic Distractor)
    Player->>Gateway: POST /api/v1/sessions/{id}/answer
    Gateway->>Evaluator: Check answer against correct rubric
    Evaluator-->>Gateway: Result: Incorrect (Distractor selected)
    Gateway->>Misconception: Diagnose underlying conceptual confusion
    Misconception-->>Gateway: Diagnosis: Confused ionic bonding with covalent sharing
    Gateway->>Orchestrator: Generate targeted Remediation Segment
    Orchestrator->>Render: Synthesize Voice + Diagram with fresh analogy
    Render-->>Gateway: Remediation MP4 ready
    Gateway-->>Player: Return diagnosis + remediation segment metadata
    Player->>Student: Play Socratic remediation segment
    Student->>Player: Retries checkpoint or continues lesson
```

---

## 8. Database Entity Relationship Model (Supabase)

The database schema is organized around the session hierarchy and pedagogical checkpoints:

```mermaid
erDiagram
    SESSIONS ||--o{ LESSON_SEGMENTS : "contains"
    LESSON_SEGMENTS ||--o{ SCENES : "decomposed into"
    LESSON_SEGMENTS ||--o| QUESTION_CHECKPOINTS : "has"
    STUDENTS ||--o{ SESSIONS : "learns via"
    STUDENTS ||--o{ LEARNER_PROFILES : "tracked by"

    SESSIONS {
        uuid id PK
        uuid student_id FK
        string topic
        string level
        string language
        string status
        int time_budget_minutes
    }

    LESSON_SEGMENTS {
        uuid id PK
        uuid session_id FK
        int segment_order
        string concept
        string depth
        string visual_type
        text narration_script
        jsonb diagram_spec_json
        string video_url
        string status
    }

    SCENES {
        uuid id PK
        uuid segment_id FK
        int scene_order
        string visual_mode
        jsonb visual_payload
        text narration_text
        string on_screen_equation
        string status
    }

    QUESTION_CHECKPOINTS {
        uuid id PK
        uuid segment_id FK
        text prompt
        jsonb options
        string correct_answer
        jsonb explanations
    }

    STUDENTS {
        uuid id PK
        string email
        string display_name
    }

    LEARNER_PROFILES {
        uuid student_id PK, FK
        jsonb weak_concepts
        string mastery_level
        jsonb learning_style
    }
```

---

## 9. Technology Stack & Directory Map

```
shikshak-ai/
├── apps/
│   ├── api/                          # FastAPI Backend & Orchestrator
│   │   ├── agents/                   # The 12 Autonomous Agents
│   │   │   ├── content_ingestion.py  # Document & PDF parsing
│   │   │   ├── lesson_planning.py    # Curriculum segmentation
│   │   │   ├── content_scriptwriter.py# Unified ContentBlueprint generator
│   │   │   ├── scene_planning.py     # Flick Universal AI Motion Director (multi-subject scene breakdown)
│   │   │   ├── visual_selection.py   # Subject & visual mode routing
│   │   │   ├── qa_grounding_guard.py # Grounding verification against source
│   │   │   └── interaction.py        # Checkpoint MCQ generation
│   │   ├── orchestrator/             # Execution Planning & Router
│   │   │   ├── router.py             # DAG pipeline runner
│   │   │   └── execution_plan.py     # Celery chain/group step builder
│   │   ├── skills/                   # Deterministic Engines & Utilities
│   │   │   ├── scene_renderers/      # Centralized Visual Router & Domain Backends
│   │   │   │   ├── router.py         # Deterministic visual_mode dispatch
│   │   │   │   ├── flick_renderer.py # Remotion engine wrapper with SHA-256 caching & CairoSVG fallback
│   │   │   │   ├── chemistry.py      # RDKit reaction lab & equation build
│   │   │   │   ├── physics.py        # IEC 60617 circuits & optics ray diagrams
│   │   │   │   ├── biology.py        # BioIcons cellular & anatomical cross-sections
│   │   │   │   └── mathematics.py    # Real number lines & algebra step solver
│   │   │   ├── diagram_engine/       # Sugiyama layout & font metric calculations
│   │   │   ├── quality_gate.py       # Scene validation & auto-repair skill
│   │   │   ├── tts_synthesis.py      # Edge-TTS voice synthesis
│   │   │   └── video_stitching.py    # FFmpeg multi-track compositing (scenes + audio + PIP avatar)
│   │   └── main.py                   # FastAPI REST API endpoints
│   │
│   └── web/                          # Next.js 15 Web Application
│       ├── app/
│       │   ├── (app)/session/[id]/   # Interactive player & checkpoint UI
│       │   ├── (app)/dashboard/      # Student learning path & weak spots
│       │   └── (marketing)/          # Landing page & demo entrance
│       └── components/               # UI components (Video, Checkpoints, Nav)
│
├── packages/
│   └── motion-engine/                # Flick / Remotion Deterministic Motion Graphics Package
│       ├── src/
│       │   ├── templates/            # 7 Reusable pedagogical motion templates
│       │   │   ├── StepByStepFlow.tsx
│       │   │   ├── AnimatedTitle.tsx
│       │   │   ├── ConceptHighlight.tsx
│       │   │   ├── Comparison.tsx
│       │   │   ├── Timeline.tsx
│       │   │   ├── TextReveal.tsx
│       │   │   └── DiagramBuild.tsx
│       │   ├── compositions/         # MotionScene composition router
│       │   ├── render.ts             # Programmatic headless Chrome CLI renderer
│       │   └── Root.tsx              # Remotion root registry
│       └── package.json              # Remotion 4.0, React 18, lucide-react
│
├── assets/                           # Vector icons, circuit symbols & teacher avatar
└── docs/assets/                      # Architectural diagrams and media
```

---

## 10. Summary of Architectural Guarantees

| Metric / Aspect | Generative AI Video (Runway / Sora) | Shikshak AI Deterministic Engine |
| :--- | :--- | :--- |
| **Generation Latency** | 3 to 10 minutes per segment | **< 2.5 seconds** per segment |
| **Scientific Accuracy** | Frequent hallucinations in formulas & bonds | **100% textbook-accurate** (RDKit / IEC) |
| **Text Legibility** | Distorted, unreadable AI artifacts | **Crisp vector typography** (CairoSVG + Inter) |
| **Audio-Visual Sync** | Random drift between voice and imagery | **100% synchronized** via unified blueprint |
| **Render-Time Failures** | High failure rate from external video APIs | **0 render-time LLM calls** (pre-computed specs) |
| **Student Interactivity** | Flat MP4 file with zero pause intelligence | **Real-time Socratic checkpoints & remediation** |
| **Compute Cost** | \$0.50 – \$3.00 per minute of video | **<\$0.01 per segment** (Groq + local CPU render) |
