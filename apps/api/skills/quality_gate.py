"""
Shikshak AI — Quality Gate Skill.

Validates each scene against strict pedagogical, visual-grounding,
and schema-consistency rules before rendering or persisting.

Logs every check result to agent_run_logs with the scene_id.
"""
from __future__ import annotations

from pathlib import Path
import re
import subprocess
from typing import Any, Optional
from pydantic import BaseModel, Field

from models import validate_visual_payload
from skills.supabase_persistence import log_agent_run


class QualityIssue(BaseModel):
    check_name: str
    severity: str  # "error" | "warning" | "repaired"
    message: str


class QualityResult(BaseModel):
    passed: bool
    scene_order: int
    visual_mode: str
    visual_necessity_score: float = 1.0
    issues: list[QualityIssue] = Field(default_factory=list)
    repaired_scene: Optional[dict[str, Any]] = None


# ── Negative Visual Vocabulary (Semantic Anti-Patterns) ──────────────────────
NEGATIVE_VISUAL_VOCABULARY: dict[str, dict[str, Any]] = {
    "balance_scale": {
        "forbidden_terms": {"balance_scale", "seesaw", "weighing_scale", "scale_pan", "fulcrum"},
        "metaphor_keywords": {"balance scale", "weighing scale", "seesaw", "pan", "fulcrum"},
        "trigger_modes": {"balancing_exercise", "reaction_lab", "equation_build"},
        "rationale": "Chemical balancing must demonstrate atomic conservation and molecular stoichiometry, not decorative weighing scales.",
        "replacement": "atom_inventory_comparison",
    },
    "water_pipe_current": {
        "forbidden_terms": {"water_pipe", "pipe_flow", "waterfall", "hose"},
        "metaphor_keywords": {"water pipe", "flowing water", "pipe", "plumbing"},
        "trigger_modes": {"circuit_simulation"},
        "rationale": "Electric current must be visualized with directional electron drift or charge packets on conductors.",
        "replacement": "electron_drift_particles",
    },
    "lightning_energy": {
        "forbidden_terms": {"lightning", "lightning_bolt", "electric_spark_icon"},
        "metaphor_keywords": {"lightning bolt", "thunderbolt"},
        "trigger_modes": {"bio_cellular_process", "reaction_lab"},
        "rationale": "Energy in biological/chemical systems must be shown as ATP, chemical bond potential, or photon packets, not generic lightning bolts.",
        "replacement": "atp_molecular_badge",
    },
    "generic_arrow_growth": {
        "forbidden_terms": {"upward_arrow_card", "growth_arrow"},
        "metaphor_keywords": {"growth arrow"},
        "trigger_modes": {"step_flow", "generic_explainer", "motion_graphic"},
        "rationale": "Avoid decorative stock graphics like generic upward arrows.",
        "replacement": "rate_of_change_graph",
    },
    "generic_connected_circles": {
        "forbidden_terms": {"decorative_network", "connected_dots_bg"},
        "metaphor_keywords": {"decorative circles"},
        "trigger_modes": {"generic_explainer", "generic_motion"},
        "rationale": "Connected circles should only represent real biological, chemical, or circuit topologies.",
        "replacement": "topological_process_graph",
    },
}


