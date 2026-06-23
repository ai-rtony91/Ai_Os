import aiosCore from './assets/aios-symbols/aios-core.svg';
import balanceLadder from './assets/aios-symbols/balance-ladder.svg';
import botAlgo from './assets/aios-symbols/bot-algo.svg';
import brokerBridgeLocked from './assets/aios-symbols/broker-bridge-locked.svg';
import capitalFlow from './assets/aios-symbols/capital-flow.svg';
import compoundTarget from './assets/aios-symbols/compound-target.svg';
import evidenceLedger from './assets/aios-symbols/evidence-ledger.svg';
import fastPath from './assets/aios-symbols/fast-path.svg';
import fundsSweep from './assets/aios-symbols/funds-sweep.svg';
import lifecycleFlow from './assets/aios-symbols/lifecycle-flow.svg';
import marketSnapshot from './assets/aios-symbols/market-snapshot.svg';
import moneyCockpit from './assets/aios-symbols/money-cockpit.svg';
import musicUtility from './assets/aios-symbols/music-utility.svg';
import pairBtcUsd from './assets/aios-symbols/pair-btc-usd.svg';
import pairEurUsd from './assets/aios-symbols/pair-eur-usd.svg';
import pairGbpJpy from './assets/aios-symbols/pair-gbp-jpy.svg';
import pairXauUsd from './assets/aios-symbols/pair-xau-usd.svg';
import proofEvidence from './assets/aios-symbols/proof-evidence.svg';
import reconciliation from './assets/aios-symbols/reconciliation.svg';
import resupply from './assets/aios-symbols/resupply.svg';
import riskBankroll from './assets/aios-symbols/risk-bankroll.svg';
import riskMetadata from './assets/aios-symbols/risk-metadata.svg';
import riskShield from './assets/aios-symbols/risk-shield.svg';
import sessionReplay from './assets/aios-symbols/session-replay.svg';
import siteAccess from './assets/aios-symbols/site-access.svg';
import statusBlocked from './assets/aios-symbols/status-blocked.svg';
import statusClear from './assets/aios-symbols/status-clear.svg';
import statusLocked from './assets/aios-symbols/status-locked.svg';
import statusReview from './assets/aios-symbols/status-review.svg';
import tradeLedger from './assets/aios-symbols/trade-ledger.svg';
import tradeSequence from './assets/aios-symbols/trade-sequence.svg';
import tradeTicket from './assets/aios-symbols/trade-ticket.svg';
import traderCockpit from './assets/aios-symbols/trader-cockpit.svg';
import withdrawalGate from './assets/aios-symbols/withdrawal-gate.svg';

export const AIOS_SYMBOLS = {
  'aios-core': { src: aiosCore, label: 'AIOS core' },
  'balance-ladder': { src: balanceLadder, label: 'Balance ladder' },
  'bot-algo': { src: botAlgo, label: 'Bot algo' },
  'broker-bridge-locked': { src: brokerBridgeLocked, label: 'Broker bridge locked' },
  'capital-flow': { src: capitalFlow, label: 'Capital flow' },
  'compound-target': { src: compoundTarget, label: 'Compound target' },
  'evidence-ledger': { src: evidenceLedger, label: 'Evidence ledger' },
  'fast-path': { src: fastPath, label: 'Fast path' },
  'funds-sweep': { src: fundsSweep, label: 'Funds sweep' },
  'lifecycle-flow': { src: lifecycleFlow, label: 'Lifecycle flow' },
  'market-snapshot': { src: marketSnapshot, label: 'Market snapshot' },
  'money-cockpit': { src: moneyCockpit, label: 'Money cockpit' },
  'music-utility': { src: musicUtility, label: 'Music utility' },
  'pair-btc-usd': { src: pairBtcUsd, label: 'BTC/USD pair' },
  'pair-eur-usd': { src: pairEurUsd, label: 'EUR/USD pair' },
  'pair-gbp-jpy': { src: pairGbpJpy, label: 'GBP/JPY pair' },
  'pair-xau-usd': { src: pairXauUsd, label: 'XAU/USD pair' },
  'proof-evidence': { src: proofEvidence, label: 'Proof evidence' },
  'reconciliation': { src: reconciliation, label: 'Reconciliation' },
  'resupply': { src: resupply, label: 'Resupply' },
  'risk-bankroll': { src: riskBankroll, label: 'Risk bankroll' },
  'risk-metadata': { src: riskMetadata, label: 'Risk metadata' },
  'risk-shield': { src: riskShield, label: 'Risk shield' },
  'session-replay': { src: sessionReplay, label: 'Session replay' },
  'site-access': { src: siteAccess, label: 'Site access' },
  'status-blocked': { src: statusBlocked, label: 'Status blocked' },
  'status-clear': { src: statusClear, label: 'Status clear' },
  'status-locked': { src: statusLocked, label: 'Status locked' },
  'status-review': { src: statusReview, label: 'Status review' },
  'trade-ledger': { src: tradeLedger, label: 'Trade ledger' },
  'trade-sequence': { src: tradeSequence, label: 'Trade sequence' },
  'trade-ticket': { src: tradeTicket, label: 'Trade ticket' },
  'trader-cockpit': { src: traderCockpit, label: 'Trader cockpit' },
  'withdrawal-gate': { src: withdrawalGate, label: 'Withdrawal gate' }
};

export function getAiosSymbol(name) {
  return AIOS_SYMBOLS[name] ?? AIOS_SYMBOLS['aios-core'];
}
