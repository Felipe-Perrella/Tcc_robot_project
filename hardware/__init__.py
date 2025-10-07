"""
hardware/__init__.py
====================
Módulo de componentes de hardware do robô.

Exporta todas as classes de hardware para fácil importação.

Uso:
    from hardware import L298NController, BrushController
    
    # Ou importar tudo:
    from hardware import *
"""

from .motors import L298NController
from .brushes import BrushController
from .sensors import UltrasonicSensor
from .camera import CameraVision

# Define o que é exportado ao usar "from hardware import *"
__all__ = [
    'L298NController',
    'BrushController',
    'UltrasonicSensor',
    'CameraVision'
]