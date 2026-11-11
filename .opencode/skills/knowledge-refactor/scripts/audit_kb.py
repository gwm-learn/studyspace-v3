#!/usr/bin/env python3
"""Generic knowledge-base audit.

Usage:
    python3 audit_kb.py <target-dir> [--figure-gaps]

Checks:
- note / SVG counts
- image references resolve
- dead relative links
- forbidden sections (抓包 / 常见坑 / 命令速查)
- frontmatter layer
- glossary presence and 3-column shape
- optional: framework/flow headings without a figure
"""

import argparse
import os
import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

FORBIDDEN = re.compile(r'^## .*(抓包|常见坑|命令速查)')
FLOW_KW = re.compile(
    r'(状态|流程|过程|交互|转发|选举|切换|协商|收敛|升级|中继|缓存|'
    r'封装|分片|握手|会话|时序|步骤|机制|架构|拓扑)')


def is_note(path: Path, root: Path) -> bool:
    if path.suffix != '.md':
        return False
    if path.name == '.readme.md':
        return False
    return 'images' not in path.relative_to(root).parts


def section_has_image(lines, start, end):
    return any('![' in line for line in lines[start:end])


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument('target')
    ap.add_argument('--figure-gaps', action='store_true')
    args = ap.parse_args()

    root = Path(args.target)
    if not root.is_dir():
        print(f'not a directory: {root}', file=sys.stderr)
        return 2

    notes, svgs, refs = [], [], []
    dead, missing_images, forbidden, no_layer, glossary_missing = [], [], [], [], []
    glossary_bad, image_unused = [], []
    gaps = []

    svg_files = {p.resolve() for p in root.rglob('*.svg')}

    for p in sorted(root.rglob('*.md')):
        rel = p.relative_to(root)
        text = p.read_text(encoding='utf-8')
        lines = text.splitlines()

        if is_note(p, root):
            notes.append(p)
            if not (text.startswith('---') and re.search(r'^layer:', text, re.M)):
                no_layer.append(str(rel))
            if '## 名词解释' not in text:
                glossary_missing.append(str(rel))
            else:
                seg = text.split('## 名词解释', 1)[1].split('\n## ', 1)[0]
                rows = [l for l in seg.splitlines() if l.startswith('|')]
                if not rows or '英文全称' not in rows[0]:
                    glossary_bad.append((str(rel), 'header'))
                for l in rows:
                    if l.startswith('| ---'):
                        continue
                    if l.count('|') != 4:
                        glossary_bad.append((str(rel), l))

            # figure gaps at ## level
            heads = [(i, l) for i, l in enumerate(lines) if l.startswith('## ')]
            for idx, (i, l) in enumerate(heads):
                end = heads[idx + 1][0] if idx + 1 < len(heads) else len(lines)
                if FLOW_KW.search(l) and '一句话模型' not in l:
                    if not section_has_image(lines, i, end):
                        gaps.append((str(rel), l))

        for m in re.finditer(r'!\[[^\]]*\]\(([^)]+)\)', text):
            target = m.group(1).strip()
            if target.startswith(('http://', 'https://')):
                continue
            full = (p.parent / target).resolve()
            refs.append(full)
            if not full.exists():
                missing_images.append((str(rel), target))

        for m in re.finditer(r'\]\(([^)#]+)(?:#[^)]*)?\)', text):
            target = m.group(1).strip()
            if target.startswith(('http://', 'https://', 'mailto:')):
                continue
            full = (p.parent / target).resolve()
            if not full.exists():
                dead.append((str(rel), target))

        if is_note(p, root):
            for l in lines:
                if FORBIDDEN.search(l):
                    forbidden.append((str(rel), l))

    for p in root.rglob('*.svg'):
        svgs.append(p)
        if p.resolve() not in {r.resolve() for r in refs}:
            image_unused.append(str(p.relative_to(root)))

    print(f'target: {root}')
    print(f'notes: {len(notes)}')
    print(f'svg: {len(svgs)}')
    print(f'image_refs: {len(refs)}')
    print(f'missing_images: {len(missing_images)}')
    print(f'dead_links: {len(dead)}')
    print(f'forbidden_sections: {len(forbidden)}')
    print(f'missing_layer: {len(no_layer)}')
    print(f'glossary_missing: {len(glossary_missing)}')
    print(f'glossary_bad_rows: {len(glossary_bad)}')
    print(f'unused_svg: {len(image_unused)}')

    for label, items in [
        ('MISSING_IMAGE', missing_images),
        ('DEAD_LINK', dead),
        ('FORBIDDEN', forbidden),
        ('NO_LAYER', no_layer),
        ('NO_GLOSSARY', glossary_missing),
        ('BAD_GLOSSARY', glossary_bad),
        ('UNUSED_SVG', image_unused),
    ]:
        for item in items:
            print(label, item)

    if args.figure_gaps:
        for rel, heading in gaps:
            print('FIGURE_GAP', rel, heading)

    issues = (len(missing_images) + len(dead) + len(forbidden) +
              len(no_layer) + len(glossary_missing) + len(glossary_bad))
    return 1 if issues else 0


if __name__ == '__main__':
    raise SystemExit(main())
