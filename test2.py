def test_brushes():
    """Testa motores das vassouras COM servo"""
    print("\n" + "="*50)
    print("TESTE DOS MOTORES DAS VASSOURAS + SERVO")
    print("="*50)
    
    """
test_components.py - Testes individuais dos componentes
=======================================================

Script para testar cada componente do robô isoladamente.
Útil para verificar conexões e funcionamento antes da integração.
"""

import time
import RPi.GPIO as GPIO
from hardware import L298NController, BrushController, UltrasonicSensor, CameraVision, ServoController
from config import MOTOR_PINS, BRUSH_MOTOR_PINS, SERVO_PIN, ULTRASONIC_PINS


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
        print("\n1. Ligando vassouras (servo abaixa 0°->90°, motores ligam)...")
        brushes.start()
        time.sleep(5)
        
        print("2. Aumentando velocidade para 90%...")
        brushes.set_speed(90)
        time.sleep(3)
        
        print("3. Diminuindo velocidade para 40%...")
        brushes.set_speed(40)
        time.sleep(3)
        
        print("4. Desligando vassouras (motores desligam, servo levanta 90°->0°)...")
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


def test_servo():
    """Testa servo isoladamente"""
    print("\n" + "="*50)
    print("TESTE DO SERVO (LEVANTA/ABAIXA VASSOURAS)")
    print("="*50)
    
    from hardware.servo import ServoController
    
    servo = ServoController(SERVO_PIN)
    
    try:
        print("\nSequência de teste:")
        print("  0° → 90° → 180° → 90° → 0°")
        print("\nObserve o movimento do servo...\n")
        
        # 1. Posição 0° (inicial - levantado)
        print("1. Indo para 0° (vassouras LEVANTADAS)...")
        servo.set_angle(0)
        time.sleep(2)
        
        # 2. Posição 90° (meio)
        print("2. Indo para 90° (vassouras ABAIXADAS - posição de limpeza)...")
        servo.set_angle(90)
        time.sleep(2)
        
        # 3. Posição 180° (máximo)
        print("3. Indo para 180° (máximo)...")
        servo.set_angle(180)
        time.sleep(2)
        
        # 4. Voltar para 90°
        print("4. Voltando para 90°...")
        servo.set_angle(90)
        time.sleep(2)
        
        # 5. Voltar para 0° (posição inicial)
        print("5. Voltando para 0° (posição inicial)...")
        servo.set_angle(0)
        time.sleep(1)
        
        print("\nTeste do servo concluído com sucesso!")
        
    except KeyboardInterrupt:
        print("\nTeste interrompido")
    
    finally:
        servo.cleanup()


def test_camera():
    """Testa sistema de visão computacional"""
    print("\n" + "="*50)
    print("TESTE DO SISTEMA DE VISÃO COMPUTACIONAL")
    print("="*50)
    
    camera = CameraVision(
        model_path='classificador_placa_solar',
        image_size=(64, 64),
        confidence_threshold=0.7
    )
    
    if not camera.camera_ready:
        print("\n[ERRO] Câmera/Modelo não disponível!")
        print("Verifique:")
        print("  1. Modelo .tflite ou .keras existe?")
        print("  2. TensorFlow ou TFLite instalado?")
        print("  3. Câmera conectada?")
        return
    
    print("\nVerificando detecção de sujeira...")
    print("(5 testes com intervalo de 2 segundos)\n")
    
    try:
        resultados = []
        
        for i in range(5):
            print(f"--- Teste {i+1}/5 ---")
            result = camera.detect_target()
            resultados.append(result)
            
            if result:
                print("  → SUJEIRA DETECTADA")
            else:
                print("  → Placa limpa")
            
            if i < 4:
                print("\nAguardando 2 segundos...")
                time.sleep(2)
        
        # Resumo
        print("\n" + "="*50)
        print("RESUMO DOS TESTES DE VISÃO:")
        print("="*50)
        sujeira_count = sum(resultados)
        limpo_count = len(resultados) - sujeira_count
        print(f"Sujeira detectada: {sujeira_count}/5 vezes")
        print(f"Placa limpa: {limpo_count}/5 vezes")
        print("="*50)
        
    except KeyboardInterrupt:
        print("\nTeste interrompido")
    
    finally:
        camera.cleanup()


