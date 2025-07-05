#!/usr/bin/env python3

import json
from pathlib import Path
from typing import List, Tuple, Dict, Any

# config.json 的路径
CFG_FILE = Path(__file__).with_name("config.json")


def parse_unit_id(unit: str) -> Tuple[int, int]:
    """
    将章节号字符串（如 '3.4' 或 '2'）解析为可排序的元组。
    '3.4' → (3, 4)
    '2'   → (2, 0)
    '3.10'→ (3, 10) # 确保数字排序正确
    """
    parts = unit.split(".")
    major = int(parts[0]) if parts[0].isdigit() else 0
    minor = int(parts[1]) if len(parts) > 1 and parts[1].isdigit() else 0
    return (major, minor)


def sort_config(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    根据 book_config 中的键顺序来排序 entries。
    """
    # 1. 创建一个从书籍代号到其在 book_config 中顺序的映射
    book_order_map = {
        book_key: index for index, book_key in enumerate(data["book_config"])
    }

    # 2. 排序 entries 列表
    #    - 主要排序键: 书籍在 book_config 中的顺序
    #    - 次要排序键: 章节号
    entries: List[List[str]] = data["entries"]
    entries.sort(
        key=lambda e: (book_order_map.get(e[0], 999), parse_unit_id(e[1]))
    )

    # book_config 保持原样，只更新排序后的 entries
    return {"book_config": data["book_config"], "entries": entries}


def main() -> None:
    """
    主函数，读取、排序并写回 config.json。
    """
    if not CFG_FILE.exists():
        raise FileNotFoundError(f"{CFG_FILE} 不存在")

    # 使用 json.loads 读取可以保持字典键的原始顺序
    raw = json.loads(CFG_FILE.read_text(encoding="utf-8"))
    
    sorted_data = sort_config(raw)

    CFG_FILE.write_text(
        json.dumps(sorted_data, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(f"✅ 已根据 book_config 的顺序格式化并覆盖 {CFG_FILE.name}")


if __name__ == "__main__":
    main()