"""
Public ATS JSON Fetchers for Greenhouse, Lever, and Ashby.
Zero scraping, 100% public structured endpoints.
"""

from typing import List, Dict, Any, Optional
import httpx
from pydantic import BaseModel

class RawJob(BaseModel):
    company_name: str
    external_id: str
    title: str
    location: str
    apply_url: str
    jd_raw: str

def fetch_greenhouse(board_token: str, company_name: str) -> List[RawJob]:
    """Fetch jobs from public Greenhouse boards API."""
    url = f"https://boards-api.greenhouse.io/v1/boards/{board_token}/jobs?content=true"
    try:
        resp = httpx.get(url, timeout=10.0)
        if resp.status_code != 200:
            return []
        data = resp.json()
        jobs = []
        for j in data.get("jobs", []):
            jobs.append(RawJob(
                company_name=company_name,
                external_id=str(j.get("id")),
                title=j.get("title", ""),
                location=j.get("location", {}).get("name", "Unknown"),
                apply_url=j.get("absolute_url", ""),
                jd_raw=j.get("content", "")
            ))
        return jobs
    except Exception:
        return []

def fetch_lever(board_token: str, company_name: str) -> List[RawJob]:
    """Fetch jobs from public Lever API."""
    url = f"https://api.lever.co/v0/postings/{board_token}?mode=json"
    try:
        resp = httpx.get(url, timeout=10.0)
        if resp.status_code != 200:
            return []
        data = resp.json()
        jobs = []
        for j in data:
            jobs.append(RawJob(
                company_name=company_name,
                external_id=str(j.get("id")),
                title=j.get("text", ""),
                location=j.get("categories", {}).get("location", "Unknown"),
                apply_url=j.get("hostedUrl", ""),
                jd_raw=j.get("descriptionPlain", "") or j.get("description", "")
            ))
        return jobs
    except Exception:
        return []

def fetch_ashby(board_token: str, company_name: str) -> List[RawJob]:
    """Fetch jobs from public Ashby API."""
    url = f"https://api.ashbyhq.com/posting-api/job-board/{board_token}"
    try:
        resp = httpx.get(url, timeout=10.0)
        if resp.status_code != 200:
            return []
        data = resp.json()
        jobs = []
        for j in data.get("jobs", []):
            jobs.append(RawJob(
                company_name=company_name,
                external_id=str(j.get("id")),
                title=j.get("title", ""),
                location=j.get("location", "Unknown"),
                apply_url=j.get("jobUrl", ""),
                jd_raw=j.get("descriptionHtml", "")
            ))
        return jobs
    except Exception:
        return []
