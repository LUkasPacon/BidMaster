"""
Utilita pro práci s vektorovou databází Pinecone.
"""
from typing import List, Dict, Any, Optional
import pinecone
import os
from langchain_openai import OpenAIEmbeddings
import json

try:
    # Zkusíme importovat z langchain_pinecone
    from langchain_pinecone import PineconeVectorStore
except ImportError:
    # Pokud to nefunguje, zkusíme starší způsob importu
    try:
        from langchain_community.vectorstores import Pinecone as PineconeVectorStore
    except ImportError:
        from langchain.vectorstores import Pinecone as PineconeVectorStore

from langchain_core.documents import Document

from app.config import get_config

config = get_config()

# Nastavení dimenze vektorů podle použitého modelu
# text-embedding-3-large má dimenzi 3072
# text-embedding-3-small má dimenzi 1536
EMBEDDING_DIMENSION = 3072

def init_pinecone() -> None:
    """
    Inicializuje připojení k Pinecone.
    """
    try:
        # Nový způsob inicializace Pinecone (verze 2.x)
        pc = pinecone.Pinecone(
            api_key=config.pinecone_api_key,
            environment=config.pinecone_environment
        )
        
        # Kontrola, zda index existuje, pokud ne, vytvoříme ho
        index_list = [index.name for index in pc.list_indexes()]
        if config.pinecone_index_name not in index_list:
            pc.create_index(
                name=config.pinecone_index_name,
                dimension=EMBEDDING_DIMENSION,  # Používáme správnou dimenzi
                metric="cosine",
                spec=pinecone.ServerlessSpec(
                    cloud="aws",
                    region="us-east-1"  # Používáme us-east-1 místo us-west-2
                )
            )
    except Exception as e:
        print(f"Chyba při inicializaci Pinecone: {e}")
        print("Zkouším starší způsob inicializace...")
        try:
            # Starší způsob inicializace Pinecone (verze 1.x)
            pinecone.init(
                api_key=config.pinecone_api_key,
                environment=config.pinecone_environment
            )
            
            # Kontrola, zda index existuje, pokud ne, vytvoříme ho
            if config.pinecone_index_name not in pinecone.list_indexes():
                pinecone.create_index(
                    name=config.pinecone_index_name,
                    dimension=EMBEDDING_DIMENSION,  # Používáme správnou dimenzi
                    metric="cosine"
                )
        except Exception as e2:
            print(f"Chyba i při starším způsobu inicializace: {e2}")
            raise

def get_embeddings() -> OpenAIEmbeddings:
    """
    Vrátí instanci OpenAI embeddings.
    
    Returns:
        OpenAIEmbeddings: Instance OpenAI embeddings
    """
    return OpenAIEmbeddings(
        model=config.embedding_model,
        openai_api_key=config.openai_api_key
    )

def get_vector_store(namespace: Optional[str] = None) -> PineconeVectorStore:
    """
    Vrátí instanci vektorového úložiště Pinecone.
    
    Args:
        namespace: Namespace pro vektorové úložiště (volitelné)
        
    Returns:
        PineconeVectorStore: Instance vektorového úložiště
    """
    # Inicializace Pinecone
    init_pinecone()
    
    # Vytvoření instance embeddings
    embeddings = get_embeddings()
    
    # Vytvoření instance vektorového úložiště
    try:
        # Zkusíme novější způsob inicializace s Pinecone 2.x
        pc = pinecone.Pinecone(api_key=config.pinecone_api_key)
        index = pc.Index(config.pinecone_index_name)
        
        print(f"Vytvářím vektorové úložiště s novým API. Namespace: {namespace}")
        return PineconeVectorStore(
            index=index,
            embedding=embeddings,
            text_key="text",
            namespace=namespace
        )
    except Exception as e:
        print(f"Chyba při vytváření vektorového úložiště s novým API: {e}")
        print("Zkouším starší způsob inicializace...")
        
        try:
            # Zkusíme starší způsob inicializace s Pinecone 1.x
            # Nejprve zkusíme získat index přímo
            try:
                index = pinecone.Index(config.pinecone_index_name)
            except:
                # Pokud to nefunguje, zkusíme nejprve inicializovat
                pinecone.init(
                    api_key=config.pinecone_api_key,
                    environment=config.pinecone_environment
                )
                index = pinecone.Index(config.pinecone_index_name)
            
            print(f"Vytvářím vektorové úložiště se starším API. Namespace: {namespace}")
            return PineconeVectorStore(
                index=index,
                embedding=embeddings,
                text_key="text",
                namespace=namespace
            )
        except Exception as e2:
            print(f"Chyba i při starším způsobu inicializace vektorového úložiště: {e2}")
            
            # Poslední pokus - zkusíme použít index_name místo index
            try:
                print(f"Poslední pokus - použití index_name místo index. Namespace: {namespace}")
                return PineconeVectorStore(
                    index_name=config.pinecone_index_name,
                    embedding=embeddings,
                    text_key="text",
                    namespace=namespace
                )
            except Exception as e3:
                print(f"Všechny pokusy o inicializaci vektorového úložiště selhaly: {e3}")
                raise