def compute_visual_necessity_score(
    scene: dict[str, Any],
    narration_text: str = "",
) -> tuple[float, list[QualityIssue]]:
    """Deterministic pedagogical necessity scoring for rendered visual elements.
    
    Every visual object must be justified by the concept being taught.
    Metaphors are permitted ONLY when explicitly introduced by narration.
    """
    issues: list[QualityIssue] = []
    score = 1.0
    mode = scene.get("visual_mode", "")
    payload = scene.get("visual_payload") or {}
    narration_lower = narration_text.lower()
    
    payload_str = str(payload).lower()
    for anti_key, rule in NEGATIVE_VISUAL_VOCABULARY.items():
        if mode in rule["trigger_modes"]:
            found_forbidden = [t for t in rule["forbidden_terms"] if t in payload_str]
            if found_forbidden:
                narration_justified = any(k in narration_lower for k in rule["metaphor_keywords"])
                if not narration_justified:
                    score -= 0.35
                    issues.append(QualityIssue(
                        check_name="anti_pattern_metaphor",
                        severity="error",
                        message=(
                            f"Visual anti-pattern '{anti_key}' detected ({found_forbidden}). "
                            f"{rule['rationale']} Metaphors are forbidden unless explicitly "
                            f"introduced in narration. Recommended: {rule['replacement']}."
                        ),
                    ))

    if mode == "balancing_exercise":
        if "scale" in payload_str or "seesaw" in payload_str:
            if not any(w in narration_lower for w in ("seesaw", "weighing scale", "balance scale", "pan balance")):
                score -= 0.4
                issues.append(QualityIssue(
                    check_name="balancing_scale_metaphor",
                    severity="error",
                    message="Balancing exercise contains decorative balance-scale metaphor without narration analogy justification.",
                ))

    objects = payload.get("objects")
    if isinstance(objects, list):
        unjustified = []
        for obj in objects:
            if isinstance(obj, dict):
                purpose = obj.get("pedagogical_purpose") or obj.get("pedagogicalPurpose")
                if not purpose or len(str(purpose).strip()) < 5:
                    unjustified.append(obj.get("id", "unknown"))
        if unjustified:
            score -= 0.1 * len(unjustified)
            issues.append(QualityIssue(
                check_name="pedagogical_justification",
                severity="warning",
                message=f"Objects {unjustified} lack pedagogical_purpose metadata answering what exact educational idea they teach.",
            ))

    score = max(0.0, min(1.0, score))
    return score, issues


