from __future__ import annotations

import csv
from pathlib import Path

from capsule_guard.agents import CapsuleAgent
from capsule_guard.charts import write_bar_chart
from capsule_guard.evaluation import evaluate
from capsule_guard.policy import CapsulePolicy, EvidenceQuorumGate
from capsule_guard.scenarios import generate_scenarios


def run_sensitivity_sweep(
    *,
    attack_mode: str,
    repetitions: int,
    noise_memories: int,
    seed: int,
    medium_thresholds: tuple[float, ...],
    topic_thresholds: tuple[float, ...],
) -> list[dict[str, object]]:
    cases = generate_scenarios(
        repetitions=repetitions,
        noise_memories=noise_memories,
        seed=seed,
        attack_mode=attack_mode,
    )
    rows: list[dict[str, object]] = []
    for medium_threshold in medium_thresholds:
        for topic_threshold in topic_thresholds:
            def factory(
                medium_threshold: float = medium_threshold,
                topic_threshold: float = topic_threshold,
            ) -> CapsuleAgent:
                agent = CapsuleAgent()
                agent.policy = CapsulePolicy(topic_overlap_threshold=topic_threshold)
                agent.quorum = EvidenceQuorumGate(medium_threshold=medium_threshold)
                return agent

            metrics = evaluate("intent_capsules", factory, cases)
            rows.append(
                {
                    "medium_threshold": medium_threshold,
                    "topic_threshold": topic_threshold,
                    "attack_success_rate": metrics.attack_success_rate,
                    "unauthorized_risky_action_rate": metrics.unauthorized_risky_action_rate,
                    "benign_accuracy": metrics.benign_accuracy,
                    "false_positive_rate": metrics.false_positive_rate,
                    "security_recall": _security_recall(metrics.attack_success_rate),
                    "benign_precision": _benign_precision(metrics.benign_correct, metrics.false_positives),
                    "calibration_score": _calibration_score(metrics),
                }
            )
    return _mark_recommended(rows)


def write_sensitivity_outputs(
    *,
    attack_mode: str,
    repetitions: int,
    noise_memories: int,
    seed: int,
    medium_thresholds: tuple[float, ...],
    topic_thresholds: tuple[float, ...],
    csv_path: str | Path,
    charts_dir: str | Path,
) -> list[dict[str, object]]:
    rows = run_sensitivity_sweep(
        attack_mode=attack_mode,
        repetitions=repetitions,
        noise_memories=noise_memories,
        seed=seed,
        medium_thresholds=medium_thresholds,
        topic_thresholds=topic_thresholds,
    )
    write_sensitivity_csv(rows, csv_path)
    write_sensitivity_charts(rows, charts_dir)
    return rows


def write_sensitivity_csv(rows: list[dict[str, object]], output_path: str | Path) -> None:
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        path.write_text("", encoding="utf-8")
        return
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def write_sensitivity_charts(rows: list[dict[str, object]], charts_dir: str | Path) -> None:
    path = Path(charts_dir)
    chart_rows = [
        {
            "agent": f"m{row['medium_threshold']}_t{row['topic_threshold']}",
            **row,
        }
        for row in rows
    ]
    write_bar_chart(
        chart_rows,
        path / "sensitivity_attack_success_rate.svg",
        metric="attack_success_rate",
        title="Sensitivity Attack Success Rate",
    )
    write_bar_chart(
        chart_rows,
        path / "sensitivity_unauthorized_risky_action_rate.svg",
        metric="unauthorized_risky_action_rate",
        title="Sensitivity Unauthorized Risky Action Rate",
    )
    write_bar_chart(
        chart_rows,
        path / "sensitivity_benign_accuracy.svg",
        metric="benign_accuracy",
        title="Sensitivity Benign Accuracy",
    )
    write_bar_chart(
        chart_rows,
        path / "sensitivity_calibration_score.svg",
        metric="calibration_score",
        title="Sensitivity Calibration Score",
    )


def _security_recall(attack_success_rate: float) -> float:
    return 1.0 - attack_success_rate


def _benign_precision(benign_correct: int, false_positives: int) -> float:
    denominator = benign_correct + false_positives
    if denominator == 0:
        return 0.0
    return benign_correct / denominator


def _calibration_score(metrics) -> float:
    return (
        (0.50 * _security_recall(metrics.attack_success_rate))
        + (0.30 * metrics.benign_accuracy)
        + (0.20 * _benign_precision(metrics.benign_correct, metrics.false_positives))
        - (0.25 * metrics.unauthorized_risky_action_rate)
        - (0.25 * metrics.false_positive_rate)
    )


def _mark_recommended(rows: list[dict[str, object]]) -> list[dict[str, object]]:
    if not rows:
        return rows
    best_index = max(
        range(len(rows)),
        key=lambda index: (
            float(rows[index]["calibration_score"]),
            float(rows[index]["security_recall"]),
            float(rows[index]["benign_precision"]),
            -float(rows[index]["attack_success_rate"]),
            -float(rows[index]["unauthorized_risky_action_rate"]),
        ),
    )
    for index, row in enumerate(rows):
        row["recommended"] = index == best_index
    return rows
