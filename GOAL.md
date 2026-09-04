You’re right to reject the current output. The narration is reasonably grounded, but the video is not teaching it visually. In the screenshot, a 92-second chemistry explanation is represented by two generic cards on an almost empty canvas; the animation engine is treating the lesson as a flowchart instead of a scientific demonstration.

The good news: we do not need stronger hardware, a different model stack, or a generic video generator. Your system already has the right foundation—SVG/Cairo rendering, FFmpeg, Manim, RDKit, source extraction, TTS, avatar compositing, and a scene blueprint. We need to connect and extend them correctly.

## What is currently going wrong

1. A whole chapter recap is being treated as one long visual segment. It includes precipitation, oxidation, respiration, atom conservation, and balancing—far too much for one canvas.

2. The system generates `scenes`, equations, and a diagram specification, but the renderer mostly ignores the scene breakdown. It renders one consolidated node graph for the entire narration.

3. Visual routing is shallow. “Chemical reaction” is not classified into a reaction animation, laboratory demonstration, or balancing exercise, so it falls into a generic diagram path.

4. The specialised visual kits are selected mainly from the segment title. They need to be selected from the actual scene content: reactants, products, conditions, equations, experiments, and learning objective.

5. Formula, scene title, visual icons, and many scene-level details are generated but are not consistently visible in the final animation.

## The target experience

For every lesson, the system should produce a sequence of short, purposeful scenes. Each scene must answer one question, use one dominant visual idea, and have its animation timed to the spoken explanation.

For the chemistry example, the result should look like this:

```text
Atoms are rearranged
  → animated atom inventory / balance scale

Sodium sulphate + barium chloride
  → two labelled beakers mix
  → white BaSO₄ precipitate visibly forms
  → balanced equation appears as ions react

Copper oxidation
  → orange copper heats up and turns black
  → oxygen particles join the surface
  → 2Cu + O₂ → 2CuO is built step-by-step

Respiration
  → glucose + oxygen enter a cell
  → carbon dioxide, water, and energy leave
  → atom counters confirm conservation

Try it
  → learner predicts products or balances an equation
```

The teacher should remain present but not dominate the screen: visible for an introduction, explanation transitions, and feedback; reduced to a well-framed side panel while the instructional visual is active.

## Build plan

### Phase 1 — Make the lesson scene-first

Replace the current “one narration + one long diagram” render unit with a scene manifest.

Each lesson segment will produce 3–6 scenes, each with:

- A single learning objective.
- Exact narration for that scene.
- A visual mode and structured visual payload.
- On-screen equation, labels, and key takeaway.
- Start/end times based on real generated audio duration.
- An interaction cue where appropriate.

We should enforce a strict rule: a scene may not introduce more than one new core idea. A long chapter recap becomes multiple visual scenes or multiple playable lesson segments.

### Phase 2 — Create a visual-intent contract

Extend the existing content blueprint so the LLM describes what needs to be shown—not pixel positions and not a vague “diagram.”

Example visual modes:

- `reaction_lab`
- `molecular_rearrangement`
- `equation_build`
- `balancing_exercise`
- `experiment_observation`
- `force_diagram`
- `graph_plot`
- `biology_cross_section`
- `timeline`
- `map`
- `code_trace`
- `comparison`
- `generic_explainer`

Every mode receives a typed payload. A chemistry reaction scene, for example, includes reactants, products, states, conditions, observation, balanced equation, and which atom counts to highlight.

This is the key universal mechanism: the planner chooses the instructional visual; deterministic renderers make it reliable.

### Phase 3 — Build domain visual packs

Start with the subjects that give the greatest visible improvement, while keeping a strong generic fallback.

