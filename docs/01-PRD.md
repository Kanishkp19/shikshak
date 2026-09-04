# 01 — Product Requirements Document — Shikshak AI

## App name & tagline

**Shikshak AI** — "Any book. Any topic. Your own teacher."

## Elevator pitch

Shikshak AI turns any uploaded textbook, PDF, or plain topic request into a personalized video lesson delivered by a human-like AI teacher — one who plans the lesson, explains it at the right depth and pace for the learner, shows the right diagram or animation for the subject, asks questions along the way, catches misunderstandings and re-explains them differently, and finishes with a report on what to study next. It is not a chatbot that answers questions; it is a teacher that runs a lesson.

## Problem statement

Existing digital learning tools are either static (pre-recorded lecture videos that can't adapt) or reactive (chatbots that only answer the exact question asked, with no lesson structure, no assessment, and no memory of what the learner struggled with last time). A student who says "I'm a beginner, teach me Chapter 4 in 20 minutes in Hindi, and test me at the end" has no single tool today that can actually do all of that together, grounded in their own uploaded material, and adjust when they get something wrong.

## Target personas

**Priya, 16, Class 10 student (beginner, exam-driven)**
Goal: understand chapters from her own NCERT textbook before a test, in Hindi-English mix, in short sessions between other commitments.
Frustration: YouTube lectures are too long and don't check if she actually understood; ChatGPT answers her questions but doesn't structure a lesson or test her.

**Arjun, 21, engineering student (intermediate, interview-driven)**
Goal: learn a topic like "React for a technical interview" from scratch, at a technical depth, with code examples.
Frustration: generic explainers are either too basic or assume prior context he doesn't have; no tool adapts depth to his stated goal.

**Meera, 34, working professional (advanced, time-constrained)**
Goal: revise a technical topic in a genuine 5-minute pocket of time on a commute.
Frustration: every learning tool assumes a 30+ minute session; nothing compresses to "just the essentials, fast."

## Core features

### 1. Document-grounded learning (RAG)
Upload a PDF/DOCX/PPTX; the system extracts, chunks, and embeds the content, then teaches only what's actually in the material, citing which section a claim came from.
**Acceptance criteria:**
- It works when a student uploads a PDF and asks to be taught a named chapter, and the resulting lesson content traces back to retrieved chunks from that PDF.
- It works when the system explicitly declines to answer something not covered in the uploaded material rather than inventing an answer.

### 2. Topic-based learning (no upload required)
A student can request any topic by name and receive a structured lesson without uploading anything.
**Acceptance criteria:**
- It works when a bare topic string ("teach me Newton's Laws") produces a full lesson plan with no document required.

### 3. Personalized depth and style
Beginner/intermediate/advanced framing changes vocabulary, analogy use, and technical depth.
**Acceptance criteria:**
- It works when the same topic requested at "beginner" vs. "advanced" produces visibly different explanations (simple analogy vs. technical/mathematical treatment).

### 4. Time-adaptive lesson structuring
5 minutes -> concise summary; 20 minutes -> structured lesson with examples; 60 minutes -> deep lesson with assessment; 7 days -> a revision/study plan.
**Acceptance criteria:**
- It works when the same topic requested at different time budgets produces a materially different segment count and depth, not just a shorter version of the same text.

### 5. Multilingual teaching with mid-lesson switching
Student can request a language up front or switch mid-session; lesson state/context is preserved across the switch.
**Acceptance criteria:**
- It works when a student says "explain that in Hindi" mid-lesson and the next segment continues in Hindi without restarting the lesson or losing prior context.

### 6. Human-like AI teaching video
A generated video with a lip-synced avatar, voice narration, and subject-appropriate visuals (diagrams, equations, animations, code) — not a static avatar reading a script over a blank background.
**Acceptance criteria:**
- It works when at least one lesson segment produces a rendered video combining avatar + voice + a visual relevant to that segment's subject matter.

### 7. Interactive questioning during the lesson
The teacher pauses periodically to ask conceptual, MCQ, or short-answer questions, not just at the end.
**Acceptance criteria:**
- It works when a lesson of meaningful length (20+ minutes) contains at least one in-lesson question checkpoint before the final assessment.

### 8. Misconception detection and adaptive re-teaching
A wrong answer triggers diagnosis of the likely misunderstanding and a re-explanation using a different analogy, not just "incorrect, try again."
**Acceptance criteria:**
- It works when an incorrect answer produces a re-explanation that is textually different from the original explanation (new analogy/example), followed by a new check.

### 9. End-of-lesson assessment and report
A quiz graded against what was actually taught, producing a score, strong/weak areas, and a specific recommendation.
**Acceptance criteria:**
- It works when finishing a lesson produces a report containing a numeric score, at least one strong area, at least one weak area, and one concrete recommended next action.

### 10. Persistent learner profile and learning paths
Progress, scores, and weak concepts persist across sessions; broad topics can be broken into an ordered curriculum.
**Acceptance criteria:**
- It works when a returning student's new session on a related topic reflects previously recorded weak areas.
- It works when a broad topic ("Machine Learning") returns an ordered list of sub-topics rather than a single flat lesson.

## Nice-to-have features (v2)

- Flashcard auto-generation from any completed lesson
- Concept map visualization of a topic
- Exam-prep mode with spaced-repetition scheduling
- Multiple selectable teacher personalities/avatars
- Emotion-aware tone adjustment based on student sentiment in responses

## User stories

1. As Priya, I want to upload my textbook chapter so that the lesson only teaches what's actually in my syllabus.
2. As Priya, I want to say "teach me in 20 minutes" so that the lesson fits my study window.
3. As Priya, I want to switch to Hindi mid-lesson so that I understand a tricky part without losing my place.
4. As Arjun, I want to request "React for a technical interview" so that the depth matches my actual goal, not a generic beginner course.
5. As Arjun, I want the teacher to show me real code and execution flow so that programming topics are demonstrated, not just described.
6. As Meera, I want a 5-minute mode so that I can learn on a commute without committing to a full session.
7. As any student, I want the teacher to ask me questions during the lesson so that I stay engaged instead of passively watching.
8. As any student, I want a wrong answer to trigger a different explanation, not just "wrong," so that I actually get unstuck.
9. As any student, I want a report at the end telling me exactly what to revise so that I know what to do next.
10. As a returning student, I want the system to remember my weak areas so that future lessons address them.
11. As a student facing a huge topic, I want it broken into an ordered path so that I know what to learn first.
12. As any student, I want the video lesson to include diagrams or animations relevant to the subject, not just a talking head, so that abstract concepts are easier to grasp.

## Non-goals

- Not building a general-purpose chatbot Q&A tool — every interaction must exist inside a lesson/teaching structure, per the brief's explicit requirement.
- Not building live real-time conversational voice interaction for the hackathon submission (turn-based text/voice input is sufficient; true low-latency voice conversation is a v2 stretch, not required by the rubric).
- Not building a full LMS (grading for institutions, teacher-side dashboards, classroom management) — this is a single-learner personal teaching tool.
- Not attempting unlimited, fully live, on-demand cinematic video generation for every possible lesson segment at submission time — video generation uses a swappable provider with caching, prioritizing reliability over infinite generative range.

## Success metrics

- End-to-end lesson (upload/topic -> video -> question -> assessment -> report) completes without manual intervention for at least 5 distinct test topics before submission day.
- At least 3 of the 5 mandatory rubric categories (Human-Like Teaching, RAG/Grounding, AI/ML Implementation) demonstrably pass their acceptance criteria above in a live demo.
- Zero hallucinated claims in a manual review of 10 document-grounded lesson segments (QA/Grounding Guard Agent flags or the explanation cites a source for every factual claim).
- Full pipeline (excluding video render time) responds within 15 seconds per agent step during a live demo, so the interactive Q&A loop doesn't feel broken.
