"""
main.py - Ponto de entrada do robô de limpeza de placas solares
================================================================

Sistema autônomo que:
1. Detecta placa solar embaixo (sensor ultrassônico)
2. Escaneia placa procurando sujeira (câmera - a cada X segundos)
3. Liga vassouras apenas quando detecta sujeira
4. Gira procurando novas placas quando sai da placa atual

Estrutura modular:
    hardware/ - Componentes físicos (motores, sensores, câmera)
    logic/    - Lógica de controle (estados, coordenação)
    config.py - Configurações centralizadas
"""

from logic import Robot
from config import (
    MOTOR_PINS, 
    BRUSH_MOTOR_PINS,
    SERVO_PIN,
    ULTRASONIC_PINS,
    PANEL_DISTANCE,
    PANEL_LOST_THRESHOLD,
    SEARCH_SPEED,
    SCAN_SPEED,
    TURN_90_TIME,
    SIDEWAYS_TIME
)


def main():
    """
    Função principal do programa.
    
    Cria robô com configurações do config.py e inicia operação.
    """
    print("\n" + "="*60)
    print("ROBÔ AUTÔNOMO DE LIMPEZA DE PLACAS SOLARES")
    print("="*60)
    
    # Validar configuração
    from config import validate_config
    errors = validate_config()
    if errors:
        print("\nERROS NA CONFIGURAÇÃO:")
        for error in errors:
            print(f"  - {error}")
        print("\nCorreja os erros em config.py antes de continuar.")
        return
    
    # Criar robô com configurações
    robot = Robot(
        motor_pins=MOTOR_PINS,
        brush_pins=BRUSH_MOTOR_PINS,
        servo_pin=SERVO_PIN,
        ultrasonic_pins=ULTRASONIC_PINS,
        panel_distance=PANEL_DISTANCE,
        search_speed=SEARCH_SPEED,
        scan_speed=SCAN_SPEED,
        vision_check_interval=15,      # Verificar visão a cada 15s
        turn_90_time=TURN_90_TIME,     # Tempo para virar 90°
        sideways_time=SIDEWAYS_TIME    # Tempo andando lateral (largura robô)
    )
    
    # Configurar filtro anti-interferência
    robot.panel_lost_threshold = PANEL_LOST_THRESHOLD
    
    # Iniciar robô (entra no loop principal)
    robot.start()


if __name__ == "__main__":
    """
    Ponto de entrada quando arquivo é executado diretamente.
    
    Uso:
        python3 main.py
    
    Para parar:
        Pressione Ctrl+C
    """
    try:
        main()
    except Exception as e:
        print(f"\nERRO CRÍTICO: {e}")
        import traceback
        traceback.print_exc()
    finally:
        print("\nPrograma finalizado.")