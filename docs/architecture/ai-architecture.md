# AI and AIOps safety architecture

The AI layer is advisory. It may summarize logs, correlate evidence, propose a root cause, and recommend one of the platform's enumerated actions. It cannot return a shell command that the orchestrator executes.

Recommended production contract:

1. Prompt contains only bounded, redacted evidence.
2. Model output is parsed as JSON and schema-validated.
3. Confidence is bounded to 0..1.
4. Recommended action is accepted only if it is in the allow-list.
5. Deterministic diagnosis remains the fallback if the model times out, fails validation, or returns low confidence.
6. Any mutation passes through the same policy engine and action executor used without AI.
