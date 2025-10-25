"""
hardware/sensors.py
===================
Interface com sensor ultrassônico HC-SR04
"""

import RPi.GPIO as GPIO
import time


class UltrasonicSensor:
    """
    Sensor ultrassônico para detecção de obstáculos.
    
    Funciona enviando ondas sonoras e medindo o tempo
    que levam para voltar após bater em um obstáculo.
    """
    
    def __init__(self, trigger_pin, echo_pin, max_distance=400):
        """
        Inicializa sensor ultrassônico.
        
        Args:
            trigger_pin: pino GPIO conectado ao TRIG
            echo_pin: pino GPIO conectado ao ECHO
            max_distance: distância máxima em cm
        """
        self.trigger = trigger_pin
        self.echo = echo_pin
        self.max_distance = max_distance
        
        # Configurar pinos
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.trigger, GPIO.OUT)
        GPIO.setup(self.echo, GPIO.IN)
        
        # Garantir TRIGGER em LOW
        GPIO.output(self.trigger, GPIO.LOW)
        time.sleep(0.1)
    
    def get_distance(self):
        """
        Mede distância até obstáculo mais próximo.
        
        Returns:
            float: distância em centímetros
        """
        try:
            # Enviar pulso de 10µs
            GPIO.output(self.trigger, GPIO.HIGH)
            time.sleep(0.00001)
            GPIO.output(self.trigger, GPIO.LOW)
            
            # Aguardar início do pulso
            pulse_start = time.time()
            timeout = time.time() + 0.1
            
            while GPIO.input(self.echo) == 0:
                pulse_start = time.time()
                if pulse_start > timeout:
                    return self.max_distance
            
            # Aguardar fim do pulso
            pulse_end = time.time()
            timeout = time.time() + 0.1
            
            while GPIO.input(self.echo) == 1:
                pulse_end = time.time()
                if pulse_end > timeout:
                    return self.max_distance
            
            # Calcular distância
            # velocidade_som / 2 = 17150 cm/s
            pulse_duration = pulse_end - pulse_start
            distance = pulse_duration * 17150
            
            return round(distance, 2) if distance <= self.max_distance else self.max_distance
            
        except Exception as e:
            print(f"Erro no sensor: {e}")
            return self.max_distance