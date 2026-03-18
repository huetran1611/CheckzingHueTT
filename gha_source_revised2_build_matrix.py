from __future__ import annotations

import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent
DEFAULT_CONFIG = ROOT / "source_revised2_c201_batch.yml"


def _load_config(path: Path) -> dict[str, Any]:
    text = path.read_text(encoding="utf-8")
    try:
        data = json.loads(text)
    except json.JSONDecodeError:
        import yaml  # type: ignore

        data = yaml.safe_load(text)
    if not isinstance(data, dict):
        raise ValueError("Config root must be an object.")
    return data


def _discover_instances(patterns: list[str]) -> list[Path]:
    import glob

    found: list[Path] = []
    seen: set[str] = set()
    for pattern in patterns:
        for match in sorted(glob.glob(pattern)):
            resolved = str(Path(match).resolve())
            if resolved not in seen:
                seen.add(resolved)
                found.append(Path(resolved))
    return found


def build_matrix(config_path: Path) -> list[dict[str, Any]]:
    cfg = _load_config(config_path)
    patterns = cfg.get("instance_patterns", [])
    if not isinstance(patterns, list) or not patterns:
        raise ValueError("Config must define a non-empty instance_patterns list.")

    instances = _discover_instances(patterns)
    a_values = cfg.get("A", [4, 8])
    l_values = cfg.get("L", [60, 90, 120])
    runs_per_config = int(cfg.get("runs_per_config", 3))
    tasks: list[dict[str, Any]] = []
    job_id = 0
    for instance in instances:
        group = "cluster" if "equal_cluster" in instance.as_posix() else "random"
        for a in a_values:
            for l_value in l_values:
                for run_idx in range(1, runs_per_config + 1):
                    job_id += 1
                    tasks.append(
                        {
                            "job_id": job_id,
                            "instance_group": group,
                            "instance_path": instance.as_posix(),
                            "instance_name": instance.name,
                            "A": a,
                            "L": l_value,
                            "run_index": run_idx,
                        }
                    )
    return tasks


def main() -> None:
    import argparse

    parser = argparse.ArgumentParser(description="Build GitHub Actions matrix for Source_revised2 batch runs.")
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG)
    args = parser.parse_args()
    tasks = build_matrix(args.config.resolve())
    print(json.dumps(tasks, ensure_ascii=False, separators=(",", ":")))


if __name__ == "__main__":
    main()