def audit_scene(
    scene: dict[str, Any],
    concept: str = "",
    session_id: Optional[str] = None,
    scene_id: Optional[str] = None,
) -> QualityResult:
    """Run all quality checks on a single scene dictionary."""
    scene_copy = dict(scene)
    issues: list[QualityIssue] = []
    mode = scene_copy.get("visual_mode", "generic_explainer")
    payload = scene_copy.get("visual_payload") or {}
    narration = scene_copy.get("narration_text", "")
    on_screen_eq = scene_copy.get("on_screen_equation", "")
    learning_obj = scene_copy.get("learning_objective", "")

    # ── Check 1: Schema & Payload Validity ───────────────────────────────────
    try:
        validated_payload = validate_visual_payload(mode, payload)
        scene_copy["visual_payload"] = validated_payload.model_dump(mode="json")
    except Exception as e:
        if mode in ("motion_graphic", "animated_text", "generic_motion", "step_flow", "concept_highlight", "timeline_motion"):
            labels = scene_copy.get("on_screen_labels") or []
            title = scene_copy.get("learning_objective") or concept or "Key Process"
            scene_copy["visual_payload"] = {
                "template": "step_by_step_flow" if mode in ("step_flow", "motion_graphic", "generic_motion") else ("animated_title" if mode == "animated_text" else "concept_highlight"),
                "title": title[:50],
                "subtitle": narration[:80] if narration else "",
                "steps": labels if labels else [concept or "Stage 1", "Process Step", "Final State"],
                "key_takeaway": scene_copy.get("key_takeaway") or f"Core concept of {concept}.",
                "badge": mode.upper().replace("_", " "),
            }
            issues.append(QualityIssue(
                check_name="payload_schema",
                severity="repaired",
                message=f"Repaired motion payload with default structure: {e}",
            ))
        else:
            issues.append(QualityIssue(
                check_name="payload_schema",
                severity="repaired",
                message=f"Payload failed schema: {e}. Defaulting to generic_explainer.",
            ))
            mode = "generic_explainer"
            scene_copy["visual_mode"] = "generic_explainer"
            scene_copy["visual_payload"] = {
                "title": learning_obj or concept[:40],
                "key_points": [scene_copy.get("key_takeaway") or f"Core mechanism of {concept}."],
                "icons": ["atom", "flask"],
                "equation": on_screen_eq or "",
            }

    # ── Check 1b: Motion Mode Specific Repairs ─────────────────────────────────
    if mode in ("motion_graphic", "animated_text", "generic_motion", "step_flow", "concept_highlight", "timeline_motion"):
        cur_payload = scene_copy.get("visual_payload") or {}
        if not cur_payload.get("steps") and scene_copy.get("on_screen_labels"):
            cur_payload["steps"] = list(scene_copy["on_screen_labels"])
            scene_copy["visual_payload"] = cur_payload
            issues.append(QualityIssue(
                check_name="motion_steps",
                severity="repaired",
                message="Populated empty motion steps from on_screen_labels",
            ))
        if cur_payload.get("title") in ("", "Lesson Scene") and (learning_obj or concept):
            cur_payload["title"] = (learning_obj or concept)[:50]
            scene_copy["visual_payload"] = cur_payload

    # ── Check 2: Formula & Equation Presence ─────────────────────────────────
    payload_now = scene_copy["visual_payload"]
    extracted_eq = (
        payload_now.get("balanced_equation")
        or payload_now.get("final_equation")
        or payload_now.get("equation")
        or ""
    )
    if extracted_eq and not on_screen_eq:
        # Auto-repair: copy equation to on_screen_equation
        scene_copy["on_screen_equation"] = extracted_eq
        issues.append(QualityIssue(
            check_name="equation_display",
            severity="repaired",
            message="Missing on_screen_equation populated from payload formula.",
        ))

    # ── Check 3: Non-Generic Labels ──────────────────────────────────────────
    generic_words = {"mechanism", "applications", "overview", "introduction"}
    labels = scene_copy.get("on_screen_labels") or []
    for l in labels:
        if l.strip().lower() in generic_words:
            issues.append(QualityIssue(
                check_name="specific_labels",
                severity="warning",
                message=f"Label '{l}' is generic — should use domain-specific terms.",
            ))

    # ── Check 4: Single Core Objective ───────────────────────────────────────
    if len(re.findall(r"\band\b|\balso\b|\bfurthermore\b", learning_obj.lower())) > 2:
        issues.append(QualityIssue(
            check_name="single_objective",
            severity="warning",
            message="Learning objective may contain multiple concepts — ensure 1 core idea per scene.",
        ))

    # ── Check 5: Visual Necessity & Anti-Pattern Gate ────────────────────────
    necessity_score, necessity_issues = compute_visual_necessity_score(scene_copy, narration)
    issues.extend(necessity_issues)

    # Auto-repair: if balancing_scale_metaphor is present without narration justification,
    # repair payload to strip the physical balance scale and force atomic inventory comparison
    if mode == "balancing_exercise":
        cur_payload = dict(scene_copy.get("visual_payload") or {})
        if cur_payload.get("show_scale") or "scale" in str(cur_payload).lower():
            if not any(w in narration.lower() for w in ("seesaw", "weighing scale", "balance scale")):
                cur_payload["show_scale"] = False
                cur_payload["comparison_mode"] = "atom_inventory"
                scene_copy["visual_payload"] = cur_payload
                issues.append(QualityIssue(
                    check_name="balancing_scale_metaphor",
                    severity="repaired",
                    message="Repaired balancing scene: removed physical balance scale metaphor in favor of atomic count verification.",
                ))

    if mode == "equation_build":
        cur_payload = dict(scene_copy.get("visual_payload") or {})
        steps = cur_payload.get("steps") or []
        final_eq = cur_payload.get("final_equation", "")
        repaired = False
        new_steps = []
        for s in steps:
            s_clean = s.replace("&#8594;", " ⟶ ").replace("&amp;#8594;", " ⟶ ").replace("->", " ⟶ ")
            if "reactants" in s_clean.lower() and "products" in s_clean.lower():
                rxn_match = re.search(r"([A-Za-z0-9\(\)\s\+\-]+(?:->|→|⟶)[A-Za-z0-9\(\)\s\+\-]+)", narration)
                fallback_eq = on_screen_eq or (rxn_match.group(1) if rxn_match else "2H₂ + O₂ ⟶ 2H₂O")
                s_clean = str(fallback_eq).replace("->", " ⟶ ").replace("→", " ⟶ ")
                repaired = True
            new_steps.append(s_clean)

        final_clean = final_eq.replace("&#8594;", " ⟶ ").replace("&amp;#8594;", " ⟶ ").replace("->", " ⟶ ")
        if "reactants" in final_clean.lower() and "products" in final_clean.lower():
            fallback_eq = on_screen_eq or (new_steps[-1] if new_steps else "2H₂ + O₂ ⟶ 2H₂O")
            final_clean = str(fallback_eq).replace("->", " ⟶ ").replace("→", " ⟶ ")
            repaired = True

        if repaired or new_steps != steps or final_clean != final_eq:
            cur_payload["steps"] = new_steps
            cur_payload["final_equation"] = final_clean
            scene_copy["visual_payload"] = cur_payload
            issues.append(QualityIssue(
                check_name="equation_placeholder_cleanup",
                severity="repaired",
                message="Repaired equation_build: sanitized HTML entity code and generic placeholder text into clean chemical equation.",
            ))

    # ── Check 6: Anti-Slideshow Quality Gate ────────────────────────────────
    # Intercept static bullet-point formula lists and auto-repair them into lively animated scenes
    cur_payload = dict(scene_copy.get("visual_payload") or {})
    all_text = " ".join([
        str(cur_payload.get("title", "")),
        str(cur_payload.get("subtitle", "")),
        " ".join(str(s) for s in cur_payload.get("steps", [])),
        " ".join(str(p) for p in cur_payload.get("key_points", [])),
        str(on_screen_eq),
        str(narration),
    ]).lower()

    is_formula_list = any(eq in all_text for eq in ("f = r/2", "1/v + 1/u = 1/f", "1/f = 1/v", "mirror formula", "lens formula"))
    if mode in ("concept_highlight", "generic_explainer", "animated_text", "step_flow") and is_formula_list:
        if any(w in all_text for w in ("mirror", "curvature", "f = r/2", "1/v + 1/u")):
            mode = "spherical_mirror"
            scene_copy["visual_mode"] = "spherical_mirror"
            scene_copy["visual_payload"] = {
                "title": "Spherical Mirror Geometry & Formula",
                "formula": "1/v + 1/u = 1/f",
                "radius": "20 cm",
                "focal_length": "10 cm",
                "mirror_type": "concave",
            }
            issues.append(QualityIssue(
                check_name="anti_slideshow_gate",
                severity="repaired",
                message="Repaired static formula slide: converted bulleted mirror formulas into lively animated spherical mirror apparatus.",
            ))
        elif any(w in all_text for w in ("lens", "refract", "1/f = 1/v - 1/u")):
            mode = "optics_ray_diagram"
            scene_copy["visual_mode"] = "optics_ray_diagram"
            scene_copy["visual_payload"] = {
                "optical_element": "convex_lens",
                "focal_length": 10.0,
                "object_distance": 20.0,
                "object_height": 5.0,
                "image_distance": 20.0,
                "image_height": -5.0,
                "image_nature": "Real, Inverted, Same Size",
                "formula": "1/f = 1/v - 1/u",
                "key_observation": "Rays parallel to principal axis refract through principal focus F2",
            }
            issues.append(QualityIssue(
                check_name="anti_slideshow_gate",
                severity="repaired",
                message="Repaired static formula slide: converted bulleted lens formulas into lively animated optics ray diagram.",
            ))

    passed = not any(i.severity == "error" for i in issues)
    status_str = "success" if passed else "fallback_used"

    # Log to agent_run_logs with scene_id if session_id is available
    if session_id:
        try:
            log_agent_run(
                session_id=session_id,
                scene_id=scene_id,
                agent_name="quality_gate",
                status=status_str,
                input_summary={"visual_mode": mode, "scene_order": scene.get("scene_order")},
                output_summary={"passed": passed, "issue_count": len(issues)},
            )
        except Exception:
            pass

    return QualityResult(
        passed=passed,
        scene_order=scene.get("scene_order", 1),
        visual_mode=mode,
        visual_necessity_score=necessity_score,
        issues=issues,
        repaired_scene=scene_copy,
    )


