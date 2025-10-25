"""
logic/robot.py
==============
Classe principal que coordena todo o robô
"""

import time
from turtle import distance
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
                 vision_check_interval=15, turn_90_time=2.6, sideways_time=0.7):
        """
        Inicializa o robô completo.

        Args:
            motor_pins: dict com pinos dos motores de locomoção
            brush_pins: dict com pinos das vassouras
            servo_pin: pino GPIO do servo (levanta/abaixa vassouras)
            ultrasonic_pins: dict com pinos do sensor {'trigger': pin, 'echo': pin}
            panel_distance: distância máxima para considerar sobre placa (cm)
            search_speed: velocidade ao procurar placa (0-100)
            scan_speed: velocidade ao escanear placa (0-100)
            vision_check_interval: intervalo entre verificações de visão (s)
            turn_90_time: tempo para virar 90 graus (s)
            sideways_time: tempo andando para o lado (s)
        """
        print("Inicializando robô de limpeza de placas solares...")
        
        # Inicializar componentes
        self.motors = L298NController(motor_pins)
        self.brushes = BrushController(brush_pins, servo_pin, brush_speed=50)
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
        self.reposition_step = RepositionStep.FIRST_TURN_90
        self.turn_direction = TurnDirection.LEFT  # Começa virando à esquerda
        self.step_start_time = 0
        self.scenario_b_active = False
        
        # NOVO: Contador de falhas para filtrar interferências
        self.panel_lost_count = 0        
        self.panel_lost_threshold = 3  # Precisa perder 3x seguidas para confirmar

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
        print(f"  - Filtro anti-interferência: {self.panel_lost_threshold} leituras")
    
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
        
    Usa contador de falhas para confirmar perda da placa.
        """
    
        # Sistema anti-interferência: contar falhas consecutivas
        if not on_panel:
            self.panel_lost_count += 1
        
            if self.panel_lost_count >= self.panel_lost_threshold:
                # Confirmado: perdeu placa (3x seguidas)
                print(f"\n>>> PLACA PERDIDA (confirmado após {self.panel_lost_count} leituras)!")
                self.motors.stop()
                time.sleep(0.2)
                self.state = RobotState.REPOSITIONING
                self.reposition_step = RepositionStep.FIRST_TURN_90
                self.step_start_time = time.time()
                self.scenario_b_active = False
                self.panel_lost_count = 0  # Resetar contador
                return
            else:
                # Interferência provável - continuar normalmente
                if self.panel_lost_count == 1:
                    print(f"[AVISO] Possível interferência ({self.panel_lost_count}/{self.panel_lost_threshold}) - continuando...")
        else:
            # Placa detectada - resetar contador de falhas
            if self.panel_lost_count > 0:
                print(f"[OK] Placa detectada novamente (resetando contador: {self.panel_lost_count}→0)")
            self.panel_lost_count = 0
            

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
        
        # Status - Preparar variáveis de status (definir ANTES de usar)
        brush = "[LIMPANDO]" if self.brushes.is_running() else "[OFF]"
        dirt = "[SUJEIRA]" if self.dirt_detected else "[Limpo]"
        next_check = max(0, self.vision_check_interval - time_since_last_check)
        fail_status = f" | Falhas:{self.panel_lost_count}/{self.panel_lost_threshold}" if self.panel_lost_count > 0 else ""

        print(f"[PLACA] {dirt} | {brush} | "
            f"Vel: {speed:3d}% | Próx: {next_check:.1f}s | "
            f"Dist: {distance:5.1f}cm{fail_status}")
        '''
        print(f"[PLACA] {dirt_status} | {brush_status} | "
              f"Vel: {speed:3d}% | Próx: {time_until_next:.1f}s | "
              f"Dist: {distance:5.1f}cm")
        '''
              
    def _state_repositioning(self, on_panel, distance):
        """
        Estado REPOSITIONING: Manobra quando perde a placa.
        
        Este método implementa dois cenários possíveis:
        
        CENÁRIO A (ainda na placa após virar 90°):
        ========================================
        1. Vira 90° (esquerda ou direita)
        2. Verifica sensor → DETECTA placa
        3. Anda largura do robô
        4. Vira 90° mesma direção
        5. INVERTE status (próxima vez vira outro lado)
        6. Volta para MOVING_TO_TARGET
        
        CENÁRIO B (saiu completamente da placa):
        ========================================
        1. Vira 90° (esquerda ou direita)
        2. Verifica sensor → NÃO detecta placa
        3. Vira 180° de volta (inverte lado)
        4. Anda largura do robô
        5. Vira 90° mesma direção do último giro
        6. MANTÉM status (próxima vez tenta mesmo lado)
        7. Volta para MOVING_TO_TARGET
        
        Args:
            on_panel: True se sensor detecta placa (distância <= 15cm)
            distance: Distância medida pelo sensor (cm)
        """
        
        # Obter tempo decorrido desde início do passo atual
        current_time = time.time()
        elapsed = current_time - self.step_start_time

        # Nome da direção para logs
        dir_name = "ESQUERDA" if self.turn_direction == TurnDirection.LEFT else "DIREITA"

        # Log de status
        print(f"[MANOBRA] {self.reposition_step.value:20s} | "
              f"Dir: {dir_name:8s} | Tempo: {elapsed:.1f}s | "
              f"Placa: {'SIM' if on_panel else 'NÃO':3s} | "
              f"Dist: {distance:5.1f}cm")

        # =========================================================================
        # PASSO 1: FIRST_TURN_90
        # Primeiro giro de 90° (esquerda ou direita conforme status)
        # =========================================================================
        if self.reposition_step == RepositionStep.FIRST_TURN_90:
            # Executar giro
            self._execute_turn(self.turn_direction)

            # Verificar se tempo decorrido >= tempo necessário
            if elapsed >= self.turn_90_time:
                print(f"[MANOBRA] Primeiro giro 90° concluído ({dir_name})")
                self.motors.stop()
                time.sleep(0.3)  # Pausa para estabilizar

                # Próximo passo: verificar se detecta placa
                self.reposition_step = RepositionStep.CHECK_PANEL
                self.step_start_time = time.time()

        # =========================================================================
        # PASSO 2: CHECK_PANEL
        # Verificar se ainda detecta placa após virar
        # =========================================================================
        elif self.reposition_step == RepositionStep.CHECK_PANEL:
            # Aguarda um momento para leitura estável do sensor
            if elapsed >= 0.3:

                # -------------------------------------------------------------
                # CENÁRIO A: Ainda detecta placa!
                # -------------------------------------------------------------
                if on_panel:
                    print(f"[MANOBRA] >>> CENÁRIO A: Placa detectada após curva!")
                    print(f"[MANOBRA] Continuando na mesma direção...")

                    # Flag indica que é cenário A
                    self.scenario_b_active = False

                    # Vai direto para andar lateral
                    self.reposition_step = RepositionStep.MOVING_SIDEWAYS
                    self.step_start_time = time.time()

                # -------------------------------------------------------------
                # CENÁRIO B: Saiu completamente da placa
                # -------------------------------------------------------------
                else:
                    print(f"[MANOBRA] >>> CENÁRIO B: Placa NÃO detectada!")
                    print(f"[MANOBRA] Virando 180° de volta...")

                    # Flag indica que é cenário B
                    self.scenario_b_active = True

                    # Precisa virar 180° de volta
                    self.reposition_step = RepositionStep.TURN_180_BACK
                    self.step_start_time = time.time()

        # =========================================================================
        # PASSO 3: TURN_180_BACK
        # Virar 180° de volta (APENAS no Cenário B)
        # =========================================================================
        elif self.reposition_step == RepositionStep.TURN_180_BACK:
            # Vira para o lado OPOSTO (180° = 2x 90°)
            # Se virou esquerda antes, agora vira direita
            opposite_dir = (TurnDirection.RIGHT if self.turn_direction == TurnDirection.LEFT 
                           else TurnDirection.LEFT)

            self._execute_turn(opposite_dir)

            # 180° = duas curvas de 90°
            if elapsed >= (self.turn_90_time * 2):
                print(f"[MANOBRA] Giro 180° concluído (agora indo para lado oposto)")
                self.motors.stop()
                time.sleep(0.2)

                # Próximo: andar lateral
                self.reposition_step = RepositionStep.MOVING_SIDEWAYS
                self.step_start_time = time.time()

        # =========================================================================
        # PASSO 4: MOVING_SIDEWAYS
        # Andar largura do robô (ambos os cenários)
        # =========================================================================
        elif self.reposition_step == RepositionStep.MOVING_SIDEWAYS:
            # Andar para frente
            self.motors.set_speed(self.search_speed)
            self.motors.move_forward()

            # Verificar se andou tempo suficiente
            if elapsed >= self.sideways_time:
                print(f"[MANOBRA] Deslocamento lateral concluído")
                self.motors.stop()
                time.sleep(0.2)

                # Próximo: giro final
                self.reposition_step = RepositionStep.FINAL_TURN_90
                self.step_start_time = time.time()

        # =========================================================================
        # PASSO 5: FINAL_TURN_90
        # Giro final de 90° (direção depende do cenário)
        # =========================================================================
        elif self.reposition_step == RepositionStep.FINAL_TURN_90:

            # -------------------------------------------------------------
            # DECISÃO: Qual direção girar no giro final?
            # -------------------------------------------------------------
            if self.scenario_b_active:
                # CENÁRIO B: última curva foi para lado oposto
                # Então gira para esse lado oposto
                final_dir = (TurnDirection.RIGHT if self.turn_direction == TurnDirection.LEFT 
                            else TurnDirection.LEFT)
            else:
                # CENÁRIO A: mesma direção original
                final_dir = self.turn_direction

            # Executar giro final
            self._execute_turn(final_dir)

            # Verificar se completou o giro
            if elapsed >= self.turn_90_time:
                print(f"[MANOBRA] Giro final concluído")
                self.motors.stop()
                time.sleep(0.2)

                # ---------------------------------------------------------
                # ATUALIZAR STATUS DA PRÓXIMA CURVA
                # ---------------------------------------------------------
                if not self.scenario_b_active:
                    # =================================================
                    # CENÁRIO A: INVERTE direção para próxima vez
                    # =================================================
                    if self.turn_direction == TurnDirection.LEFT:
                        self.turn_direction = TurnDirection.RIGHT
                        print("[MANOBRA] >>> Status atualizado: Próxima curva = DIREITA")
                    else:
                        self.turn_direction = TurnDirection.LEFT
                        print("[MANOBRA] >>> Status atualizado: Próxima curva = ESQUERDA")
                else:
                    # =================================================
                    # CENÁRIO B: MANTÉM direção
                    # =================================================
                    print(f"[MANOBRA] >>> Status mantido: Próxima curva = {dir_name}")

                # ---------------------------------------------------------
                # VOLTAR PARA LIMPEZA
                # ---------------------------------------------------------
                print("[MANOBRA] Retornando ao modo de limpeza...")
                self.state = RobotState.MOVING_TO_TARGET
                self.last_vision_check = 0  # Forçar verificação de visão
    
    # ==============================================================================
    # MÉTODO AUXILIAR: _execute_turn()
    # ==============================================================================

    def _execute_turn(self, direction):
        """
        Executa curva na direção especificada.

        Este método é chamado pelos passos da manobra para virar o robô.

        Args:
            direction: TurnDirection.LEFT ou TurnDirection.RIGHT
        """
        # Definir velocidade
        self.motors.set_speed(self.search_speed)

        # Executar giro
        if direction == TurnDirection.LEFT:
            self.motors.turn_left()
        else:
            self.motors.turn_right()

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