def test_servo_and_brushes():
    """Testa servo + vassouras juntos (sequência completa)"""
    print("\n" + "="*50)
    print("TESTE SERVO + VASSOURAS (SEQUÊNCIA COMPLETA)")
    print("="*50)
    
    brushes = BrushController(BRUSH_MOTOR_PINS, SERVO_PIN, brush_speed=70)
    
    try:
        print("\nSequência de teste:")
        print("  1. Servo abaixa (0° → 90°)")
        print("  2. Liga vassouras")
        print("  3. Varia velocidade")
        print("  4. Desliga vassouras")
        print("  5. Servo levanta (90° → 0°)")
        print()
        
        input("Pressione ENTER para iniciar...")
        
        # 1. Estado inicial
        print("\n1. Estado inicial (vassouras levantadas)...")
        time.sleep(1)
        
        # 2. Ligar (abaixa servo + liga motores)
        print("\n2. LIGANDO vassouras...")
        print("   - Servo abaixando (0° → 90°)...")
        print("   - Motores ligando...")
        brushes.start()
        print("   ✓ Vassouras ATIVAS!")
        time.sleep(3)
        
        # 3. Testar velocidades
        print("\n3. Testando velocidades...")
        
        print("   - Velocidade: 50%")
        brushes.set_speed(50)
        time.sleep(2)
        
        print("   - Velocidade: 80%")
        brushes.set_speed(80)
        time.sleep(2)
        
        print("   - Velocidade: 40%")
        brushes.set_speed(40)
        time.sleep(2)
        
        # 4. Desligar (desliga motores + levanta servo)
        print("\n4. DESLIGANDO vassouras...")
        print("   - Motores desligando...")
        print("   - Servo levantando (90° → 0°)...")
        brushes.stop()
        print("   ✓ Vassouras DESATIVADAS!")
        time.sleep(2)
        
        # 5. Repetir uma vez
        print("\n5. Repetindo sequência (mais rápida)...")
        
        print("   - Ligando...")
        brushes.start()
        time.sleep(2)
        
        print("   - Desligando...")
        brushes.stop()
        
        print("\nTeste completo concluído!")
        
    except KeyboardInterrupt:
        print("\nTeste interrompido")
    
    finally:
        brushes.cleanup()


def test_full_integration():
    """Teste integrado completo: todos os componentes funcionando juntos"""
    print("\n" + "="*50)
    print("TESTE INTEGRADO COMPLETO")
    print("="*50)
    print("\nEste teste simula o funcionamento real do robô:")
    print("  1. Move para frente")
    print("  2. Monitora distância (sensor ultrassônico)")
    print("  3. Se detecta 'placa' (≤15cm):")
    print("     a) Abaixa vassouras")
    print("     b) Liga vassouras")
    print("     c) Verifica visão (a cada 5s neste teste)")
    print("     d) Continua movendo")
    print("  4. Se perde 'placa' (>15cm):")
    print("     a) Desliga vassouras")
    print("     b) Levanta vassouras")
    print("     c) Gira procurando")
    print("\nPressione Ctrl+C para parar\n")
    
    input("Pressione ENTER para iniciar...")
    
    # Inicializar componentes
    motors = L298NController(MOTOR_PINS)
    brushes = BrushController(BRUSH_MOTOR_PINS, SERVO_PIN)
    sensor = UltrasonicSensor(
        ULTRASONIC_PINS['trigger'],
        ULTRASONIC_PINS['echo']
    )
    camera = CameraVision(
        model_path='classificador_placa_solar',
        confidence_threshold=0.7
    )
    
    # Variáveis de controle
    on_panel = False
    last_vision_check = 0
    vision_interval = 5  # 5 segundos para teste (no robô real é 15s)
    dirt_detected = False
    
    try:
        print("\nIniciando teste integrado...\n")
        motors.set_speed(40)
        iteration = 0
        
        while True:
            iteration += 1
            
            # 1. LER SENSOR
            distance = sensor.get_distance()
            was_on_panel = on_panel
            on_panel = (distance > 0 and distance <= 15)
            
            # 2. MUDANÇA DE ESTADO
            if on_panel and not was_on_panel:
                print("\n>>> PLACA DETECTADA! <<<")
                print("Iniciando limpeza...")
                last_vision_check = 0  # Força verificação imediata
            
            elif not on_panel and was_on_panel:
                print("\n>>> PLACA PERDIDA! <<<")
                print("Parando limpeza...")
                if brushes.is_running():
                    brushes.stop()
            
            # 3. VERIFICAR VISÃO (se sobre placa)
            if on_panel and camera.camera_ready:
                current_time = time.time()
                if current_time - last_vision_check >= vision_interval:
                    print(f"\n[{vision_interval}s] Verificando visão...")
                    dirt_detected = camera.detect_target()
                    last_vision_check = current_time
            
            # 4. CONTROLAR VASSOURAS
            should_clean = on_panel and dirt_detected
            
            if should_clean and not brushes.is_running():
                print(">>> Ligando vassouras (sujeira detectada)")
                brushes.start()
            elif not should_clean and brushes.is_running():
                print(">>> Desligando vassouras")
                brushes.stop()
            
            # 5. MOVIMENTAR
            if on_panel:
                # Sobre placa: andar devagar
                speed = 20 if dirt_detected else 35
                motors.set_speed(speed)
                motors.move_forward()
                state = "LIMPANDO" if brushes.is_running() else "ESCANEANDO"
            else:
                # Fora da placa: girar procurando
                motors.set_speed(40)
                motors.turn_right()
                state = "PROCURANDO"
            
            # 6. STATUS
            if iteration % 3 == 0:  # A cada 3 iterações (300ms)
                panel_status = "SIM" if on_panel else "NÃO"
                brush_status = "ON" if brushes.is_running() else "OFF"
                dirt_status = "SUJEIRA" if dirt_detected else "Limpo"
                
                print(f"[{state:12s}] Placa:{panel_status:3s} | "
                      f"Dist:{distance:5.1f}cm | "
                      f"{dirt_status:7s} | "
                      f"Vassouras:{brush_status}")
            
            time.sleep(0.1)
    
    except KeyboardInterrupt:
        print("\n\nTeste interrompido!")
    
    finally:
        print("\nDesligando componentes...")
        motors.stop()
        brushes.stop()
        motors.cleanup()
        brushes.cleanup()
        camera.cleanup()
        GPIO.cleanup()
        print("Teste integrado concluído!")


