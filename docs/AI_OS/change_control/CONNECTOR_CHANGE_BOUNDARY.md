# Connector Change Boundary

A connector is a link to another app, account, service, or platform.

Planning-only connector work may describe:

- what the connector would do
- what data it would read
- what data it must not read
- what approval is required
- what validation is required

Blocked unless separately approved:

- real credentials
- real tokens
- account login
- browser profile access
- background sync
- startup persistence
- broker connector activation
- OANDA connector activation
- secret storage
- live API calls

Every connector change must fail closed. Fail closed means the safe result is to stop, not to continue.
