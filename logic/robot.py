"""
logic/robot.py
==============
Classe principal que coordena todo o robô
"""

import time
from .states import RobotState
from hardware import L298NController, BrushController, UltrasonicSensor, CameraVision


class Robot:
    """
    Classe principal do robô autônomo de limpeza de placas solares.
    
    Funcionamento com intervalos de verificação:
    1. Sensor ultrassônico (embaixo) detecta se está sobre placa solar
    2. Enquanto sobre placa: anda escaneando
    3. A cada X segundos (configurável): lê câmera e processa visão
    4. Se detecta sujeira: liga vassouras e limpa
    5. Se não detecta: continua andando (vassouras OFF)
    6. Quando sai da placa: gira procurando nova placa
    """
    
    def __init__(self, motor_pins, brush_pins, ultrasonic_pins, 
                 panel_distance=15, search_speed=50, scan_speed=40,
                 vision_check_interval=15):
        """
        Inicializa o robô completo.
        
        Args:
            motor_pins: dict com pinos dos motores de locomoção
            brush_pins: dict com pinos das vassouras
            ultrasonic_pins: dict com pinos do sensor {'trigger': pin, 'echo': pin}
            panel_distance: distância máxima para considerar que está sobre placa (cm)
            search_speed: velocidade ao procurar placa (girando) (0-100)
            scan_speed: velocidade ao escanear placa procurando sujeira (0-100)
            vision_check_interval: intervalo entre verificações de visão (segundos)
        """
        print("Inicializando robô de limpeza de placas solares...")
        
        # Inicializar componentes
        self.motors = L298NController(motor_pins)
        self.brushes = BrushController(brush_pins, brush_speed=80)
        self.ultrasonic = UltrasonicSensor(
            ultrasonic_pins['trigger'], 
            ultrasonic_pins['echo']
        )
        self.camera = CameraVision()
        
        # Estado e controle
        self.state = RobotState.SEARCHING
        self.running = False
        
        # Parâmetros
        self.panel_distance = panel_distance
        self.search_speed = search_speed
        self.scan_speed = scan_speed
        self.brush_activation_delay = 0.2
        
        # Controle de intervalo de visão
        self.vision_check_interval = vision_check_interval  # segundos entre verificações
        self.last_vision_check = 0  # timestamp da última verificação
        self.dirt_detected = False  # último resultado da visão
        
        print("✓ Robô inicializado!")
        print(f"  - Distância da placa: {panel_distance}cm")
        print(f"  - Velocidade de busca: {search_speed}%")
        print(f"  - Velocidade de escaneamento: {scan_speed}%")
        print(f"  - Intervalo de verificação de visão: {vision_check_interval}s")
    
    def start(self):
        """Inicia o robô e entra no loop principal"""
        self.running = True
        print("\n" + "="*50)
        print("ROBÔ DE LIMPEZA INICIADO!")
        print("="*50)
        print("Funcionamento:")
        print("  1. Sensor detecta placa embaixo")
        print("  2. Sobre placa: anda escaneando")
        print(f"  3. A cada {self.vision_check_interval}s: verifica visão")
        print("  4. Se detecta sujeira → Liga vassouras")
        print("  5. Se não detecta → Vassouras OFF")
        print("  6. Fora da placa: gira procurando")
        print("\nPressione Ctrl+C para parar\n")
        
        try:
            while self.running:
                self.main_loop()
                time.sleep(0.1)  # Loop a 10Hz
                
        except KeyboardInterrupt:
            print("\n\n⚠️  Parando robô...")
        finally:
            self.stop()
    
    def main_loop(self):
        """
        Loop principal - executado a cada 100ms (10Hz).
        
        Lógica com verificação periódica de visão:
        1. Sensor ultrassônico verifica se está sobre placa (sempre)
        2. SE sobre placa:
           - Anda pela placa escaneando
           - A cada X segundos: lê câmera e processa visão
           - Usa último resultado da visão para controlar vassouras
        3. SE fora da placa:
           - Gira procurando placa
           - Reseta timer de visão
        """
        # Ler sensor ultrassônico (sempre lê)
        distance_to_ground = self.ultrasonic.get_distance()
        
        # Verificar se está sobre a placa solar
        on_panel = distance_to_ground <= self.panel_distance
        
        # Verificar se deve checar visão (apenas se sobre placa)
        if on_panel:
            current_time = time.time()
            time_since_last_check = current_time - self.last_vision_check
            
            if time_since_last_check >= self.vision_check_interval:
                # Chegou a hora de verificar visão!
                print(f"\n {self.vision_check_interval}s passados. Verificando visão...")
                self.dirt_detected = self.camera.detect_target()
                self.last_vision_check = current_time
                
                if self.dirt_detected:
                    print(f"  SUJEIRA DETECTADA! Iniciando limpeza...")
                else:
                    print(f"  Placa limpa. Continuando escaneamento...")
        else:
            # Fora da placa → resetar timer
            self.last_vision_check = time.time()
            self.dirt_detected = False
        
        # Controlar vassouras baseado no ÚLTIMO resultado da visão
        self._control_brushes(self.dirt_detected, on_panel)
        
        # Status para debug
        panel_status = " SOBRE PLACA" if on_panel else " FORA DA PLACA"
        brush_status = " LIMPANDO" if self.brushes.is_running() else " OFF"
        dirt_status = " SUJEIRA" if self.dirt_detected else " Limpo"
        
        # Calcular tempo até próxima verificação
        if on_panel:
            time_until_next = self.vision_check_interval - (time.time() - self.last_vision_check)
            time_until_next = max(0, time_until_next)
            next_check = f"Próx: {time_until_next:.1f}s"
        else:
            next_check = "N/A"
        
        print(f"Estado: {self.state.value:20s} | "
              f"Dist: {distance_to_ground:5.1f}cm | "
              f"{panel_status} | "
              f"{dirt_status} | "
              f"{brush_status} | "
              f"{next_check}")
        
        # Máquina de estados
        if on_panel:
            # ESTÁ SOBRE A PLACA
            if self.state != RobotState.MOVING_TO_TARGET:
                print("\n✓ Placa detectada! Iniciando escaneamento...")
                self.state = RobotState.MOVING_TO_TARGET
                # Fazer primeira verificação imediatamente
                self.last_vision_check = 0
            
            # Escanear placa
            self.scan_panel(self.dirt_detected)
        
        else:
            # FORA DA PLACA
            if self.state != RobotState.SEARCHING:
                print("\n Placa não detectada! Procurando...")
                self.state = RobotState.SEARCHING
            
            # Procurar placa
            self.search_for_panel()
    
    def _control_brushes(self, dirt_detected, on_panel):
        """
        Controla vassouras: APENAS liga quando detecta sujeira!
        
        Usa o ÚLTIMO resultado da verificação de visão.
        Não verifica câmera aqui - apenas usa o resultado salvo.
        
        Args:
            dirt_detected: último resultado da visão (True/False)
            on_panel: True se está sobre a placa
        """
        # Condição para ligar: DEVE estar sobre placa E ter detectado sujeira
        should_clean = on_panel and dirt_detected
        
        if should_clean and not self.brushes.is_running():
            # Detectou sujeira → LIGAR vassouras
            time.sleep(self.brush_activation_delay)
            self.brushes.start()
            print("    🧹 Ativando vassouras para limpeza...")
        
        elif not should_clean and self.brushes.is_running():
            # Não detecta mais sujeira OU saiu da placa → DESLIGAR vassouras
            self.brushes.stop()
            if not on_panel:
                print("    🧹 Saiu da placa! Desligando vassouras...")
            else:
                print("    🧹 Área limpa! Desligando vassouras...")
    
    def search_for_panel(self):
        """
        Comportamento: PROCURAR PLACA SOLAR.
        
        Robô gira até sensor detectar placa embaixo.
        Vassouras permanecem desligadas.
        """
        self.motors.set_speed(self.search_speed)
        self.motors.turn_right()  # Gira procurando placa
    
    def scan_panel(self, dirt_detected):
        """
        Comportamento: ESCANEAR PLACA procurando sujeira.
        
        Robô anda sobre a placa.
        Câmera é verificada periodicamente (a cada X segundos).
        Vassouras ligam apenas quando detecta sujeira.
        
        Args:
            dirt_detected: último resultado da visão
        """
        if dirt_detected:
            # Sujeira detectada → ir MUITO devagar para limpar bem
            self.motors.set_speed(self.scan_speed // 3)  # 33% da velocidade
        else:
            # Sem sujeira → velocidade normal de escaneamento
            self.motors.set_speed(self.scan_speed)
        
        self.motors.move_forward()  # Avança escaneando
    
    def stop(self):
        """Para o robô e limpa recursos"""
        self.running = False
        self.motors.stop()
        self.brushes.stop()
        self.motors.cleanup()
        self.brushes.cleanup()
        
        print("\n" + "="*50)
        print(" Robô parado!")
        print("="*50)