def test_servo():
    """Testa servo isoladamente"""
    print("\n" + "="*50)
    print("TESTE DO SERVO (LEVANTA/ABAIXA)")
    print("="*50)
    
    servo = ServoController(SERVO_PIN)
    
    try:
        print("\n1. Servo em 0° (vassouras levantadas)...")
        servo.lift_up()
        time.sleep(2)
        
        print("2. Servo em 90° (vassouras abaixadas)...")
        servo.lower_down()
        time.sleep(2)
        
        print("3. Testando posições intermediárias...")
        for angle in [0, 30, 60, 90, 60, 30, 0]:
            print(f"   Posição: {angle}°")
            servo.set_angle(angle)
            time.sleep(1)
        
        print("\n4. Retornando para posição inicial (0°)...")
        servo.lift_up()
        
        print("\nTeste do servo concluído")
        
    except KeyboardInterrupt:
        print("\nTeste interrompido")
    
    finally:
        servo.cleanup()


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
    print("1. Mover para frente devagar")
    print("2. Monitorar distância do chão")
    print("3. Se distância <= 15cm:")
    print("   -> Abaixa vassouras (servo)")
    print("   -> Liga vassouras")
    print("   -> Continua movendo")
    print("4. Se distância > 15cm:")
    print("   -> Desliga vassouras")
    print("   -> Levanta vassouras (servo)")
    print("   -> Gira procurando placa")
    print("\nPressione Ctrl+C para parar\n")
    
    input("Pressione ENTER para iniciar...")
    
    # Inicializar componentes
    motors = L298NController(MOTOR_PINS)
    brushes = BrushController(BRUSH_MOTOR_PINS, SERVO_PIN)
    sensor = UltrasonicSensor(
        ULTRASONIC_PINS['trigger'],
        ULTRASONIC_PINS['echo']
    )
    
    try:
        print("Iniciando movimento...")
        motors.set_speed(40)
        
        while True:
            distance = sensor.get_distance()
            
            if distance < 999:
                print(f"Distância: {distance:6.2f} cm", end='')
                
                if distance <= 15:
                    # Sobre placa - ligar vassouras e continuar
                    print(" [SOBRE PLACA] ", end='')
                    if not brushes.is_running():
                        print("Ligando vassouras...")
                        brushes.start()
                    else:
                        print("Movendo e limpando...")
                    motors.move_forward()
                else:
                    # Fora da placa - desligar vassouras e girar
                    print(" [FORA DA PLACA] ", end='')
                    if brushes.is_running():
                        print("Desligando vassouras...")
                        brushes.stop()
                    else:
                        print("Girando...")
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
        print("\n=== TESTES DE HARDWARE ===")
        print("[1] Testar Motores de Locomoção")
        print("[2] Testar Motores das Vassouras + Servo")
        print("[3] Testar Sensor Ultrassônico")
        print("[4] Testar Servo Isoladamente (0°→90°→180°→90°→0°)")
        print("\n=== TESTES AVANÇADOS ===")
        print("[5] Testar Sistema de Visão Computacional")
        print("[6] Testar Servo + Vassouras (Sequência Completa)")
        print("[7] Teste Integrado Completo (TUDO)")
        print("\n[0] Sair")
        print("-"*50)
        
        choice = input("\nEscolha uma opção: ").strip()
        
        if choice == '1':
            test_motors()
        elif choice == '2':
            test_brushes()
        elif choice == '3':
            test_ultrasonic()
        elif choice == '4':
            test_servo()
        elif choice == '5':
            test_camera()
        elif choice == '6':
            test_servo_and_brushes()
        elif choice == '7':
            test_full_integration()
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