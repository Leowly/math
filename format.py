#!/usr/bin/env python3

import json
import re
from pathlib import Path
from typing import List, Tuple, Dict, Any


CFG_FILE = Path(__file__).with_name("config.json")


def parse_book_key(key: str) -> Tuple[int, int]:
    """
    'b1' → (0, 1)   # 必修优先
    'x3' → (1, 3)   # 选修其次
    其他   → (99, 0) # 未知放最后
    """
    m = re.match(r"([a-zA-Z])(\d+)", key)
    if not m:
        return (99, 0)
    prefix, num = m.groups()
    order = 0 if prefix.lower() == "b" else 1
    return (order, int(num))


def parse_unit_id(unit: str) -> Tuple[int, int]:
    """
    '3.4' → (3, 4)
    '2'   → (2, 0)
    """
    parts = unit.split(".")
    major = int(parts[0]) if parts[0].isdigit() else 0
    minor = int(parts[1]) if len(parts) > 1 and parts[1].isdigit() else 0
    return (major, minor)


def sort_config(data: Dict[str, Any]) -> Dict[str, Any]:
    # 1) 排序 book_config
    sorted_book_cfg = dict(
        sorted(data["book_config"].items(), key=lambda kv: parse_book_key(kv[0]))
    )

    # 2) 排序 entries
    entries: List[List[str]] = data["entries"]
    entries.sort(key=lambda e: (parse_book_key(e[0]), parse_unit_id(e[1])))

    return {"book_config": sorted_book_cfg, "entries": entries}


def main() -> None:
    if not CFG_FILE.exists():
        raise FileNotFoundError(f"{CFG_FILE} 不存在")

    raw = json.loads(CFG_FILE.read_text(encoding="utf-8"))
    sorted_data = sort_config(raw)

    CFG_FILE.write_text(
        json.dumps(sorted_data, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(f"✅ 已格式化并覆盖 {CFG_FILE.name}")


if __name__ == "__main__":
    main()