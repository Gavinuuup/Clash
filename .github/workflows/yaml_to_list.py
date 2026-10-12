#!/usr/bin/env python3
"""
把 Clash YAML 规则集转成纯文本 list。
用法: yaml_to_list.py <in.yaml> <out.list>
"""
import sys
import yaml


def normalize_to_text(raw):
    """把一条规则转成 text 写法，返回 None 表示丢弃。"""
    s = str(raw).strip()
    if not s or s.startswith("#"):
        return None

    s = s.rstrip(",").strip()
    if not s:
        return None

    # DOMAIN-SUFFIX,x  ->  +.x
    if s.upper().startswith("DOMAIN-SUFFIX"):
        parts = s.split(",", 1)
        if len(parts) == 2:
            domain = parts[1].strip().lstrip("+.")
            return f"+.{domain}"

    # DOMAIN,x  ->  x
    if s.upper().startswith("DOMAIN,"):
        parts = s.split(",", 1)
        if len(parts) == 2:
            return parts[1].strip()

    # 其他规则原样保留，只去掉逗号周围空格
    if "," in s:
        parts = [p.strip() for p in s.split(",")]
        s = ",".join(parts)

    return s


def main():
    if len(sys.argv) != 3:
        print(__doc__)
        sys.exit(1)

    in_path, out_path = sys.argv[1], sys.argv[2]

    with open(in_path, encoding="utf-8") as f:
        data = yaml.safe_load(f) or {}

    payload = data.get("payload", []) or []

    lines = []
    seen = set()
    for item in payload:
        norm = normalize_to_text(item)
        if norm is None:
            continue
        if norm in seen:
            continue
        seen.add(norm)
        lines.append(norm)

    with open(out_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
        if lines:
            f.write("\n")

    print(f"[ok] {out_path}: {len(lines)} lines")


if __name__ == "__main__":
    main()
