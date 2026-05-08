# AI_OS AI Assistant Panel Contract Draft

Status: DRAFT
Phase: Phase 12
Stage: 12.18 - AI Assistance Core Foundation

## Purpose

Define the dashboard panel contract for future AI Assistance display.

## Existing Surface

The static dashboard already has an assistant rail with:

- `assistantOutput`
- `mockMessage`
- preview-only Send button

## Planned Panel Inputs

- current phase and stage
- latest checkpoint summary
- progress status
- validator health status
- safety status
- next safe action
- operator question
- local mock assistant fixture

## Planned Panel Outputs

- assistant message
- next safe action
- safety reminder
- blocked action explanation
- source reference
- approval requirement

## Boundary

This contract does not authorize dashboard HTML, CSS, or JavaScript edits. It does not connect live AI APIs.

