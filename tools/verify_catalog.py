#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""校验 catalog 自签名与每个课程包的 SHA-256。

为什么单独做成工具：`sync_pages_assets.py` 会在同步时顺带校验，但那是
「生成产物」的副作用；发布前需要一条**只读**的独立校验命令，能单独跑、
能在 CI 里作为独立门禁，失败时明确告诉你是哪个包对不上。

退出码：0 全部一致；1 有不一致或文件缺失。
"""
import hashlib
import json
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
CATALOG = ROOT / "catalog.json"
PACKS = ROOT / "content_packs"

SHA_FIELD = re.compile(r'"sha256"\s*:\s*"[0-9a-f]{64}"')


def strip_self_sha(text: str) -> str:
    """与 ContentCenter.stripSelfSha 一致：只剥离顶层（第一次出现）的 sha256。"""
    return SHA_FIELD.sub('"sha256": ""', text, count=1)


def main() -> int:
    if not CATALOG.exists():
        print("[FAIL] catalog.json 不存在")
        return 1

    text = CATALOG.read_text(encoding="utf-8")
    try:
        data = json.loads(text)
    except json.JSONDecodeError as exc:
        print(f"[FAIL] catalog.json 不是合法 JSON：{exc}")
        return 1

    problems = []

    # 1) 自签名
    declared = data.get("sha256", "")
    calc = hashlib.sha256(strip_self_sha(text).encode("utf-8")).hexdigest()
    if not declared:
        problems.append("catalog 缺少顶层 sha256 自签名")
    elif calc != declared:
        problems.append(f"catalog 自签名不符：声明 {declared[:16]}… 实算 {calc[:16]}…")

    # 2) 每个包
    packs = data.get("packs", [])
    if not packs:
        problems.append("catalog.packs 为空")
    for p in packs:
        pid = p.get("id", "?")
        f = PACKS / f"{pid}.json"
        if not f.exists():
            problems.append(f"{pid}: 课程包文件缺失（{f.name}）")
            continue
        actual = hashlib.sha256(f.read_bytes()).hexdigest()
        expected = p.get("sha256", "")
        if not expected:
            problems.append(f"{pid}: catalog 未登记 sha256")
        elif actual != expected:
            problems.append(f"{pid}: sha256 不符（声明 {expected[:12]}… 实算 {actual[:12]}…）")
        # 语言字段必填，否则语言中心无法判断运行时
        if not p.get("lang"):
            problems.append(f"{pid}: 缺少 lang 字段")

    if problems:
        print(f"[FAIL] 发现 {len(problems)} 个问题：")
        for x in problems:
            print(f"  - {x}")
        return 1

    print(f"[OK] catalog 自签名有效，{len(packs)} 个课程包哈希全部一致")
    for p in packs:
        print(f"    {p['id']:16} {p.get('lang', '-'):12} v{p.get('version', '?')}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
