#!/usr/bin/env python3
"""Generate/check counts and an SVG from the README literature table only."""
from __future__ import annotations

import argparse
import html
import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parent.parent
BEGIN = '<!-- learning-progress:start -->'
END = '<!-- learning-progress:end -->'
STATES = ('已读完', '阅读中', '待读')


def read_papers(readme):
    section = readme.split('## 文献与笔记\n', 1)[1].split('\n## ', 1)[0]
    papers = []
    seen = set()
    for line in section.splitlines():
        if not line.startswith('|'):
            continue
        cells = [cell.strip() for cell in line.strip('|').split('|')]
        if cells[0] == '论文' or re.fullmatch(r'[-: ]+', cells[0]):
            continue
        if len(cells) != 7:
            raise ValueError(f'Expected 7 columns: {line}')
        paper_id, year, category, status, note, source, experiment = cells
        if paper_id.casefold() in seen:
            raise ValueError(f'Duplicate paper: {paper_id}')
        seen.add(paper_id.casefold())
        state = next((s for s in STATES if status == s or status.startswith(s + '（')), None)
        if state is None:
            raise ValueError(f'Unknown reading status: {paper_id}: {status}')
        for target in re.findall(r'\]\(([^)]+)\)', note + ' ' + experiment):
            if not re.match(r'https?://', target) and not (ROOT / target.split('#')[0]).exists():
                raise ValueError(f'Missing reference: {paper_id}: {target}')
        papers.append(dict(id=paper_id, year=year, category=category, reading_status=status,
                           state=state, note=note, source=source, experiment=experiment))
    if not papers:
        raise ValueError('Literature table is empty')
    return papers


def render_svg(counts, total):
    colors = ('#16826c', '#c57b19', '#dbe3ed')
    labels = ('Guided reading complete', 'Reading in progress', 'To read')
    items = ['<svg xmlns="http://www.w3.org/2000/svg" width="800" height="170" viewBox="0 0 800 170" role="img" aria-labelledby="title desc">',
             f'<title id="title">Paper reading progress: {total} papers</title>',
             '<desc id="desc">' + html.escape(', '.join(f'{s}: {counts[s]}' for s in STATES)) + '. Reading status does not indicate experiment completion.</desc>',
             '<rect width="800" height="170" rx="12" fill="#f7f9fc"/>',
             '<g font-family="Segoe UI, Arial, sans-serif" fill="#203047">',
             f'<text x="24" y="32" font-size="19" font-weight="600">Paper reading progress · {total} papers</text>']
    x = 24.0
    for state, color in zip(STATES, colors):
        width = 752 * counts[state] / total
        if width:
            items.append(f'<rect x="{x:.2f}" y="50" width="{width:.2f}" height="24" fill="{color}"/>')
        x += width
    for i, (state, color, label) in enumerate(zip(STATES, colors, labels)):
        left = 24 + i * 260
        items.extend([f'<rect x="{left}" y="96" width="12" height="12" fill="{color}"/>',
                      f'<text x="{left + 19}" y="107" font-size="13">{label}: {counts[state]}</text>'])
    items.extend(['<text x="24" y="144" font-size="13">Guided reading ≠ independent mastery or experiment reproduction.</text>', '</g>', '</svg>'])
    return '\n'.join(items) + '\n'


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument('--write', action='store_true', help='Refresh README totals, JSON and SVG')
    mode.add_argument('--check', action='store_true', help='Check generated files (default)')
    args = parser.parse_args()
    readme_path = ROOT / 'README.md'
    readme = readme_path.read_text(encoding='utf-8')
    papers = read_papers(readme)
    counts = {state: sum(p['state'] == state for p in papers) for state in STATES}
    total = len(papers)
    with_notes = sum('](' in p['note'] for p in papers)
    totals = f'已读完 {counts["已读完"]} 篇，阅读中 {counts["阅读中"]} 篇，待读 {counts["待读"]} 篇'
    done = '、'.join(p['id'] for p in papers if p['state'] == '已读完')
    summary = (f'{BEGIN}\n**共 {total} 篇：{with_notes} 篇已有笔记或导读入口，{total - with_notes} 篇候选；{totals}。**\n\n'
               f'已读完名单：{done}。统计口径是一轮引导阅读/讲解完成；独立掌握、答题与实验复现分别记录。\n\n'
               f'![论文阅读进度](assets/learning_progress.svg)\n{END}')
    if readme.count(BEGIN) != 1 or readme.count(END) != 1:
        raise ValueError('README must have exactly one progress marker pair')
    updated = re.sub(re.escape(BEGIN) + r'.*?' + re.escape(END), lambda _: summary, readme, flags=re.S)
    updated, matches = re.subn(r'^\| 文献整理 \|.*$',
                               f'| 文献整理 | 共 {total} 篇；{totals} | [完整表格](#文献与笔记) · [原 13 篇目录](研/README.md) |',
                               updated, flags=re.M)
    if matches != 1:
        raise ValueError('Expected one literature summary row')
    data = {'source': 'README.md#文献与笔记', 'scope': 'guided_reading_only', 'total': total,
            'with_notes': with_notes, 'counts': counts, 'papers': papers}
    outputs = {readme_path: updated,
               ROOT / 'data/learning_progress.json': json.dumps(data, ensure_ascii=False, indent=2) + '\n',
               ROOT / 'assets/learning_progress.svg': render_svg(counts, total)}
    stale = []
    for path, content in outputs.items():
        if args.write:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content, encoding='utf-8', newline='\n')
        elif not path.exists() or path.read_text(encoding='utf-8') != content:
            stale.append(path.relative_to(ROOT).as_posix())
    print(f'Total={total}; ' + '; '.join(f'{k}={v}' for k, v in counts.items()))
    if stale:
        raise SystemExit('Stale generated files: ' + ', '.join(stale) + '\nRun: python scripts/update_learning_progress.py --write')
    print('Updated.' if args.write else 'Progress files are consistent; no duplicate paper IDs.')


if __name__ == '__main__':
    main()
