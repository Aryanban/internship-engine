import pytest
from engine.gate1 import Gate1Filter

@pytest.fixture
def filter_engine():
    return Gate1Filter()

def test_accepts_ai_intern_remote(filter_engine):
    res = filter_engine.evaluate(
        title="AI Systems Engineer Intern",
        location="Remote Worldwide",
        jd_text="Work with LLM agents and prompt pipelines."
    )
    assert res.passed is True
    assert res.is_remote is True
    assert res.detected_level == "intern"

def test_accepts_india_bangalore_product_intern(filter_engine):
    res = filter_engine.evaluate(
        title="Product Engineer Intern",
        location="Bangalore, India",
        jd_text="Build fast full-stack Next.js web applications."
    )
    assert res.passed is True
    assert res.is_remote is False

def test_rejects_senior_roles(filter_engine):
    res = filter_engine.evaluate(
        title="Senior AI Engineer",
        location="Remote",
        jd_text="Looking for someone with 8 years experience."
    )
    assert res.passed is False
    assert "Excluded level" in res.reason

def test_rejects_us_only_residency(filter_engine):
    res = filter_engine.evaluate(
        title="Software Engineer Intern",
        location="Remote, US Only",
        jd_text="Must be located in the US."
    )
    assert res.passed is False
    assert "restriction" in res.reason

def test_rejects_leetcode_hard_dsa(filter_engine):
    res = filter_engine.evaluate(
        title="Fullstack Intern",
        location="Remote",
        jd_text="The interview will consist of a 60-minute LeetCode algorithmic test."
    )
    assert res.passed is False
    assert "DSA hard barrier" in res.reason
