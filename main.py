"""
main.py - Ponto de entrada do robô (versão modular)
====================================================

Este é o arquivo principal simplificado.
As classes foram movidas para módulos separados.

Estrutura:
    hardware/ - Classes de hardware (motores, sensores)
    logic/    - Classes de lógica (estados, robô)
    config.py - Configurações
"""

# Importar classes dos módulos
from logic import Robot
from config import MOTOR_PINS, BRUSH_MOTOR_PINS, ULTRASONIC_PINS
from config import SAFE_DISTANCE, SEARCH_SPEED, MOVE_SPEED


def main():
    """
    Função principal do programa.
    
    Cria e inicia o robô com as configurações do config.py
    """
    # Criar robô com configurações
    robot = Robot(
        motor_pins=MOTOR_PINS,
        brush_pins=BRUSH_MOTOR_PINS,
        ultrasonic_pins=ULTRASONIC_PINS,
        safe_distance=SAFE_DISTANCE,
        search_speed=SEARCH_SPEED,
        move_speed=MOVE_SPEED
    )
    
    # Iniciar robô (entra no loop principal)
    robot.start()


if __name__ == "__main__":
    """
    Ponto de entrada quando arquivo é executado diretamente.
    
    Uso:
        python3 main.py
    """
    main()