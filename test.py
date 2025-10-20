"""
test_pins_mockados.py - Teste com pinos configurados
=====================================================

Testa todos os pinos GPIO configurados no projeto.
Usa os pinos reais definidos no config.py
"""

import RPi.GPIO as GPIO
import time


# Configuração dos pinos (mesma do config.py)
MOTOR_PINS = {
    'left_motor': {
        'in1': 22,  # Direção motor esquerdo
        'in2': 27,  # Direção motor esquerdo
        'ena': 17   # PWM velocidade motor esquerdo
    },
    'right_motor': {
        'in3': 23,  # Direção motor direito
        'in4': 24,  # Direção motor direito
        'enb': 25   # PWM velocidade motor direito
    }
}

ULTRASONIC_PINS = {
    'trigger': 6,
    'echo': 5
}

SERVO_PIN = 12

BRUSH_MOTOR_PINS = {
    'brush_1': {
        'in1': 26,   # Direção vassoura 1
        'in2': 19,   # Direção vassoura 1
        'enable': 13  # PWM velocidade vassoura 1
    },
    'brush_2': {
        'in1': 21,  # Direção vassoura 2
        'in2': 20,  # Direção vassoura 2
        'enable': 16  # PWM velocidade vassoura 2
    }
}


def listar_todos_pinos():
    """Lista todos os pinos usados no projeto"""
    pinos = []
    
    # Motores de locomoção
    for motor in MOTOR_PINS.values():
        pinos.extend(motor.values())
    
    # Vassouras
    for brush in BRUSH_MOTOR_PINS.values():
        pinos.extend(brush.values())
    
    # Sensor
    pinos.extend(ULTRASONIC_PINS.values())
    
    # Servo
    pinos.append(SERVO_PIN)
    
    return sorted(set(pinos))


def test_setup_all_pins():
    """Testa configuração de todos os pinos"""
    print("\n" + "="*60)
    print("TESTE DE CONFIGURAÇÃO DE TODOS OS PINOS GPIO")
    print("="*60)
    
    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)
    
    todos_pinos = listar_todos_pinos()
    
    print(f"\nTotal de pinos a testar: {len(todos_pinos)}")
    print(f"Pinos: {todos_pinos}\n")
    
    print("Configurando pinos como OUTPUT...\n")
    
    sucesso = []
    falha = []
    
    for pin in todos_pinos:
        try:
            GPIO.setup(pin, GPIO.OUT)
            print(f"  GPIO {pin:2d}: OK")
            sucesso.append(pin)
        except Exception as e:
            print(f"  GPIO {pin:2d}: ERRO - {e}")
            falha.append(pin)
    
    print("\n" + "-"*60)
    print(f"Sucesso: {len(sucesso)}/{len(todos_pinos)}")
    if falha:
        print(f"Falhas: {falha}")
    print("-"*60)
    
    GPIO.cleanup()
    
    return len(falha) == 0


def test_motors():
    """Testa motores de locomoção"""
    print("\n" + "="*60)
    print("TESTE DOS MOTORES DE LOCOMOÇÃO")
    print("="*60)
    
    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)
    
    # Setup
    GPIO.setup(MOTOR_PINS['left_motor']['in1'], GPIO.OUT)
    GPIO.setup(MOTOR_PINS['left_motor']['in2'], GPIO.OUT)
    GPIO.setup(MOTOR_PINS['left_motor']['ena'], GPIO.OUT)
    GPIO.setup(MOTOR_PINS['right_motor']['in3'], GPIO.OUT)
    GPIO.setup(MOTOR_PINS['right_motor']['in4'], GPIO.OUT)
    GPIO.setup(MOTOR_PINS['right_motor']['enb'], GPIO.OUT)
    
    # PWM
    pwm_left = GPIO.PWM(MOTOR_PINS['left_motor']['ena'], 1000)
    pwm_right = GPIO.PWM(MOTOR_PINS['right_motor']['enb'], 1000)
    pwm_left.start(0)
    pwm_right.start(0)
    
    try:
        print("\n1. Frente (2 segundos)...")
        GPIO.output(MOTOR_PINS['left_motor']['in1'], GPIO.HIGH)
        GPIO.output(MOTOR_PINS['left_motor']['in2'], GPIO.LOW)
        GPIO.output(MOTOR_PINS['right_motor']['in3'], GPIO.HIGH)
        GPIO.output(MOTOR_PINS['right_motor']['in4'], GPIO.LOW)
        pwm_left.ChangeDutyCycle(50)
        pwm_right.ChangeDutyCycle(50)
        time.sleep(2)
        
        print("2. Para...")
        pwm_left.ChangeDutyCycle(0)
        pwm_right.ChangeDutyCycle(0)
        time.sleep(1)
        
        print("3. Trás (2 segundos)...")
        GPIO.output(MOTOR_PINS['left_motor']['in1'], GPIO.LOW)
        GPIO.output(MOTOR_PINS['left_motor']['in2'], GPIO.HIGH)
        GPIO.output(MOTOR_PINS['right_motor']['in3'], GPIO.LOW)
        GPIO.output(MOTOR_PINS['right_motor']['in4'], GPIO.HIGH)
        pwm_left.ChangeDutyCycle(50)
        pwm_right.ChangeDutyCycle(50)
        time.sleep(2)
        
        print("4. Para...")
        pwm_left.ChangeDutyCycle(0)
        pwm_right.ChangeDutyCycle(0)
        
        print("\nTeste concluído!")
        
    except KeyboardInterrupt:
        print("\nInterrompido!")
    
    finally:
        pwm_left.stop()
        pwm_right.stop()
        GPIO.cleanup()


