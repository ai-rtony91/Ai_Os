# YubiKey Passkey Model

## Purpose

YubiKey or FIDO2 passkey provides a strong physical login factor for AI_OS.

It should be used for phishing-resistant access, especially for admin and dangerous zones.

## Target Use

- Require strong factor during login where policy allows.
- Require stronger re-check before Admin Zone actions.
- Require stronger re-check before dangerous local actions.

## Admin Re-Check

Admin Zone access should not rely only on an existing browser session.

AI_OS should require a fresh strong-factor confirmation before admin operations.

## Not In This Stage

This document does not register a key, change account settings, install software, or configure a live identity provider.

