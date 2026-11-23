import json
import sys
from pathlib import Path
from deepdiff import DeepDiff

try:
    # 升级前的 JSON 文件
    pre_file = Path(sys.argv[1])

    # 升级后的 JSON 文件
    post_file = Path(sys.argv[2])

    # 读取升级前数据
    with pre_file.open(encoding="utf-8") as f:
        pre_data = json.load(f)

    # 读取升级后数据
    with post_file.open(encoding="utf-8") as f:
        post_data = json.load(f)

    # 确认四类网络数据都存在
    required_keys = {
        "cdp",
        "lldp",
        "routing",
        "mac_address_table",
    }

    for name, data in [
        ("precheck", pre_data),
        ("postcheck", post_data),
    ]:
        if not isinstance(data, dict):
            raise ValueError(f"{name} is not a JSON object")

        missing = required_keys - data.keys()
        if missing:
            raise ValueError(f"{name} missing keys: {missing}")

    # 比较升级前后的网络状态
    diff = DeepDiff(pre_data, post_data)

    # 输出 JSON 格式的差异
    print(diff.to_json(indent=2))

    # 0 = 无差异
    # 1 = 有差异
    sys.exit(1 if diff else 0)

except Exception as error:
    print(f"Comparison error: {error}", file=sys.stderr)
    sys.exit(2)