def test_servo():
    """Testa servo motor"""
    print("\n" + "="*60)
    print("TESTE DO SERVO MOTOR")
    print("="*60)
    print(f"Pino: GPIO {SERVO_PIN}")
    
    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)
    GPIO.setup(SERVO_PIN, GPIO.OUT)
    
    pwm = GPIO.PWM(SERVO_PIN, 50)
    pwm.start(0)
    
    def set_angle(angle):
        duty = 2.5 + (angle / 180.0) * 10.0
        pwm.ChangeDutyCycle(duty)
        time.sleep(0.5)
        pwm.ChangeDutyCycle(0)
    
    try:
        print("\nSequência: 0° → 90° → 180° → 90° → 0°\n")
        
        print("1. Indo para 0° (vassouras levantadas)...")
        set_angle(0)
        time.sleep(2)
        
        print("2. Indo para 90° (vassouras abaixadas - limpeza)...")
        set_angle(90)
        time.sleep(2)
        
        print("3. Indo para 180° (máximo)...")
        set_angle(180)
        time.sleep(2)
        
        print("4. Voltando para 90°...")
        set_angle(90)
        time.sleep(2)
        
        print("5. Voltando para 0° (posição inicial)...")
        set_angle(0)
        time.sleep(1)
        
        print("\nTeste do servo concluído!")
        
    except KeyboardInterrupt:
        print("\nInterrompido!")
    
    finally:
        pwm.stop()
        GPIO.cleanup()


def test_ultrasonic():
    """Testa sensor ultrassônico"""
    print("\n" + "="*60)
    print("TESTE DO SENSOR ULTRASSÔNICO")
    print("="*60)
    print(f"Trigger: GPIO {ULTRASONIC_PINS['trigger']}")
    print(f"Echo: GPIO {ULTRASONIC_PINS['echo']}")
    
    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)
    GPIO.setup(ULTRASONIC_PINS['trigger'], GPIO.OUT)
    GPIO.setup(ULTRASONIC_PINS['echo'], GPIO.IN)
    
    GPIO.output(ULTRASONIC_PINS['trigger'], GPIO.LOW)
    time.sleep(0.1)
    
    print("\nMedindo distância (10 leituras)...")
    print("Pressione Ctrl+C para parar\n")
    
    try:
        for i in range(10):
            # Enviar pulso
            GPIO.output(ULTRASONIC_PINS['trigger'], GPIO.HIGH)
            time.sleep(0.00001)
            GPIO.output(ULTRASONIC_PINS['trigger'], GPIO.LOW)
            
            # Medir tempo
            timeout = time.time() + 0.5
            
            while GPIO.input(ULTRASONIC_PINS['echo']) == GPIO.LOW:
                pulse_start = time.time()
                if pulse_start > timeout:
                    break
            
            while GPIO.input(ULTRASONIC_PINS['echo']) == GPIO.HIGH:
                pulse_end = time.time()
                if pulse_end > timeout:
                    break
            
            # Calcular distância
            try:
                pulse_duration = pulse_end - pulse_start
                distance = pulse_duration * 17150
                distance = round(distance, 2)
                
                print(f"Leitura {i+1:2d}: {distance:6.2f} cm")
            except:
                print(f"Leitura {i+1:2d}: ERRO")
            
            time.sleep(0.5)
        
        print("\nTeste concluído!")
        
    except KeyboardInterrupt:
        print("\nInterrompido!")
    
    finally:
        GPIO.cleanup()


