import pytest
from app.guardrails.evaluator import BrandComplianceEvaluator
from app.models.schemas import ChannelPost


def test_clean_post_passes_compliance():
    evaluator = BrandComplianceEvaluator()
    clean_post = ChannelPost(
        channel="LINKEDIN_POST",
        title="Engineering Update",
        content="We released version 2.4 improving query execution latency by 40% based on production benchmarks.",
        character_count=100
    )
    report = evaluator.evaluate_posts([clean_post])
    assert report.is_compliant is True
    assert report.overall_score == 100.0
    assert len(report.violations) == 0


def test_banned_buzzwords_trigger_warning():
    evaluator = BrandComplianceEvaluator()
    hype_post = ChannelPost(
        channel="LINKEDIN_POST",
        title="Hype Post",
        content="Our revolutionary new tool is a game-changing silver bullet that makes developers 10x faster.",
        character_count=98
    )
    report = evaluator.evaluate_posts([hype_post])
    assert len(report.violations) >= 2
    assert any("revolutionary" in v.message for v in report.violations)
    assert any("game-changing" in v.message for v in report.violations)
    assert report.overall_score < 100.0


def test_competitor_disparagement_triggers_critical():
    evaluator = BrandComplianceEvaluator()
    bad_post = ChannelPost(
        channel="LINKEDIN_POST",
        title="Rival Bash",
        content="Don't use legacy vendors because our rivals suck and their architecture is broken.",
        character_count=85
    )
    report = evaluator.evaluate_posts([bad_post])
    assert report.is_compliant is False
    assert any(v.severity == "CRITICAL" for v in report.violations)
