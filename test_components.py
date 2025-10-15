"""
test_components.py - Testes individuais dos componentes
=======================================================

Script para testar cada componente do robô isoladamente.
Útil para verificar conexões e funcionamento antes da integração.
"""

import time
import RPi.GPIO as GPIO
from hardware import L298NController, BrushController, UltrasonicSensor, CameraVision
from config import MOTOR_PINS, BRUSH_MOTOR_PINS, ULTRASONIC_PINS


def test_motors():
    """Testa motores de locomoção"""
    print("\n" + "="*50)
    print("TESTE DOS MOTORES DE LOCOMOÇÃO")
    print("="*50)
    
    motors = L298NController(MOTOR_PINS)
    
    try:
        print("\n1. Frente (3 segundos)...")
        motors.set_speed(50)
        motors.move_forward()
        time.sleep(3)
        motors.stop()
        time.sleep(1)
        
        print("2. Trás (3 segundos)...")
        motors.move_backward()
        time.sleep(3)
        motors.stop()
        time.sleep(1)
        
        print("3. Girar esquerda (2 segundos)...")
        motors.turn_left()
        time.sleep(2)
        motors.stop()
        time.sleep(1)
        
        print("4. Girar direita (2 segundos)...")
        motors.turn_right()
        time.sleep(2)
        motors.stop()
        
        print("\nTeste dos motores concluído")
        
    except KeyboardInterrupt:
        print("\nTeste interrompido")
    
    finally:
        motors.cleanup()


def test_brushes():
    """Testa motores das vassouras"""
    print("\n" + "="*50)
    print("TESTE DOS MOTORES DAS VASSOURAS")
    print("="*50)
    
    brushes = BrushController(BRUSH_MOTOR_PINS, brush_speed=60)
    
    try:
        print("\n1. Ligando vassouras a 60% (5 segundos)...")
        brushes.start()
        time.sleep(5)
        
        print("2. Aumentando para 90% (3 segundos)...")
        brushes.set_speed(90)
        time.sleep(3)
        
        print("3. Diminuindo para 40% (3 segundos)...")
        brushes.set_speed(40)
        time.sleep(3)
        
        brushes.stop()
        print("\nTeste das vassouras concluído")
        
    except KeyboardInterrupt:
        print("\nTeste interrompido")
    
    finally:
        brushes.cleanup()


def test_ultrasonic():
    """Testa sensor ultrassônico"""
    print("\n" + "="*50)
    print("TESTE DO SENSOR ULTRASSÔNICO")
    print("="*50)
    print("\nMedindo distância continuamente...")
    print("(O sensor está embaixo do robô)")
    print("Pressione Ctrl+C para parar\n")
    
    sensor = UltrasonicSensor(
        ULTRASONIC_PINS['trigger'],
        ULTRASONIC_PINS['echo']
    )
    
    try:
        while True:
            distance = sensor.get_distance()
            
            if distance < 999:
                # Indicador visual
                bars = int(distance / 2)  # 1 barra a cada 2cm
                bars = min(bars, 50)  # Máximo 50 barras
                
                print(f"Distância: {distance:6.2f} cm | {'█' * bars}")
                
                # Indicar se está sobre placa
                if distance <= 15:
                    print("         >>> SOBRE PLACA SOLAR <<<")
            else:
                print("Erro na leitura")
            
            time.sleep(0.5)
    
    except KeyboardInterrupt:
        print("\n\nTeste do sensor concluído")


def test_camera():
    """Testa sistema de visão"""
    print("\n" + "="*50)
    print("TESTE DO SISTEMA DE VISÃO")
    print("="*50)
    
    camera = CameraVision()
    
    print("\nVerificando detecção de sujeira...")
    print("(Se não implementou ainda, sempre retornará False)\n")
    
    try:
        for i in range(5):
            print(f"Teste {i+1}/5: ", end='')
            result = camera.detect_target()
            
            if result:
                print("SUJEIRA DETECTADA")
            else:
                print("Placa limpa")
            
            time.sleep(1)
        
        print("\nTeste da câmera concluído")
        
    except KeyboardInterrupt:
        print("\nTeste interrompido")
    
    finally:
        camera.cleanup()


def test_integration():
    """Teste integrado básico"""
    print("\n" + "="*50)
    print("TESTE INTEGRADO")
    print("="*50)
    print("\nO robô irá:")
    print("1. Ligar vassouras")
    print("2. Mover para frente devagar")
    print("3. Monitorar distância do chão")
    print("4. Se distância <= 15cm: continuar")
    print("5. Se distância > 15cm: parar e girar")
    print("\nPressione Ctrl+C para parar\n")
    
    input("Pressione ENTER para iniciar...")
    
    # Inicializar componentes
    motors = L298NController(MOTOR_PINS)
    brushes = BrushController(BRUSH_MOTOR_PINS)
    sensor = UltrasonicSensor(
        ULTRASONIC_PINS['trigger'],
        ULTRASONIC_PINS['echo']
    )
    
    try:
        print("Ligando vassouras...")
        brushes.start()
        time.sleep(1)
        
        print("Iniciando movimento...")
        motors.set_speed(40)
        
        while True:
            distance = sensor.get_distance()
            
            if distance < 999:
                print(f"Distância: {distance:6.2f} cm", end='')
                
                if distance <= 15:
                    # Sobre placa - continuar
                    print(" [SOBRE PLACA] Movendo...")
                    motors.move_forward()
                else:
                    # Fora da placa - girar
                    print(" [FORA DA PLACA] Girando...")
                    motors.turn_right()
            
            time.sleep(0.3)
    
    except KeyboardInterrupt:
        print("\n\nTeste interrompido")
    
    finally:
        motors.stop()
        brushes.stop()
        motors.cleanup()
        brushes.cleanup()
        GPIO.cleanup()
        print("Teste integrado concluído")


def menu():
    """Menu principal de testes"""
    while True:
        print("\n" + "="*50)
        print("    MENU DE TESTES - ROBÔ DE LIMPEZA")
        print("="*50)
        print("\n[1] Testar Motores de Locomoção")
        print("[2] Testar Motores das Vassouras")
        print("[3] Testar Sensor Ultrassônico")
        print("[4] Testar Sistema de Visão")
        print("[5] Teste Integrado")
        print("[0] Sair")
        print("-"*50)
        
        choice = input("\nEscolha uma opção: ").strip()
        
        if choice == '1':
            test_motors()
        elif choice == '2':
            test_brushes()
        elif choice == '3':
            test_ultrasonic()
        elif choice == '4':
            test_camera()
        elif choice == '5':
            test_integration()
        elif choice == '0':
            print("\nSaindo...")
            break
        else:
            print("\nOpção inválida")


if __name__ == "__main__":
    try:
        menu()
    except KeyboardInterrupt:
        print("\n\nPrograma encerrado")
    finally:
        GPIO.cleanup()
        print("GPIO limpo. Até logo")