# GitHub Repo Identity Boundary

## Purpose

GitHub is the code and repository identity boundary.

GitHub is used for:

- source code
- repo permissions
- commits
- pull identity
- push identity
- future pull request review identity

## Not The Main AI_OS Login

GitHub is not the main AI_OS user login in this architecture stage.

AI_OS user access should use Microsoft Entra SSO through Cloudflare Access.

## Boundary Rule

GitHub identity controls repo operations. It should not be treated as proof that a browser visitor is approved to enter AI_OS.

