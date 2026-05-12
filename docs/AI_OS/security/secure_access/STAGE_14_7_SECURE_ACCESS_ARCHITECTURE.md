# Stage 14.7 Secure Access Architecture

Status: APPLY documentation scaffold  
Mode: docs-only  
Trading mode: paper-only

## Objective

Define the AI_OS secure access architecture:

GitHub = code and repo identity  
Microsoft Entra = main SSO identity  
YubiKey/passkey = strong login factor  
Cloudflare Access = protected HTTPS front door  
AI_OS = protected app behind the door

## Target Flow

1. User opens `https://aios.algobots.trade`.
2. Cloudflare Access checks whether the visitor is allowed before AI_OS loads.
3. Microsoft Entra handles SSO login.
4. YubiKey or FIDO2 passkey challenge confirms strong identity.
5. AI_OS home portal loads for approved users.
6. User enters allowed zones: Home Portal, Trading Lab, Work Table, Personal Apps, or Admin Zone.

## Boundary

This stage is architecture documentation only. It does not create live Cloudflare configuration, live Azure configuration, account changes, installed tools, credentials, secrets, or trading execution.

Trading Lab remains paper-only. Secure access does not enable live trading.

