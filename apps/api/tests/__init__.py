"""Shikshak AI — backend test suite entry point.

Run with:  cd apps/api && pytest

Per the testing strategy in 06-IMPLEMENTATION-PLAN.md:
  - skills get unit tests with small real sample inputs
  - agents get tests that mock their LLM call and assert output validates
    against the Pydantic schema
  - integration test runs the full Phase 1 + Phase 2 checkpoint flows
"""
