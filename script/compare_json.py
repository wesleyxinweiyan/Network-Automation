
import json
import sys
from pathlib import Path
from deepdiff import DeepDiff

try:
    # JSON before restarting
    pre_file = Path(sys.argv[1])

    # JSON after restarting
    post_file = Path(sys.argv[2])

    # Read data before restarting
    with pre_file.open(encoding="utf-8") as f:
        pre_data = json.load(f)

    # Read data after restarting
    with post_file.open(encoding="utf-8") as f:
        post_data = json.load(f)

    # Compare network states
    diff = DeepDiff(pre_data, post_data)

    # Output differences as JSON
    print(diff.to_json(indent=2))

    # Exit codes:
    # 0 = No differences
    # 1 = Differences detected
    sys.exit(1 if diff else 0)

except Exception as error:
    print(f"Comparison error: {error}", file=sys.stderr)
    sys.exit(2)
