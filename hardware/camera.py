"""
hardware/camera.py
==================
Interface para visão computacional
Suporta: .keras, .h5 (TensorFlow) e .tflite (TFLite Runtime)
"""

import cv2
import numpy as np
import time
import os

# Tentar importar TensorFlow Lite
TFLITE_AVAILABLE = False
try:
    import tflite_runtime.interpreter as tflite
    TFLITE_AVAILABLE = True
    TFLITE_MODE = "runtime"
    print("[CAMERA] TFLite Runtime disponível")
except ImportError:
    try:
        import tensorflow as tf
        tflite = tf.lite
        TFLITE_AVAILABLE = True
        TFLITE_MODE = "tensorflow"
        print("[CAMERA] TensorFlow disponível")
    except ImportError:
        print("[CAMERA] TensorFlow não disponível")

# Tentar importar TensorFlow para modelos Keras
TENSORFLOW_AVAILABLE = False
try:
    import tensorflow as tf
    TENSORFLOW_AVAILABLE = True
except ImportError:
    print("[CAMERA] TensorFlow não disponível para carregar .keras")


class CameraVision:
    """
    Sistema de visão computacional.
    
    Suporta 3 formatos:
    1. .tflite (recomendado para RPi - mais rápido)
    2. .keras (novo formato Keras 3)
    3. .h5 (formato antigo Keras)
    """
    
    def __init__(self, model_path='classificador_placa_solar', 
                 image_size=(64, 64), confidence_threshold=0.7):
        """
        Inicializa sistema de visão.
        
        Args:
            model_path: Caminho do modelo (sem extensão ou com .keras/.h5/.tflite)
            image_size: Tamanho entrada (64, 64)
            confidence_threshold: Confiança mínima (0.7 = 70%)
        """
        print("[CAMERA] Inicializando visão computacional...")
        
        self.image_size = image_size
        self.confidence_threshold = confidence_threshold
        self.camera_ready = False
        
        # Detectar tipo de modelo e carregar
        self.model_type = None
        self.model = None
        self.interpreter = None
        
        # Contador para modo STUB (quando modelo não carregado)
        self.stub_call_count = 0
        
        # Tentar carregar modelo
        self._load_model(model_path)
    
    def _load_model(self, model_path):
        """
        Carrega modelo automaticamente detectando formato.
        
        Prioridade:
        1. .tflite (mais rápido)
        2. .keras (formato atual)
        3. .h5 (formato antigo)
        """
        # Lista de extensões para tentar
        extensions = ['.tflite', '.keras', '.h5', '']
        
        # Tentar cada extensão
        for ext in extensions:
            test_path = model_path if model_path.endswith(ext) else model_path + ext
            
            if os.path.exists(test_path):
                print(f"[CAMERA] Encontrado: {test_path}")
                
                if test_path.endswith('.tflite'):
                    return self._load_tflite(test_path)
                elif test_path.endswith('.keras') or test_path.endswith('.h5'):
                    return self._load_keras(test_path)
        
        # Nenhum modelo encontrado
        print(f"[CAMERA] ERRO: Modelo não encontrado!")
        print(f"[CAMERA] Procurado em:")
        for ext in extensions:
            print(f"  - {model_path}{ext}")
        print("[CAMERA] Modo STUB ativado")
        print("[CAMERA] STUB: 2 primeiras chamadas = LIMPA, depois alterna LIMPA/SUJA")
    
    def _load_tflite(self, model_path):
        """Carrega modelo TFLite"""
        if not TFLITE_AVAILABLE:
            print("[CAMERA] TFLite não disponível")
            return False
        
        try:
            self.interpreter = tflite.Interpreter(model_path=model_path)
            self.interpreter.allocate_tensors()
            
            self.input_details = self.interpreter.get_input_details()
            self.output_details = self.interpreter.get_output_details()
            
            self.model_type = 'tflite'
            self.camera_ready = True
            
            print(f"[CAMERA] Modelo TFLite carregado")
            print(f"[CAMERA] Input: {self.input_details[0]['shape']}")
            print(f"[CAMERA] Output: {self.output_details[0]['shape']}")
            return True
        
        except Exception as e:
            print(f"[CAMERA] Erro ao carregar TFLite: {e}")
            return False
    
    def _load_keras(self, model_path):
        """Carrega modelo Keras (.keras ou .h5)"""
        if not TENSORFLOW_AVAILABLE:
            print("[CAMERA] TensorFlow não disponível para .keras/.h5")
            print("[CAMERA] Instale: pip3 install tensorflow")
            return False
        
        try:
            self.model = tf.keras.models.load_model(model_path)
            self.model_type = 'keras'
            self.camera_ready = True
            
            print(f"[CAMERA] Modelo Keras carregado")
            print(f"[CAMERA] Input: {self.model.input_shape}")
            print(f"[CAMERA] Output: {self.model.output_shape}")
            return True
        
        except Exception as e:
            print(f"[CAMERA] Erro ao carregar Keras: {e}")
            return False
    
    def capture_frame(self):
        """Captura frame da câmera"""
        try:
            cap = cv2.VideoCapture(0)
            
            if not cap.isOpened():
                print("[CAMERA] Câmera não disponível")
                return None
            
            time.sleep(1)  # Estabilizar
            ret, frame = cap.read()
            cap.release()
            
            if not ret:
                print("[CAMERA] Falha ao capturar")
                return None
            
            return frame
        
        except Exception as e:
            print(f"[CAMERA] Erro: {e}")
            return None
    
    def preprocess_frame(self, frame):
        """
        Preprocessa frame.
        
        Args:
            frame: Frame BGR
            
        Returns:
            numpy.ndarray: Tensor preprocessado
        """
        # Redimensionar
        img = cv2.resize(frame, self.image_size)
        
        # BGR → RGB
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        
        # Normalizar [0, 255] → [0, 1]
        img = img.astype(np.float32) / 255.0
        
        # VGG16 preprocessing (subtrair média ImageNet)
        mean = np.array([0.485, 0.456, 0.406], dtype=np.float32)
        std = np.array([0.229, 0.224, 0.225], dtype=np.float32)
        img = (img - mean) / std
        
        # Batch dimension (1, 64, 64, 3)
        img = np.expand_dims(img, axis=0)
        
        return img.astype(np.float32)
    
    def _stub_detection(self):
        """
        Modo STUB quando modelo não está carregado.
        
        Lógica:
        - Chamadas 1 e 2: Retorna LIMPA (False)
        - Chamada 3+: Alterna entre LIMPA e SUJA
        
        Returns:
            bool: True = SUJEIRA, False = LIMPA
        """
        self.stub_call_count += 1
        
        print(f"[CAMERA] STUB - Verificação #{self.stub_call_count}")
        
        # Primeiras 2 chamadas: LIMPA
        if self.stub_call_count <= 2:
            print(f"[CAMERA] STUB: Placa limpa (primeiras verificações)")
            print(f"[CAMERA] Confiança: 0.85 (85%) [SIMULADO]")
            print(f"[CAMERA] Probs: Clean=0.85, Dusty=0.15 [SIMULADO]")
            return False
        
        # A partir da 3ª chamada: alterna
        is_dusty = (self.stub_call_count % 2) == 1  # Ímpar = Suja, Par = Limpa
        
        if is_dusty:
            print(f"[CAMERA] STUB: >>> SUJEIRA! <<< [SIMULADO]")
            print(f"[CAMERA] Confiança: 0.80 (80%) [SIMULADO]")
            print(f"[CAMERA] Probs: Clean=0.20, Dusty=0.80 [SIMULADO]")
        else:
            print(f"[CAMERA] STUB: Placa limpa [SIMULADO]")
            print(f"[CAMERA] Confiança: 0.85 (85%) [SIMULADO]")
            print(f"[CAMERA] Probs: Clean=0.85, Dusty=0.15 [SIMULADO]")
        
        return is_dusty
    
    def detect_target(self):
        """
        Detecta sujeira na placa solar.
        
        CHAMADO PELO ROBÔ A CADA 15 SEGUNDOS!
        
        Returns:
            bool: True = SUJEIRA, False = LIMPA
        """
        # Se modelo não está carregado, usa STUB
        if not self.camera_ready:
            return self._stub_detection()
        
        try:
            # 1. Capturar
            frame = self.capture_frame()
            if frame is None:
                return False
            
            # 2. Preprocessar
            input_data = self.preprocess_frame(frame)
            
            # 3. Inferência (depende do tipo)
            if self.model_type == 'tflite':
                prediction = self._predict_tflite(input_data)
            elif self.model_type == 'keras':
                prediction = self._predict_keras(input_data)
            else:
                return False
            
            # 4. Interpretar
            prob_clean = prediction[0][0]
            prob_dusty = prediction[0][1]
            
            predicted_class = np.argmax(prediction[0])
            confidence = np.max(prediction[0])
            
            # 0 = Clean, 1 = Dusty
            is_dusty = (predicted_class == 1)
            
            # 5. Threshold
            if confidence < self.confidence_threshold:
                print(f"[CAMERA] Confiança baixa ({confidence:.2f})")
                return False
            
            # 6. Log
            if is_dusty:
                print(f"[CAMERA] >>> SUJEIRA! <<<")
                print(f"[CAMERA] Confiança: {confidence:.2f} ({confidence*100:.0f}%)")
            else:
                print(f"[CAMERA] Placa limpa")
                print(f"[CAMERA] Confiança: {confidence:.2f} ({confidence*100:.0f}%)")
            
            print(f"[CAMERA] Probs: Clean={prob_clean:.2f}, Dusty={prob_dusty:.2f}")
            
            return is_dusty
        
        except Exception as e:
            print(f"[CAMERA] Erro: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def _predict_tflite(self, input_data):
        """Inferência TFLite"""
        self.interpreter.set_tensor(self.input_details[0]['index'], input_data)
        self.interpreter.invoke()
        output = self.interpreter.get_tensor(self.output_details[0]['index'])
        return output
    
    def _predict_keras(self, input_data):
        """Inferência Keras"""
        output = self.model.predict(input_data, verbose=0)
        return output
    
    def cleanup(self):
        """Limpa recursos"""
        print("[CAMERA] Recursos liberados")


# ==================== CONVERSÃO ====================
def converter_keras_para_tflite(modelo_keras, saida_tflite):
    """
    Converte .keras → .tflite
    
    Args:
        modelo_keras: Caminho .keras ou .h5
        saida_tflite: Caminho saída .tflite
    """
    if not TENSORFLOW_AVAILABLE:
        print("ERRO: TensorFlow necessário para conversão")
        print("Instale: pip3 install tensorflow")
        return False
    
    try:
        print(f"\n{'='*60}")
        print(f"CONVERSÃO: {modelo_keras} → {saida_tflite}")
        print('='*60)
        
        print(f"\n1. Carregando {modelo_keras}...")
        model = tf.keras.models.load_model(modelo_keras)
        print("   OK")
        
        print("\n2. Criando conversor...")
        converter = tf.lite.TFLiteConverter.from_keras_model(model)
        print("   OK")
        
        print("\n3. Convertendo para TFLite...")
        tflite_model = converter.convert()
        print("   OK")
        
        print(f"\n4. Salvando {saida_tflite}...")
        with open(saida_tflite, 'wb') as f:
            f.write(tflite_model)
        print("   OK")
        
        # Comparar tamanhos
        tamanho_keras = os.path.getsize(modelo_keras) / 1024 / 1024
        tamanho_tflite = os.path.getsize(saida_tflite) / 1024 / 1024
        reducao = ((tamanho_keras - tamanho_tflite) / tamanho_keras * 100)
        
        print(f"\n{'='*60}")
        print("CONVERSÃO CONCLUÍDA!")
        print('='*60)
        print(f"Tamanho original: {tamanho_keras:.2f} MB")
        print(f"Tamanho TFLite:   {tamanho_tflite:.2f} MB")
        print(f"Redução:          {reducao:.1f}%")
        print('='*60)
        
        return True
    
    except Exception as e:
        print(f"\nERRO na conversão: {e}")
        import traceback
        traceback.print_exc()
        return False


# ==================== TESTE ====================
if __name__ == "__main__":
    import sys
    
    # Comando: convert
    if len(sys.argv) > 1 and sys.argv[1] == 'convert':
        print("\n" + "="*60)
        print("    CONVERSOR .keras → .tflite")
        print("="*60 + "\n")
        
        # Entrada
        if len(sys.argv) > 2:
            modelo_keras = sys.argv[2]
        else:
            modelo_keras = 'classificador_placa_solar.keras'
        
        # Saída
        if len(sys.argv) > 3:
            saida_tflite = sys.argv[3]
        else:
            saida_tflite = modelo_keras.replace('.keras', '.tflite').replace('.h5', '.tflite')
        
        # Converter
        if converter_keras_para_tflite(modelo_keras, saida_tflite):
            print(f"\nAgora teste com:")
            print(f"  python3 hardware/camera.py")
        
        sys.exit(0)
    
    # Teste normal
    print("\n" + "="*60)
    print("    TESTE DO SISTEMA DE VISÃO")
    print("="*60)
    
    print("\nInicializando...")
    camera = CameraVision(
        model_path='classificador_placa_solar',  # Busca .tflite, .keras, .h5
        image_size=(64, 64),
        confidence_threshold=0.7
    )
    
    if not camera.camera_ready:
        print("\n" + "="*60)
        print("AVISO: Modelo não carregado - usando modo STUB!")
        print("="*60)
        print("\nArquivos procurados:")
        print("  - classificador_placa_solar.tflite")
        print("  - classificador_placa_solar.keras")
        print("  - classificador_placa_solar.h5")
        print("\nModo STUB ativo:")
        print("  - Verificações 1-2: LIMPA")
        print("  - Verificação 3+: Alterna LIMPA/SUJA")
        print("\nSe tem .keras, converta:")
        print("  python3 hardware/camera.py convert classificador_placa_solar.keras")
    else:
        print(f"\nModelo tipo: {camera.model_type}")
    
    print(f"Threshold: {camera.confidence_threshold}")
    
    # Menu
    print("\n" + "-"*60)
    print("1. Teste único")
    print("2. Teste contínuo (5x)")
    print("3. Teste infinito (Ctrl+C para parar)")
    print("-"*60)
    
    escolha = input("\nEscolha (1-3): ").strip()
    
    try:
        if escolha == '1':
            print("\n>>> Teste único...\n")
            result = camera.detect_target()
            print("\n" + "="*60)
            print("RESULTADO:", "SUJEIRA" if result else "LIMPA")
            print("="*60)
        
        elif escolha == '2':
            print("\n>>> 5 testes...\n")
            resultados = []
            for i in range(5):
                print(f"\n--- {i+1}/5 ---")
                resultados.append(camera.detect_target())
                if i < 4:
                    time.sleep(2)
            
            print("\n" + "="*60)
            print(f"Sujeira: {sum(resultados)}/5")
            print(f"Limpa: {5-sum(resultados)}/5")
            print("="*60)
        
        elif escolha == '3':
            print("\n>>> Contínuo...\n")
            n = 0
            while True:
                n += 1
                print(f"\n--- Teste #{n} ---")
                camera.detect_target()
                time.sleep(3)
    
    except KeyboardInterrupt:
        print("\n\nInterrompido!")
    
    finally:
        camera.cleanup()
        print("\n=== FIM ===\n")