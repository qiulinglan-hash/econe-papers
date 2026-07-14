#!/usr/bin/env python3
"""
ArXiv 半导体全球经济与地缘政治论文抓取 + AI 分析脚本
"""

import argparse
import json
import os
import re
import time
from datetime import datetime
from urllib.parse import urlencode

import requests
from bs4 import BeautifulSoup

# 加载环境变量
MINIMAX_API_KEY = os.getenv("MINIMAX_API_KEY", "")
MINIMAX_BASE_URL = "https://api.minimaxi.com/v1/text/chatcompletion_v2"

# 1. 关注的学科分类：经济学、量化金融、计算机与社会
ARXIV_CATEGORIES = [
    "econ.GN",     # 通用经济学 (General Economics)
    "econ.EM",     # 计量经济学 (Econometrics)
    "q-fin.EC",    # 金融经济学 (Economics in Finance)
    "cs.CY",       # 计算机与社会 (Computers and Society - 经常有芯片法案、地缘政治、供应链的讨论)
]

def search_arxiv(category: str, max_results: int = 200) -> list:
    """从 ArXiv 搜索半导体地缘政治、经济、供应链相关的最新论文"""
    base_url = "https://export.arxiv.org/api/query"
    
    # 半导体核心词
    semi_terms = '("semiconductor" OR "microchip" OR "integrated circuit" OR "foundry" OR "lithography" OR "silicon")'
    # 经济与地缘政治核心词
    econ_terms = '("geopolitics" OR "supply chain" OR "value chain" OR "trade" OR "policy" OR "tariff" OR "sanction" OR "subsidy" OR "industrial policy" OR "market")'
    
    # 组合查询：必须同时满足（半导体相关）和（经济/政治相关）
    query = f"cat:{category} AND {semi_terms} AND {econ_terms}"
    
    params = {
        "search_query": query,
        "start": 0,
        "max_results": max_results,
        "sortBy": "submittedDate",
        "sortOrder": "descending"
    }
    
    url = f"{base_url}?{urlencode(params)}"
    print(f"   🔍 正在检索 {category} 分类下的半导体经济学论文...")
    
    try:
        response = requests.get(url, timeout=60)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, "html.parser")
        entries = soup.find_all("entry")
        
        papers = []
        for entry in entries:
            paper = {
                "id": entry.find("id").text.strip() if entry.find("id") else "",
                "title": entry.find("title").text.replace("\n", " ").strip() if entry.find("title") else "",
                "authors": [a.text.strip() for a in entry.find_all("author")] if entry.find_all("author") else [],
                "abstract": entry.find("summary").text.replace("\n", " ").strip() if entry.find("summary") else "",
                "categories": [cat.get("term", "") for cat in entry.find_all("category")] if entry.find_all("category") else [],
                "published": entry.find("published").text[:10] if entry.find("published") else "",
                "updated": entry.find("updated").text[:10] if entry.find("updated") else "",
                "pdfUrl": "",
            }
            
            # 获取 PDF 链接
            for link in entry.find_all("link"):
                if link.get("title") == "pdf":
                    paper["pdfUrl"] = link.get("href", "")
                    break
            
            if paper["title"]:
                papers.append(paper)
        
        print(f"      找到 {len(papers)} 篇相关论文")
        return papers
        
    except Exception as e:
        print(f"      Error: {e}")
        return []