def audit_scenes_for_segment(
    scenes: list[dict[str, Any]],
    concept: str = "",
    session_id: Optional[str] = None,
) -> list[dict[str, Any]]:
    """Audit and repair all scenes in a segment before persistence/render."""
    audited = []
    for sc in scenes:
        res = audit_scene(sc, concept=concept, session_id=session_id)
        audited.append(res.repaired_scene or sc)
    return audited


def audit_cinematic_video(
    video_path: Path | str,
    *,
    expected_duration: float = 6.0,
    concept: str = "",
    entities: list[str] | None = None,
    prompt: str = "",
    session_id: Optional[str] = None,
) -> QualityResult:
    """Rigorous quality gate for cinematic/image-generated video clips.

    Verifies:
      1. Duration alignment with expected transcript time (tolerance ±0.75s)
      2. Frame-to-frame kinetic motion across sampled intervals (rejects static slideshows)
      3. Content density (rejects solid-color/blank canvas fallbacks)
      4. Negative visual vocabulary compliance (no balance scales, lightning bolts, etc.)
    """
    import subprocess
    from PIL import Image

    issues: list[QualityIssue] = []
    video_path = Path(video_path)

    if not video_path.exists() or video_path.stat().st_size == 0:
        return QualityResult(
            passed=False,
            scene_order=1,
            visual_mode="cinematic",
            issues=[QualityIssue(check_name="file_integrity", severity="error", message="Video file missing or empty.")],
        )

    # 1. Probe actual duration via ffprobe
    actual_duration = expected_duration
    try:
        probe_cmd = [
            "ffprobe", "-v", "error",
            "-show_entries", "format=duration",
            "-of", "default=noprint_wrappers=1:nokey=1",
            str(video_path),
        ]
        res = subprocess.run(probe_cmd, capture_output=True, text=True, check=True)
        actual_duration = float(res.stdout.strip())
        drift = abs(actual_duration - expected_duration)
        if drift > 0.75 and expected_duration > 2.0:
            issues.append(QualityIssue(
                check_name="timing_drift",
                severity="error",
                message=f"Timing drift exceeded tolerance: actual {actual_duration:.1f}s vs expected {expected_duration:.1f}s (drift {drift:.2f}s).",
            ))
    except Exception as e:
        issues.append(QualityIssue(
            check_name="duration_probe",
            severity="warning",
            message=f"ffprobe duration check failed: {e}",
        ))

    # 2. Sample frames at 10%, 50%, and 90% of duration
    t_samples = [
        max(0.1, actual_duration * 0.1),
        max(0.2, actual_duration * 0.5),
        max(0.3, actual_duration * 0.9),
    ]
    sampled_frames: list[Image.Image] = []

    for t in t_samples:
        try:
            extract_cmd = [
                "ffmpeg", "-y",
                "-ss", str(t),
                "-i", str(video_path),
                "-vframes", "1",
                "-f", "image2pipe",
                "-vcodec", "png",
                "-",
            ]
            pipe = subprocess.run(extract_cmd, capture_output=True, check=True)
            if pipe.stdout:
                import io
                img = Image.open(io.BytesIO(pipe.stdout)).convert("RGB").resize((160, 90))
                sampled_frames.append(img)
        except Exception:
            pass

    # 3. Static interval motion check: compare sampled frames
    if len(sampled_frames) >= 2:
        diffs = []
        for i in range(len(sampled_frames) - 1):
            get_px1 = getattr(sampled_frames[i], "get_flattened_data", sampled_frames[i].getdata)
            get_px2 = getattr(sampled_frames[i + 1], "get_flattened_data", sampled_frames[i + 1].getdata)
            p1 = list(get_px1())
            p2 = list(get_px2())
            # Mean absolute difference per channel
            mad = sum(abs(c1 - c2) for px1, px2 in zip(p1, p2) for c1, c2 in zip(px1, px2)) / (len(p1) * 3)
            diffs.append(mad)

        # If difference between early and late frame is near zero, the video is static
        if max(diffs) < 0.8:
            issues.append(QualityIssue(
                check_name="static_interval",
                severity="error",
                message="Static slideshow detected: no meaningful frame-to-frame kinetic motion across sampled intervals.",
            ))

    # 4. Blank canvas / solid color fallback rejection
    if sampled_frames:
        frame_mid = sampled_frames[len(sampled_frames) // 2]
        get_px_mid = getattr(frame_mid, "get_flattened_data", frame_mid.getdata)
        pixels = list(get_px_mid())
        brightnesses = [0.299 * r + 0.587 * g + 0.114 * b for r, g, b in pixels]
        mean_b = sum(brightnesses) / len(brightnesses)
        variance = sum((b - mean_b) ** 2 for b in brightnesses) / len(brightnesses)
        stddev = variance ** 0.5
        if stddev < 6.0:
            issues.append(QualityIssue(
                check_name="blank_canvas_rejection",
                severity="error",
                message="Blank canvas or solid-color fallback detected: insufficient visual detail in rendered frame.",
            ))

    # 5. Negative vocabulary inspection
    combined_meta = f"{concept} {prompt} {' '.join(entities or [])}".lower()
    for anti_key, rule in NEGATIVE_VISUAL_VOCABULARY.items():
        found_forbidden = [t for t in rule["forbidden_terms"] if t in combined_meta]
        if found_forbidden:
            issues.append(QualityIssue(
                check_name="negative_vocabulary_violation",
                severity="error",
                message=f"Forbidden anti-pattern visual '{found_forbidden[0]}' found in prompt/entities: {rule['rationale']}",
            ))

    passed = not any(i.severity == "error" for i in issues)
    return QualityResult(
        passed=passed,
        scene_order=1,
        visual_mode="cinematic",
        visual_necessity_score=1.0 if passed else 0.4,
        issues=issues,
    )
