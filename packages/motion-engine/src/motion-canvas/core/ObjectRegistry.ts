/**
 * Shikshak AI — Object Registry & Semantic State Resolver.
 *
 * Tracks semantic objects across time:
 * - Computes visual state (opacity, highlight pulse, active coefficient, transform progress)
 * - Returns precise bounding boxes for semantic camera framing
 * - Invariant: Objects are identified by semantic ID, not pixel coordinates
 */

import { SemanticObject, SemanticBeat } from "../../types/animation-spec";
import { BoundingBox, easeInOutCubic } from "./CameraSystem";

export interface ResolvedObjectVisual {
  id: string;
  type: string;
  semanticRole: string;
  label: string;
  opacity: number;
  scale: number;
  highlightIntensity: number; // 0.0 to 1.0
  activeCoefficient?: number;
  count?: number;
  isFocused: boolean;
  isDimmed: boolean;
  bounds: BoundingBox;
}

export class ObjectRegistry {
  private objects: Map<string, SemanticObject> = new Map();
  private boundsMap: Map<string, BoundingBox> = new Map();
  private beats: SemanticBeat[] = [];

  constructor(objects: SemanticObject[] = [], beats: SemanticBeat[] = []) {
    this.setObjects(objects);
    this.setBeats(beats);
  }

  public setObjects(objects: SemanticObject[]): void {
    this.objects.clear();
    for (const obj of objects) {
      this.objects.set(obj.id, obj);
    }
  }

  public setBeats(beats: SemanticBeat[]): void {
    this.beats = [...beats].sort((a, b) => a.at - b.at);
  }

  public registerBounds(id: string, bounds: BoundingBox): void {
    this.boundsMap.set(id, bounds);
  }

  public getBounds(targetIds: string[]): BoundingBox | null {
    if (targetIds.length === 0) return null;

    let minX = Infinity;
    let minY = Infinity;
    let maxX = -Infinity;
    let maxY = -Infinity;
    let found = false;

    for (const id of targetIds) {
      const b = this.boundsMap.get(id);
      if (b) {
        minX = Math.min(minX, b.minX);
        minY = Math.min(minY, b.minY);
        maxX = Math.max(maxX, b.maxX);
        maxY = Math.max(maxY, b.maxY);
        found = true;
      }
    }

    return found ? { minX, minY, maxX, maxY } : null;
  }

  public getObject(id: string): SemanticObject | undefined {
    return this.objects.get(id);
  }

  public getAllObjects(): SemanticObject[] {
    return Array.from(this.objects.values());
  }

  /**
   * Resolve state of all objects at timestamp t
   */
  public resolveVisualsAt(t: number): Map<string, ResolvedObjectVisual> {
    const result = new Map<string, ResolvedObjectVisual>();

    // Determine currently active beats affecting objects at time t
    const activeHighlights = new Map<string, number>(); // id -> intensity
    const activeCoefficients = new Map<string, number>(); // id -> coefficient
    const activeCounts = new Map<string, number>(); // id -> count
    let activeFocusTargets: Set<string> | null = null;

    for (const beat of this.beats) {
      if (beat.at > t) continue;

      const dur = beat.duration ?? 0.8;
      const elapsed = t - beat.at;
      const progress = Math.min(1.0, Math.max(0.0, elapsed / dur));
      const eased = easeInOutCubic(progress);

      const targets = beat.target ?? [];

      if (beat.action === "highlight" || beat.action === "emphasize") {
        const pulse = Math.sin(progress * Math.PI) * 0.8 + 0.2;
        for (const tid of targets) {
          activeHighlights.set(tid, pulse);
        }
      } else if (beat.action === "focus") {
        activeFocusTargets = new Set(targets);
      } else if (beat.action === "coefficient_insert") {
        for (const tid of targets) {
          if (typeof beat.semanticValue === "number") {
            activeCoefficients.set(tid, beat.semanticValue);
          }
        }
      } else if (beat.action === "count") {
        for (const tid of targets) {
          if (typeof beat.semanticValue === "number") {
            const val = Math.round(beat.semanticValue * eased);
            activeCounts.set(tid, val);
          }
        }
      }
    }

    for (const [id, obj] of this.objects.entries()) {
      const bounds = this.boundsMap.get(id) ?? { minX: 0, minY: 0, maxX: 100, maxY: 60 };
      const isFocused = activeFocusTargets ? activeFocusTargets.has(id) : true;
      const isDimmed = activeFocusTargets ? !activeFocusTargets.has(id) : false;
      const highlight = activeHighlights.get(id) ?? 0.0;
      const coeff = activeCoefficients.get(id);
      const cnt = activeCounts.get(id) ?? obj.count;

      result.set(id, {
        id,
        type: obj.type,
        semanticRole: obj.semanticRole,
        label: obj.label ?? obj.formula ?? id,
        opacity: isDimmed ? 0.35 : 1.0,
        scale: highlight > 0 ? 1.0 + highlight * 0.08 : 1.0,
        highlightIntensity: highlight,
        activeCoefficient: coeff,
        count: cnt,
        isFocused,
        isDimmed,
        bounds,
      });
    }

    return result;
  }
}
