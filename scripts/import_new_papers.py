#!/usr/bin/env python3
"""合并 data/papers_to_add.csv 至当前仓库 data/papers.csv；保留已有记录与状态，支持重复执行。"""
from __future__ import annotations
import argparse
import csv
import re
from pathlib import Path

ROOT=Path(__file__).resolve().parent.parent
BASE=ROOT/'data/papers.csv'
ADD=ROOT/'data/papers_to_add.csv'

def read_csv(path):
    with path.open('r',encoding='utf-8-sig',newline='') as f:
        reader=csv.DictReader(f)
        return list(reader.fieldnames or []), list(reader)

def arxiv_key(url):
    m=re.search(r'arxiv\.org/(?:abs|pdf)/([0-9]{4}\.[0-9]{4,5})',url or '',re.I)
    return m.group(1) if m else (url or '').strip().lower()

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--dry-run',action='store_true',help='仅检查，不写入')
    args=ap.parse_args()
    if not BASE.exists() or not ADD.exists():
        raise SystemExit('缺少 data/papers.csv 或 data/papers_to_add.csv。请先在仓库根目录解压全部增量文件。')
    fields,existing=read_csv(BASE)
    incoming_fields,incoming=read_csv(ADD)
    if set(incoming_fields)-set(fields):
        raise SystemExit('当前 data/papers.csv 的列缺失；请核对模板字段。')
    known_ids={r['id'].strip().casefold() for r in existing}
    known_urls={arxiv_key(r.get('paper_url')) for r in existing if r.get('paper_url')}
    added=[];skipped=[]
    for r in incoming:
        paper_id=r['id'].strip();paper_key=arxiv_key(r.get('paper_url'))
        if paper_id.casefold() in known_ids or paper_key in known_urls:
            skipped.append(paper_id)
            continue
        existing.append({k:r.get(k,'') for k in fields})
        known_ids.add(paper_id.casefold());known_urls.add(paper_key);added.append(paper_id)
    print('新增：'+(', '.join(added) if added else '无'))
    print('跳过（已存在）：'+(', '.join(skipped) if skipped else '无'))
    print('合并后总论文数：'+str(len(existing)))
    if args.dry_run:
        return
    if added:
        with BASE.open('w',encoding='utf-8-sig',newline='') as f:
            w=csv.DictWriter(f,fieldnames=fields,extrasaction='ignore')
            w.writeheader();w.writerows(existing)
        print('已更新 data/papers.csv；原有记录与阅读/复现状态均保留。')
    generator=ROOT/'scripts/update_dashboard.py'
    if generator.exists():
        import subprocess,sys
        subprocess.run([sys.executable,str(generator)],cwd=ROOT,check=True)
        print('已刷新 README、SVG 进度图和 HTML 看板。')
    else:
        print('未找到自动看板脚本，可稍后自行刷新。')
if __name__=='__main__':
    main()
