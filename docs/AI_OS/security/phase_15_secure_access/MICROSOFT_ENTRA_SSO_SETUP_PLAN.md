# Microsoft Entra SSO Setup Plan

## Purpose

Microsoft Entra is the planned main SSO identity provider for AI_OS.

It should manage:

- operator identity
- future organization login
- future role groups
- future access review

## Flow Role

Cloudflare Access should send approved login attempts to Microsoft Entra SSO.

Microsoft Entra confirms the user identity before AI_OS loads.

## Future Role Groups

Future groups may include:

- Home Portal user
- Trading Lab paper reviewer
- Work Table operator
- Personal Apps user
- Admin Zone operator

## Boundary

This document includes no live Entra setup, identifiers, credential material, account changes, or config changes.

