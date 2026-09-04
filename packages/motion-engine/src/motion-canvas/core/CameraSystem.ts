/**
 * Shikshak AI — Deterministic Educational Camera System.
 *
 * Provides semantic camera choreography:
 * - establish: Full 1280x720 canvas overview
 * - focus: Automatically frames and centers targeted educational objects
 * - zoom_in / zoom_out: Smooth scale transitions
 * - pan: Smooth translation to target
 * - pullback: Returns cleanly to the full establishing shot
 *
 * Invariant: The LLM specifies targets semantically (e.g. ["fe_left", "fe_right"]).
 * The CameraSystem resolves bounding boxes and computes smooth matrix transforms.
 */

import { SemanticCameraKeyframe } from "../../types/animation-spec";

export interface BoundingBox {
  minX: number;
  minY: number;
  maxX: number;
  maxY: number;
}

export interface CameraState {
  x: number; // Center x in world space
  y: number; // Center y in world space
  zoom: number; // 1.0 = normal, 1.5 = 150% zoom
}

export function easeInOutCubic(t: number): number {
  return t < 0.5 ? 4 * t * t * t : 1 - Math.pow(-2 * t + 2, 3) / 2;
}

export class CameraSystem {
  private width: number;
  private height: number;
  private defaultState: CameraState;
  private keyframes: SemanticCameraKeyframe[] = [];
  private targetBoundsProvider: (targetIds: string[]) => BoundingBox | null;

  constructor(
    width = 1280,
    height = 720,
    targetBoundsProvider: (targetIds: string[]) => BoundingBox | null
  ) {
    this.width = width;
    this.height = height;
    this.defaultState = {
      x: width / 2,
      y: height / 2,
      zoom: 1.0,
    };
    this.targetBoundsProvider = targetBoundsProvider;
  }

  public setKeyframes(keyframes: SemanticCameraKeyframe[]): void {
    this.keyframes = [...keyframes].sort((a, b) => a.at - b.at);
  }

  /**
   * Resolve camera state at time t (seconds)
   */
  public getStateAt(t: number): CameraState {
    if (this.keyframes.length === 0) {
      return { ...this.defaultState };
    }

    // Find previous and next keyframe
    let prevIndex = -1;
    for (let i = 0; i < this.keyframes.length; i++) {
      if (this.keyframes[i].at <= t) {
        prevIndex = i;
      } else {
        break;
      }
    }

    if (prevIndex === -1) {
      return { ...this.defaultState };
    }

    const currentKf = this.keyframes[prevIndex];
    const currentState = this.resolveKeyframeState(currentKf);

    // If there is no subsequent keyframe, hold current state
    if (prevIndex === this.keyframes.length - 1) {
      return currentState;
    }

    const nextKf = this.keyframes[prevIndex + 1];
    const transitionDur = nextKf.transitionDuration ?? 0.8;
    const transitionStart = nextKf.at - transitionDur;

    if (t < transitionStart) {
      return currentState;
    }

    const nextState = this.resolveKeyframeState(nextKf);
    const progress = Math.min(1.0, Math.max(0.0, (t - transitionStart) / transitionDur));
    const eased = easeInOutCubic(progress);

    return {
      x: currentState.x + (nextState.x - currentState.x) * eased,
      y: currentState.y + (nextState.y - currentState.y) * eased,
      zoom: currentState.zoom + (nextState.zoom - currentState.zoom) * eased,
    };
  }

  private resolveKeyframeState(kf: SemanticCameraKeyframe): CameraState {
    if (kf.action === "establish" || kf.action === "pullback") {
      return { ...this.defaultState };
    }

    if (kf.target && kf.target.length > 0) {
      const bounds = this.targetBoundsProvider(kf.target);
      if (bounds) {
        const targetCenterX = (bounds.minX + bounds.maxX) / 2;
        const targetCenterY = (bounds.minY + bounds.maxY) / 2;
        const targetW = Math.max(100, bounds.maxX - bounds.minX);
        const targetH = Math.max(80, bounds.maxY - bounds.minY);

        // Auto zoom calculation to fit targets with comfort margin
        const fitZoomX = (this.width * 0.75) / targetW;
        const fitZoomY = (this.height * 0.75) / targetH;
        const autoZoom = Math.min(fitZoomX, fitZoomY, 2.2);

        const zoom = (kf.zoomFactor ?? 1.0) * Math.max(1.0, autoZoom);

        return {
          x: targetCenterX,
          y: targetCenterY,
          zoom: Math.min(2.5, Math.max(1.0, zoom)),
        };
      }
    }

    return {
      x: this.width / 2,
      y: this.height / 2,
      zoom: kf.zoomFactor ?? 1.0,
    };
  }

  /**
   * Apply camera view transform to 2D canvas context
   */
  public applyToContext(ctx: any, state: CameraState): void {
    // Translate origin to viewport center
    ctx.translate(this.width / 2, this.height / 2);
    // Scale for zoom
    ctx.scale(state.zoom, state.zoom);
    // Translate world coordinate center
    ctx.translate(-state.x, -state.y);
  }
}
