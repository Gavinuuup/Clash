#!/usr/bin/env python3
"""
合并两个 Clash 规则集，生成带多行注释头的新规则集。
用法: merge_rules.py <name> <author> <base.yaml> <custom.yaml> <out.yaml>
"""
import sys
import datetime
import yaml


def load_payload(path):
    try:
        with open(path, encoding="utf-8") as f:
            data = yaml.safe_load(f) or {}
        payload = data.get("payload", []) or []
        return [str(x).strip() for x in payload if str(x).strip()]
    except FileNotFoundError:
        print(f"[warn] not found: {path}, treat as empty")
        return []


def main():
    if len(sys.argv) != 6:
        print(__doc__)
        sys.exit(1)

    name, author, base_path, custom_path, out_path = sys.argv[1:6]

    base = load_payload(base_path)
    custom = load_payload(custom_path)

    # 合并 + 去重，保持顺序：上游在前，自定义在后
    seen = set()
    merged = []
    for item in base + custom:
        if item not in seen:
            seen.add(item)
            merged.append(item)

    updated = datetime.datetime.utcnow() + datetime.timedelta(hours=8)  # 北京时间
    updated_str = updated.strftime("%Y-%m-%d %H:%M:%S")

    header = (
        f"# NAME: {name}\n"
        f"# AUTHOR: {author}\n"
        f"# UPDATED: {updated_str}\n"
        f"# TOTAL: {len(merged)}\n"
        f"# BASE: {len(base)}\n"
        f"# CUSTOM: {len(custom)}\n"
    )

    with open(out_path, "w", encoding="utf-8") as f:
        f.write(header)
        yaml.safe_dump(
            {"payload": merged},
            f,
            allow_unicode=True,
            sort_keys=False,
            default_flow_style=False,
            width=10**6,
        )

    print(f"[ok] {out_path}: base={len(base)} custom={len(custom)} total={len(merged)}")


if __name__ == "__main__":
    main()