- Chemistry: beakers, test tubes, precipitates, gas bubbles, heating, colour changes, ions, molecular rearrangement, equation balancing, pH/energy indicators. Use the existing RDKit capability for molecular structures.
- Physics: vectors, motion paths, free-body diagrams, rays, circuit simulations, graphs, field lines.
- Biology: labelled cross-sections, organ systems, cellular processes, cycles, inheritance diagrams.
- Mathematics: step-by-step transformations, number lines, graphs, geometry construction, proofs.
- Computing: animated traces, memory/state diagrams, call stacks, algorithms and code execution.
- Humanities: timelines, maps, cause-and-effect chains, primary-source callouts, comparisons.

The fallback must still be meaningful: a well-composed illustrated explainer with icons, equations, source imagery, and progressive highlights—not generic cards.

### Phase 4 — Render the scene sequence, not a static graph

Use the existing local toolchain:

- CairoSVG/SVG for crisp labels, diagrams, chemistry apparatus, charts, and interactive-ready assets.
- FFmpeg for scene stitching, audio synchronisation, captions, transitions, and final compositing.
- Manim only where real mathematical or physical motion is valuable.
- RDKit for structurally correct chemistry.
- PyMuPDF to extract useful diagrams, figures, tables, and equation regions from an uploaded PDF when they genuinely support the lesson.

The renderer should:

- Show only the elements relevant to the currently spoken sentence.
- Build an equation progressively rather than display it all at once.
- Animate cause-and-effect: mix → observe → explain.
- Use composition rules that reserve a safe region for the avatar.
- Use camera moves, zooms, and transitions sparingly but intentionally.
- Avoid empty space, card-only frames, and decoration with no teaching value.
- Render subtitles from the same scene manifest.

No external generative-video provider should be responsible for precise labelled educational content. It can remain an optional, cached enhancement for short atmosphere/intro footage only.

### Phase 5 — Make it genuinely interactive

Do not bake all interactivity into video. Keep the rendered video deterministic, then layer interactions in the Next.js player using the same scene manifest.

Add:

- “Pause and predict” moments before an outcome is revealed.
- Tap-to-reveal equation steps.
- Atom-count toggles for balancing equations.
- “Why did this happen?” micro-prompts after a visible change.
- Replay-current-scene and slow-motion controls.
- Interactive diagrams—click a reactant, organ, vector, code line, or graph point.
- A concise answer check after a concept, with an immediate targeted re-teach scene when needed.

This gives the learner a real lesson rather than a passive clip, without increasing rendering hardware requirements.

### Phase 6 — Quality gates before a video is accepted

Before rendering, automatically reject or repair a scene when:

- Its visual does not contain the entities referenced by narration.
- A science claim has no corresponding source support.
- A formula is generated but not displayed.
- A scene has generic labels such as “Mechanism” or “Applications” instead of topic-specific content.
- A visual plan is too dense or contains unrelated concepts.
- The audio duration and visual duration differ materially.
- Labels collide, overflow, or become unreadable.
- The fallback output is generic when source material was available.

We should save a scene-level trace in the database: narration, visual intent, source citations, renderer used, render status, and quality-check results. That makes bad output diagnosable instead of mysterious.

## Implementation order

1. Add scene-level contracts and validation.
2. Update the renderer to consume all scenes, timings, formulas, titles, and visual payloads.
3. Build the chemistry pack first and use your supplied “chemical reactions” lesson as the acceptance benchmark.
4. Add the generic visual fallback and source-PDF figure extraction.
5. Add the other high-value subject packs.
6. Add player overlays and interactive checkpoints.
7. Add visual regression tests and a curated benchmark library across subjects and source PDFs.

## Definition of success

For your chemistry sample, a reviewer should be able to mute the audio and still understand:

- which chemicals are involved;
- what is being mixed or heated;
- what changed visibly;
- what product formed;
- how the balanced equation represents atom conservation.

That is the standard we should apply to every generated scene.

The first build milestone should be a polished chemistry lesson benchmark, not a broad but generic “any topic” upgrade. Once the scene contract and renderer work for chemistry, the same architecture scales cleanly to physics, biology, maths, code, and PDF-based lessons. 