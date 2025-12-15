# search_controller.py
import re

# from bs4 import BeautifulSoup
from fastapi import APIRouter, Request, Query
import httpx
from duckduckgo_search import DDGS
from urllib.parse import urlparse

from logic.AppLogger import AppLogger


APP_NAME = "api_server"
router = APIRouter(tags=["Service"])

DUCK_API_URL = "https://api.duckduckgo.com/"


@router.post("/search")
async def search_web(q: str = Query(..., description="Search keyword")):
    """DuckDuckGoのInstant Answer APIで検索＋スニペット抽出"""
    params = {"q": q, "format": "json", "no_redirect": 1, "no_html": 1}
    results = []

    async with httpx.AsyncClient() as client:
        res = await client.get(DUCK_API_URL, params=params)
        data = res.json()

        if "RelatedTopics" in data:
            # RelatedTopics からURLとタイトルを取得
            for topic in data["RelatedTopics"]:
                if "Text" in topic and "FirstURL" in topic:
                    snippet = await fetch_snippet(client, topic["FirstURL"])
                    results.append(
                        {
                            "title": topic["Text"],
                            "uri": topic["FirstURL"],
                            "snippet": snippet,
                        }
                    )

    return {"count": len(results), "results": results}


async def fetch_snippet(client: httpx.AsyncClient, url: str) -> str:
    """ページのスニペットをmetaタグや冒頭文から抽出"""
    try:
        # print(f"scrape uri: {url}")
        # 1. URLを解析
        parsed = urlparse(url)

        # 2. パスの末尾部分
        # （例: "/c/Artificial_intelligence_associations"
        #  → "Artificial_intelligence_associations"）
        path = parsed.path.strip("/")
        parts = path.split("/")
        if len(parts) >= 2 and parts[0] == "c":
            query = parts[1]
        else:
            return {"error": "Invalid DuckDuckGo category URI"}

        results = DDGS().text(query, max_results=5)
        # print(results)
        return results
    except Exception:
        raise "(スニペット取得に失敗しました)"
    # return "(説明文なし)"


@router.post("/search_scrape")
async def search_scrape(request: Request):
    api_logger = AppLogger(f"{APP_NAME}({request.url.path}):")
    api_logger.info_log(f"Receive {request.method}")
    try:
        body_data = await request.json()

        """DuckDuckGoのInstant Answer APIで検索＋スニペット抽出"""
        query = body_data.get("query")
        # 半角・全角スペースをまとめてハイフン1個に置換
        normalized = re.sub(r"[\s\u3000]+", "-", query.strip())

        params = {
            "q": normalized,
            "format": "json",
            "no_redirect": 1,
            "no_html": 1,
        }
        results = []
        api_logger.info_log(f"Search: {params}")

        async with httpx.AsyncClient() as client:
            res = await client.get(DUCK_API_URL, params=params)
            data = res.json()

            if "RelatedTopics" in data:
                # RelatedTopics からURLとタイトルを取得
                for topic in data["RelatedTopics"]:
                    if "Text" in topic and "FirstURL" in topic:
                        snippet = await fetch_snippet(
                            client, topic["FirstURL"]
                        )
                        results.append(
                            {
                                "title": topic["Text"],
                                "uri": topic["FirstURL"],
                                "snippet": snippet,
                            }
                        )

        response = {"count": len(results), "results": results}
        api_logger.info_log(f"search response: {response}")

    except Exception as e:
        api_logger.error_log(f"error occured: {e}")

    finally:
        return response
