"""Modul pro řízení toku generování nabídek."""
from enum import Enum
from typing import Dict, Any, Optional
from dataclasses import dataclass, field
from datetime import date

class Step(str, Enum):
    """Kroky v procesu generování nabídky."""
    ANALYZE_REQUEST = "analyze_request"
    GATHER_INFORMATION = "gather_information"
    GENERATE_PROPOSAL = "generate_proposal"
    CREATE_DOCUMENT = "create_document"
    HUMAN_FEEDBACK = "human_feedback"
    END = "end"

@dataclass
class ProposalState:
    """Stav procesu generování nabídky."""
    client_request: str = ""
    expected_users: int = 100
    deadline: Optional[date] = None
    modules: list = field(default_factory=list)
    integrations: list = field(default_factory=list)
    training: list = field(default_factory=list)
    support_level: str = "Basic"
    chat_history: list = field(default_factory=list)
    current_step: Step = Step.ANALYZE_REQUEST
    step_counter: Dict[str, int] = field(default_factory=dict)

class SimpleStateGraph:
    """Jednoduchá implementace grafu stavů."""
    
    def __init__(self):
        self.nodes = {}
        self.entry_point = None
    
    def add_node(self, name: str, function: callable):
        """Přidá uzel do grafu."""
        self.nodes[name] = function
    
    def set_entry_point(self, name: str):
        """Nastaví počáteční uzel."""
        self.entry_point = name
    
    def invoke(self, state: ProposalState) -> ProposalState:
        """Spustí graf s daným stavem."""
        current_step = state.current_step
        
        # Kontrola počtu rekurzivních volání
        state.step_counter[current_step] = state.step_counter.get(current_step, 0) + 1
        
        # Prevence zacyklení
        if state.step_counter[current_step] > 10:
            state.current_step = Step.HUMAN_FEEDBACK
            return state
        
        try:
            # Spuštění funkce pro aktuální krok
            if current_step in self.nodes:
                state = self.nodes[current_step](state)
        except Exception as e:
            print(f"Chyba při spuštění funkce pro krok {current_step}: {e}")
            state.current_step = Step.HUMAN_FEEDBACK
        
        return state 