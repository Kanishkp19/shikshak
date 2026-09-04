"use client";

import * as React from "react";
import { cn } from "@/lib/utils";

interface ClassroomBackgroundProps {
  variant?: "parchment" | "chalkboard";
  withVignette?: boolean;
  className?: string;
  children?: React.ReactNode;
}

/**
 * ClassroomBackground Component (Scholarly Atmospheric Edition)
 *
 * Implements an immersive classroom & study desk atmosphere:
 * - Mathematical symbols: +, -, ×, ÷, ±, =, ≠, ≈, ≤, ≥, ∞, ∑, ∏, ∇, ∂, ℏ
 * - Alphabets & Greek notation: x, y, z, f(x), α, β, γ, θ, λ, μ, σ, ω, Ω, Δ, φ, ψ
 * - Numeric constants: 0..9, π ≈ 3.14159, e ≈ 2.718, √2, Fibonacci
 * - Real calculus & physics expressions: ∫ f(x)dx, dy/dx, lim (h→0), E=mc², F=ma, e^(iπ)+1=0
 * - Engineering notebook dot-grid texture
 * - Warm desk focus lighting vignette
 */
export function ClassroomBackground({
  variant = "parchment",
  withVignette = true,
  className,
  children,
}: ClassroomBackgroundProps) {
  const isChalkboard = variant === "chalkboard";

  return (
    <div
      className={cn(
        "relative min-h-screen w-full overflow-x-hidden transition-colors duration-200",
        isChalkboard
          ? "bg-study-grid-dark text-[var(--color-chalk-text)]"
          : "bg-study-grid text-[var(--color-ink)]"
      )}
    >
      {/* Mathematical Classroom Wallpaper Layer (Numbers, Alphabets, Symbols & Calculus) */}
      <div
        aria-hidden="true"
        className={cn(
          "pointer-events-none fixed inset-0 z-0 select-none overflow-hidden transition-opacity",
          isChalkboard ? "text-white opacity-[0.075]" : "text-stone-900 opacity-[0.065]"
        )}
      >
        <svg
          className="h-full w-full"
          xmlns="http://www.w3.org/2000/svg"
          width="100%"
          height="100%"
        >
          <defs>
            <pattern
              id="scholarly-math-pattern"
              width="680"
              height="640"
              patternUnits="userSpaceOnUse"
            >
              {/* Row 1: Calculus Integrals & Greek Variables */}
              <text x="30" y="45" fontFamily="var(--font-serif), Georgia, serif" fontStyle="italic" fontSize="17" fill="currentColor">
                ∫ f(x) dx = F(x) + C
              </text>
              <text x="240" y="42" fontFamily="var(--font-serif), Georgia, serif" fontStyle="italic" fontSize="15" fill="currentColor">
                α + β = θ
              </text>
              <text x="360" y="46" fontFamily="var(--font-serif), Georgia, serif" fontStyle="italic" fontSize="14" fill="currentColor">
                lim (h→0) [f(x+h) - f(x)] / h
              </text>
              <text x="590" y="42" fontFamily="var(--font-mono), monospace" fontSize="13" fill="currentColor">
                i² = -1
              </text>

              {/* Row 2: Fundamental Constants & Basic Arithmetic */}
              <text x="70" y="105" fontFamily="var(--font-mono), monospace" fontSize="14" fill="currentColor">
                π ≈ 3.14159265
              </text>
              <text x="260" y="108" fontFamily="var(--font-mono), monospace" fontSize="16" letterSpacing="3px" fill="currentColor">
                +  -  ×  ÷  ±  ≠  ≈
              </text>
              <text x="470" y="105" fontFamily="var(--font-serif), Georgia, serif" fontStyle="italic" fontSize="14" fill="currentColor">
                d/dx [sin x] = cos x
              </text>

              {/* Geometry sketch: Right triangle */}
              <path
                d="M 170 165 L 215 165 L 215 130 Z"
                fill="none"
                stroke="currentColor"
                strokeWidth="1.2"
                strokeDasharray="2,2"
              />
              <text x="185" y="178" fontFamily="var(--font-serif), Georgia, serif" fontStyle="italic" fontSize="11" fill="currentColor">
                a
              </text>
              <text x="222" y="150" fontFamily="var(--font-serif), Georgia, serif" fontStyle="italic" fontSize="11" fill="currentColor">
                b
              </text>
              <text x="186" y="142" fontFamily="var(--font-serif), Georgia, serif" fontStyle="italic" fontSize="11" fill="currentColor">
                c
              </text>

              {/* Row 3: Physics Energy & Digits Sequence */}
              <text x="35" y="170" fontFamily="var(--font-serif), Georgia, serif" fontStyle="italic" fontSize="18" fontWeight="600" fill="currentColor">
                E = mc²
              </text>
              <text x="260" y="172" fontFamily="var(--font-mono), monospace" fontSize="15" letterSpacing="4px" fill="currentColor">
                0  1  2  3  4  5  6  7  8  9
              </text>
              <text x="480" y="170" fontFamily="var(--font-serif), Georgia, serif" fontSize="14" fill="currentColor">
                ∑ (n=1 to ∞) 1/n² = π²/6
              </text>

              {/* Row 4: Partial Derivatives & Pythagorean Equation */}
              <text x="60" y="235" fontFamily="var(--font-serif), Georgia, serif" fontStyle="italic" fontSize="14" fill="currentColor">
                ∂²u/∂t² = c² ∇²u
              </text>
              <text x="240" y="238" fontFamily="var(--font-serif), Georgia, serif" fontStyle="italic" fontSize="16" fill="currentColor">
                a² + b² = c²
              </text>
              <text x="390" y="235" fontFamily="var(--font-mono), monospace" fontSize="13" fill="currentColor">
                √2 ≈ 1.414 · e ≈ 2.718
              </text>
              <text x="560" y="238" fontFamily="var(--font-serif), Georgia, serif" fontStyle="italic" fontSize="14" fill="currentColor">
                λ = h/p
              </text>

              {/* Geometry sketch: Gaussian Bell Curve */}
              <path
                d="M 330 300 Q 355 300, 365 275 Q 375 250, 385 275 Q 395 300, 420 300"
                fill="none"
                stroke="currentColor"
                strokeWidth="1.2"
              />
              <text x="360" y="315" fontFamily="var(--font-mono), monospace" fontSize="10" fill="currentColor">
                ~ N(0, σ²)
              </text>

              {/* Row 5: Trigonometry, Mechanics & Matrices */}
              <text x="30" y="305" fontFamily="var(--font-serif), Georgia, serif" fontStyle="italic" fontSize="14" fill="currentColor">
                sin²θ + cos²θ = 1
              </text>
              <text x="210" y="308" fontFamily="var(--font-serif), Georgia, serif" fontStyle="italic" fontSize="15" fill="currentColor">
                F = ma = m(dv/dt)
              </text>
              <text x="450" y="305" fontFamily="var(--font-mono), monospace" fontSize="13" fill="currentColor">
                det(A) = ad - bc
              </text>
              <text x="580" y="308" fontFamily="var(--font-serif), Georgia, serif" fontSize="14" fill="currentColor">
                ∇ · B = 0
              </text>

              {/* Row 6: Greek Alphabet & Sets */}
              <text x="45" y="375" fontFamily="var(--font-serif), Georgia, serif" fontSize="17" letterSpacing="5px" fill="currentColor">
                γ  μ  σ  ω  Ω  Δ  φ  ψ  ξ
              </text>
              <text x="280" y="375" fontFamily="var(--font-serif), Georgia, serif" fontStyle="italic" fontSize="15" fill="currentColor">
                ∫₀^∞ e^(-x²) dx = √π / 2
              </text>
              <text x="500" y="375" fontFamily="var(--font-mono), monospace" fontSize="14" letterSpacing="3px" fill="currentColor">
                ≤  ≥  ∈  ⊂  ∩  ∪  ∝  ∞
              </text>

              {/* Sine Wave Curve */}
              <path
                d="M 120 440 Q 140 415, 160 440 T 200 440 T 240 440"
                fill="none"
                stroke="currentColor"
                strokeWidth="1.2"
              />
              <text x="140" y="455" fontFamily="var(--font-serif), Georgia, serif" fontStyle="italic" fontSize="10" fill="currentColor">
                y = A sin(ωt + φ)
              </text>

              {/* Row 7: Chain Rule, Euler Identity & Quantum State */}
              <text x="35" y="445" fontFamily="var(--font-serif), Georgia, serif" fontStyle="italic" fontSize="14" fill="currentColor">
                dy/dx = (dy/du) · (du/dx)
              </text>
              <text x="270" y="448" fontFamily="var(--font-serif), Georgia, serif" fontStyle="italic" fontSize="16" fontWeight="600" fill="currentColor">
                e^(iπ) + 1 = 0
              </text>
              <text x="460" y="445" fontFamily="var(--font-serif), Georgia, serif" fontStyle="italic" fontSize="15" fill="currentColor">
                Ĥ |ψ⟩ = E |ψ⟩
              </text>
              <text x="580" y="445" fontFamily="var(--font-serif), Georgia, serif" fontStyle="italic" fontSize="14" fill="currentColor">
                {"f'(x) = 3x²"}
              </text>

              {/* Row 8: Power Rule & Maxwell Equations */}
              <text x="50" y="515" fontFamily="var(--font-serif), Georgia, serif" fontStyle="italic" fontSize="14" fill="currentColor">
                ∫ xⁿ dx = [xⁿ⁺¹ / (n+1)] + C
              </text>
              <text x="310" y="518" fontFamily="var(--font-mono), monospace" fontSize="13" letterSpacing="2px" fill="currentColor">
                x, y, z ∈ ℝⁿ
              </text>
              <text x="460" y="515" fontFamily="var(--font-serif), Georgia, serif" fontSize="14" fill="currentColor">
                ∇ × E = -∂B/∂t
              </text>

              {/* Row 9: Circle Area, Sequence & Asymptotic Limits */}
              <text x="30" y="585" fontFamily="var(--font-serif), Georgia, serif" fontStyle="italic" fontSize="15" fill="currentColor">
                A = π r²  ·  C = 2π r
              </text>
              <text x="220" y="585" fontFamily="var(--font-mono), monospace" fontSize="12" letterSpacing="2px" fill="currentColor">
                Fₙ = Fₙ₋₁ + Fₙ₋₂ (0, 1, 1, 2, 3, 5, 8...)
              </text>
              <text x="490" y="585" fontFamily="var(--font-serif), Georgia, serif" fontStyle="italic" fontSize="14" fill="currentColor">
                lim (x→∞) (1 + 1/x)ˣ = e
              </text>
            </pattern>
          </defs>
          <rect width="100%" height="100%" fill="url(#scholarly-math-pattern)" />
        </svg>
      </div>

      {/* Subtle Study Desk Focus Lighting */}
      {withVignette && (
        <div
          aria-hidden="true"
          className={cn(
            "pointer-events-none fixed inset-0 z-0",
            isChalkboard
              ? "bg-[radial-gradient(ellipse_80%_60%_at_50%_0%,rgba(30,41,59,0.5),transparent_80%)]"
              : "bg-[radial-gradient(ellipse_75%_50%_at_50%_0%,rgba(254,243,199,0.2),transparent_70%)]"
          )}
        />
      )}

      {/* Content Canvas */}
      <div className={cn("relative z-10 w-full min-h-screen", className)}>{children}</div>
    </div>
  );
}
