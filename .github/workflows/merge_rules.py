#!/usr/bin/env python3
"""
合并两个 Clash 规则集，生成带多行注释头的新规则集。
用法: merge_rules.py <name> <author> <base.yaml> <custom.yaml> <out.yaml>
"""
import sys
import datetime
import re
import yaml


class IndentDumper(yaml.Dumper):
    def increase_indent(self, flow=False, indentless=False):
        return super().increase_indent(flow, False)


# DOMAIN-SUFFIX,x -> +.x（语义等价，安全）
CONVERT_SUFFIX_TO_PLUS = True

# DOMAIN,x -> x（会变成后缀匹配，注意语义变化）
CONVERT_DOMAIN_TO_BARE = True


def normalize(raw):
    """把一条规则规整成规范写法，返回 None 表示丢弃。"""
    s = str(raw).strip()

    if not s or s.startswith("#"):
        return None

    s = s.rstrip(",").strip()
    if not s:
        return None

    if CONVERT_SUFFIX_TO_PLUS:
        m = re.fullmatch(r"DOMAIN-SUFFIX\s*,\s*(.+)", s, re.IGNORECASE)
        if m:
            domain = m.group(1).strip().lstrip("+.")
            return f"+.{domain}"

    if CONVERT_DOMAIN_TO_BARE:
        m = re.fullmatch(r"DOMAIN\s*,\s*(.+)", s, re.IGNORECASE)
        if m:
            return m.group(1).strip()

    if "," in s:
        parts = [p.strip() for p in s.split(",")]
        s = ",".join(parts)

    return s


def load_payload(path):
    try:
        with open(path, encoding="utf-8") as f:
            data = yaml.safe_load(f) or {}
        payload = data.get("payload", []) or []
    except FileNotFoundError:
        print(f"[warn] not found: {path}, treat as empty")
        return []

    result = []
    for item in payload:
        norm = normalize(item)
        if norm is not None:
            result.append(norm)
    return result


def main():
    if len(sys.argv) != 6:
        print(__doc__)
        sys.exit(1)

    name, author, base_path, custom_path, out_path = sys.argv[1:6]

    base = load_payload(base_path)
    custom = load_payload(custom_path)

    seen = set()
    merged = []
    for item in base + custom:
        if item not in seen:
            seen.add(item)
            merged.append(item)

    updated = datetime.datetime.utcnow() + datetime.timedelta(hours=8)
    updated_str = updated.strftime("%Y-%m-%d %H:%M:%S")

    header = (
        f"# NAME: {name}\n"
        f"# AUTHOR: {author}\n"
        f"# UPDATED: {updated_str}\n"
        f"# TOTAL: {len(merged)}\n"
        f"# BASE: {len(base)}\n"
        f"# CUSTOM: {len(custom)}\n"
    )

    body = yaml.dump(
        {"payload": merged},
        Dumper=IndentDumper,
        allow_unicode=True,
        sort_keys=False,
        default_flow_style=False,
        width=10**6,
    )

    with open(out_path, "w", encoding="utf-8") as f:
        f.write(header)
        f.write(body)

    print(f"[ok] {out_path}: base={len(base)} custom={len(custom)} total={len(merged)}")


if __name__ == "__main__":
    main()
