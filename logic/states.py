"""
logic/states.py
===============
Define os estados possíveis do robô de limpeza de placas solares
"""

from enum import Enum


class RobotState(Enum):
    """
    Estados da máquina de estados do robô.
    
    O robô opera em 2 estados principais:
    - SEARCHING: Procurando placa solar (girando)
    - MOVING_TO_TARGET: Sobre a placa (escaneando/limpando)
    
    Fluxo típico:
        SEARCHING → (sensor detecta placa) → MOVING_TO_TARGET
                                                    ↓
                                            (a cada 15s verifica visão)
                                                    ↓
                                            (se sai da placa)
                                                    ↓
        SEARCHING ← ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ┘
    """
    
    SEARCHING = "searching"
    """
    Estado: Procurando placa solar
    
    Comportamento:
    - Robô gira no próprio eixo
    - Sensor ultrassônico procura placa embaixo
    - Vassouras: OFF (economizar energia)
    - Velocidade: SEARCH_SPEED (50%)
    
    Transição para MOVING_TO_TARGET quando:
    - Sensor ultrassônico ≤ PANEL_DISTANCE (15cm)
    """
    
    MOVING_TO_TARGET = "moving_to_target"
    """
    Estado: Sobre a placa (escaneando ou limpando)
    
    Comportamento:
    - Robô anda para frente sobre a placa
    - Sensor ultrassônico confirma presença da placa
    - A cada 15s: verifica visão computacional
    - Vassouras: ON se detectou sujeira, OFF se não detectou
    - Velocidade: 
      - Sem sujeira: SCAN_SPEED (40%)
      - Com sujeira: SCAN_SPEED // 3 (13% - devagar para limpar)
    
    Transição para SEARCHING quando:
    - Sensor ultrassônico > PANEL_DISTANCE (saiu da placa)
    """
    
    STOPPED = "stopped"
    """
    Estado: Robô parado
    
    Comportamento:
    - Todos os motores parados
    - Vassouras: OFF
    - Usado apenas ao encerrar programa
    """


# Mensagens amigáveis para cada estado (opcional, para logs)
STATE_MESSAGES = {
    RobotState.SEARCHING: "🔍 Procurando placa solar...",
    RobotState.MOVING_TO_TARGET: "🤖 Escaneando/limpando placa",
    RobotState.STOPPED: "🛑 Robô parado"
}


def get_state_message(state: RobotState) -> str:
    """
    Retorna mensagem amigável para um estado.
    
    Args:
        state: Estado do robô
        
    Returns:
        str: Mensagem descritiva do estado
    """
    return STATE_MESSAGES.get(state, f"Estado: {state.value}")