# Secure Access Setup Checklist Template

Use this as a planning checklist only.

## Planning

- Confirm AI_OS public URL.
- Confirm Cloudflare Access is the front door concept.
- Confirm Microsoft Entra is the main SSO identity provider concept.
- Confirm YubiKey/passkey is the strong factor concept.
- Confirm GitHub remains repo identity, not main AI_OS login.

## Safety Review

- No secrets in docs.
- No live Cloudflare config in docs.
- No live Azure config in docs.
- No account changes from docs.
- No installs from docs.
- No trading execution changes from docs.

## Trading Safety

- Trading Lab remains paper-only.
- No broker login.
- No live orders.
- No OANDA/Webull connection.
- Secure access does not enable live trading.

## Future APPLY Gate

Any future live setup must have a separate approved DRY_RUN, exact target account, exact files, exact commands, and a rollback plan.

