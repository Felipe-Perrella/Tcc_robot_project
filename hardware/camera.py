"""
hardware/camera.py
==================
Interface para visão computacional com modelo treinado
"""

import cv2
import numpy as np
import time

# Importações TensorFlow (só se modelo disponível)
try:
    from tensorflow.keras.models import load_model
    from tensorflow.keras.applications.vgg16 import preprocess_input
    from tensorflow.keras.preprocessing.image import img_to_array
    TENSORFLOW_AVAILABLE = True
except ImportError:
    TENSORFLOW_AVAILABLE = False
    print("[CAMERA] TensorFlow não instalado. Modo STUB ativado.")


class CameraVision:
    """
    Sistema de visão computacional usando Deep Learning.
    
    Classifica placas solares como limpas ou sujas usando
    modelo CNN treinado (VGG16 transfer learning).
    """
    
    def __init__(self, model_path='classificador_placa_solar.h5', 
                 image_size=(64, 64), confidence_threshold=0.7):
        """
        Inicializa sistema de visão.
        
        Args:
            model_path: Caminho do modelo .h5
            image_size: Tamanho de entrada da rede (64, 64)
            confidence_threshold: Confiança mínima (padrão: 0.7 = 70%)
        """
        print("[CAMERA] Inicializando visão computacional...")
        
        self.model_path = model_path
        self.image_size = image_size
        self.confidence_threshold = confidence_threshold
        self.model = None
        self.camera_ready = False
        
        # Verificar se TensorFlow está disponível
        if not TENSORFLOW_AVAILABLE:
            print("[CAMERA] TensorFlow não disponível!")
            print("[CAMERA] Instale com: pip install tensorflow")
            print("[CAMERA] Modo STUB ativado (sempre retorna False)")
            return
        
        # Tentar carregar modelo
        try:
            self.model = load_model(model_path)
            self.camera_ready = True
            print(f"[CAMERA] Modelo carregado: {model_path}")
            print(f"[CAMERA] Tamanho de entrada: {image_size}")
            print(f"[CAMERA] Threshold de confiança: {confidence_threshold * 100}%")
        
        except FileNotFoundError:
            print(f"[CAMERA] ERRO: Arquivo '{model_path}' não encontrado!")
            print(f"[CAMERA] Certifique-se que o modelo está no diretório do projeto")
            print("[CAMERA] Modo STUB ativado (sempre retorna False)")
        
        except Exception as e:
            print(f"[CAMERA] ERRO ao carregar modelo: {e}")
            print("[CAMERA] Modo STUB ativado (sempre retorna False)")
    
    def capture_frame(self):
        """
        Captura frame da câmera.
        
        Returns:
            numpy.ndarray: Frame capturado ou None se erro
        """
        try:
            cap = cv2.VideoCapture(0)
            
            if not cap.isOpened():
                print("[CAMERA] Erro: Não conseguiu abrir câmera")
                return None
            
            # Aguardar estabilização
            time.sleep(1)
            
            ret, frame = cap.read()
            cap.release()
            
            if not ret:
                print("[CAMERA] Falha ao capturar frame")
                return None
            
            return frame
        
        except Exception as e:
            print(f"[CAMERA] Erro na captura: {e}")
            return None
    
    def preprocess_frame(self, frame):
        """
        Preprocessa frame para entrada na rede.
        
        Args:
            frame: Frame capturado (numpy array BGR)
            
        Returns:
            numpy.ndarray: Frame preprocessado para o modelo
        """
        # Redimensionar para tamanho da rede
        img_resized = cv2.resize(frame, self.image_size)
        
        # Converter BGR (OpenCV) para RGB (Keras)
        img_rgb = cv2.cvtColor(img_resized, cv2.COLOR_BGR2RGB)
        
        # Converter para array
        img_array = img_to_array(img_rgb)
        
        # Preprocessamento VGG16
        img_array = preprocess_input(img_array)
        
        # Adicionar batch dimension (1, 64, 64, 3)
        img_batch = np.expand_dims(img_array, axis=0)
        
        return img_batch
    
    def detect_target(self):
        """
        Detecta se há sujeira na placa solar.
        
        ESTE É O MÉTODO CHAMADO PELO ROBÔ A CADA 15 SEGUNDOS!
        
        Fluxo:
        1. Captura frame da câmera
        2. Preprocessa imagem
        3. Passa pelo modelo neural
        4. Interpreta resultado
        5. Aplica threshold de confiança
        
        Returns:
            bool: True se DETECTOU SUJEIRA (Dusty)
                  False se PLACA LIMPA (Clean) ou erro
        """
        # Modo STUB: modelo não disponível
        if not self.camera_ready or self.model is None:
            return False
        
        try:
            # 1. CAPTURAR FRAME
            frame = self.capture_frame()
            if frame is None:
                print("[CAMERA] Frame não capturado, retornando False")
                return False
            
            # 2. PREPROCESSAR
            img_batch = self.preprocess_frame(frame)
            
            # 3. FAZER PREDIÇÃO
            prediction = self.model.predict(img_batch, verbose=0)
            
            # 4. INTERPRETAR RESULTADO
            # prediction = [[prob_clean, prob_dusty]]
            prob_clean = prediction[0][0]
            prob_dusty = prediction[0][1]
            
            # Índice da classe com maior probabilidade
            predicted_class = np.argmax(prediction[0])
            confidence = np.max(prediction[0])
            
            # Classes: 0 = Clean, 1 = Dusty
            is_dusty = (predicted_class == 1)
            
            # 5. APLICAR THRESHOLD DE CONFIANÇA
            if confidence < self.confidence_threshold:
                print(f"[CAMERA] Confiança baixa ({confidence:.2f}), "
                      f"considerando limpo por segurança")
                return False
            
            # 6. LOG DO RESULTADO
            if is_dusty:
                print(f"[CAMERA] >>> SUJEIRA DETECTADA! <<<")
                print(f"[CAMERA] Confiança: {confidence:.2f} ({confidence*100:.0f}%)")
                print(f"[CAMERA] Probabilidades: Clean={prob_clean:.2f}, Dusty={prob_dusty:.2f}")
            else:
                print(f"[CAMERA] Placa LIMPA")
                print(f"[CAMERA] Confiança: {confidence:.2f} ({confidence*100:.0f}%)")
                print(f"[CAMERA] Probabilidades: Clean={prob_clean:.2f}, Dusty={prob_dusty:.2f}")
            
            return is_dusty
        
        except Exception as e:
            print(f"[CAMERA] ERRO na detecção: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def cleanup(self):
        """Limpa recursos da câmera"""
        print("[CAMERA] Recursos liberados")


# ==================== TESTE ISOLADO ====================
if __name__ == "__main__":
    """
    Teste do sistema de visão isoladamente.
    
    Uso:
        cd ~/robot_project
        python3 hardware/camera.py
    """
    import sys
    
    print("\n" + "="*60)
    print("    TESTE DO SISTEMA DE VISÃO COMPUTACIONAL")
    print("="*60)
    
    # Verificar se TensorFlow disponível
    if not TENSORFLOW_AVAILABLE:
        print("\nERRO: TensorFlow não está instalado!")
        print("\nPara instalar:")
        print("  pip install tensorflow")
        print("  ou")
        print("  pip install tensorflow-lite (para Raspberry Pi)")
        sys.exit(1)
    
    # Criar instância
    print("\nInicializando câmera...")
    camera = CameraVision(
        model_path='classificador_placa_solar.h5',
        image_size=(64, 64),
        confidence_threshold=0.7
    )
    
    # Verificar se modelo carregou
    if not camera.camera_ready:
        print("\n" + "="*60)
        print("ERRO: Modelo não carregado!")
        print("="*60)
        print("\nVerifique:")
        print("  1. Arquivo 'classificador_placa_solar.h5' existe?")
        print("  2. Está no diretório correto?")
        print("  3. Modelo foi treinado corretamente?")
        print("\nCaminho esperado:")
        print(f"  {camera.model_path}")
        sys.exit(1)
    
    # Menu de testes
    print("\n" + "-"*60)
    print("OPÇÕES DE TESTE:")
    print("-"*60)
    print("1. Teste único")
    print("2. Teste contínuo (5 vezes)")
    print("3. Teste contínuo infinito (Ctrl+C para parar)")
    print("-"*60)
    
    escolha = input("\nEscolha uma opção (1-3): ").strip()
    
    try:
        if escolha == '1':
            # Teste único
            print("\n>>> Executando teste único...\n")
            result = camera.detect_target()
            
            print("\n" + "="*60)
            if result:
                print("RESULTADO FINAL: SUJEIRA DETECTADA")
            else:
                print("RESULTADO FINAL: PLACA LIMPA")
            print("="*60)
        
        elif escolha == '2':
            # 5 testes
            print("\n>>> Executando 5 testes...\n")
            resultados = []
            
            for i in range(5):
                print(f"\n--- Teste {i+1}/5 ---")
                result = camera.detect_target()
                resultados.append(result)
                
                if i < 4:  # Não aguardar no último
                    print("\nAguardando 2 segundos...")
                    time.sleep(2)
            
            # Resumo
            print("\n" + "="*60)
            print("RESUMO DOS TESTES:")
            print("="*60)
            sujeira_count = sum(resultados)
            limpo_count = len(resultados) - sujeira_count
            print(f"Sujeira detectada: {sujeira_count}/5 vezes")
            print(f"Placa limpa: {limpo_count}/5 vezes")
            print("="*60)
        
        elif escolha == '3':
            # Teste infinito
            print("\n>>> Teste contínuo (Pressione Ctrl+C para parar)...\n")
            contador = 0
            
            while True:
                contador += 1
                print(f"\n--- Teste #{contador} ---")
                result = camera.detect_target()
                
                print("\nAguardando 3 segundos...")
                time.sleep(3)
        
        else:
            print("\nOpção inválida!")
    
    except KeyboardInterrupt:
        print("\n\nTeste interrompido pelo usuário!")
    
    finally:
        camera.cleanup()
        print("\n=== TESTE CONCLUÍDO ===\n")