def test_brushes():
    """Testa motores das vassouras"""
    print("\n" + "="*60)
    print("TESTE DOS MOTORES DAS VASSOURAS")
    print("="*60)
    
    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)
    
    # Setup
    GPIO.setup(BRUSH_MOTOR_PINS['brush_1']['in1'], GPIO.OUT)
    GPIO.setup(BRUSH_MOTOR_PINS['brush_1']['in2'], GPIO.OUT)
    GPIO.setup(BRUSH_MOTOR_PINS['brush_1']['enable'], GPIO.OUT)
    GPIO.setup(BRUSH_MOTOR_PINS['brush_2']['in1'], GPIO.OUT)
    GPIO.setup(BRUSH_MOTOR_PINS['brush_2']['in2'], GPIO.OUT)
    GPIO.setup(BRUSH_MOTOR_PINS['brush_2']['enable'], GPIO.OUT)
    
    # PWM
    pwm1 = GPIO.PWM(BRUSH_MOTOR_PINS['brush_1']['enable'], 1000)
    pwm2 = GPIO.PWM(BRUSH_MOTOR_PINS['brush_2']['enable'], 1000)
    pwm1.start(0)
    pwm2.start(0)
    
    try:
        print("\n1. Ligando vassouras a 60% (3 segundos)...")
        GPIO.output(BRUSH_MOTOR_PINS['brush_1']['in1'], GPIO.HIGH)
        GPIO.output(BRUSH_MOTOR_PINS['brush_1']['in2'], GPIO.LOW)
        GPIO.output(BRUSH_MOTOR_PINS['brush_2']['in1'], GPIO.HIGH)
        GPIO.output(BRUSH_MOTOR_PINS['brush_2']['in2'], GPIO.LOW)
        pwm1.ChangeDutyCycle(60)
        pwm2.ChangeDutyCycle(60)
        time.sleep(3)
        
        print("2. Aumentando para 80% (2 segundos)...")
        pwm1.ChangeDutyCycle(80)
        pwm2.ChangeDutyCycle(80)
        time.sleep(2)
        
        print("3. Desligando...")
        pwm1.ChangeDutyCycle(0)
        pwm2.ChangeDutyCycle(0)
        
        print("\nTeste concluído!")
        
    except KeyboardInterrupt:
        print("\nInterrompido!")
    
    finally:
        pwm1.stop()
        pwm2.stop()
        GPIO.cleanup()


def menu():
    """Menu principal"""
    while True:
        print("\n" + "="*60)
        print("    TESTE DE PINOS - CONFIGURAÇÃO REAL")
        print("="*60)
        print("\n[1] Testar Setup de TODOS os Pinos")
        print("[2] Testar Motores de Locomoção")
        print("[3] Testar Servo Motor")
        print("[4] Testar Sensor Ultrassônico")
        print("[5] Testar Motores das Vassouras")
        print("[0] Sair")
        print("-"*60)
        print("\nPinos configurados:")
        print(f"  Motores: {MOTOR_PINS['left_motor']['ena']}, {MOTOR_PINS['left_motor']['in1']}, "
              f"{MOTOR_PINS['left_motor']['in2']}, {MOTOR_PINS['right_motor']['enb']}, "
              f"{MOTOR_PINS['right_motor']['in3']}, {MOTOR_PINS['right_motor']['in4']}")
        print(f"  Servo: {SERVO_PIN}")
        print(f"  Sensor: Trig={ULTRASONIC_PINS['trigger']}, Echo={ULTRASONIC_PINS['echo']}")
        print(f"  Vassouras: {BRUSH_MOTOR_PINS['brush_1']['enable']}, "
              f"{BRUSH_MOTOR_PINS['brush_2']['enable']}")
        print("-"*60)
        
        choice = input("\nEscolha uma opção: ").strip()
        
        if choice == '1':
            if test_setup_all_pins():
                print("\nTodos os pinos configurados com sucesso!")
            else:
                print("\nAlguns pinos falharam. Verifique as conexões.")
        elif choice == '2':
            test_motors()
        elif choice == '3':
            test_servo()
        elif choice == '4':
            test_ultrasonic()
        elif choice == '5':
            test_brushes()
        elif choice == '0':
            print("\nSaindo...")
            break
        else:
            print("\nOpção inválida!")


if __name__ == "__main__":
    try:
        print("\n" + "="*60)
        print("TESTE COM PINOS REAIS CONFIGURADOS")
        print("="*60)
        print("\nEste script usa os pinos definidos no seu projeto:")
        print(f"  - Motores: GPIOs 17, 22, 23, 24, 25, 27")
        print(f"  - Servo: GPIO 12")
        print(f"  - Sensor: GPIOs 5, 6")
        print(f"  - Vassouras: GPIOs 13, 16, 19, 20, 21, 26")
        
        input("\nPressione ENTER para continuar...")
        
        menu()
        
    except KeyboardInterrupt:
        print("\n\nPrograma encerrado!")
    finally:
        GPIO.cleanup()
        print("GPIO limpo. Até logo!")