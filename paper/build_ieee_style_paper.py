from __future__ import annotations

import re
from pathlib import Path

import build_research_paper_v3 as base


ROOT = Path(__file__).resolve().parent

OUT_MD = ROOT / "Sealing_Jutsu_IEEE_Style_Paper.md"
OUT_DOCX = ROOT / "Sealing_Jutsu_IEEE_Style_Paper.docx"
OUT_PDF = ROOT / "Sealing_Jutsu_IEEE_Style_Paper.pdf"
OUT_TEX = ROOT / "Sealing_Jutsu_IEEE_Style_Paper.tex"

TITLE = "Intent-Bound Memory Authorization for Persistent LLM-Agent Memory Poisoning"


def ieee_blocks(ctx: dict[str, object]) -> list[tuple[str, object]]:
    workflow: dict[str, dict[str, str]] = ctx["workflow"]  # type: ignore[assignment]
    lifecycle: dict[str, dict[str, str]] = ctx["lifecycle"]  # type: ignore[assignment]
    agentdojo: dict[str, dict[str, str]] = ctx["agentdojo"]  # type: ignore[assignment]
    injec_all: dict[str, dict[str, str]] = ctx["injec_all"]  # type: ignore[assignment]
    injec_dh: dict[str, dict[str, str]] = ctx["injec_dh"]  # type: ignore[assignment]
    injec_ds: dict[str, dict[str, str]] = ctx["injec_ds"]  # type: ignore[assignment]
    live_llm: dict[str, dict[str, str]] = ctx["live_llm"]  # type: ignore[assignment]
    live_models: list[dict[str, str]] = ctx["live_models"]  # type: ignore[assignment]
    generated: dict[str, dict[str, str]] = ctx["generated"]  # type: ignore[assignment]
    advanced: dict[str, dict[str, str]] = ctx["advanced"]  # type: ignore[assignment]

    def m(row: dict[str, str], key: str) -> str:
        return base.metric(row, key)

    def pct(row: dict[str, str], key: str) -> str:
        return base.pct(m(row, key))

    def workflow_row(agent: str) -> list[str]:
        row = workflow[agent]
        return [
            agent,
            pct(row, "attack_success_rate_mean"),
            pct(row, "unauthorized_risky_action_rate_mean"),
            pct(row, "benign_accuracy_mean"),
            pct(row, "false_positive_rate_mean"),
            pct(row, "poison_sealing_rate_mean"),
        ]

    def influence_row(corpus: str, data: dict[str, dict[str, str]]) -> list[str]:
        out_mod = data["output_moderation"]
        cap = data["intent_capsules"]
        return [
            corpus,
            pct(out_mod, "attack_success_rate_mean"),
            pct(out_mod, "poison_influence_rate_mean"),
            pct(cap, "attack_success_rate_mean"),
            pct(cap, "poison_influence_rate_mean"),
            pct(cap, "poison_sealing_rate_mean"),
        ]

    live_model_rows = []
    for row in live_models:
        if row["condition"] == "capsule_filtered_prompt":
            live_model_rows.append(
                [
                    row["model"],
                    str(int(float(row["cases"]))),
                    base.pct(row["planner_attack_success_rate"]),
                    base.pct(row["attack_success_rate"]),
                    base.pct(row["unauthorized_risky_action_rate"]),
                    base.pct(row["raw_parse_error_rate"]),
                ]
            )

    return [
        ("abstract", (
            "Persistent memory gives LLM agents continuity across tasks, but it also turns retrieved memory into a long-lived attack "
            "surface. A poisoned memory injected through web content, tool output, OCR text, summaries, or experience logs can later "
            "resurface as normal context and steer recommendations or tool calls. This paper presents intent-bound memory authorization, "
            "a least-privilege memory control layer implemented in the CapsuleGuard prototype. CapsuleGuard compiles each stored memory "
            "into a capsule containing source type, topic scope, denied actions, authority score, influence budget, verification, lineage, "
            "freshness, and status. The central invariant is that retrieval is not authorization: a memory may be relevant without being "
            "allowed to influence a plan or action. Across a held-out workflow corpus, intent capsules reduce attack success from "
            f"{base.pct(m(workflow['ambient_memory'], 'attack_success_rate_mean'))} for ambient memory to "
            f"{base.pct(m(workflow['intent_capsules'], 'attack_success_rate_mean'))} while preserving "
            f"{base.pct(m(workflow['intent_capsules'], 'benign_accuracy_mean'))} benign accuracy. On converted AgentDojo and InjecAgent "
            "traces, output moderation reaches 0.00% final ASR but still permits 30.00%-90.62% poison influence, whereas intent capsules "
            "reach 0.00% ASR and 0.00% poison influence. Live local LLM planner experiments across llama3, mistral, and phi3 reduce "
            "ambient final ASR of 22.22% to 0.00% under capsule-filtered authorization. The results support memory authorization as a "
            "complementary defense for persistent agent poisoning under the stated threat model."
        )),
        ("keywords", "LLM agents, memory poisoning, prompt injection, least privilege, authorization, long-term memory, tool safety"),
        ("h1", "I. Introduction"),
        ("p", (
            "LLM agents increasingly use long-term memory for personalization, tool reuse, session summaries, and prior-task experience. "
            "This persistent memory is valuable, but it allows adversarial content to survive beyond the conversation in which it was "
            "introduced. The resulting attack is not merely a prompt-injection problem; it is an authority problem. Once retrieved, a "
            "memory may influence planning as if relevance implied permission."
        )),
        ("p", (
            "We argue that memory systems should separate three questions: whether a memory is relevant, where it came from, and what it "
            "is authorized to influence. Existing defenses often focus on suspicious text, source provenance, retrieval ranking, or final "
            "output moderation. Those layers remain useful, but they do not by themselves define action-specific memory authority."
        )),
        ("h2", "Contributions"),
        ("bullets", [
            "We formulate persistent memory poisoning as an ambient-authority failure in LLM-agent memory.",
            "We propose intent-bound capsules that bind each memory to explicit influence constraints.",
            "We implement CapsuleGuard, a reproducible prototype with baselines, stress suites, trace-corpus loading, signed provenance, vector-style retrieval, tool traces, and live LLM planner support.",
            "We introduce poison influence rate to distinguish late output blocking from pre-planning memory authorization.",
            "We evaluate against workflow, lifecycle-gap, converted AgentDojo/InjecAgent, stress-suite, ablation, threshold, and live LLM planner settings.",
        ]),
        ("h1", "II. Background and Related Work"),
        ("p", (
            "Prior work demonstrates that agent memory can be poisoned through knowledge bases, tool output, web-agent context, query-only "
            "interaction, multimodal inputs, self-reinforcing injections, and poisoned experience retrieval. These attacks differ in entry "
            "point, but they share a common failure mode: stored content becomes future steering authority."
        )),
        ("table", (
            "Table I. Defense gap addressed by intent-bound authorization.",
            ["Defense", "Primary check", "Residual gap"],
            [
                ["Keyword filtering", "Suspicious text", "Benign-phrased poison survives."],
                ["Provenance only", "Source label", "Source does not define allowed action influence."],
                ["Trust-score retrieval", "Rank high-trust records", "Trust score is not authorization."],
                ["Output moderation", "Final response/action", "Planner may already be poisoned."],
                ["Intent capsules", "Influence permission", "Complements, rather than replaces, other layers."],
            ],
        )),
        ("h1", "III. Threat Model"),
        ("figure", (base.FIGURES / "figure2_threat_model_v2.png", "Fig. 1. Threat model and trust boundaries.")),
        ("p", (
            "The adversary can inject text through web pages, tool outputs, OCR-visible content, alt text, summaries, experience logs, or "
            "memory import paths. The adversary may use delayed triggers, cross-session activation, semantic paraphrases, split payloads, "
            "or retrieval-collision phrasing. The goal is to alter a recommendation, planning path, memory-derived preference, or medium/"
            "high-risk tool action."
        )),
        ("p", (
            "The adversary cannot directly modify the system prompt, policy code, capsule authorization gate, benchmark labels, tool runtime, "
            "OCR binary, model weights, verified-writer identity, or cryptographic provenance. The core trust boundary is between retrieved "
            "memory as relevance evidence and retrieved memory as authority."
        )),
        ("table", (
            "Table II. Security objectives.",
            ["Objective", "Requirement"],
            [
                ["Recommendation integrity", "Unauthorized memory must not choose attacker-preferred options."],
                ["Action safety", "Medium/high-risk actions require explicit supporting authority."],
                ["Lifecycle integrity", "Derived summaries must not launder weak memory authority."],
                ["Auditability", "Blocked or sealed memories remain traceable."],
                ["Utility", "Benign memory should remain useful."],
            ],
        )),
        ("h1", "IV. Intent-Bound Memory Capsules"),
        ("figure", (base.FIGURES / "figure1_architecture_v2.png", "Fig. 2. CapsuleGuard architecture.")),
        ("p", (
            "A capsule is a memory record plus an influence contract. The contract stores the source class, memory kind, allowed topics, "
            "denied actions, source authority, influence budget, verification count, lineage, freshness, and status. A retrieved memory can "
            "be useful context while still being forbidden from authorizing a purchase, email, deletion, data sharing, or recommendation."
        )),
        ("table", (
            "Table III. Capsule controls.",
            ["Control", "Purpose"],
            [
                ["Topic scope", "Limits influence to matching user intents."],
                ["Denied actions", "Prevents weak sources from authorizing risky operations."],
                ["Authority floor", "Requires stronger source authority for higher-risk actions."],
                ["Influence budget", "Caps decision weight per memory."],
                ["Evidence quorum", "Requires independent support for risky plans."],
                ["Lineage/freshness", "Caps derived or stale records."],
                ["Sealing", "Keeps suspicious memories auditable but ineligible."],
            ],
        )),
        ("figure", (base.FIGURES / "figure3_trust_rules_v2.png", "Fig. 3. Memory trust and influence rule set.")),
        ("h1", "V. Prototype"),
        ("p", (
            "CapsuleGuard is implemented in Python in the Sealing-Jutsu repository. The prototype includes capsule compilation, policy gates, "
            "baseline agents, scenario generation, external trace-corpus loading, signed provenance, vector-style retrieval, safe tool traces, "
            "CSV/JSONL reporting, charts, and a live LLM planner harness. The current test suite contains 163 passing tests."
        )),
        ("h1", "VI. Evaluation Methodology"),
        ("p", (
            "We compare intent capsules against ambient memory, keyword filtering, quarantine-only retrieval, trust-score retrieval, provenance-"
            "only retrieval, counterfactual memory, output moderation, and semantic output judging. We report attack success rate (ASR), "
            "unauthorized risky action rate, poison influence rate, benign accuracy, false positive rate, sealing rate, and latency."
        )),
        ("p", (
            "Poison influence rate counts poisoned cases where poisoned memory is used by the planner and the planner selects the attacker "
            "target before final output blocking. This metric is central because a defense can block the final action while still allowing "
            "the planner to be compromised."
        )),
        ("h1", "VII. Results"),
        ("h2", "A. Held-Out Workflow Corpus"),
        ("table", (
            "Table IV. Held-out workflow-corpus result.",
            ["Agent", "ASR", "Risky", "Benign", "FPR", "Seal"],
            [
                workflow_row("ambient_memory"),
                workflow_row("keyword_filter"),
                workflow_row("output_moderation"),
                workflow_row("provenance_only"),
                workflow_row("counterfactual_memory"),
                workflow_row("intent_capsules"),
            ],
        )),
        ("p", (
            "Intent capsules are the only tested defense in this split to jointly achieve 0.00% ASR, 0.00% risky action, 100.00% benign "
            "accuracy, and 0.00% FPR."
        )),
        ("h2", "B. Poison Influence and Lifecycle Gap"),
        ("table", (
            "Table V. Lifecycle-gap result.",
            ["Agent", "ASR", "Risky", "Influence", "Benign"],
            [
                [
                    "output_moderation",
                    pct(lifecycle["output_moderation"], "attack_success_rate_mean"),
                    pct(lifecycle["output_moderation"], "unauthorized_risky_action_rate_mean"),
                    pct(lifecycle["output_moderation"], "poison_influence_rate_mean"),
                    pct(lifecycle["output_moderation"], "benign_accuracy_mean"),
                ],
                [
                    "semantic_output_judge",
                    pct(lifecycle["semantic_output_judge"], "attack_success_rate_mean"),
                    pct(lifecycle["semantic_output_judge"], "unauthorized_risky_action_rate_mean"),
                    pct(lifecycle["semantic_output_judge"], "poison_influence_rate_mean"),
                    pct(lifecycle["semantic_output_judge"], "benign_accuracy_mean"),
                ],
                [
                    "ablation_no_denied_actions",
                    pct(lifecycle["ablation_no_denied_actions"], "attack_success_rate_mean"),
                    pct(lifecycle["ablation_no_denied_actions"], "unauthorized_risky_action_rate_mean"),
                    pct(lifecycle["ablation_no_denied_actions"], "poison_influence_rate_mean"),
                    pct(lifecycle["ablation_no_denied_actions"], "benign_accuracy_mean"),
                ],
                [
                    "intent_capsules",
                    pct(lifecycle["intent_capsules"], "attack_success_rate_mean"),
                    pct(lifecycle["intent_capsules"], "unauthorized_risky_action_rate_mean"),
                    pct(lifecycle["intent_capsules"], "poison_influence_rate_mean"),
                    pct(lifecycle["intent_capsules"], "benign_accuracy_mean"),
                ],
            ],
        )),
        ("h2", "C. Converted AgentDojo/InjecAgent Traces"),
        ("table", (
            "Table VI. Converted external trace-corpus result.",
            ["Corpus", "Out ASR", "Out infl.", "Cap ASR", "Cap infl.", "Cap seal"],
            [
                influence_row("AgentDojo all", agentdojo),
                influence_row("InjecAgent all", injec_all),
                influence_row("InjecAgent DH", injec_dh),
                influence_row("InjecAgent DS", injec_ds),
            ],
        )),
        ("p", (
            "On converted AgentDojo and InjecAgent traces, output moderation and semantic judges can reach 0.00% final ASR but still allow "
            "30.00%-90.62% poison influence. Intent capsules reach 0.00% ASR and 0.00% poison influence across all converted splits."
        )),
        ("h2", "D. Stress and Live LLM Results"),
        ("table", (
            "Table VII. Stress-suite examples.",
            ["Suite", "Ambient ASR", "Provenance ASR", "Capsule ASR", "Capsule benign"],
            [
                [
                    "Generated holdout",
                    pct(generated["ambient_memory"], "attack_success_rate_mean"),
                    pct(generated["provenance_only"], "attack_success_rate_mean"),
                    pct(generated["intent_capsules"], "attack_success_rate_mean"),
                    pct(generated["intent_capsules"], "benign_accuracy_mean"),
                ],
                [
                    "Advanced suite",
                    pct(advanced["ambient_memory"], "attack_success_rate_mean"),
                    pct(advanced["provenance_only"], "attack_success_rate_mean"),
                    pct(advanced["intent_capsules"], "attack_success_rate_mean"),
                    pct(advanced["intent_capsules"], "benign_accuracy_mean"),
                ],
            ],
        )),
        ("table", (
            "Table VIII. Medium live LLM planner result.",
            ["Condition", "Rows", "Tempted", "Final ASR", "Risky", "Raw parse"],
            [
                [
                    "ambient",
                    str(int(float(live_llm["ambient_prompt"]["cases"]))),
                    base.pct(live_llm["ambient_prompt"]["planner_attack_success_rate"]),
                    base.pct(live_llm["ambient_prompt"]["attack_success_rate"]),
                    base.pct(live_llm["ambient_prompt"]["unauthorized_risky_action_rate"]),
                    base.pct(live_llm["ambient_prompt"]["raw_parse_error_rate"]),
                ],
                [
                    "capsule-filtered",
                    str(int(float(live_llm["capsule_filtered_prompt"]["cases"]))),
                    base.pct(live_llm["capsule_filtered_prompt"]["planner_attack_success_rate"]),
                    base.pct(live_llm["capsule_filtered_prompt"]["attack_success_rate"]),
                    base.pct(live_llm["capsule_filtered_prompt"]["unauthorized_risky_action_rate"]),
                    base.pct(live_llm["capsule_filtered_prompt"]["raw_parse_error_rate"]),
                ],
            ],
        )),
        ("table", (
            "Table IX. Defended live LLM result by model.",
            ["Model", "Rows", "Tempted", "Final ASR", "Risky", "Raw parse"],
            live_model_rows,
        )),
        ("h1", "VIII. Discussion"),
        ("p", (
            "The evaluation suggests that ASR alone is insufficient for memory-security evaluation. Output moderation may prevent a visible "
            "unsafe action while leaving poisoned memory influence intact. Intent-bound authorization instead rejects unauthorized influence "
            "before the memory becomes planning authority."
        )),
        ("h1", "IX. Limitations"),
        ("bullets", [
            "The highest-volume benchmark uses a deterministic planner, although live LLM results are included as a realism check.",
            "Several corpora are generated, converted, or synthetic rather than collected from deployed user workflows.",
            "The raw-image multimodal/OCR pipeline is not fully evaluated.",
            "The prototype assumes policy code, verified identities, and cryptographic attestations are not compromised.",
            "The results support a defense layer under the stated threat model; they do not prove universal memory-poisoning security.",
        ]),
        ("h1", "X. Conclusion"),
        ("p", (
            "Persistent memory poisoning exploits the gap between retrieval and authority. Intent-bound memory capsules close this gap by "
            "requiring memories to carry explicit influence contracts. CapsuleGuard's results show that memory authorization can reduce both "
            "final attack success and poisoned planning influence while preserving benign utility in the tested prototype."
        )),
        ("h1", "References"),
        ("references", [
            "M. A. Ferrag, A. Lakas, N. Tihanyi, and M. Debbah, Securing LLM agents: From prompt sanitization to autonomous red teaming and beyond, Internet of Things and Cyber-Physical Systems, 2025.",
            "J. Qian, Visual Inception: Compromising Long-term Planning in Agentic Recommenders via Multimodal Memory Poisoning, arXiv, 2026.",
            "X. Yang, Y. He, S. Ji, B. Hooi, and J. S. Dong, Zombie Agents: Persistent Control of Self-Evolving LLM Agents via Self-Reinforcing Injections, arXiv, 2026.",
            "Z. Chen, Z. Xiang, C. Xiao, D. Song, and B. Li, AgentPoison: Red-teaming LLM Agents via Poisoning Memory or Knowledge Bases, arXiv, 2024.",
            "A. S. Patlan, A. Hebbar, P. Viswanath, and P. Mittal, Context manipulation attacks: Web agents are susceptible to corrupted memory, arXiv, 2025.",
            "Z. Xu, X. Zhu, Y. Yao, M. Xue, and Y. Song, From Storage to Steering: Memory Control Flow Attacks on LLM Agents, arXiv, 2026.",
            "H. Tian, Z. Sha, J. Wang, Y. Liu, Z. Huang, and X. Huang, InjecMEM: Memory Injection Attack on LLM Agent Memory Systems, OpenReview, 2025.",
            "S. S. Srivastava and H. He, MemoryGraft: Persistent Compromise of LLM Agents via Poisoned Experience Retrieval, arXiv, 2025.",
            "S. Dong et al., Memory Injection Attacks on LLM Agents via Query-Only Interaction, arXiv, 2025.",
            "OWASP Foundation, OWASP Top 10 for Large Language Model Applications, 2025.",
            "A. Jain and S. Suryawanshi, Sealing-Jutsu: CapsuleGuard prototype, https://github.com/Mr-Akuma/Sealing-Jutsu.",
        ]),
    ]


