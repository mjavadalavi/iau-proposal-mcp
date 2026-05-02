"""Academic paper search clients — Semantic Scholar and arXiv."""
from __future__ import annotations

import time
import xml.etree.ElementTree as ET
from dataclasses import dataclass

import httpx

_SEMANTIC_SCHOLAR_URL = "https://api.semanticscholar.org/graph/v1/paper/search"
_ARXIV_URL = "https://export.arxiv.org/api/query"
_ARXIV_NS = "http://www.w3.org/2005/Atom"

_last_arxiv_call: float = 0.0


@dataclass
class Paper:
    title: str
    authors: list[str]
    year: int | None
    abstract: str
    url: str
    source: str
    open_access_pdf: str | None = None


def search_semantic_scholar(
    query: str,
    year_from: int | None = None,
    limit: int = 10,
) -> list[Paper]:
    params: dict = {
        "query": query,
        "limit": min(limit, 100),
        "fields": "title,authors,year,abstract,externalIds,openAccessPdf,url",
    }
    if year_from:
        params["year"] = f"{year_from}-"

    with httpx.Client(timeout=15) as client:
        resp = client.get(_SEMANTIC_SCHOLAR_URL, params=params)
        resp.raise_for_status()

    papers: list[Paper] = []
    for item in resp.json().get("data", []):
        pdf_url = None
        if item.get("openAccessPdf"):
            pdf_url = item["openAccessPdf"].get("url")

        papers.append(Paper(
            title=item.get("title", ""),
            authors=[a["name"] for a in item.get("authors", [])[:3]],
            year=item.get("year"),
            abstract=(item.get("abstract") or "")[:300],
            url=item.get("url") or f"https://www.semanticscholar.org/paper/{item.get('paperId', '')}",
            source="Semantic Scholar",
            open_access_pdf=pdf_url,
        ))
    return papers


def search_arxiv(
    query: str,
    year_from: int | None = None,
    limit: int = 10,
) -> list[Paper]:
    global _last_arxiv_call
    elapsed = time.time() - _last_arxiv_call
    if elapsed < 3.0:
        time.sleep(3.0 - elapsed)

    search_query = query
    if year_from:
        search_query += f" AND submittedDate:[{year_from}0101 TO 99991231]"

    params = {
        "search_query": f"all:{search_query}",
        "max_results": min(limit, 50),
        "sortBy": "relevance",
    }

    with httpx.Client(timeout=15) as client:
        resp = client.get(_ARXIV_URL, params=params)
        resp.raise_for_status()

    _last_arxiv_call = time.time()

    root = ET.fromstring(resp.text)
    papers: list[Paper] = []

    for entry in root.findall(f"{{{_ARXIV_NS}}}entry"):
        title_el = entry.find(f"{{{_ARXIV_NS}}}title")
        abstract_el = entry.find(f"{{{_ARXIV_NS}}}summary")
        published_el = entry.find(f"{{{_ARXIV_NS}}}published")
        id_el = entry.find(f"{{{_ARXIV_NS}}}id")

        authors = [
            (a.find(f"{{{_ARXIV_NS}}}name") or ET.Element("")).text or ""
            for a in entry.findall(f"{{{_ARXIV_NS}}}author")[:3]
        ]

        year = None
        if published_el is not None and published_el.text:
            try:
                year = int(published_el.text[:4])
            except ValueError:
                pass

        arxiv_id = (id_el.text or "").strip()
        pdf_url = arxiv_id.replace("abs", "pdf") if "abs" in arxiv_id else None

        papers.append(Paper(
            title=(title_el.text or "").strip().replace("\n", " "),
            authors=authors,
            year=year,
            abstract=((abstract_el.text or "").strip().replace("\n", " "))[:300],
            url=arxiv_id,
            source="arXiv",
            open_access_pdf=pdf_url,
        ))

    return papers
