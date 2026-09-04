# Classroom Whiteboard Visual Animation Invariant

## Core Directive
Never produce text-only slides or unillustrated bullet lists. Every video scene must be an engaging, illustrated, whiteboard-style educational animation.

## Mandatory Invariants
1. **Whiteboard Classroom Aesthetic:**
   - Canvas background must use clean, warm whiteboard tones (`#f8fafc` / `#fdfbf7`) with subtle dot-matrix/grid lines.
   - Text must be crisp dark charcoal/slate (`#0f172a` / `#1e293b`) paired with vibrant marker accents (royal blue `#2563eb`, emerald `#059669`, warm amber `#d97706`, violet `#7c3aed`).
2. **Deep Transcript Understanding & Concept Decomposition:**
   - Parse the narration transcript to extract the physical entities, actions, and transformations.
   - Represent physical/chemical/mechanical processes visually (e.g. state change diagrams, motion trajectories, component breakdowns) rather than summarizing them into text sentences.
3. **Multi-Domain Visual Catalog First, Dynamic Synthesis Fallback:**
   - First check the multi-domain visual toolkit (Physics, Chemistry, Biology, Math, Social Studies, ML, Engineering, Medical).
   - If a ready-made animation or schematic exists, instantiate and customize it with segment parameters.
   - If none matches, dynamically generate an illustrated vector diagram, process flow, or comparison matrix.
4. **Active Motion & Pedagogical Phasing:**
   - Progressive reveal: Elements draw or fade in sequentially matching the spoken timeline.
   - Continuous subtle micro-animations (e.g. pulsing active node, flowing arrow dashes, subtle particle drift, moving vectors).
5. **Zero Aspect Ratio Distortion:**
   - Geometry must natively target the studio stage dimensions (980×720) to eliminate black bars, downscaling blur, and pillarboxing.
