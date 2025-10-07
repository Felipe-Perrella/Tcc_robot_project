"""
hardware/motors.py
==================
Controlador dos motores de locomoção usando driver L298N
"""

import RPi.GPIO as GPIO


class L298NController:
    """
    Controla os motores DC de locomoção via driver L298N.
    
    Responsável por:
    - Movimento para frente/trás
    - Rotação esquerda/direita
    - Controle de velocidade via PWM
    """
    
    def __init__(self, motor_pins):
        """
        Inicializa controlador dos motores.
        
        Args:
            motor_pins: dict com pinos do L298N
                {
                    'left_motor': {'in1': pin, 'in2': pin, 'ena': pin},
                    'right_motor': {'in3': pin, 'in4': pin, 'enb': pin}
                }
        """
        self.pins = motor_pins
        
        # Configurar GPIO
        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)
        
        # Configurar pinos como saída
        for motor in self.pins.values():
            for pin in motor.values():
                GPIO.setup(pin, GPIO.OUT)
        
        # Criar objetos PWM (1000 Hz)
        self.left_pwm = GPIO.PWM(self.pins['left_motor']['ena'], 1000)
        self.right_pwm = GPIO.PWM(self.pins['right_motor']['enb'], 1000)
        
        # Iniciar PWM com duty cycle 0
        self.left_pwm.start(0)
        self.right_pwm.start(0)
        
        self.current_speed = 60
        self.is_running = False
    
    def set_speed(self, speed):
        """Define velocidade (0-100%)"""
        self.current_speed = max(0, min(100, speed))
    
    def move_forward(self):
        """Move para frente"""
        # Motor esquerdo: frente
        GPIO.output(self.pins['left_motor']['in1'], GPIO.HIGH)
        GPIO.output(self.pins['left_motor']['in2'], GPIO.LOW)
        
        # Motor direito: frente
        GPIO.output(self.pins['right_motor']['in3'], GPIO.HIGH)
        GPIO.output(self.pins['right_motor']['in4'], GPIO.LOW)
        
        self._apply_speed()
        self.is_running = True
    
    def move_backward(self):
        """Move para trás"""
        GPIO.output(self.pins['left_motor']['in1'], GPIO.LOW)
        GPIO.output(self.pins['left_motor']['in2'], GPIO.HIGH)
        GPIO.output(self.pins['right_motor']['in3'], GPIO.LOW)
        GPIO.output(self.pins['right_motor']['in4'], GPIO.HIGH)
        
        self._apply_speed()
        self.is_running = True
    
    def turn_left(self):
        """Gira à esquerda"""
        GPIO.output(self.pins['left_motor']['in1'], GPIO.LOW)
        GPIO.output(self.pins['left_motor']['in2'], GPIO.HIGH)
        GPIO.output(self.pins['right_motor']['in3'], GPIO.HIGH)
        GPIO.output(self.pins['right_motor']['in4'], GPIO.LOW)
        
        self._apply_speed()
        self.is_running = True
    
    def turn_right(self):
        """Gira à direita"""
        GPIO.output(self.pins['left_motor']['in1'], GPIO.HIGH)
        GPIO.output(self.pins['left_motor']['in2'], GPIO.LOW)
        GPIO.output(self.pins['right_motor']['in3'], GPIO.LOW)
        GPIO.output(self.pins['right_motor']['in4'], GPIO.HIGH)
        
        self._apply_speed()
        self.is_running = True
    
    def stop(self):
        """Para todos os motores"""
        self.left_pwm.ChangeDutyCycle(0)
        self.right_pwm.ChangeDutyCycle(0)
        self.is_running = False
    
    def _apply_speed(self):
        """Aplica velocidade atual via PWM"""
        self.left_pwm.ChangeDutyCycle(self.current_speed)
        self.right_pwm.ChangeDutyCycle(self.current_speed)
    
    def cleanup(self):
        """Limpa recursos GPIO"""
        self.stop()
        self.left_pwm.stop()
        self.right_pwm.stop()
        GPIO.cleanup()