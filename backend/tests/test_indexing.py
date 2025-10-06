from __future__ import annotations

from bs4 import BeautifulSoup  # type: ignore


def _extract_robots_meta(html: bytes) -> str | None:
    soup = BeautifulSoup(html, "html.parser")
    tag = soup.find("meta", attrs={"name": "robots"})
    return tag.get("content") if tag else None


def test_homepage_allows_indexing(client):
    response = client.get("/en/")
    assert response.status_code == 200
    meta_value = _extract_robots_meta(response.data)
    assert meta_value is not None
    assert "noindex" not in meta_value.lower()
    assert "index" in meta_value.lower()


def test_search_results_marked_noindex(client):
    response = client.get("/en/?q=keywords")
    assert response.status_code == 200
    meta_value = _extract_robots_meta(response.data)
    assert meta_value == "noindex, nofollow"


def test_locale_robots_blocks_query_params(client):
    response = client.get("/en/robots.txt")
    assert response.status_code == 200
    body = response.get_data(as_text=True)
    assert "Disallow: /*?q=" in body
