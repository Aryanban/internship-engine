"""
Gate 1: Deterministic Ingestion & Filtering Engine
Evaluates jobs locally in < 1ms before any LLM API is invoked.
"""

from dataclasses import dataclass
from typing import Optional, Tuple
import yaml
from pathlib import Path

CONFIG_PATH = Path(__file__).parent.parent / "config" / "filters.yaml"

@dataclass
class FilterResult:
    passed: bool
    reason: str
    is_remote: bool
    detected_level: str
    detected_role: str

class Gate1Filter:
    def __init__(self, config_path: Path = CONFIG_PATH):
        with open(config_path, "r", encoding="utf-8") as f:
            self.config = yaml.safe_load(f)

    def evaluate(self, title: str, location: str, jd_text: str = "") -> FilterResult:
        title_lower = title.lower()
        location_lower = location.lower()
        full_text_lower = f"{title_lower} {jd_text.lower()}"

        # 1. Level Exclusions
        for excluded_lvl in self.config.get("level_exclude", []):
            if excluded_lvl in title_lower:
                return FilterResult(
                    passed=False,
                    reason=f"Excluded level in title: '{excluded_lvl}'",
                    is_remote=False,
                    detected_level=excluded_lvl,
                    detected_role=""
                )

        # 2. Level Inclusions
        matched_level = None
        for inc_lvl in self.config.get("level_include", []):
            if inc_lvl in title_lower:
                matched_level = inc_lvl
                break

        # If title doesn't state level, look for intern/student in first 300 chars of JD
        if not matched_level:
            for inc_lvl in self.config.get("level_include", []):
                if inc_lvl in full_text_lower[:500]:
                    matched_level = inc_lvl
                    break

        if not matched_level:
            return FilterResult(
                passed=False,
                reason="No entry-level or intern keywords identified",
                is_remote=False,
                detected_level="none",
                detected_role=""
            )

        # 3. Role Exclusions
        for excluded_role in self.config.get("roles_exclude", []):
            if excluded_role in title_lower:
                return FilterResult(
                    passed=False,
                    reason=f"Excluded role category: '{excluded_role}'",
                    is_remote=False,
                    detected_level=matched_level,
                    detected_role=excluded_role
                )

        # 4. Role Inclusions
        matched_role = None
        for inc_role in self.config.get("roles_include", []):
            if inc_role in title_lower or inc_role in full_text_lower[:400]:
                matched_role = inc_role
                break

        if not matched_role:
            return FilterResult(
                passed=False,
                reason="Role title does not match target technical disciplines",
                is_remote=False,
                detected_level=matched_level,
                detected_role="none"
            )

        # 5. Location Blockers & Visa Restrictions
        for reject_phrase in self.config.get("location_reject_phrases", []):
            if reject_phrase in location_lower or reject_phrase in full_text_lower:
                return FilterResult(
                    passed=False,
                    reason=f"Location/residency restriction: '{reject_phrase}'",
                    is_remote=False,
                    detected_level=matched_level,
                    detected_role=matched_role
                )

        # 6. DSA Hard-Rejections
        for dsa_term in self.config.get("dsa_hard_reject", []):
            if dsa_term in full_text_lower:
                return FilterResult(
                    passed=False,
                    reason=f"DSA hard barrier detected: '{dsa_term}'",
                    is_remote=False,
                    detected_level=matched_level,
                    detected_role=matched_role
                )

        # 7. Check Location Approved (India Tech Cities OR Global Remote Hubs)
        is_remote = any(rem in location_lower for rem in ["remote", "anywhere", "worldwide"])
        approved_india = any(city in location_lower for city in self.config.get("india_onsite_cities", []))
        approved_hub = any(hub in location_lower for hub in self.config.get("global_approved_hubs", []))

        if not (is_remote or approved_india or approved_hub):
            return FilterResult(
                passed=False,
                reason=f"Location '{location}' not in approved hubs or remote policy",
                is_remote=is_remote,
                detected_level=matched_level,
                detected_role=matched_role
            )

        return FilterResult(
            passed=True,
            reason="Passed Gate 1 deterministic criteria",
            is_remote=is_remote,
            detected_level=matched_level,
            detected_role=matched_role
        )
