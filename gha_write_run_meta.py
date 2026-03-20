#!/usr/bin/env python3
import argparse
import json
import pathlib
import re

FIT_RE = re.compile(r'(?:Fitness_full \(makespan\)|Objective \(full\) makespan|Makespan:)\s*[: ]\s*([0-9]+(?:\.[0-9]+)?)')
MV_RE = re.compile(r'best multi-visit makespan:\s*([0-9]+(?:\.[0-9]+)?)', flags=re.IGNORECASE)


def extract_metrics(log_path: pathlib.Path):
    if not log_path.exists():
        return None, None
    txt = log_path.read_text(encoding='utf-8', errors='ignore')
    vals = [float(x) for x in FIT_RE.findall(txt)]
    mv_vals = [float(x) for x in MV_RE.findall(txt)]
    return (min(vals) if vals else None, min(mv_vals) if mv_vals else None)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--results-dir', required=True)
    ap.add_argument('--base', required=True)
    ap.add_argument('--a', required=True, type=float)
    ap.add_argument('--l', required=True, type=float)
    ap.add_argument('--reps', required=True, type=int)
    ap.add_argument('--job-id', required=True, type=int)
    ap.add_argument('--instance', required=True)
    args = ap.parse_args()

    results_dir = pathlib.Path(args.results_dir)
    for idx in range(1, args.reps + 1):
        log_name = f"{args.base}_A{int(args.a) if args.a.is_integer() else args.a}_L{int(args.l) if args.l.is_integer() else args.l}_r{idx}.log"
        log_path = results_dir / log_name
        best_fit, best_mv = extract_metrics(log_path)
        meta = {
            'job_id': args.job_id,
            'run_index': idx,
            'instance': args.instance,
            'A': args.a,
            'L': args.l,
            'best_fitness': best_fit,
            'best_multi_fitness': best_mv,
            'log': log_name,
        }
        out_path = results_dir / f'meta_run{idx}.json'
        out_path.write_text(json.dumps(meta, indent=2), encoding='utf-8')


if __name__ == '__main__':
    main()
