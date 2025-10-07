"""
logic/__init__.py
=================
Módulo de lógica de controle do robô.

Exporta classes relacionadas à lógica e estados.

Uso:
    from logic import Robot, RobotState
"""

from .states import RobotState
from .robot import Robot

# Define o que é exportado
__all__ = [
    'RobotState',
    'Robot'
]