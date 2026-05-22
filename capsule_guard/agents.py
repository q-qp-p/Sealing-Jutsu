from __future__ import annotations

from pathlib import Path
from typing import Any

from capsule_guard.compiler import CapsuleCompiler
from capsule_guard.intent import IntentParser
from capsule_guard.models import CapsuleDecision, CapsuleStatus, MemoryCapsule, MemorySeed
from capsule_guard.planner import AmbientPlanner, CapsulePlanner
from capsule_guard.policy import (
    CapsulePolicy,
    EvidenceQuorumGate,
    PermissiveQuorumGate,
    PlanAuthorizationGate,
    extract_recommendation,
)
from capsule_guard.risk import action_risk, extract_action
from capsule_guard.store import CapsuleStore


class AmbientMemoryAgent:
    def __init__(self) -> None:
        self.compiler = CapsuleCompiler()
        self.intent_parser = IntentParser()
        self.store = CapsuleStore()
        self.planner = AmbientPlanner()

    def remember(self, seed: MemorySeed) -> None:
        capsule = self.compiler.compile(seed)
        # Baseline deliberately grants full ambient authority so we can measure the risk.
        capsule.status = CapsuleStatus.ACTIVE
        capsule.influence_budget = 1.0
        self.store.add(capsule)

    def answer(self, query: str) -> CapsuleDecision:
        intent = self.intent_parser.parse(query)
        hits = self.store.retrieve(intent, k=4, include_sealed=True)
        capsules = [hit.capsule for hit in hits]
        plan = self.planner.plan(intent, capsules)
        return CapsuleDecision(
            allowed=True,
            reason="ambient_memory_allowed",
            plan=plan,
            retrieved_capsule_ids=tuple(capsule.id for capsule in capsules),
        )


class KeywordFilterAgent(AmbientMemoryAgent):
    def remember(self, seed: MemorySeed) -> None:
        capsule = self.compiler.compile(seed)
        if capsule.status == CapsuleStatus.SEALED:
            self.store.add(capsule)
            return
        capsule.influence_budget = 1.0
        self.store.add(capsule)


class QuarantineOnlyAgent(AmbientMemoryAgent):
    def remember(self, seed: MemorySeed) -> None:
        capsule = self.compiler.compile(seed)
        if capsule.status == CapsuleStatus.SEALED:
            self.store.add(capsule)
            return
        capsule.status = CapsuleStatus.ACTIVE
        capsule.influence_budget = 1.0
        self.store.add(capsule)


class TrustScoreRetrievalAgent(AmbientMemoryAgent):
    def remember(self, seed: MemorySeed) -> None:
        capsule = self.compiler.compile(seed)
        capsule.status = CapsuleStatus.ACTIVE
        capsule.influence_budget = max(capsule.source_authority, 0.05)
        self.store.add(capsule)


class OutputModerationAgent(AmbientMemoryAgent):
    def answer(self, query: str) -> CapsuleDecision:
        decision = super().answer(query)
        if decision.plan.action_risk.value == "high":
            decision.allowed = False
            decision.reason = "output_moderation_blocked_high_risk_action"
        return decision


class CounterfactualMemoryAgent(AmbientMemoryAgent):
    def answer(self, query: str) -> CapsuleDecision:
        decision = super().answer(query)
        intent = self.intent_parser.parse(query)
        hits = self.store.retrieve(intent, k=4, include_sealed=True)
        if len(hits) < 2:
            return decision
        top_capsule = hits[0].capsule
        without_top = [hit.capsule for hit in hits[1:]]
        counterfactual = self.planner.plan(intent, without_top)
        if (
            extract_recommendation(top_capsule.content) == decision.plan.recommendation
            and counterfactual.recommendation != decision.plan.recommendation
            and not (top_capsule.verification_count >= 1 and top_capsule.source_authority >= 0.85)
        ):
            decision.allowed = False
            decision.reason = "counterfactual_memory_shift_detected"
        return decision


class ProvenanceOnlyAgent(AmbientMemoryAgent):
    def remember(self, seed: MemorySeed) -> None:
        capsule = self.compiler.compile(seed)
        # Provenance-only uses source trust as a score but does not enforce topic/action contracts.
        capsule.status = CapsuleStatus.ACTIVE
        capsule.influence_budget = capsule.source_authority
        self.store.add(capsule)


