"""
hardware/servo.py
=================
Controlador do servo motor para levantar/abaixar vassouras
"""

import RPi.GPIO as GPIO
import time


class ServoController:
    """
    Controla servo motor que levanta/abaixa as vassouras.
    
    Posições:
    - 0°: Vassouras levantadas (não tocam a placa)
    - 90°: Vassouras abaixadas (tocam a placa para limpar)
    """
    
    def __init__(self, servo_pin, pwm_frequency=50):
        """
        Inicializa controlador do servo.
        
        Args:
            servo_pin: pino GPIO do servo
            pwm_frequency: frequência PWM (padrão 50Hz para servos)
        """
        self.pin = servo_pin
        
        # Configurar GPIO
        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)
        GPIO.setup(self.pin, GPIO.OUT)
        
        # Criar objeto PWM (50Hz padrão para servos)
        self.pwm = GPIO.PWM(self.pin, pwm_frequency)
        self.pwm.start(0)
        
        # Estado atual
        self.current_angle = 0
        
        # Iniciar na posição levantada (0°)
        self.lift_up()
        
        print(f"[SERVO] Inicializado no pino {servo_pin}")
    
    def _angle_to_duty_cycle(self, angle):
        """
        Converte ângulo (0-180°) para duty cycle PWM.
        
        Servo SG90 típico:
        - 0°   = 2.5% duty cycle (0.5ms pulse)
        - 90°  = 7.5% duty cycle (1.5ms pulse)
        - 180° = 12.5% duty cycle (2.5ms pulse)
        
        Args:
            angle: ângulo desejado (0-180)
            
        Returns:
            float: duty cycle correspondente
        """
        # Limitar ângulo
        angle = max(0, min(180, angle))
        
        # Fórmula: duty_cycle = 2.5 + (angle / 180) * 10
        duty_cycle = 2.5 + (angle / 180.0) * 10.0
        
        return duty_cycle
    
    def set_angle(self, angle):
        """
        Move servo para ângulo específico.
        
        Args:
            angle: ângulo desejado (0-180°)
        """
        duty_cycle = self._angle_to_duty_cycle(angle)
        
        self.pwm.ChangeDutyCycle(duty_cycle)
        time.sleep(0.5)  # Aguardar servo atingir posição
        self.pwm.ChangeDutyCycle(0)  # Parar envio de sinal
        
        self.current_angle = angle
    
    def lift_up(self):
        """
        Levanta vassouras (posição 0°).
        
        Vassouras NÃO tocam a placa.
        """
        print("[SERVO] Levantando vassouras (0°)...")
        self.set_angle(0)
    
    def lower_down(self):
        """
        Abaixa vassouras (posição 90°).
        
        Vassouras tocam a placa para limpar.
        """
        print("[SERVO] Abaixando vassouras (90°)...")
        self.set_angle(90)
    
    def get_angle(self):
        """
        Retorna ângulo atual do servo.
        
        Returns:
            int: ângulo atual (0-180°)
        """
        return self.current_angle
    
    def is_down(self):
        """
        Verifica se vassouras estão abaixadas.
        
        Returns:
            bool: True se vassouras estão na posição de limpeza
        """
        return self.current_angle >= 45  # Considera "abaixado" se > 45°
    
    def cleanup(self):
        """Limpa recursos GPIO"""
        # Levantar vassouras antes de desligar
        self.lift_up()
        time.sleep(0.3)
        
        self.pwm.stop()
        print("[SERVO] Recursos liberados")