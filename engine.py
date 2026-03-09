import os
import requests
from bs4 import BeautifulSoup
from typing import TypedDict, List, Annotated
from langchain_groq import ChatGroq
from langchain_core.messages import BaseMessage, HumanMessage, SystemMessage
from langgraph.graph import StateGraph, END
from langchain_community.utilities import DuckDuckGoSearchAPIWrapper

# Initialize Search Tool with result URLs
search = DuckDuckGoSearchAPIWrapper(max_results=5)

class ResearchState(TypedDict):
    target: str
    search_queries: List[str]
    raw_info: Annotated[List[str], lambda x, y: x + y]
    structured_data: dict
    logs: Annotated[List[str], lambda x, y: x + y]
    iteration: int

def get_engine(api_key: str):
    llm = ChatGroq(temperature=0.1, model_name="llama-3.3-70b-versatile", groq_api_key=api_key)

    def planner_node(state: ResearchState):
        """Initializes the research plan."""
        target = state["target"]
        query_prompt = f"Generate 2 broad search queries to understand the career and background of {target}."
        response = llm.invoke([SystemMessage(content="You are a research planner."), HumanMessage(content=query_prompt)])
        queries = response.content.strip().split("\n")
        return {"search_queries": queries, "logs": [f"🚀 Initializing deep research for {target}..."]}

    def explorer_node(state: ResearchState):
        """Performs iterative depth search with link tracking."""
        queries = state["search_queries"]
        raw_info = []
        new_logs = []
        
        def run_detailed_search(query):
            results = search.results(query, max_results=5)
            formatted_results = []
            for r in results:
                formatted_results.append(f"Title: {r['title']}\nSource: {r['link']}\nSnippet: {r['snippet']}")
            return "\n\n".join(formatted_results)

        # Hop 1: Broad Search
        for q in queries:
            if not q or not q.strip(): continue
            new_logs.append(f"🔍 Initial search: {q}")
            try:
                raw_info.append(run_detailed_search(q))
            except: pass
            
        # Hop 2: Deep Dive with Quotes & Links
        snippet_context = "\n".join(raw_info)[:1500]
        refinement_prompt = f"Based on this info about {state['target']}: {snippet_context}... Generate 2 specific queries to find direct quotes and verified career links for {state['target']}."
        gap_queries = llm.invoke([SystemMessage(content="You are a meticulous researcher."), HumanMessage(content=refinement_prompt)]).content.strip().split("\n")
        
        new_logs.append("📍 Harvesting source links and deep context...")
        for q in gap_queries[:2]:
            if not q or not q.strip(): continue
            new_logs.append(f"🔎 Deep-dive research: {q}")
            try:
                raw_info.append(run_detailed_search(f"{q} official sources"))
            except: pass
        
        return {
            "raw_info": raw_info, 
            "logs": new_logs,
            "iteration": state.get("iteration", 0) + 1
        }

    def analyst_node(state: ResearchState):
        """Synthesizes everything into a high-impact executive dossier with links."""
        full_context = "\n".join(state["raw_info"])
        template = f"""
        # 👑 EXECUTIVE INVESTIGATIVE DOSSIER: {state['target']}
        
        **Objective:** High-integrity intelligence report with verified source links.
        
        ### 📊 Intelligence Snapshot (Table)
        (Columns: Parameter | Verified Detail)
        
        ### 📖 The Narrative: Origins & Drive
        (A sophisticated 2-paragraph biography)
        
        ### 📈 Strategic Milestones
        (An annotated timeline with impact analysis)
        
        ### 🎙️ The Voice (Direct Quotes)
        (Extract and format exactly 3-5 high-impact direct quotes with source attribution)
        
        ### ⚠️ Notable Challenges & Nuance
        (Setbacks, controversies, or complex transitions)
        
        ### 🔗 Verified Sources & Reading
        (LIST THE ACTUAL LINKS FOUND IN THE DATA. Format as: [Title](Link))
        
        DATA CONTEXT: {full_context}
        """
        response = llm.invoke([SystemMessage(content="You are a partner at an elite global intelligence firm specializing in OSINT."), HumanMessage(content=template)])
        return {"structured_data": {"report": response.content}, "logs": ["💎 Intelligence Dossier finalized with source links."]}

    # Build Graph
    builder = StateGraph(ResearchState)
    builder.add_node("planner", planner_node)
    builder.add_node("explorer", explorer_node)
    builder.add_node("analyst", analyst_node)

    builder.set_entry_point("planner")
    builder.add_edge("planner", "explorer")
    builder.add_edge("explorer", "analyst")
    builder.add_edge("analyst", END)

    return builder.compile()
