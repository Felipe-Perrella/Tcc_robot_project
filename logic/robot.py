"""
logic/robot.py
==============
Classe principal que coordena todo o robô
"""

import time
from .states import RobotState, TurnDirection, RepositionStep
from hardware import L298NController, BrushController, UltrasonicSensor, CameraVision


class Robot:
    """
    Classe principal do robô autônomo de limpeza de placas solares.
    
    Lógica de funcionamento:
    1. INITIAL_SEARCH: Gira procurando placa
    2. Encontrou placa → MOVING_TO_TARGET
    3. MOVING_TO_TARGET: Anda reto limpando, verifica visão a cada 15s
    4. Perdeu placa → REPOSITIONING (manobra)
    5. REPOSITIONING: Vira 90°, anda largura do robô, vira 90° volta
    6. Volta para MOVING_TO_TARGET (anda reto procurando placa)
    7. Se não achar placa: repete manobra invertendo lado
    """
    
    def __init__(self, motor_pins, brush_pins, servo_pin, ultrasonic_pins, 
                 panel_distance=15, search_speed=50, scan_speed=40,
                 vision_check_interval=15, turn_90_time=0.5, sideways_time=1.0):
        """
        Inicializa o robô completo.
        """
        print("Inicializando robô de limpeza de placas solares...")
        
        # Inicializar componentes
        self.motors = L298NController(motor_pins)
        self.brushes = BrushController(brush_pins, servo_pin, brush_speed=80)
        self.ultrasonic = UltrasonicSensor(
            ultrasonic_pins['trigger'], 
            ultrasonic_pins['echo']
        )
        self.camera = CameraVision()
        
        # Estado e controle
        self.state = RobotState.INITIAL_SEARCH
        self.running = False
        
        # Parâmetros
        self.panel_distance = panel_distance
        self.search_speed = search_speed
        self.scan_speed = scan_speed
        self.brush_activation_delay = 0.2
        
        # Parâmetros de manobra
        self.turn_90_time = turn_90_time
        self.sideways_time = sideways_time
        
        # Estado da manobra de reposicionamento
        self.reposition_step = RepositionStep.TURNING_90
        self.turn_direction = TurnDirection.LEFT  # Começa virando à esquerda
        self.step_start_time = 0
        
        # Controle de intervalo de visão
        self.vision_check_interval = vision_check_interval
        self.last_vision_check = 0
        self.dirt_detected = False
        
        print("Robô inicializado!")
        print(f"  - Distância da placa: {panel_distance}cm")
        print(f"  - Velocidade de busca: {search_speed}%")
        print(f"  - Velocidade de escaneamento: {scan_speed}%")
        print(f"  - Tempo de curva 90°: {turn_90_time}s")
        print(f"  - Tempo lateral (largura robô): {sideways_time}s")
    
    def start(self):
        """Inicia o robô e entra no loop principal"""
        self.running = True
        print("\n" + "="*60)
        print("ROBÔ DE LIMPEZA INICIADO!")
        print("="*60)
        print("Lógica de Funcionamento:")
        print("  1. Busca Inicial: Gira procurando placa")
        print("  2. Encontrou: Anda reto limpando")
        print("  3. Perdeu placa: Executa manobra")
        print("     a) Vira 90° (esquerda ou direita)")
        print("     b) Anda largura do robô")
        print("     c) Vira 90° de volta")
        print("     d) Anda reto procurando placa")
        print("  4. Se não achar: repete invertendo lado")
        print("\nPressione Ctrl+C para parar\n")
        
        try:
            while self.running:
                self.main_loop()
                time.sleep(0.1)
                
        except KeyboardInterrupt:
            print("\n\nParando robô...")
        finally:
            self.stop()
    
    def main_loop(self):
        """Loop principal - executado a cada 100ms (10Hz)"""
        # Ler sensor ultrassônico (sempre)
        distance_to_ground = self.ultrasonic.get_distance()
        
        # Verificar se está sobre a placa solar
        on_panel = distance_to_ground <= self.panel_distance
        
        # Máquina de estados principal
        if self.state == RobotState.INITIAL_SEARCH:
            # Busca inicial: girando procurando placa
            self._state_initial_search(on_panel, distance_to_ground)
        
        elif self.state == RobotState.MOVING_TO_TARGET:
            # Sobre a placa: limpando
            self._state_moving_on_panel(on_panel, distance_to_ground)
        
        elif self.state == RobotState.REPOSITIONING:
            # Perdeu placa: fazendo manobra
            self._state_repositioning(on_panel, distance_to_ground)
    
    def _state_initial_search(self, on_panel, distance):
        """
        INITIAL_SEARCH: Busca inicial girando no próprio eixo.
        """
        print(f"[BUSCA INICIAL] Girando... | Dist: {distance:5.1f}cm")
        
        if on_panel:
            # Encontrou placa!
            print("\n>>> PLACA ENCONTRADA! Iniciando limpeza...")
            self.motors.stop()
            time.sleep(0.2)
            self.state = RobotState.MOVING_TO_TARGET
            self.last_vision_check = 0  # Verificar visão imediatamente
        else:
            # Continua girando
            self.motors.set_speed(self.search_speed)
            self.motors.turn_right()
    
    def _state_moving_on_panel(self, on_panel, distance):
        """
        MOVING_TO_TARGET: Sobre a placa, andando reto e limpando.
        """
        if not on_panel:
            # Perdeu a placa! Iniciar manobra
            print("\n>>> PERDEU A PLACA! Iniciando manobra...")
            self.motors.stop()
            time.sleep(0.2)
            self.state = RobotState.REPOSITIONING
            self.reposition_step = RepositionStep.TURNING_90
            self.step_start_time = time.time()
            return
        
        # Está sobre a placa: verificar visão periodicamente
        current_time = time.time()
        time_since_last_check = current_time - self.last_vision_check
        
        if time_since_last_check >= self.vision_check_interval:
            # Verificar visão
            print(f"\n[{self.vision_check_interval}s] Verificando visão...")
            self.dirt_detected = self.camera.detect_target()
            self.last_vision_check = current_time
            
            if self.dirt_detected:
                print(f"   >>> SUJEIRA DETECTADA! Limpando...")
            else:
                print(f"   >>> Placa limpa. Continuando...")
        
        # Controlar vassouras
        self._control_brushes(self.dirt_detected, on_panel=True)
        
        # Ajustar velocidade
        if self.dirt_detected:
            speed = self.scan_speed // 3  # Devagar para limpar bem
        else:
            speed = self.scan_speed
        
        # Andar para frente
        self.motors.set_speed(speed)
        self.motors.move_forward()
        
        # Status
        brush_status = "[LIMPANDO]" if self.brushes.is_running() else "[OFF]"
        dirt_status = "[SUJEIRA]" if self.dirt_detected else "[Limpo]"
        time_until_next = max(0, self.vision_check_interval - time_since_last_check)
        
        print(f"[PLACA] {dirt_status} | {brush_status} | "
              f"Vel: {speed:3d}% | Próx: {time_until_next:.1f}s | "
              f"Dist: {distance:5.1f}cm")
    
    def _state_repositioning(self, on_panel, distance):
        """
        REPOSITIONING: Manobra quando perde a placa.
        
        Sequência:
        1. Vira 90° (esquerda ou direita)
        2. Anda largura do robô
        3. Vira 90° de volta
        4. Anda reto procurando placa
        
        Se encontrar placa em qualquer momento: volta para MOVING_TO_TARGET
        Se não encontrar após andar reto: inverte direção e repete
        """
        current_time = time.time()
        elapsed = current_time - self.step_start_time
        
        # Se encontrou placa durante manobra: voltar para limpeza
        if on_panel:
            print(f"\n>>> PLACA DETECTADA durante manobra! Voltando à limpeza...")
            self.motors.stop()
            time.sleep(0.2)
            self.state = RobotState.MOVING_TO_TARGET
            self.last_vision_check = 0
            return
        
        # Nome da direção para display
        dir_name = "ESQUERDA" if self.turn_direction == TurnDirection.LEFT else "DIREITA"
        
        # Status
        print(f"[MANOBRA] Passo: {self.reposition_step.value:20s} | "
              f"Dir: {dir_name:8s} | Tempo: {elapsed:.1f}s | "
              f"Dist: {distance:5.1f}cm")
        
        # Máquina de estados da manobra
        if self.reposition_step == RepositionStep.TURNING_90:
            # Passo 1: Virando 90°
            self._execute_turn(self.turn_direction)
            
            if elapsed >= self.turn_90_time:
                print(f"[MANOBRA] Curva 90° concluída ({dir_name})")
                self.motors.stop()
                time.sleep(0.1)
                self.reposition_step = RepositionStep.MOVING_SIDEWAYS
                self.step_start_time = time.time()
        
        elif self.reposition_step == RepositionStep.MOVING_SIDEWAYS:
            # Passo 2: Andando para o lado (largura do robô)
            self.motors.set_speed(self.search_speed)
            self.motors.move_forward()
            
            if elapsed >= self.sideways_time:
                print(f"[MANOBRA] Deslocamento lateral concluído")
                self.motors.stop()
                time.sleep(0.1)
                self.reposition_step = RepositionStep.TURNING_90_BACK
                self.step_start_time = time.time()
        
        elif self.reposition_step == RepositionStep.TURNING_90_BACK:
            # Passo 3: Virando 90° de volta
            self._execute_turn(self.turn_direction)
            
            if elapsed >= self.turn_90_time:
                print(f"[MANOBRA] Curva de retorno concluída ({dir_name})")
                self.motors.stop()
                time.sleep(0.1)
                self.reposition_step = RepositionStep.MOVING_FORWARD
                self.step_start_time = time.time()
        
        elif self.reposition_step == RepositionStep.MOVING_FORWARD:
            # Passo 4: Andando para frente procurando placa
            self.motors.set_speed(self.search_speed)
            self.motors.move_forward()
            
            # Define um tempo máximo para procurar (ex: 3 segundos)
            if elapsed >= 3.0:
                # Não encontrou placa: inverter direção e repetir manobra
                print(f"[MANOBRA] Placa não encontrada. Invertendo direção...")
                self.motors.stop()
                time.sleep(0.1)
                
                # Inverter direção
                if self.turn_direction == TurnDirection.LEFT:
                    self.turn_direction = TurnDirection.RIGHT
                    print("[MANOBRA] >>> Próxima tentativa: DIREITA")
                else:
                    self.turn_direction = TurnDirection.LEFT
                    print("[MANOBRA] >>> Próxima tentativa: ESQUERDA")
                
                # Reiniciar manobra
                self.reposition_step = RepositionStep.TURNING_90
                self.step_start_time = time.time()
    
    def _execute_turn(self, direction):
        """Executa curva na direção especificada"""
        self.motors.set_speed(self.search_speed)
        
        if direction == TurnDirection.LEFT:
            self.motors.turn_left()
        else:
            self.motors.turn_right()
    
    def _control_brushes(self, dirt_detected, on_panel):
        """Controla vassouras baseado na detecção de sujeira"""
        should_clean = on_panel and dirt_detected
        
        if should_clean and not self.brushes.is_running():
            time.sleep(self.brush_activation_delay)
            self.brushes.start()
            print("    [VASSOURAS] >>> Ativadas")
        
        elif not should_clean and self.brushes.is_running():
            self.brushes.stop()
            print("    [VASSOURAS] >>> Desativadas")
    
    def stop(self):
        """Para o robô e limpa recursos"""
        self.running = False
        self.motors.stop()
        self.brushes.stop()
        self.motors.cleanup()
        self.brushes.cleanup()
        
        print("\n" + "="*60)
        print("Robô parado!")
        print("="*60)