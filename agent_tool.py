from langgraph.graph import StateGraph
from langchain_tavily import TavilySearch
from langchain_google_genai import ChatGoogleGenerativeAI
import tiktoken
import trafilatura
from PyPDF2 import PdfReader
from io import BytesIO
import requests
import os
from dotenv import load_dotenv
load_dotenv()
TAVILY_API_KEY = os.getenv('TAVILY_API_KEY')
GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')


search_tool = TavilySearch(tavily_api_key=TAVILY_API_KEY)

def search_node(query, max_results=6):
    results = search_tool.run(query, max_results=max_results)
    if isinstance(results, dict):
        results_list = results.get("results") or results.get("documents") or []
    else:
        results_list = results
    return results_list if results_list else []

def extract_node(sources):
    extracted = []
    for source in sources:
        url = source['url']
        title = source.get('title', url)
        text = ""
        if url.lower().endswith('.pdf'):
            try:
                response = requests.get(url)
                response.raise_for_status()
                pdf = PdfReader(BytesIO(response.content))
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text
            except Exception:
                print(f"Skipping source: {title} ({url}) - PDF scraping blocked or failed.")
                continue
        else:
            downloaded = trafilatura.fetch_url(url)
            if downloaded:
                text = trafilatura.extract(downloaded)
        if text and text.strip():
            extracted.append({'title': title, 'content': text, 'url': url})
        else:
            print(f"Skipping source: {title} ({url}) - scraping blocked or no content extracted.")
            continue
    return extracted

llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash", google_api_key=GOOGLE_API_KEY)

def summarize_node(extracted, query):
    summaries = []
    key_points = []
    enc = tiktoken.get_encoding("cl100k_base")
    for item in extracted:
        title = item['title']
        content = item['content']
        prompt_sum = f"Summarize the following content in relation to the query '{query}'. Provide a concise summary only.\n\nContent:\n{content}"
        prompt_kp = f"Extract key points from the following content in relation to the query '{query}'. List them as bullet points.\n\nContent:\n{content}"
        if len(enc.encode(prompt_sum)) > 12000 or len(enc.encode(prompt_kp)) > 12000:
            continue
        try:
            summary = llm.invoke(prompt_sum)
            key_pts = llm.invoke(prompt_kp)
            summaries.append(f"Title: {title}\n{summary.content.strip() if hasattr(summary, 'content') else str(summary)}")
            key_points.append(f"Title: {title}\n{key_pts.content.strip() if hasattr(key_pts, 'content') else str(key_pts)}")
        except Exception:
            continue
    return summaries, key_points, [item['url'] for item in extracted]

class ReportState:
    def __init__(self, query):
        self.query = query
        self.sources = None
        self.extracted = None
        self.summaries = None
        self.key_points = None
        self.links = None

workflow = StateGraph(ReportState)
workflow.add_node('search', search_node)
workflow.add_node('extract', extract_node)
workflow.add_node('summarize', summarize_node)
workflow.add_edge('search', 'extract')
workflow.add_edge('extract', 'summarize')
workflow.set_entry_point('search')

def generate_report(query):
    state = ReportState(query)
    max_attempts = 5
    attempt = 0
    all_tried_urls = set()
    extracted = []
    while len(extracted) < 2 and attempt < max_attempts:
        sources = search_node(query, max_results=8)
        sources = [s for s in sources if s['url'] not in all_tried_urls]
        all_tried_urls.update(s['url'] for s in sources)
        extracted += extract_node(sources)
        attempt += 1
    if not extracted:
        return None, "No extractable sources found for this query. Please try a different query."
    state.extracted = extracted[:3]  # Use up to 3 sources
    summaries, key_points, links = summarize_node(state.extracted, query)
    report = {
        'query': query,
        'summary': "\n\n".join(summaries),
        'key_points': "\n\n".join(key_points),
        'links': "\n".join(links)
    }
    return report, None
