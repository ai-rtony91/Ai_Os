# AIOS No Automatic Destructive Repair Draft

Stage: 11.3
Status: Draft planning doc

## Purpose

Define the absolute block on automatic destructive repair.

## Destructive Actions

- delete
- move
- rename
- overwrite
- reset
- clean
- force push
- credential or security setting changes

## Rule

Any destructive repair must be blocked and escalated to the human operator. AI_OS may only report the issue and recommend a safe next action.