def tex_escape(text: str) -> str:
    replacements = {
        "\\": r"\textbackslash{}",
        "&": r"\&",
        "%": r"\%",
        "$": r"\$",
        "#": r"\#",
        "_": r"\_",
        "{": r"\{",
        "}": r"\}",
        "~": r"\textasciitilde{}",
        "^": r"\textasciicircum{}",
    }
    return "".join(replacements.get(ch, ch) for ch in str(text))


def tex_table(caption: str, headers: list[str], rows: list[list[str]]) -> str:
    caption = re.sub(r"^Table\s+[IVX]+\.\s*", "", caption)
    cols = "l" * len(headers)
    out = [r"\begin{table}[t]", r"\centering", r"\scriptsize", rf"\caption{{{tex_escape(caption)}}}", rf"\begin{{tabular}}{{{cols}}}", r"\hline"]
    out.append(" & ".join(tex_escape(h) for h in headers) + r" \\")
    out.append(r"\hline")
    for row in rows:
        out.append(" & ".join(tex_escape(c) for c in row) + r" \\")
    out.extend([r"\hline", r"\end{tabular}", r"\end{table}"])
    return "\n".join(out)


def write_tex(blocks: list[tuple[str, object]]) -> None:
    abstract = ""
    keywords = ""
    body: list[str] = []
    refs: list[str] = []
    for kind, payload in blocks:
        if kind == "abstract":
            abstract = tex_escape(str(payload))
        elif kind == "keywords":
            keywords = tex_escape(str(payload))
        elif kind == "h1":
            title = re.sub(r"^[IVX]+\.\s*", "", str(payload))
            if title.lower() == "references":
                continue
            body.append(rf"\section{{{tex_escape(title)}}}")
        elif kind == "h2":
            title = re.sub(r"^[A-Z]\.\s*", "", str(payload))
            body.append(rf"\subsection{{{tex_escape(title)}}}")
        elif kind == "p":
            body.append(tex_escape(str(payload)) + "\n")
        elif kind == "bullets":
            body.append(r"\begin{itemize}")
            body.extend(rf"\item {tex_escape(item)}" for item in payload)
            body.append(r"\end{itemize}")
        elif kind == "table":
            caption, headers, data = payload
            body.append(tex_table(caption, headers, data))
        elif kind == "figure":
            path, caption = payload
            caption = re.sub(r"^Fig\.\s+\d+\.\s*", "", str(caption))
            rel = path.relative_to(ROOT).as_posix()
            body.append(
                "\n".join(
                    [
                        r"\begin{figure}[t]",
                        r"\centering",
                        rf"\includegraphics[width=\linewidth]{{\detokenize{{{rel}}}}}",
                        rf"\caption{{{tex_escape(caption)}}}",
                        r"\end{figure}",
                    ]
                )
            )
        elif kind == "references":
            refs = list(payload)

    ref_lines = [r"\begin{thebibliography}{99}"]
    for idx, ref in enumerate(refs, 1):
        ref_lines.append(rf"\bibitem{{ref{idx}}} {tex_escape(ref)}")
    ref_lines.append(r"\end{thebibliography}")

    tex = rf"""\documentclass[conference]{{IEEEtran}}
\usepackage{{graphicx}}
\usepackage{{booktabs}}
\usepackage{{array}}
\usepackage{{url}}
\title{{{tex_escape(TITLE)}}}
\author{{
\IEEEauthorblockN{{Akshay Jain}}
\IEEEauthorblockA{{Independent Researcher\\
Email: jakshay623@gmail.com}}
\and
\IEEEauthorblockN{{Sujit Suryawanshi}}
\IEEEauthorblockA{{Independent Researcher\\
Email: sujitsuryawanshi987@gmail.com}}
}}
\begin{{document}}
\maketitle
\begin{{abstract}}
{abstract}
\end{{abstract}}
\begin{{IEEEkeywords}}
{keywords}
\end{{IEEEkeywords}}

{chr(10).join(body)}

{chr(10).join(ref_lines)}
\end{{document}}
"""
    OUT_TEX.write_text(tex, encoding="utf-8")


def main() -> None:
    ctx = base.build_context()
    blocks = ieee_blocks(ctx)
    base.TITLE = TITLE
    base.OUT_MD = OUT_MD
    base.OUT_DOCX = OUT_DOCX
    base.OUT_PDF = OUT_PDF
    base.write_markdown(blocks)
    base.build_docx(blocks)
    base.build_pdf(blocks)
    write_tex(blocks)
    print(f"wrote {OUT_MD}")
    print(f"wrote {OUT_DOCX}")
    print(f"wrote {OUT_PDF}")
    print(f"wrote {OUT_TEX}")


if __name__ == "__main__":
    main()