class CapsuleAgent:
    def __init__(
        self,
        retrieval_mode: str = "lexical",
        vector_db_path: str | Path | None = None,
        external_vector_backend: Any | None = None,
    ) -> None:
        self.compiler = CapsuleCompiler()
        self.intent_parser = IntentParser()
        self.store = CapsuleStore(
            retrieval_mode=retrieval_mode,
            vector_db_path=vector_db_path,
            external_vector_backend=external_vector_backend,
        )
        self.policy = CapsulePolicy()
        self.plan_authorizer = PlanAuthorizationGate()
        self.quorum = EvidenceQuorumGate()
        self.planner = CapsulePlanner()

    def remember(self, seed: MemorySeed) -> None:
        self.store.add(self.compiler.compile(seed))

    def answer(self, query: str) -> CapsuleDecision:
        intent = self.intent_parser.parse(query)
        sealed_hits = self._sealed_hits_for_intent(query)
        hits = self.store.retrieve(intent, k=5)
        retrieved = [hit.capsule for hit in hits]
        # Retrieval finds candidates; policy decides whether those candidates are authorized.
        policy_trace = tuple(self.policy.trace(capsule, intent) for capsule in retrieved)
        eligible_ids = {trace.capsule_id for trace in policy_trace if trace.eligible}
        eligible = [capsule for capsule in retrieved if capsule.id in eligible_ids]
        plan = self.planner.plan(intent, eligible)
        if not eligible and any(action_risk(extract_action(capsule.content)).value == "high" for capsule in sealed_hits):
            return CapsuleDecision(
                allowed=False,
                reason="sealed_high_risk_capsule_requires_review",
                plan=plan,
                retrieved_capsule_ids=tuple(capsule.id for capsule in retrieved),
                eligible_capsule_ids=(),
                sealed_capsule_ids=tuple(capsule.id for capsule in sealed_hits),
                policy_trace=policy_trace,
            )
        sealed = tuple(capsule.id for capsule in self.store.all() if capsule.status == CapsuleStatus.SEALED)
        plan_allowed, plan_reason = self.plan_authorizer.allowed(plan, eligible)
        if not plan_allowed:
            return CapsuleDecision(
                allowed=False,
                reason=plan_reason,
                plan=plan,
                retrieved_capsule_ids=tuple(capsule.id for capsule in retrieved),
                eligible_capsule_ids=tuple(capsule.id for capsule in eligible),
                sealed_capsule_ids=sealed,
                policy_trace=policy_trace,
            )
        allowed, reason = self.quorum.allowed(plan, eligible)
        return CapsuleDecision(
            allowed=allowed,
            reason=reason,
            plan=plan,
            retrieved_capsule_ids=tuple(capsule.id for capsule in retrieved),
            eligible_capsule_ids=tuple(capsule.id for capsule in eligible),
            sealed_capsule_ids=sealed,
            policy_trace=policy_trace,
        )

    def _sealed_hits_for_intent(self, query: str) -> list[MemoryCapsule]:
        intent = self.intent_parser.parse(query)
        return [
            hit.capsule
            for hit in self.store.retrieve(intent, k=5, include_sealed=True)
            if hit.capsule.status == CapsuleStatus.SEALED and hit.similarity > 0
        ]


class NoTopicScopeCapsuleAgent(CapsuleAgent):
    def __init__(self) -> None:
        super().__init__()
        self.policy = CapsulePolicy(enforce_topic_scope=False)


class NoQuorumCapsuleAgent(CapsuleAgent):
    def __init__(self) -> None:
        super().__init__()
        self.quorum = PermissiveQuorumGate()


class NoDeniedActionsCapsuleAgent(CapsuleAgent):
    def __init__(self) -> None:
        super().__init__()
        self.policy = CapsulePolicy(enforce_denied_actions=False, enforce_authority_floor=False)
        self.quorum = PermissiveQuorumGate()

    def remember(self, seed: MemorySeed) -> None:
        capsule = self.compiler.compile(seed)
        # Ablation: remove action restrictions to show why denied actions matter.
        capsule.status = CapsuleStatus.ACTIVE
        capsule.denied_actions = frozenset()
        capsule.source_authority = 1.0
        capsule.influence_budget = max(capsule.influence_budget, 1.0)
        self.store.add(capsule)