def add_documents_to_vector_store(
    vector_store: Optional[PineconeVectorStore] = None,
    texts: Optional[List[str]] = None,
    metadatas: Optional[List[Dict[str, Any]]] = None,
    namespace: Optional[str] = None,
    documents: Optional[List[Document]] = None
) -> None:
    """
    Přidá dokumenty do vektorové databáze.
    
    Args:
        vector_store: Instance vektorové databáze
        texts: Seznam textů k přidání
        metadatas: Seznam metadat k přidání
        namespace: Namespace pro vektorovou databázi
        documents: Seznam dokumentů k přidání (alternativa k texts a metadatas)
    """
    if vector_store is None:
        vector_store = get_vector_store()
    
    # Maximální velikost metadat v bajtech (30 KB - s rezervou pod limit 40 KB)
    MAX_METADATA_SIZE = 30 * 1024
    
    try:
        if documents:
            # Kontrola velikosti metadat pro každý dokument
            for i, doc in enumerate(documents):
                metadata_size = len(json.dumps(doc.metadata).encode('utf-8'))
                if metadata_size > MAX_METADATA_SIZE:
                    print(f"Varování: Metadata pro dokument {i+1} jsou příliš velká ({metadata_size} bajtů). Budou zkrácena.")
                    
                    # Zkrácení metadat - ponecháme jen základní informace
                    minimal_metadata = {
                        "source": doc.metadata.get("source", "")[-100:],  # Omezení délky cesty
                        "title": doc.metadata.get("title", "")[:50],      # Omezení délky názvu
                        "truncated": True
                    }
                    
                    # Aktualizace metadat dokumentu
                    doc.metadata = minimal_metadata
            
            # Přidání dokumentů do vektorové databáze
            try:
                vector_store.add_documents(documents, namespace=namespace)
            except Exception as e:
                print(f"Chyba při hromadném přidávání dokumentů: {e}")
                print("Pokusím se přidat dokumenty jednotlivě...")
                
                # Pokud selže hromadné přidání, zkusíme přidat dokumenty jednotlivě
                for i, doc in enumerate(documents):
                    try:
                        vector_store.add_documents([doc], namespace=namespace)
                        print(f"Dokument {i+1}/{len(documents)} úspěšně přidán.")
                    except Exception as e2:
                        print(f"Chyba při přidávání dokumentu {i+1}/{len(documents)}: {e2}")
        
        elif texts and metadatas:
            # Kontrola velikosti metadat pro každý dokument
            for i, metadata in enumerate(metadatas):
                metadata_size = len(json.dumps(metadata).encode('utf-8'))
                if metadata_size > MAX_METADATA_SIZE:
                    print(f"Varování: Metadata pro dokument {i+1} jsou příliš velká ({metadata_size} bajtů). Budou zkrácena.")
                    
                    # Zkrácení metadat - ponecháme jen základní informace
                    minimal_metadata = {
                        "source": metadata.get("source", "")[-100:],  # Omezení délky cesty
                        "title": metadata.get("title", "")[:50],      # Omezení délky názvu
                        "truncated": True
                    }
                    
                    # Aktualizace metadat
                    metadatas[i] = minimal_metadata
            
            # Vytvoření dokumentů
            docs = [Document(page_content=text, metadata=metadata) 
                   for text, metadata in zip(texts, metadatas)]
            
            # Přidání dokumentů do vektorové databáze
            try:
                vector_store.add_documents(docs, namespace=namespace)
            except Exception as e:
                print(f"Chyba při hromadném přidávání dokumentů: {e}")
                print("Pokusím se přidat dokumenty jednotlivě...")
                
                # Pokud selže hromadné přidání, zkusíme přidat dokumenty jednotlivě
                for i, doc in enumerate(docs):
                    try:
                        vector_store.add_documents([doc], namespace=namespace)
                        print(f"Dokument {i+1}/{len(docs)} úspěšně přidán.")
                    except Exception as e2:
                        print(f"Chyba při přidávání dokumentu {i+1}/{len(docs)}: {e2}")
        
        else:
            raise ValueError("Je třeba poskytnout buď documents nebo texts a metadatas")
    
    except Exception as e:
        print(f"Chyba při přidávání dokumentů do vektorové databáze: {e}")
        raise

