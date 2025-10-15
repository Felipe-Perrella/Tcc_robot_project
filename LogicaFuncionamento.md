# Documentação Completa - Lógica de Funcionamento do Robô

## Índice
1. [Visão Geral](#visão-geral)
2. [Estados do Robô](#estados-do-robô)
3. [Lógica de Busca Inicial](#lógica-de-busca-inicial)
4. [Lógica de Limpeza (Andar Reto)](#lógica-de-limpeza-andar-reto)
5. [Lógica de Reposicionamento (Manobra)](#lógica-de-reposicionamento-manobra)
6. [Controle das Vassouras com Servo](#controle-das-vassouras-com-servo)
7. [Sistema de Visão Computacional](#sistema-de-visão-computacional)
8. [Fluxograma Completo](#fluxograma-completo)
9. [Parâmetros Configuráveis](#parâmetros-configuráveis)

---

## Visão Geral

O robô é um **sistema autônomo de limpeza de placas solares** que:

- Detecta placas solares usando sensor ultrassônico (embaixo do robô)
- Escaneia placas procurando sujeira usando visão computacional
- Liga vassouras (com servo) apenas quando detecta sujeira
- Executa manobras inteligentes quando perde a placa
- Economiza bateria verificando visão periodicamente (a cada 15 segundos)

### Componentes Principais

- **Motores de locomoção**: 2x motores DC (L298N)
- **Vassouras**: 2x motores DC (L298N) + 1x servo (levanta/abaixa)
- **Sensor ultrassônico**: HC-SR04 (montado embaixo, aponta para chão)
- **Câmera**: Visão computacional para detecção de sujeira

---

## Estados do Robô

O robô opera em **3 estados principais**:

### 1. INITIAL_SEARCH
**Busca inicial da placa solar**
- Robô gira no próprio eixo
- Sensor ultrassônico procura placa embaixo
- Transição: Quando detecta placa (distância ≤ 15cm) → MOVING_TO_TARGET

### 2. MOVING_TO_TARGET
**Sobre a placa, limpando**
- Robô anda reto sobre a placa
- Verifica visão a cada 15 segundos
- Liga/desliga vassouras conforme detecção
- Transição: Quando perde placa (distância > 15cm) → REPOSITIONING

### 3. REPOSITIONING
**Manobra quando perde a placa**
- Executa sequência de movimentos
- Tenta reposicionar sobre a placa
- Dois cenários possíveis (A ou B)
- Transição: Sempre volta para MOVING_TO_TARGET

---

## Lógica de Busca Inicial

### Estado: INITIAL_SEARCH

**Objetivo**: Encontrar uma placa solar

**Comportamento**:
```
Loop a cada 100ms:
  1. Ler sensor ultrassônico
  2. Se distância ≤ 15cm:
     → PLACA ENCONTRADA!
     → Parar motores
     → Mudar para MOVING_TO_TARGET
  3. Se não:
     → Continuar girando à direita
```

**Diagrama**:
```
      [R]
       ↻  (girando)
       ↻
       ↻
       
  Sensor detecta placa embaixo
       ↓
       
  =================
  ===== [R] ========
  =================
       ↓
  Inicia limpeza
```

**Parâmetros**:
- Velocidade: `SEARCH_SPEED` (padrão: 50%)
- Distância de detecção: `PANEL_DISTANCE` (padrão: 15cm)

---

## Lógica de Limpeza (Andar Reto)

### Estado: MOVING_TO_TARGET

**Objetivo**: Limpar a placa andando reto

**Comportamento Principal**:
```
Loop a cada 100ms:
  1. Ler sensor ultrassônico
  
  2. Se distância > 15cm:
     → Perdeu placa!
     → Iniciar REPOSITIONING
     → Sair do loop
  
  3. Verificar tempo desde última verificação de visão
  
  4. Se passaram 15 segundos:
     → Capturar imagem da câmera
     → Processar visão computacional
     → Salvar resultado (True = sujeira, False = limpo)
     → Resetar contador
  
  5. Controlar vassouras baseado no último resultado:
     → Se detectou sujeira: ligar vassouras
     → Se não: desligar vassouras
  
  6. Ajustar velocidade:
     → Com sujeira: velocidade baixa (scan_speed / 3)
     → Sem sujeira: velocidade normal (scan_speed)
  
  7. Andar para frente
```

### Verificação de Visão Periódica

**Por que a cada 15 segundos?**

| Modo | Verificações/min | CPU | Autonomia |
|------|-----------------|-----|-----------|
| Contínuo (10Hz) | 600 | 95% | ~2 horas |
| Periódico (15s) | 4 | 15% | ~8 horas |

**Economia: 4x mais bateria!**

**Fluxo da Verificação**:
```
Tempo = 0s
└─> Verifica visão IMEDIATAMENTE
    └─> Resultado: True (sujeira)
        └─> Liga vassouras

Tempo = 5s
└─> Usa resultado anterior: True
    └─> Vassouras continuam ligadas

Tempo = 10s
└─> Usa resultado anterior: True
    └─> Vassouras continuam ligadas

Tempo = 15s
└─> Verifica visão NOVAMENTE
    └─> Resultado: False (limpo)
        └─> Desliga vassouras

Tempo = 20s
└─> Usa resultado anterior: False
    └─> Vassouras continuam desligadas
```

### Diagrama Visual

```
Linha do tempo de limpeza:

t=0s   [VISÃO] Detecta sujeira
       └─> Liga vassouras + abaixa servo
       
t=5s   Andando e limpando (usa resultado anterior)
t=10s  Andando e limpando (usa resultado anterior)

t=15s  [VISÃO] Não detecta sujeira
       └─> Desliga vassouras + levanta servo
       
t=20s  Andando apenas escaneando (usa resultado anterior)
t=25s  Andando apenas escaneando (usa resultado anterior)

t=30s  [VISÃO] Detecta sujeira novamente
       └─> Liga vassouras + abaixa servo
       
...continua...
```

**Movimento na Placa**:
```
Vista de cima:

===================================
===== [R] → → → → → → → → → → ====
===================================

[R] = Robô
→   = Andando reto
=   = Placa solar

Vassouras:
- Ligadas quando última visão = sujeira
- Desligadas quando última visão = limpo
```

**Parâmetros**:
- Velocidade com sujeira: `SCAN_SPEED / 3` (padrão: 40/3 = 13%)
- Velocidade sem sujeira: `SCAN_SPEED` (padrão: 40%)
- Intervalo de visão: 15 segundos (configurável)
- Distância da placa: `PANEL_DISTANCE` ≤ 15cm

---

## Lógica de Reposicionamento (Manobra)

### Estado: REPOSITIONING

**Objetivo**: Reposicionar quando perde a placa

**Quando ativa**: Sensor detecta distância > 15cm (saiu da placa)

### Variável de Status

O robô mantém uma variável `turn_direction` que define para qual lado virará:
- Valores: `LEFT` (esquerda) ou `RIGHT` (direita)
- Inicial: `LEFT`
- Atualização: Depende do cenário executado

### Dois Cenários Possíveis

#### CENÁRIO A: Ainda na placa após virar 90°

**Situação**: Robô chegou na borda, mas ainda está parcialmente sobre a placa

**Sequência**:
```
1. Vira 90° (conforme status: esquerda ou direita)
2. Aguarda 0.3s e verifica sensor
3. DETECTA PLACA! (distância ≤ 15cm)
4. Anda largura do robô para frente
5. Vira 90° novamente (mesma direção)
6. INVERTE status (próxima vez vira outro lado)
7. Volta para MOVING_TO_TARGET
```

**Diagrama Visual**:
```
Status atual: LEFT (próxima curva à esquerda)

===================================
========== [R] → → → → → → → ======  (perde placa na frente)
===================================
             ↓
        ⤶ (vira 90° ESQ)
        ⤶
        ↓
====== ⤶ (DETECTA PLACA!)
====== ↓
====== → (anda largura)
====== →
====== ↓
====== ⤶ (vira 90° ESQ)
====== ⤶
====== ↓
====== → → → → (continua limpando)

Status atualizado: RIGHT (próxima curva à direita)
```

#### CENÁRIO B: Saiu completamente da placa

**Situação**: Robô saiu totalmente da placa

**Sequência**:
```
1. Vira 90° (conforme status: esquerda ou direita)
2. Aguarda 0.3s e verifica sensor
3. NÃO DETECTA PLACA! (distância > 15cm)
4. Vira 180° de volta (2x 90° no sentido oposto)
5. Anda largura do robô para frente
6. Vira 90° (mesma direção do último giro)
7. MANTÉM status (próxima vez tenta mesmo lado)
8. Volta para MOVING_TO_TARGET
```

**Diagrama Visual**:
```
Status atual: LEFT (próxima curva à esquerda)

===================================
========== [R] → → → → → → → ======  (perde placa na frente)
===================================
             ↓
        ⤶ (vira 90° ESQ)
        ⤶
        ↓
        ↓ (NÃO DETECTA PLACA!)
        ↓
        ⤷ (vira 180° = 2x90° DIR)
        ⤷
        ⤷
        ⤷
        ↓
        → (anda largura)
        →
        ↓
====== ⤷ (vira 90° DIR)
====== ⤷
====== ↓
====== → → → → (continua limpando)

Status mantido: LEFT (próxima ainda à esquerda)
```

### Máquina de Estados da Manobra

```
FIRST_TURN_90
    ↓
    Vira 90° (tempo: TURN_90_TIME)
    ↓
CHECK_PANEL
    ↓
    Aguarda 0.3s e verifica sensor
    ↓
    ┌─────────────┐
    │ Detecta?    │
    └──┬──────┬───┘
       │      │
     SIM    NÃO
       │      │
       │   TURN_180_BACK
       │      ↓
       │   Vira 180° (2x TURN_90_TIME)
       │      │
       └──┬───┘
          ↓
    MOVING_SIDEWAYS
          ↓
    Anda largura (tempo: SIDEWAYS_TIME)
          ↓
    FINAL_TURN_90
          ↓
    Vira 90° final
          ↓
    ┌──────────────┐
    │ Foi cenário? │
    └──┬───────┬───┘
       │       │
       A       B
       │       │
    Inverte  Mantém
    status   status
       │       │
       └───┬───┘
           ↓
    Volta para MOVING_TO_TARGET
```

### Exemplo Completo de Sequência

**Situação inicial**: Status = LEFT

```
1ª vez que perde placa:
  └─> Vira 90° ESQ
      └─> NÃO detecta (Cenário B)
          └─> Vira 180° volta (DIR)
              └─> Anda lateral
                  └─> Vira 90° DIR
                      └─> Status MANTÉM: LEFT

2ª vez que perde placa:
  └─> Vira 90° ESQ (ainda LEFT)
      └─> DETECTA placa! (Cenário A)
          └─> Anda lateral
              └─> Vira 90° ESQ
                  └─> Status INVERTE: RIGHT

3ª vez que perde placa:
  └─> Vira 90° DIR (agora RIGHT)
      └─> DETECTA placa! (Cenário A)
          └─> Anda lateral
              └─> Vira 90° DIR
                  └─> Status INVERTE: LEFT

4ª vez que perde placa:
  └─> Vira 90° ESQ (volta para LEFT)
      └─> ...continua...
```

### Por que essa Lógica?

**Cenário A (inverte)**:
- Robô está na borda da placa
- Alterna lados para cobrir toda a placa
- Cria padrão de varredura eficiente

**Cenário B (mantém)**:
- Robô saiu completamente
- Tenta voltar pelo mesmo lado
- Se saiu de um lado, faz sentido tentar entrar por ali

**Parâmetros**:
- Tempo curva 90°: `TURN_90_TIME` (padrão: 0.5s)
- Tempo lateral: `SIDEWAYS_TIME` (padrão: 1.0s)
- Tempo aguardo verificação: 0.3s (fixo)
- Tempo procura após manobra: 3.0s (antes de repetir)

---

## Controle das Vassouras com Servo

### Sistema de Levantamento

As vassouras possuem um **servo motor** que as levanta/abaixa:
- **0°**: Vassouras levantadas (não tocam a placa)
- **90°**: Vassouras abaixadas (tocam a placa para limpar)

### Sequência de Ativação

**LIGAR vassouras** (quando detecta sujeira):
```
1. Servo move de 0° para 90° (0.5s)
   └─> Vassouras abaixam e tocam a placa
   
2. Aguarda 0.3s para estabilizar
   
3. Liga motores das vassouras (PWM 80%)
   └─> Vassouras começam a girar
   
STATUS: Limpando
```

**DESLIGAR vassouras** (quando não detecta sujeira):
```
1. Desliga motores das vassouras
   └─> Vassouras param de girar
   
2. Aguarda 0.2s para motores pararem
   
3. Servo move de 90° para 0° (0.5s)
   └─> Vassouras levantam e não tocam placa
   
STATUS: Apenas escaneando
```

### Diagrama de Estados das Vassouras

```
        ┌──────────────┐
        │ VASSOURAS    │
        │ DESLIGADAS   │
        │ (servo 0°)   │
        └──────┬───────┘
               │
        Detecta sujeira
               ↓
        ┌──────────────┐
        │ Servo abaixa │
        │ 0° → 90°     │
        └──────┬───────┘
               ↓
        ┌──────────────┐
        │ Motores ON   │
        │ (PWM 80%)    │
        └──────┬───────┘
               │
        ┌──────┴───────┐
        │ VASSOURAS    │
        │ LIMPANDO     │
        │ (servo 90°)  │
        └──────┬───────┘
               │
        Não detecta sujeira
               ↓
        ┌──────────────┐
        │ Motores OFF  │
        └──────┬───────┘
               ↓
        ┌──────────────┐
        │ Servo levanta│
        │ 90° → 0°     │
        └──────┬───────┘
               │
               ↓
        (volta ao início)
```

### Controle Inteligente

**Condições para LIGAR**:
```
if (está_sobre_placa AND última_visão_detectou_sujeira):
    ligar_vassouras()
```

**Condições para DESLIGAR**:
```
if (NOT está_sobre_placa OR NOT última_visão_detectou_sujeira):
    desligar_vassouras()
```

**Vantagens**:
- Economiza energia: vassouras só ligam quando necessário
- Protege placa: não arranha quando não há sujeira
- Aumenta vida útil das vassouras

---

## Sistema de Visão Computacional

### Interface com Câmera

O sistema possui um módulo `CameraVision` que deve ser implementado:

```python
class CameraVision:
    def detect_target(self):
        """
        Detecta se há sujeira na imagem.
        
        Returns:
            bool: True se DETECTOU SUJEIRA
                  False se PLACA LIMPA
        """
        # SEU ALGORITMO AQUI
        return False  # placeholder
```

### Implementações Possíveis

#### Opção 1: Threshold de Cor
```python
def detect_target(self):
    frame = self.camera.capture_array()
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    
    # Pixels escuros = sujeira
    dark_pixels = cv2.countNonZero(gray < 50)
    total_pixels = gray.shape[0] * gray.shape[1]
    dirt_ratio = dark_pixels / total_pixels
    
    return dirt_ratio > 0.15  # 15% de sujeira
```

#### Opção 2: Machine Learning
```python
def detect_target(self):
    frame = self.camera.capture_array()
    processed = preprocess(frame)
    
    prediction = self.model.predict(processed)
    confidence = prediction[0][1]  # probabilidade de sujeira
    
    return confidence > 0.7  # 70% de confiança
```

#### Opção 3: Análise de Textura
```python
def detect_target(self):
    frame = self.camera.capture_array()
    
    # Detectar bordas (sujeira tem mais bordas)
    edges = cv2.Canny(frame, 50, 150)
    edge_density = cv2.countNonZero(edges) / edges.size
    
    return edge_density > 0.3
```

### Integração no Sistema

O método `detect_target()` é chamado:
- **Quando**: A cada 15 segundos (configurável)
- **Onde**: Apenas no estado MOVING_TO_TARGET
- **Resultado**: Armazenado e usado até próxima verificação

---

## Fluxograma Completo

### Visão Geral do Sistema

```
              ┌─────────────┐
              │   INÍCIO    │
              └──────┬──────┘
                     ↓
              ┌──────────────┐
              │ INITIAL_     │
              │ SEARCH       │
              │ (gira)       │
              └──────┬───────┘
                     │
              Detecta placa
                     ↓
              ┌──────────────────────┐
              │ MOVING_TO_TARGET     │
              │                      │
              │ Loop:                │
              │ 1. Anda reto         │
              │ 2. A cada 15s:       │
              │    verifica visão    │
              │ 3. Controla vassouras│
              └──────┬───────────────┘
                     │
              Perde placa
                     ↓
              ┌───────────────────────┐
              │ REPOSITIONING         │
              │                       │
              │ Vira 90°              │
              │ Verifica sensor       │
              │ ┌────────┐            │
              │ │Detecta?│            │
              │ └┬──────┬┘            │
              │  │ SIM  │ NÃO         │
              │  │      │             │
              │  A      B             │
              │  │      │             │
              │  └───┬──┘             │
              │      │                │
              │ Anda + Vira           │
              │ Atualiza status       │
              └──────┬────────────────┘
                     │
              Volta para MOVING_TO_TARGET
                     ↓
              (repete ciclo)
```

### Fluxo Detalhado por Frame (10Hz)

```
A cada 100ms (10 vezes por segundo):

┌─────────────────────────┐
│ 1. Ler Sensor           │
│    Ultrassônico         │
└───────────┬─────────────┘
            ↓
┌─────────────────────────┐
│ 2. Calcular distância   │
│    ao chão              │
└───────────┬─────────────┘
            ↓
┌─────────────────────────┐
│ 3. Determinar estado    │
│    atual do robô        │
└───────────┬─────────────┘
            ↓
     ┌──────┴──────┐
     │             │
INITIAL_    MOVING_TO_   REPOSITIONING
SEARCH      TARGET
     │             │             │
     ↓             ↓             ↓
  Gira      ┌──────────┐    Executa
procurando  │Conta tempo│    manobra
            │desde visão│
            └─────┬─────┘
                  ↓
            ┌────────────┐
            │≥15 segundos?│
            └─┬────────┬─┘
              │ SIM    │ NÃO
              ↓        ↓
          Verifica   Usa último
          câmera     resultado
              │        │
              └───┬────┘
                  ↓
            Controla
            vassouras
                  ↓
            Anda para
            frente
```

---

## Parâmetros Configuráveis

### Arquivo: `config.py`

#### Pinos GPIO

```python
# Motores de locomoção
MOTOR_PINS = {
    'left_motor': {'in1': 18, 'in2': 19, 'ena': 12},
    'right_motor': {'in3': 20, 'in4': 21, 'enb': 13}
}

# Motores das vassouras
BRUSH_MOTOR_PINS = {
    'brush_1': {'in1': 5, 'in2': 6, 'enable': 16},
    'brush_2': {'in1': 22, 'in2': 27, 'enable': 17}
}

# Servo
SERVO_PIN = 4

# Sensor ultrassônico
ULTRASONIC_PINS = {
    'trigger': 24,
    'echo': 23
}
```

#### Distâncias

```python
PANEL_DISTANCE = 15  # cm - considera "sobre placa"
```

**Como ajustar**:
- Teste com régua: meça distância quando robô está sobre placa
- Se placa tem 2cm de espessura: sensor lerá ~2cm
- Adicione margem de segurança: 15cm é conservador

#### Velocidades

```python
SEARCH_SPEED = 50    # 0-100 - velocidade ao procurar
SCAN_SPEED = 40      # 0-100 - velocidade ao escanear
BRUSH_SPEED = 80     # 0-100 - velocidade das vassouras
```

**Como ajustar**:
- Teste incrementalmente: comece com 30%, aumente aos poucos
- Muito rápido: robô não detecta mudanças a tempo
- Muito lento: limpeza demora demais

#### Tempos

```python
# Manobras
TURN_90_TIME = 0.5      # segundos para virar 90°
SIDEWAYS_TIME = 1.0     # segundos andando lateral

# Visão
vision_check_interval = 15  # segundos entre verificações
```

**Como calibrar TURN_90_TIME**:
1. Coloque robô no chão
2. Execute: `motors.turn_left()` por X segundos
3. Meça ângulo girado
4. Ajuste tempo até girar exatos 90°

**Como calibrar SIDEWAYS_TIME**:
1. Meça largura do robô (ex: 20cm)
2. Coloque robô andando em linha reta
3. Meça quanto anda em 1 segundo na velocidade de busca
4. Calcule: `SIDEWAYS_TIME = largura_robo / velocidade`

#### Ajustes Avançados

```python
PWM_FREQUENCY = 1000        # Hz - frequência PWM dos motores
MAIN_LOOP_DELAY = 0.1       # segundos - delay do loop (10Hz)
```

### Tabela Resumo

| Parâmetro | Padrão | Unidade | O que afeta |
|-----------|--------|---------|-------------|
| PANEL_DISTANCE | 15 | cm | Sensibilidade de detecção |
| SEARCH_SPEED | 50 | % | Velocidade de busca/manobra |
| SCAN_SPEED | 40 | % | Velocidade de escaneamento |
| BRUSH_SPEED | 80 | % | Potência das vassouras |
| TURN_90_TIME | 0.5 | s | Precisão das curvas |
| SIDEWAYS_TIME | 1.0 | s | Deslocamento lateral |
| vision_check_interval | 15 | s | Frequência de visão/bateria |

---

## Resumo Executivo

### Funcionamento em 5 Passos

1. **Busca**: Robô gira até encontrar placa (sensor ≤ 15cm)

2. **Limpeza**: Anda reto sobre placa
   - Verifica visão a cada 15s
   - Liga vassouras se detecta sujeira

3. **Manobra**: Quando perde placa
   - Vira 90° e verifica sensor
   - Se ainda detecta: continua (Cenário A)
   - Se não detecta: volta 180° (Cenário B)

4. **Reposicionamento**: Anda lateral e vira de volta

5. **Repetição**: Volta a andar reto limpando

### Benefícios da Arquitetura

- **Eficiência energética**: Visão periódica economiza 4x bateria
- **Cobertura inteligente**: Alterna lados para varrer toda placa
- **Proteção**: Vassouras só tocam quando necessário
- **Robustez**: Dois cenários cobrem todas situações
- **Modularidade**: Fácil ajustar parâmetros e algoritmos

---

**Versão**: 1.0  
**Data**: 2025-01-15  
**Projeto**: Robô Autônomo de Limpeza de Placas Solares