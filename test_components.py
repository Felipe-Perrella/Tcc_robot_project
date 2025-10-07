# test_components.py - Testes individuais dos componentes

import sys
import time
from config import *

# Importar as classes do main.py
try:
    from main import L298NController, UltrasonicSensor, CameraVision, BrushController
except ImportError:
    print("ERRO: Não foi possível importar main.py")
    sys.exit(1)


def test_motors():
    """Testa os motores individualmente"""
    print("\n" + "="*50)
    print("TESTE DOS MOTORES")
    print("="*50)
    
    motors = L298NController(MOTOR_PINS)
    
    try:
        # Teste de velocidade baixa
        print("\n1. Testando velocidade baixa (30%)...")
        motors.set_speed(30)
        
        print("   - Frente por 2 segundos")
        motors.move_forward()
        time.sleep(2)
        motors.stop()
        time.sleep(1)
        
        print("   - Trás por 2 segundos")
        motors.move_backward()
        time.sleep(2)
        motors.stop()
        time.sleep(1)
        
        # Teste de giros
        print("\n2. Testando giros (velocidade 50%)...")
        motors.set_speed(50)
        
        print("   - Girando à esquerda por 1 segundo")
        motors.turn_left()
        time.sleep(1)
        motors.stop()
        time.sleep(1)
        
        print("   - Girando à direita por 1 segundo")
        motors.turn_right()
        time.sleep(1)
        motors.stop()
        time.sleep(1)
        
        # Teste de velocidade alta
        print("\n3. Testando velocidade alta (80%)...")
        motors.set_speed(80)
        print("   - Frente por 1 segundo")
        motors.move_forward()
        time.sleep(1)
        motors.stop()
        
        print("\n✓ Teste dos motores concluído!")
        
    except KeyboardInterrupt:
        print("\nTeste interrompido pelo usuário")
    finally:
        motors.cleanup()


def test_ultrasonic():
    """Testa o sensor ultrassônico"""
    print("\n" + "="*50)
    print("TESTE DO SENSOR ULTRASSÔNICO")
    print("="*50)
    
    sensor = UltrasonicSensor(
        ULTRASONIC_PINS['trigger'],
        ULTRASONIC_PINS['echo']
    )
    
    print("\nLendo distâncias por 10 segundos...")
    print("(Pressione Ctrl+C para parar)")
    print("\nDistância (cm):")
    
    try:
        for i in range(100):  # 10 segundos com leitura a cada 0.1s
            distance = sensor.get_distance()
            
            # Barra de progresso visual
            bar_length = int(distance / 5)  # Cada '#' representa 5cm
            bar = '#' * min(bar_length, 40)
            
            print(f"\r{distance:6.2f} cm [{bar:<40}]", end='')
            
            if distance < SAFE_DISTANCE:
                print(" ⚠️  OBSTÁCULO!", end='')
            
            time.sleep(0.1)
        
        print("\n\n✓ Teste do sensor concluído!")
        
    except KeyboardInterrupt:
        print("\n\nTeste interrompido pelo usuário")


def test_camera():
    """Testa a interface da câmera"""
    print("\n" + "="*50)
    print("TESTE DA CÂMERA/VISÃO")
    print("="*50)
    
    camera = CameraVision()
    
    print("\nSimulando detecções...")
    
    # Simulação
    test_cases = [True, False, True, True, False]
    
    for i, result in enumerate(test_cases):
        camera.set_detection_result(result)
        detection = camera.detect_target()
        status = "✓ ALVO DETECTADO" if detection else "✗ Sem alvo"
        print(f"Teste {i+1}: {status}")
        time.sleep(0.5)
    
    print("\n⚠️  IMPORTANTE: Substitua a classe CameraVision")
    print("   pelo seu algoritmo real de visão!")
    print("\n✓ Teste da câmera concluído!")


def test_brushes():
    """Testa os motores das vassouras"""
    print("\n" + "="*50)
    print("TESTE DOS MOTORES DAS VASSOURAS")
    print("="*50)
    
    from config import BRUSH_MOTOR_PINS, BRUSH_CONFIG
    
    brushes = BrushController(BRUSH_MOTOR_PINS, BRUSH_CONFIG['speed'])
    
    try:
        print("\n1. Ligando vassouras por 3 segundos...")
        brushes.start()
        time.sleep(3)
        
        print("\n2. Desligando vassouras...")
        brushes.stop()
        time.sleep(1)
        
        print("\n3. Teste de velocidade diferente (50%)...")
        brushes.set_speed(50)
        brushes.start()
        time.sleep(2)
        brushes.stop()
        
        print("\n✓ Teste das vassouras concluído!")
        
    except KeyboardInterrupt:
        print("\nTeste interrompido pelo usuário")
    finally:
        brushes.cleanup()


