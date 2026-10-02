import re
from typing import List, Tuple
from app.config import settings
from app.models.schemas import ChannelPost, RuleViolation, ComplianceReport
from app.guardrails.brand_rules import (
    BANNED_BUZZWORDS,
    COMPETITOR_DISPARAGEMENT_PHRASES,
    CHANNEL_MAX_CHARS
)


class BrandComplianceEvaluator:
    def __init__(self, min_score: float = None):
        self.min_score = min_score if min_score is not None else settings.MIN_COMPLIANCE_SCORE_PERCENT

    def evaluate_posts(self, posts: List[ChannelPost], source_text: str = "") -> ComplianceReport:
        violations: List[RuleViolation] = []
        checks_performed = [
            "Banned Buzzwords & Hyperbole Rule",
            "Competitor Non-Disparagement Rule",
            "Platform Length & Chunking Constraint",
            "Empty Content & Formatting Check"
        ]

        score = 100.0

        for post in posts:
            content_lower = post.content.lower()

            # 1. Banned Buzzwords Check
            for word in BANNED_BUZZWORDS:
                if re.search(r"\b" + re.escape(word) + r"\b", content_lower):
                    violations.append(RuleViolation(
                        rule_name="Banned Buzzwords & Hyperbole",
                        severity="WARNING",
                        message=f"Post contains prohibited hype buzzword: '{word}'. Replace with factual evidence or metrics.",
                        offending_text=word
                    ))
                    score -= 10.0

            # 2. Competitor Disparagement Check
            for phrase in COMPETITOR_DISPARAGEMENT_PHRASES:
                if phrase in content_lower:
                    violations.append(RuleViolation(
                        rule_name="Competitor Non-Disparagement",
                        severity="CRITICAL",
                        message=f"Post disparages competitors ('{phrase}'). Our brand guidelines mandate strictly professional communication.",
                        offending_text=phrase
                    ))
                    score -= 25.0

            # 3. Channel Length Constraint
            max_allowed = CHANNEL_MAX_CHARS.get(post.channel, 5000)
            if post.channel == "TWITTER_THREAD":
                # For threads, check each individual tweet chunk separated by --- or numbered 1/, 2/
                tweets = [t.strip() for t in post.content.split("\n\n") if t.strip()]
                for idx, tweet in enumerate(tweets, 1):
                    if len(tweet) > max_allowed:
                        violations.append(RuleViolation(
                            rule_name="Platform Length Constraint",
                            severity="WARNING",
                            message=f"Tweet #{idx} in thread exceeds 280-char limit ({len(tweet)} chars).",
                            offending_text=tweet[:50] + "..."
                        ))
                        score -= 5.0
            else:
                if len(post.content) > max_allowed:
                    violations.append(RuleViolation(
                        rule_name="Platform Length Constraint",
                        severity="WARNING",
                        message=f"{post.channel} exceeds maximum character limit ({len(post.content)} > {max_allowed}).",
                        offending_text=post.content[:50] + "..."
                    ))
                    score -= 10.0

            # 4. Empty or Too Brief Check
            if len(post.content.strip()) < 20:
                violations.append(RuleViolation(
                    rule_name="Content Completeness",
                    severity="CRITICAL",
                    message=f"{post.channel} is too short or empty.",
                    offending_text=post.content
                ))
                score -= 30.0

        normalized_score = max(0.0, round(score, 1))
        is_compliant = (normalized_score >= self.min_score) and not any(v.severity == "CRITICAL" for v in violations)

        return ComplianceReport(
            overall_score=normalized_score,
            is_compliant=is_compliant,
            violations=violations,
            checks_performed=checks_performed
        )
