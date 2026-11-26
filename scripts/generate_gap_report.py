"""Generate the T23 module and documentation gap report."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from fsai_agents.core.memory.inventory import (  # noqa: E402
    evaluate_inventory,
    modules_without_documents,
    render_gap_report_markdown,
)


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate T23 module/doc gap report.")
    parser.add_argument(
        "--config",
        default="configs/module_inventory.json",
        help="Path to module inventory JSON.",
    )
    parser.add_argument("--base-dir", default=".", help="Repository root directory.")
    parser.add_argument(
        "--out",
        default="docs/gap_report_v1.md",
        help="Output Markdown gap report path.",
    )
    args = parser.parse_args()

    report = evaluate_inventory(Path(args.config), base_dir=Path(args.base_dir))
    markdown = render_gap_report_markdown(report)
    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(markdown, encoding="utf-8")

    gaps = modules_without_documents(report)
    print(
        f"Inventory: {report.documented_count}/{report.total_modules} documented, "
        f"{len(gaps)} with no substantive docs."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
