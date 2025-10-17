# config.py - Configurações centralizadas do robô

# ==================== CONFIGURAÇÃO DOS PINOS GPIO ====================

# for GPIO numbering, choose BCM  
# GPIO.setmode(GPIO.BCM)  
  
# or, for pin numbering, choose BOARD  
#GPIO.setmode(GPIO.BOARD)  


# Pinos do L298N para controle dos motores
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

# Pinos do sensor ultrassônico HC-SR04
ULTRASONIC_PINS = {
    'trigger': 6,
    'echo': 5
}

# Pino do servo que levanta/abaixa as vassouras
SERVO_PIN = 12  # GPIO 4  (4 - bcm | 7 - board)

# Pinos dos motores das vassouras
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

# ==================== PARÂMETROS DO ROBÔ ====================

# Distâncias (em centímetros)
PANEL_DISTANCE = 15             # Distância máxima para considerar "sobre a placa"
MAX_DETECTION_DISTANCE = 400    # Distância máxima do sensor

# Velocidades (0-100)
SEARCH_SPEED = 50               # Velocidade ao procurar placa (girando)
MOVE_SPEED = 60                 # Velocidade ao mover em direção ao alvo (VERIFICAR)
SCAN_SPEED = 40                 # Velocidade ao escanear placa procurando sujeira
BRUSH_SPEED = 80                # Velocidade das vassouras quando limpando

# Distância segura para evitar obstáculos (em centímetros)
SAFE_DISTANCE = 20              # Ajuste conforme necessário (VERIFICAR)

# Tempos (em segundos)
MAIN_LOOP_DELAY = 0.1       # Delay entre iterações do loop principal
BACKWARD_TIME = 0.5         # Tempo de recuo ao evitar obstáculo
TURN_TIME = 0.8             # Tempo de giro ao evitar obstáculo
STOP_PAUSE = 0.2            # Pausa antes de manobras

# PWM
PWM_FREQUENCY = 1000        # Frequência do PWM para os motores

# ==================== CONFIGURAÇÕES DAS VASSOURAS ====================

# Controle das vassouras
BRUSH_CONFIG = {
    'auto_activate': True,      # Ativar automaticamente ao detectar alvo
    'speed': 80,                # Velocidade das vassouras (0-100)
    'activation_delay': 0.2     # Delay antes de ativar (segundos)
}

# ==================== CONFIGURAÇÕES DA CÂMERA ====================

# Parâmetros para o algoritmo de visão
CAMERA_CONFIG = {
    'resolution': (640, 480),
    'framerate': 30,
    'detection_threshold': 0.5  # Threshold para considerar detecção positiva
}

# ==================== CONFIGURAÇÕES DE DEBUG ====================

DEBUG_MODE = True           # Ativa/desativa mensagens de debug
VERBOSE_SENSORS = True      # Mostra leituras detalhadas dos sensores
LOG_TO_FILE = False         # Salva logs em arquivo

# ==================== MAPEAMENTO DE ESTADOS ====================

STATE_MESSAGES = {
    'SEARCHING': 'Procurando alvo...',
    'MOVING_TO_TARGET': 'Movendo em direção ao alvo!',
    'AVOIDING_OBSTACLE': 'Obstáculo detectado! Evitando...',
    'STOPPED': 'Robô parado.'
}

# ==================== VALIDAÇÃO ====================

def validate_config():
    """Valida as configurações antes de iniciar o robô"""
    errors = []
    
    # Verificar se os pinos não estão duplicados
    all_pins = []
    for motor in MOTOR_PINS.values():
        all_pins.extend(motor.values())
    for brush in BRUSH_MOTOR_PINS.values():
        all_pins.extend(brush.values())
    all_pins.extend(ULTRASONIC_PINS.values())
    
    if len(all_pins) != len(set(all_pins)):
        errors.append("ERRO: Pinos duplicados detectados!")
    
    # Verificar valores de velocidade
    if not (0 <= SEARCH_SPEED <= 100):
        errors.append("ERRO: SEARCH_SPEED deve estar entre 0 e 100")
    if not (0 <= MOVE_SPEED <= 100):
        errors.append("ERRO: MOVE_SPEED deve estar entre 0 e 100")
    
    # Verificar distâncias
    if SAFE_DISTANCE <= 0:
        errors.append("ERRO: SAFE_DISTANCE deve ser maior que 0")
    
    return errors

# Executar validação ao importar
if __name__ == "__main__":
    errors = validate_config()
    if errors:
        for error in errors:
            print(error)
    else:
        print("✓ Configuração válida!")
        print(f"\nPinos configurados:")
        print(f"  Motor Esquerdo: IN1={MOTOR_PINS['left_motor']['in1']}, "
              f"IN2={MOTOR_PINS['left_motor']['in2']}, "
              f"ENA={MOTOR_PINS['left_motor']['ena']}")
        print(f"  Motor Direito: IN3={MOTOR_PINS['right_motor']['in3']}, "
              f"IN4={MOTOR_PINS['right_motor']['in4']}, "
              f"ENB={MOTOR_PINS['right_motor']['enb']}")
        print(f"  Ultrassônico: TRIG={ULTRASONIC_PINS['trigger']}, "
              f"ECHO={ULTRASONIC_PINS['echo']}")