def similarity_search(query: str, k: int = 5, namespace: Optional[str] = None) -> List[Document]:
    """
    Provede vyhledávání podobných dokumentů.
    
    Args:
        query: Dotaz pro vyhledávání
        k: Počet výsledků
        namespace: Namespace pro vyhledávání (volitelné)
        
    Returns:
        List[Document]: Seznam podobných dokumentů
    """
    # Pokud není zadán namespace, použijeme výchozí z konfigurace
    if namespace is None:
        namespace = os.getenv("PINECONE_NAMESPACE", "proposals")
        print(f"Používám výchozí namespace pro vyhledávání: {namespace}")
    
    print(f"Inicializace vektorové databáze pro vyhledávání...")
    vector_store = get_vector_store(namespace=namespace)
    
    print(f"Vyhledávání dokumentů podobných dotazu: '{query}'")
    print(f"Počet požadovaných výsledků: {k}")
    print(f"Namespace: {namespace}")
    
    try:
        results = vector_store.similarity_search(query, k=k)
        print(f"Nalezeno {len(results)} výsledků.")
        return results
    except Exception as e:
        print(f"Chyba při vyhledávání: {e}")
        return []

def delete_all_vectors() -> None:
    """
    Smaže všechny vektory z vektorové databáze.
    """
    try:
        # Inicializace Pinecone
        init_pinecone()
        
        # Získání instance indexu
        try:
            # Zkusíme novější způsob inicializace s Pinecone 2.x
            pc = pinecone.Pinecone(api_key=config.pinecone_api_key)
            index = pc.Index(config.pinecone_index_name)
            
            # Smazání všech vektorů
            index.delete(delete_all=True)
            print("Všechny vektory byly úspěšně smazány.")
        except Exception as e:
            print(f"Chyba při mazání vektorů s novým API: {e}")
            print("Zkouším starší způsob mazání...")
            
            try:
                # Zkusíme starší způsob inicializace s Pinecone 1.x
                index = pinecone.Index(config.pinecone_index_name)
                index.delete(delete_all=True)
                print("Všechny vektory byly úspěšně smazány (starší API).")
            except Exception as e2:
                print(f"Chyba i při starším způsobu mazání vektorů: {e2}")
                raise
    except Exception as e:
        print(f"Chyba při mazání vektorů: {e}")
        raise

def init_vector_store() -> PineconeVectorStore:
    """
    Inicializuje a vrací instanci vektorového úložiště Pinecone.
    
    Returns:
        PineconeVectorStore: Instance vektorového úložiště
    """
    return get_vector_store() 