def call_minimax(prompt: str) -> str:
    """调用 MiniMax API"""
    if not MINIMAX_API_KEY:
        print("  ⚠️ MINIMAX_API_KEY not set")
        return ""
    
    headers = {
        "Authorization": f"Bearer {MINIMAX_API_KEY}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": "MiniMax-Text-01",
        "messages": [
            {"role": "system", "content": "你是一个专业的半导体产业经济学与地缘政治专家。请只返回 JSON，不要其他内容。"},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.7
    }
    
    try:
        response = requests.post(
            MINIMAX_BASE_URL,
            headers=headers,
            json=payload,
            timeout=60
        )
        response.raise_for_status()
        result = response.json()
        return result["choices"][0]["message"]["content"]
    except Exception as e:
        print(f"  ⚠️ MiniMax API error: {e}")
        return ""

def analyze_paper(paper: dict) -> dict:
    """用 AI 深度分析半导体经济学论文"""
    prompt = f"""请分析以下 ArXiv 上关于半导体产业经济与地缘政治的论文。

标题: {paper['title']}
作者: {', '.join(paper['authors'])}
摘要: {paper['abstract'][:800]}

请按以下 JSON 格式返回分析结果（只返回 JSON，不要其他内容）:
{{
    "chineseTitle": "翻译成准确、学术通顺的中文标题",
    "chineseAbstract": "中文摘要（100-200字，要求学术术语准确，体现地缘政治、供应链或经济学影响）",
    "researchField": "研究子领域（地缘政治与政策/供应链与价值链/市场与产业经济/技术创新与博弈/其他）",
    "keywords": ["关键词1", "关键词2", "关键词3"],
    "scores": {{
        "overall": 8,
        "novelty": 4,
        "quality": 4,
        "readability": 4
    }},
    "summary": "一句话总结（20字以内，说明该研究对半导体行业的经济学启示或政策影响）"
}}
"""
    
    result = call_minimax(prompt)
    
    if result:
        try:
            json_match = re.search(r'\{[\s\S]*\}', result)
            if json_match:
                analysis = json.loads(json_match.group())
                print(f"     ✓ Analyzed: {analysis.get('chineseTitle', '')[:30]}...")
                return {**paper, **analysis}
        except json.JSONDecodeError as e:
            print(f"  ⚠️ JSON parse error: {e}")
    
    # 失败降级
    scores = calculate_initial_scores(paper)
    field = determine_research_field(paper)
    
    return {
        **paper,
        "chineseTitle": paper["title"],
        "chineseAbstract": paper["abstract"][:200] if paper["abstract"] else "",
        "researchField": field,
        "keywords": [],
        "scores": scores,
        "summary": paper["abstract"][:50] if paper["abstract"] else ""
    }

def calculate_initial_scores(paper: dict) -> dict:
    """基于关键词简单计算初始评分"""
    title = paper.get("title", "").lower()
    abstract = paper.get("abstract", "").lower()
    
    novelty = 3.0
    quality = 3.0
    readability = 3.0
    
    novelty_keywords = ["policy", "chips act", "geopolitics", "tariff", "trade war", "sanction"]
    for kw in novelty_keywords:
        if kw in abstract or kw in title:
            novelty = min(5.0, novelty + 0.4)
            quality = min(5.0, quality + 0.2)
            
    authors = paper.get("authors", [])
    if 2 <= len(authors) <= 5:
        readability = 4.0
    
    overall = novelty * 0.4 + quality * 0.4 + readability * 0.2
    return {
        "overall": round(overall, 1),
        "novelty": round(novelty, 1),
        "quality": round(quality, 1),
        "readability": round(readability, 1)
    }

def determine_research_field(paper: dict) -> str:
    """分类识别：地缘政治/供应链/市场经济"""
    title = paper.get("title", "").lower()
    abstract = paper.get("abstract", "").lower()
    
    field_keywords = {
        "地缘政治与政策": ["geopolitics", "policy", "chips act", "sanction", "subsidy", "tariff", "trade war", "national security"],
        "供应链与价值链": ["supply chain", "value chain", "logistics", "resilience", "foundry", "shortage", "disruption"],
        "市场与产业经济": ["market", "competition", "oligopoly", "cost", "investment", "price", "firm", "industry economics"]
    }
    
    for field, keywords in field_keywords.items():
        for kw in keywords:
            if kw in abstract or kw in title:
                return field
    
    return "其他半导体经济学"

def main():
    parser = argparse.ArgumentParser(description="ArXiv 半导体经济学论文抓取")
    parser.add_argument("--max", type=int, default=200, help="每个分类最多抓取数量")
    parser.add_argument("--analyze", type=int, default=30, help="AI 分析前 N 篇")
    parser.add_argument("--output", type=str, default="papers.json", help="输出文件名")
    args = parser.parse_args()
    
    if not MINIMAX_API_KEY:
        print("⚠️ MINIMAX_API_KEY not found!")
    
    print(f"\n📡 正在从 ArXiv 检索【半导体地缘政治与全球经济】相关研究...")
    
    all_papers = []
    for category in ARXIV_CATEGORIES:
        papers = search_arxiv(category, args.max)
        for paper in papers:
            if not any(p["id"] == paper["id"] for p in all_papers):
                all_papers.append(paper)
        time.sleep(0.5)
    
    print(f"\n📊 过滤出 {len(all_papers)} 篇半导体经济学/政治学相关论文")
    
    # 按日期分组
    from collections import defaultdict
    by_date = defaultdict(list)
    for paper in all_papers:
        date = paper.get("published", "unknown")
        by_date[date].append(paper)
    
    # 截止日期
    cutoff_date = "2026-01-01"
    analyzed_papers_by_date = {}
    
    if by_date and MINIMAX_API_KEY:
        print(f"\n✍️ AI 深度解读分析中...")
        for date_str in sorted(by_date.keys(), reverse=True):
            if date_str < cutoff_date:
                continue
            
            papers = by_date[date_str]
            print(f"\n  📅 {date_str}: 正在用 AI 深度分析前 {min(args.analyze, len(papers))} 篇高价值论文...")
            
            analyzed_day_papers = []
            for i, paper in enumerate(papers[:args.analyze]):
                print(f"     [{i+1}/{min(args.analyze, len(papers))}] Processing...")
                analyzed = analyze_paper(paper)
                analyzed_day_papers.append(analyzed)
                time.sleep(0.8)
            
            for paper in papers[args.analyze:]:
                analyzed_day_papers.append({
                    **paper,
                    "chineseTitle": paper["title"],
                    "chineseAbstract": paper["abstract"][:200] if paper["abstract"] else "",
                    "researchField": determine_research_field(paper),
                    "keywords": [],
                    "scores": calculate_initial_scores(paper),
                    "summary": paper["abstract"][:50] if paper["abstract"] else ""
                })
            
            analyzed_papers_by_date[date_str] = analyzed_day_papers
            
    elif by_date:
        print("\n⚠️ 缺失 MiniMax API KEY，直接跳过 AI 润色并生成基本字段...")
        for date_str, papers in by_date.items():
            if date_str < cutoff_date:
                continue
            analyzed_day_papers = []
            for paper in papers:
                analyzed_day_papers.append({
                    **paper,
                    "chineseTitle": paper["title"],
                    "chineseAbstract": paper["abstract"][:200] if paper["abstract"] else "",
                    "researchField": determine_research_field(paper),
                    "keywords": [],
                    "scores": calculate_initial_scores(paper),
                    "summary": paper["abstract"][:50] if paper["abstract"] else ""
                })
            analyzed_papers_by_date[date_str] = analyzed_day_papers
    
    day_papers = []
    for date_str in sorted(analyzed_papers_by_date.keys(), reverse=True):
        papers = analyzed_papers_by_date[date_str]
        papers.sort(key=lambda x: x.get("scores", {}).get("overall", 0), reverse=True)
        selected = papers[:30]
        
        day_papers.append({
            "date": date_str,
            "papers": selected,
            "total": len(papers)
        })
    
    output = {
        "days": day_papers,
        "lastUpdated": datetime.now().isoformat(),
        "total": sum(d["total"] for d in day_papers)
    }
    
    output_path = os.path.join(os.path.dirname(__file__), args.output)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)
    
    web_data_path = os.path.join(
        os.path.dirname(os.path.dirname(__file__)), 
        "web", "src", "lib", "data.json"
    )
    with open(web_data_path, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)
    
    print(f"\n✅ 重新配置成功！半导体全球经济学数据已保存至 web 目录。")

if __name__ == "__main__":
    main()
