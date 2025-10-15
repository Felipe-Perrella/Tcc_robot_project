"""
logic/states.py
===============
Define os estados possíveis do robô
"""

from enum import Enum


class RobotState(Enum):
    """
    Estados do robô de limpeza de placas solares.
    """
    
    # Procurando placa solar pela primeira vez (gira no lugar)
    INITIAL_SEARCH = "initial_search"
    
    # Sobre a placa, escaneando e limpando
    MOVING_TO_TARGET = "moving_to_target"
    
    # Saiu da placa, executando manobra para voltar
    REPOSITIONING = "repositioning"
    
    # Robô parado (emergência ou fim)
    STOPPED = "stopped"


class TurnDirection(Enum):
    """
    Direção da próxima curva quando sai da placa.
    
    Alterna entre esquerda e direita.
    """
    LEFT = "left"
    RIGHT = "right"


class RepositionStep(Enum):
    """
    Passos da manobra quando perde a placa.
    
    Sequência:
    1. TURNING_90: Vira 90° (esquerda ou direita)
    2. MOVING_SIDEWAYS: Anda largura do robô
    3. TURNING_90_BACK: Vira 90° de volta
    4. MOVING_FORWARD: Anda reto procurando placa novamente
    """
    TURNING_90 = "turning_90"             # Virando 90°
    MOVING_SIDEWAYS = "moving_sideways"   # Andando para o lado (largura do robô)
    TURNING_90_BACK = "turning_90_back"   # Virando 90° de volta
    MOVING_FORWARD = "moving_forward"     # Andando para frente procurando placa