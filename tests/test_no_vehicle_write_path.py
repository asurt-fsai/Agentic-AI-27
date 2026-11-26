import re
from pathlib import Path

FORBIDDEN_PATTERNS = [
    r"create_publisher",
    r"vehiclecontrol_msgs",
    r"VehicleControl",
    r"ros2 topic pub",
]


def find_violations(root):
    violations = []
    for path in Path(root).rglob("*.py"):
        text = path.read_text(encoding="utf-8")
        for pattern in FORBIDDEN_PATTERNS:
            if re.search(pattern, text):
                violations.append((str(path), pattern))
    return violations


def test_source_has_no_vehicle_write_path():
    assert find_violations("src") == []


def test_scanner_catches_a_write_call(tmp_path):
    bad_file = tmp_path / "bad_tool.py"
    bad_file.write_text("node.create_publisher(VehicleControl, '/cmd', 10)\n", encoding="utf-8")
    assert find_violations(tmp_path) != []
