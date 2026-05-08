# AI_OS Tool Auth Boundary Rules Draft

## Purpose

Define authentication boundaries for AI_OS tool readiness detection.

## Rules

- Do not store passwords.
- Do not store tokens.
- Do not store recovery codes.
- Do not store API keys.
- Do not automate login flows.
- Do not connect GitHub, Azure, Bitwarden, Claude, OpenAI, or broker APIs during detection.
- Do not inspect private browser sessions.
- Do not scrape account pages.
- Do not assume login state without evidence.

## Allowed Detection

- Executable presence checks.
- Version checks for local CLI tools.
- Folder existence checks.
- Repo remote checks.
- Read-only report/folder existence checks.

## Conditional Detection

`gh auth status` is read-only but may reveal account state. It must be separately approved before inclusion in validators.

## Reporting

When auth state cannot be safely verified, report NEEDS_LOGIN or UNKNOWN.
