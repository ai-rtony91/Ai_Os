# Trading Lab Modular Window System

AI_OS Trading Lab now plans a flexible workspace window system for paper trading.

The goal is to make Trading Lab feel like a trading workspace, not a fixed wall of small cards. The first version uses safe local data and window-style panels. Resize, detach, popout, and layout memory are planned for later. They are not active yet.

## Window Areas

- TradingView Chart Window: safe placeholder for a future official chart widget or embed. No login, API key, webhook, account connection, or real integration is active.
- AI_OS Paper Trade Engine Window: the AI_OS-owned core. It shows Paper Trade Signal, Paper Risk Gate, Paper Decision, Paper Trade Result, Paper Scorecard, and Next Safe Action.
- TradersPost Route Preview: planning-only route preview area. No iframe assumption, login, broker, real webhook, route, or execution is active.
- Status / Telemetry Window: shows blocked safety state.
- Next Action Window: shows one safe next step.

## External Platform Placement

TradingView, TradersPost, and MetaTrader 5 are external platform windows. They are not main-screen buttons.

Correct path:

Trading Lab -> Tools / Connectors -> External Trading Platforms -> MetaTrader 5 / TradingView / TradersPost

They remain hidden or collapsed by default and are planning-only until future approval.

## Safety Boundary

AI_OS-owned Paper Trade Engine remains the core system.

Blocked:

- live trading
- broker connection
- OANDA connection
- MT5 login
- TradingView login
- TradersPost login
- API keys
- credentials
- real webhooks
- real orders
- account connection
- background automation
- scheduled trading

This window system is paper-only and does not place real trades.
