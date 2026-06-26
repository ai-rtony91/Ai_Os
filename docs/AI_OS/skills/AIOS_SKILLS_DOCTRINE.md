# AI_OS Skills Doctrine

Purpose:
Define how AI_OS packages repeatable workflows as reviewed, versioned skill-style bundles without creating unsafe arbitrary automation.

## Definition

An AI_OS skill is a reviewed, versioned bundle of instructions, examples, files, schemas, and workflow rules for one repeatable task family.

AI_OS skills must follow a SKILL.md-style manifest concept:

- skill name
- version
- owner
- workflow purpose
- allowed inputs
- allowed outputs
- allowed paths
- forbidden paths
- required validators
- approval requirements
- risk class
- stop point

Skills are capability bundles, not unrestricted tools. They must be mapped to specific AI_OS workflows and reviewed before use.

## Default Pattern

Local AI_OS skills are preferred first. They keep instructions inspectable in the repo, versioned through PR review, and bounded by AGENTS.md.

Hosted skills are future-only and separately gated. They require a later human-approved packet, explicit trust review, and a clear upload/execution boundary.

## Non-Bypass Rule

Skills must not bypass:

- AGENTS.md
- AI_OS execution tokens
- allowed and forbidden path rules
- approval gates
- validator chains
- protected action gates
- Trading Lab default paper/simulation safety
- Night Supervisor runtime boundaries
- clean-state verification

## Candidate Workflows

Good skill candidates are repeated, bounded, reviewable workflows such as repo prechecks, packet validation, guardrail truth evals, OpenAI CLI readiness checks, and Night Supervisor runtime prechecks.

Skills with network, shell, write, secret, trading, broker, motor, runtime, or hosted execution access are high-risk and require explicit review before any use.
