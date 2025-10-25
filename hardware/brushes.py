"""
hardware/brushes.py
===================
Controlador dos motores das vassouras com servo para levantar/abaixar
"""

import RPi.GPIO as GPIO
import time
from .servo import ServoController


class BrushController:
    """
    Controla os motores DC das vassouras e servo de levantamento.
    
    Sequência de operação:
    1. Abaixar vassouras (servo 0° -> 90°)
    2. Ligar motores das vassouras
    3. Limpar...
    4. Desligar motores das vassouras
    5. Levantar vassouras (servo 90° -> 0°)
    
    Responsável por:
    - Ligar/desligar vassouras
    - Controle de velocidade via PWM
    - Levantar/abaixar via servo motor
    """
    
    def __init__(self, brush_pins, servo_pin, brush_speed=50):
        """
        Inicializa controlador das vassouras.
        
        Args:
            brush_pins: dict com pinos do L298N
                {
                    'brush_1': {'in1': pin, 'in2': pin, 'enable': pin},
                    'brush_2': {'in1': pin, 'in2': pin, 'enable': pin}
                }
            servo_pin: pino GPIO do servo (levanta/abaixa)
            brush_speed: velocidade padrão das vassouras (0-100)
        """
        self.pins = brush_pins
        self.brush_speed = brush_speed
        
        # Configurar GPIO
        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)
        
        # Configurar pinos como saída
        for brush in self.pins.values():
            for pin in brush.values():
                GPIO.setup(pin, GPIO.OUT)
        
        # Criar objetos PWM (1000 Hz)
        self.brush1_pwm = GPIO.PWM(self.pins['brush_1']['enable'], 1000)
        self.brush2_pwm = GPIO.PWM(self.pins['brush_2']['enable'], 1000)
        
        # Iniciar PWM com duty cycle 0
        self.brush1_pwm.start(0)
        self.brush2_pwm.start(0)
        
        # Inicializar servo
        self.servo = ServoController(servo_pin)
        
        self._running = False
        
        print(f"[BRUSHES] Inicializadas (velocidade: {brush_speed}%)")
        print(f"[BRUSHES] Servo no pino {servo_pin}")
    
    def start(self):
        """
        Inicia limpeza: abaixa vassouras e liga motores.
        
        Sequência:
        1. Abaixar servo (0° -> 90°)
        2. Aguardar servo estabilizar
        3. Ligar motores das vassouras
        """
        if not self._running:
            print("[BRUSHES] Iniciando limpeza...")
            
            # 1. Abaixar vassouras
            self.servo.lower_down()
            time.sleep(0.3)  # Aguardar servo estabilizar
            
            # 2. Ligar motores
            # Vassoura 1: girar
            GPIO.output(self.pins['brush_1']['in1'], GPIO.LOW)
            GPIO.output(self.pins['brush_1']['in2'], GPIO.HIGH)
            
            # Vassoura 2: girar
            GPIO.output(self.pins['brush_2']['in1'], GPIO.HIGH)
            GPIO.output(self.pins['brush_2']['in2'], GPIO.LOW)
            
            # Aplicar velocidade
            self.brush1_pwm.ChangeDutyCycle(self.brush_speed)
            self.brush2_pwm.ChangeDutyCycle(self.brush_speed)
            
            self._running = True
            print("[BRUSHES] Limpando (vassouras abaixadas e girando)")
    
    def stop(self):
        """
        Para limpeza: desliga motores e levanta vassouras.
        
        Sequência:
        1. Desligar motores das vassouras
        2. Aguardar motores pararem
        3. Levantar servo (90° -> 0°)
        """
        if self._running:
            print("[BRUSHES] Parando limpeza...")
            
            # 1. Desligar motores
            self.brush1_pwm.ChangeDutyCycle(0)
            self.brush2_pwm.ChangeDutyCycle(0)
            
            GPIO.output(self.pins['brush_1']['in1'], GPIO.LOW)
            GPIO.output(self.pins['brush_1']['in2'], GPIO.LOW)
            GPIO.output(self.pins['brush_2']['in1'], GPIO.LOW)
            GPIO.output(self.pins['brush_2']['in2'], GPIO.LOW)
            
            time.sleep(0.2)  # Aguardar motores pararem
            
            # 2. Levantar vassouras
            self.servo.lift_up()
            
            self._running = False
            print("[BRUSHES] Paradas (vassouras levantadas)")
    
    def set_speed(self, speed):
        """
        Define velocidade das vassouras (0-100%)
        
        Args:
            speed: velocidade (0-100)
        """
        self.brush_speed = max(0, min(100, speed))
        
        if self._running:
            self.brush1_pwm.ChangeDutyCycle(self.brush_speed)
            self.brush2_pwm.ChangeDutyCycle(self.brush_speed)
    
    def is_running(self):
        """
        Verifica se vassouras estão ligadas
        
        Returns:
            bool: True se vassouras estão ligadas
        """
        return self._running
    
    def cleanup(self):
        """Limpa recursos GPIO"""
        # Garantir que para corretamente
        if self._running:
            self.stop()
        
        # Limpar recursos
        self.brush1_pwm.stop()
        self.brush2_pwm.stop()
        self.servo.cleanup()
        
        print("[BRUSHES] Recursos liberados")