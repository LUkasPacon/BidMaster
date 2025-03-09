"""
LangChain řetězec pro generování nabídek.
"""
from typing import Dict, Any, List, Optional
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough, RunnableLambda
from langchain_core.messages import AIMessage, HumanMessage

from app.utils.config import get_config
from app.utils.vector_store import similarity_search

config = get_config()

# Systémová zpráva pro chatbota
SYSTEM_TEMPLATE = """
Jsi asistent pro generování obchodních nabídek na implementaci produktu MidPoint.
Tvým úkolem je pomoci obchodníkovi vytvořit kvalitní nabídku na základě požadavků klienta.

Budeš pracovat s následujícími informacemi:
1. Poptávka klienta - text popisující, co klient požaduje
2. Relevantní části z předchozích nabídek - pro inspiraci a konzistenci

Při vytváření nabídky se zaměř na:
- Jasný popis řešení MidPoint a jeho výhod
- Konkrétní implementační kroky
- Realistický harmonogram
- Přesnou cenovou kalkulaci
- Profesionální a přesvědčivý tón

Pokud nemáš dostatek informací, ptej se obchodníka na doplňující otázky.
"""

def get_relevant_context(query: str) -> str:
    """
    Získá relevantní kontext z vektorové databáze.
    
    Args:
        query: Dotaz pro vyhledávání
        
    Returns:
        str: Relevantní kontext
    """
    documents = similarity_search(query, k=5)
    
    if not documents:
        return "Nebyly nalezeny žádné relevantní dokumenty."
    
    # Spojení dokumentů do jednoho textu
    context = "\n\n---\n\n".join([doc.page_content for doc in documents])
    
    return context

def format_chat_history(chat_history: List[Dict[str, Any]]) -> List[Any]:
    """
    Formátuje historii chatu pro LangChain.
    
    Args:
        chat_history: Historie chatu
        
    Returns:
        List[Any]: Formátovaná historie chatu
    """
    formatted_history = []
    
    for message in chat_history:
        if message["role"] == "user":
            formatted_history.append(HumanMessage(content=message["content"]))
        elif message["role"] == "assistant":
            formatted_history.append(AIMessage(content=message["content"]))
    
    return formatted_history

def create_proposal_chain():
    """
    Vytvoří LangChain řetězec pro generování nabídek.
    
    Returns:
        Runnable: LangChain řetězec
    """
    # Vytvoření LLM
    llm = ChatOpenAI(
        model=config.model_name,
        temperature=0.7,
        openai_api_key=config.openai_api_key
    )
    
    # Vytvoření promptu
    prompt = ChatPromptTemplate.from_messages([
        ("system", SYSTEM_TEMPLATE),
        MessagesPlaceholder(variable_name="chat_history"),
        ("human", "{input}"),
        ("human", "Relevantní kontext z předchozích nabídek:\n{context}")
    ])
    
    # Vytvoření řetězce
    chain = (
        {
            "input": RunnablePassthrough(),
            "chat_history": lambda x: format_chat_history(x.get("chat_history", [])),
            "context": lambda x: get_relevant_context(x.get("input", ""))
        }
        | prompt
        | llm
        | StrOutputParser()
    )
    
    return chain

def generate_proposal_data(
    client_request: str,
    client_name: str,
    additional_info: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Generuje data pro vytvoření nabídky.
    
    Args:
        client_request: Poptávka klienta
        client_name: Název klienta
        additional_info: Dodatečné informace (volitelné)
        
    Returns:
        Dict[str, Any]: Data pro vytvoření nabídky
    """
    # Vytvoření LLM
    llm = ChatOpenAI(
        model=config.model_name,
        temperature=0.2,
        openai_api_key=config.openai_api_key
    )
    
    # Získání relevantního kontextu
    context = get_relevant_context(client_request)
    
    # Vytvoření promptu pro generování dat
    prompt = ChatPromptTemplate.from_messages([
        ("system", """
        Jsi asistent pro generování strukturovaných dat pro obchodní nabídky na implementaci produktu MidPoint.
        Na základě poptávky klienta a relevantního kontextu vytvoř strukturovaná data pro nabídku.
        
        Výstup musí být ve formátu JSON s následujícími klíči:
        - client_name: Název klienta
        - introduction: Úvod nabídky (1-2 odstavce)
        - solution_description: Popis řešení MidPoint (3-5 odstavců)
        - scope_of_work: Rozsah prací (seznam položek s popisem)
        - timeline: Harmonogram implementace (seznam fází s časovým odhadem)
        - pricing: Cenová kalkulace (tabulka položek s cenami)
        - contact_info: Kontaktní informace
        """),
        ("human", f"""
        Poptávka klienta:
        {client_request}
        
        Název klienta: {client_name}
        
        Relevantní kontext z předchozích nabídek:
        {context}
        
        Dodatečné informace:
        {additional_info if additional_info else "Žádné dodatečné informace."}
        """)
    ])
    
    # Generování dat
    response = llm.invoke(prompt)
    
    # Parsování JSON odpovědi
    try:
        import json
        data = json.loads(response.content)
        return data
    except Exception as e:
        print(f"Chyba při parsování JSON: {e}")
        # Vrátíme alespoň základní data
        return {
            "client_name": client_name,
            "introduction": "Chyba při generování dat.",
            "solution_description": "Chyba při generování dat.",
            "scope_of_work": "Chyba při generování dat.",
            "timeline": "Chyba při generování dat.",
            "pricing": "Chyba při generování dat.",
            "contact_info": "Chyba při generování dat."
        } 