def test_camera():
    """Testa a interface da câmera"""
    print("\n" + "="*50)
    print("TESTE DA CÂMERA/VISÃO")
    print("="*50)
    
    camera = CameraVision()
    
    print("\nSimulando detecções...")
    
    # Simulação
    test_cases = [True, False, True, True, False]
    
    for i, result in enumerate(test_cases):
        camera.set_detection_result(result)
        detection = camera.detect_target()
        status = "✓ ALVO DETECTADO" if detection else "✗ Sem alvo"
        print(f"Teste {i+1}: {status}")
        time.sleep(0.5)
    
    print("\n⚠️  IMPORTANTE: Substitua a classe CameraVision")
    print("   pelo seu algoritmo real de visão!")
    print("\n✓ Teste da câmera concluído!")


def test_complete_system():
    """Teste rápido do sistema completo"""
    print("\n" + "="*50)
    print("TESTE DO SISTEMA COMPLETO")
    print("="*50)
    
    from config import BRUSH_MOTOR_PINS, BRUSH_CONFIG
    
    motors = L298NController(MOTOR_PINS)
    sensor = UltrasonicSensor(
        ULTRASONIC_PINS['trigger'],
        ULTRASONIC_PINS['echo']
    )
    camera = CameraVision()
    brushes = BrushController(BRUSH_MOTOR_PINS, BRUSH_CONFIG['speed'])
    
    print("\nTestando integração completa por 10 segundos...")
    print("O robô vai girar procurando alvo e monitorar obstáculos")
    print("Vassouras vão ligar quando alvo for 'detectado'")
    
    try:
        start_time = time.time()
        motors.set_speed(40)
        
        # Simular algumas detecções
        detection_times = [2, 4, 6, 8]
        next_detection_idx = 0
        
        while time.time() - start_time < 10:
            distance = sensor.get_distance()
            
            # Simular detecção em tempos específicos
            elapsed = time.time() - start_time
            if next_detection_idx < len(detection_times):
                if elapsed >= detection_times[next_detection_idx]:
                    target = True
                    next_detection_idx += 1
                elif elapsed >= detection_times[next_detection_idx-1] + 1:
                    target = False
                else:
                    target = camera.detect_target()
            else:
                target = False
            
            # Controlar vassouras
            if target and not brushes.is_running():
                brushes.start()
            elif not target and brushes.is_running():
                brushes.stop()
            
            brush_status = "🧹 ON" if brushes.is_running() else "🧹 OFF"
            print(f"\rDist: {distance:6.2f}cm | Alvo: {target} | {brush_status}", end='')
            
            if distance < SAFE_DISTANCE:
                motors.stop()
                brushes.stop()
                print(" - OBSTÁCULO! Parando...", end='')
            else:
                motors.turn_right()
            
            time.sleep(0.1)
        
        motors.stop()
        brushes.stop()
        print("\n\n✓ Teste do sistema completo concluído!")
        
    except KeyboardInterrupt:
        print("\n\nTeste interrompido")
    finally:
        motors.cleanup()
        brushes.cleanup()


def menu():
    """Menu principal de testes"""
    print("\n" + "="*50)
    print("MENU DE TESTES DO ROBÔ")
    print("="*50)
    print("\n1. Testar motores (L298N)")
    print("2. Testar sensor ultrassônico")
    print("3. Testar câmera/visão")
    print("4. Testar motores das vassouras")
    print("5. Teste completo do sistema")
    print("6. Validar configurações")
    print("0. Sair")
    print("\n" + "="*50)


if __name__ == "__main__":
    # Validar configurações primeiro
    errors = validate_config()
    if errors:
        print("\n⚠️  ERROS NA CONFIGURAÇÃO:")
        for error in errors:
            print(f"  {error}")
        print("\nCorreja os erros em config.py antes de continuar!")
        sys.exit(1)
    
    print("✓ Configurações válidas!")
    
    while True:
        menu()
        
        try:
            choice = input("\nEscolha uma opção: ").strip()
            
            if choice == '1':
                test_motors()
            elif choice == '2':
                test_ultrasonic()
            elif choice == '3':
                test_camera()
            elif choice == '4':
                test_brushes()
            elif choice == '5':
                test_complete_system()
            elif choice == '6':
                errors = validate_config()
                if errors:
                    for error in errors:
                        print(f"  {error}")
                else:
                    print("\n✓ Todas as configurações estão válidas!")
            elif choice == '0':
                print("\nSaindo...")
                break
            else:
                print("\n⚠️  Opção inválida!")
                
            input("\nPressione ENTER para continuar...")
            
        except KeyboardInterrupt:
            print("\n\nSaindo...")
            break
        except Exception as e:
            print(f"\n⚠️  Erro: {e}")
            input("\nPressione ENTER para continuar...")