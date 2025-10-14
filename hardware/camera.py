"""
hardware/camera.py
==================
Interface para visão computacional

IMPORTANTE: Este é um STUB (modelo básico).
Você deve implementar seu próprio algoritmo de detecção aqui.
"""

import time


class CameraVision:
    """
    Interface para sistema de visão computacional.
    
    Detecta sujeira em placas solares usando câmera.
    
    VOCÊ DEVE IMPLEMENTAR:
    - Captura de imagens
    - Processamento (filtros, thresholds, etc)
    - Modelo de ML (se aplicável)
    - Lógica de detecção
    """
    
    def __init__(self):
        """
        Inicializa sistema de visão.
        
        IMPLEMENTE AQUI:
        - Inicialização da câmera (picamera2 ou opencv)
        - Carregamento de modelo (se usar ML)
        - Configurações de processamento
        """
        print("[CAMERA] Inicializando visão computacional...")
        
        # TODO: Inicializar sua câmera
        # Exemplo com picamera2:
        # from picamera2 import Picamera2
        # self.camera = Picamera2()
        # config = self.camera.create_still_configuration(main={"size": (640, 480)})
        # self.camera.configure(config)
        # self.camera.start()
        
        # TODO: Carregar modelo (se usar)
        # self.model = load_your_model()
        
        self.camera_ready = False  # Mude para True quando implementar
        
        if self.camera_ready:
            print("[CAMERA] Pronta para detecção")
        else:
            print("[CAMERA] STUB MODE - retornará sempre False")
            print("[CAMERA] IMPLEMENTE seu algoritmo em hardware/camera.py")
    
    def detect_target(self):
        """
        Detecta se há sujeira na imagem atual.
        
        Este método é chamado a cada X segundos (configurável em config.py).
        
        IMPLEMENTAR:
        1. Capturar frame da câmera
        2. Processar imagem (filtros, normalização, etc)
        3. Aplicar seu algoritmo de detecção
        4. Retornar resultado
        
        Returns:
            bool: True se DETECTOU SUJEIRA
                  False se PLACA LIMPA
        
        Exemplo de implementação:

        """
        
        # STUB: Sempre retorna False enquanto não implementado
        if not self.camera_ready:
            # Modo simulação para testes (retorna False)
            return False
        
        # TODO: IMPLEMENTAR SEU ALGORITMO AQUI
        
        # Exemplo básico:
        # frame = self.capture_frame()
        # result = self.process_frame(frame)
        # return result
        
        return False
    
    def capture_frame(self):
        """
        Captura um frame da câmera.
        
        IMPLEMENTE AQUI a captura de imagem.
        
        Returns:
            numpy.ndarray: frame capturado
        """
        # TODO: Implementar
        # return self.camera.capture_array()
        pass
    
    def process_frame(self, frame):
        """
        Processa frame e detecta sujeira.
        
        IMPLEMENTE AQUI seu algoritmo de processamento.
        
        Args:
            frame: frame capturado
            
        Returns:
            bool: True se detectou sujeira
        """
        # TODO: Implementar seu algoritmo
        # Exemplos de técnicas:
        # - Threshold de cor
        # - Edge detection
        # - Template matching
        # - Machine Learning (CNN, YOLO, etc)
        # - Análise de textura
        pass
    
    def cleanup(self):
        """Limpa recursos da câmera"""
        if self.camera_ready:
            # TODO: Parar câmera
            # self.camera.stop()
            pass
        
        print("[CAMERA] Recursos liberados")


# GUIA DE IMPLEMENTAÇÃO
# =====================
#
# 1. ESCOLHER BIBLIOTECA:
#    - picamera2 (recomendado para Pi Camera)
#    - opencv (para USB camera)
#
# 2. INSTALAR DEPENDÊNCIAS:
#    pip install picamera2  # ou opencv-python
#
# 3. IMPLEMENTAR detect_target():
#    Opções:
#    
#    A) Detecção simples (threshold de cor):
#       - Converter para HSV
#       - Definir range de cores da sujeira
#       - Contar pixels no range
#       - Se > threshold: sujeira detectada
#    
#    B) Machine Learning:
#       - Treinar modelo CNN
#       - Classificação binária: limpo/sujo
#       - Carregar modelo no __init__
#       - Usar em detect_target()
#    
#    C) Template matching:
#       - Ter templates de sujeira comum
#       - Buscar padrões similares na imagem
#
# 4. TESTAR ISOLADAMENTE:
#    python3 -c "from hardware.camera import CameraVision; c = CameraVision(); print(c.detect_target())"
#
# 5. AJUSTAR THRESHOLD:
#    Encontre o melhor valor de threshold testando em placas reais
#
# 6. OTIMIZAR:
#    - Reduzir resolução se processamento lento
#    - Usar ROI (region of interest)
#    - Cache de resultados