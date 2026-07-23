import os
from pathlib import Path

ROOT = Path('.')
TARGET_DIRS = [
    ROOT / 'automation/forex_engine',
    ROOT / 'tests/forex_engine',
    ROOT / 'Reports/forex_delivery'
]

KEYWORDS = {
    'expectancy logic': ['expectancy'],
    'profit factor logic': ['profit_factor', 'pf'],
    'drawdown logic': ['drawdown', 'dd'],
    'trade count enforcement': ['trade_count', 'min_trades'],
    'walk-forward validation references': ['walk_forward', 'walkforward']
}

PIPELINE = ['data','strategy','mitigation','evaluation','candidate','gate','decision']


def scan_files():
    corpus = ''
    for d in TARGET_DIRS:
        if not d.exists():
            continue
        for p in d.rglob('*'):
            if p.is_file():
                try:
                    corpus += p.read_text(errors='ignore').lower()
                except:
                    pass
    return corpus


def classify(corpus):
    results = {}
    for k, terms in KEYWORDS.items():
        hits = sum(1 for t in terms if t in corpus)
        if hits == 0:
            results[k] = 'MISSING'
        elif hits == len(terms):
            results[k] = 'PRESENT'
        else:
            results[k] = 'PARTIAL'
    return results


def pipeline_check(corpus):
    return all(p in corpus for p in PIPELINE)


def build_report(classification, pipeline_ok):
    report_path = ROOT / 'Reports/forex_delivery/AIOS_FOREX_PHASE0_GAP_AUDIT_V1.md'
    report_path.parent.mkdir(parents=True, exist_ok=True)

    lines = []
    lines.append('# AIOS FOREX PHASE 0 GAP AUDIT V1')
    lines.append('')
    lines.append('## Classification Table')

    for k, v in classification.items():
        lines.append(f'- {k}: {v}')

    lines.append('')
    lines.append('## Pipeline Continuity')
    lines.append('PRESENT' if pipeline_ok else 'UNVERIFIED')

    report_path.write_text('\n'.join(lines))


if __name__ == '__main__':
    corpus = scan_files()
    classification = classify(corpus)
    pipeline_ok = pipeline_check(corpus)
    build_report(classification, pipeline_ok)
    print('PHASE0_AUDIT_COMPLETE')
