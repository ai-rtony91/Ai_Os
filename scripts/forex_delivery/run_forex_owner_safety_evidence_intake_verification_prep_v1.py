"""Runner for owner safety evidence intake and verification-prep classification."""

from __future__ import annotations

import json
from pathlib import Path
import sys

ROOT_DIR = Path(__file__).resolve().parents[2]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from automation.forex_engine import forex_owner_safety_evidence_intake_verification_prep_v1 as module


def main() -> None:
    args = module.parse_args()
    input_path = (
        Path(args.input_template_path)
        if args.input_template_path is not None
        else None
    )
    template_output = Path(args.template_output_path)
    state_output = Path(args.state_output_path)
    report_output = Path(args.report_output_path)
    next_packet_output = Path(args.next_packet_output_path)

    output = module.run_collection_pipeline(
        input_template_path=input_path,
        template_output_path=template_output if args.write_template else None,
        state_output_path=state_output if args.write_state else None,
        report_output_path=report_output if args.write_report else None,
        next_packet_output_path=(
            next_packet_output
            if args.write_next_packet or args.write_report
            else None
        ),
    )
    print(json.dumps(output, indent=2, ensure_ascii=True))


if __name__ == "__main__":
    main()
