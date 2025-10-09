# utils.py - Funções utilitárias e helpers

import time
import signal
import sys
from functools import wraps

class GracefulShutdown:
    """Gerenciador de desligamento gracioso do robô"""
    
    def __init__(self):
        self.shutdown_flag = False
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
    
    def _signal_handler(self, signum, frame):
        """Captura sinais de interrupção"""
        print("\n\n⚠️  Sinal de interrupção recebido...")
        self.shutdown_flag = True
    
    def is_shutdown_requested(self):
        """Verifica se foi solicitado o desligamento"""
        return self.shutdown_flag


class Timer:
    """Timer simples para controle de tempo"""
    
    def __init__(self):
        self.start_time = None
        self.running = False
    
    def start(self):
        """Inicia o timer"""
        self.start_time = time.time()
        self.running = True
    
    def elapsed(self):
        """Retorna tempo decorrido em segundos"""
        if not self.running or self.start_time is None:
            return 0
        return time.time() - self.start_time
    
    def reset(self):
        """Reinicia o timer"""
        self.start()
    
    def stop(self):
        """Para o timer"""
        self.running = False
        return self.elapsed()


class RateLimiter:
    """Limitador de taxa de execução"""
    
    def __init__(self, max_calls_per_second):
        self.min_interval = 1.0 / max_calls_per_second
        self.last_call = 0
    
    def wait_if_needed(self):
        """Aguarda se necessário para respeitar a taxa"""
        elapsed = time.time() - self.last_call
        if elapsed < self.min_interval:
            time.sleep(self.min_interval - elapsed)
        self.last_call = time.time()
    
    def __call__(self, func):
        """Permite usar como decorador"""
        @wraps(func)
        def wrapper(*args, **kwargs):
            self.wait_if_needed()
            return func(*args, **kwargs)
        return wrapper


class MovingAverage:
    """Filtro de média móvel para suavizar leituras de sensores"""
    
    def __init__(self, window_size=5):
        self.window_size = window_size
        self.values = []
    
    def add(self, value):
        """Adiciona um valor e retorna a média"""
        self.values.append(value)
        if len(self.values) > self.window_size:
            self.values.pop(0)
        return self.get_average()
    
    def get_average(self):
        """Retorna a média atual"""
        if not self.values:
            return 0
        return sum(self.values) / len(self.values)
    
    def reset(self):
        """Limpa todos os valores"""
        self.values = []


def clamp(value, min_value, max_value):
    """Limita um valor entre min e max"""
    return max(min_value, min(value, max_value))


def map_range(value, in_min, in_max, out_min, out_max):
    """Mapeia um valor de um range para outro"""
    return (value - in_min) * (out_max - out_min) / (in_max - in_min) + out_min


def distance_to_percentage(distance, max_distance=400):
    """Converte distância em porcentagem (100% = muito longe, 0% = muito perto)"""
    return clamp(100 * (distance / max_distance), 0, 100)


def retry_on_error(max_retries=3, delay=0.5):
    """Decorador para tentar novamente em caso de erro"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    if attempt == max_retries - 1:
                        raise
                    print(f"Erro em {func.__name__}, tentativa {attempt + 1}/{max_retries}: {e}")
                    time.sleep(delay)
        return wrapper
    return decorator


class PerformanceMonitor:
    """Monitor de performance para identificar gargalos"""
    
    def __init__(self):
        self.measurements = {}
    
    def measure(self, name):
        """Retorna um context manager para medir tempo"""
        return self._Measurement(self, name)
    
    class _Measurement:
        def __init__(self, monitor, name):
            self.monitor = monitor
            self.name = name
            self.start_time = None
        
        def __enter__(self):
            self.start_time = time.time()
            return self
        
        def __exit__(self, *args):
            elapsed = (time.time() - self.start_time) * 1000
            if self.name not in self.monitor.measurements:
                self.monitor.measurements[self.name] = []
            self.monitor.measurements[self.name].append(elapsed)
    
    def get_stats(self, name):
        """Retorna estatísticas de uma medição"""
        if name not in self.measurements or not self.measurements[name]:
            return None
        
        values = self.measurements[name]
        return {
            'count': len(values),
            'avg': sum(values) / len(values),
            'min': min(values),
            'max': max(values)
        }
    
    def print_report(self):
        """Imprime relatório de performance"""
        print("\n" + "="*50)
        print("RELATÓRIO DE PERFORMANCE")
        print("="*50)
        
        for name in sorted(self.measurements.keys()):
            stats = self.get_stats(name)
            if stats:
                print(f"\n{name}:")
                print(f"  Chamadas: {stats['count']}")
                print(f"  Média: {stats['avg']:.2f}ms")
                print(f"  Mín: {stats['min']:.2f}ms")
                print(f"  Máx: {stats['max']:.2f}ms")


class StateHistory:
    """Mantém histórico dos estados do robô"""
    
    def __init__(self, max_history=100):
        self.max_history = max_history
        self.history = []
    
    def add(self, state):
        """Adiciona um estado ao histórico"""
        self.history.append({
            'state': state,
            'timestamp': time.time()
        })
        
        if len(self.history) > self.max_history:
            self.history.pop(0)
    
    def get_last(self, n=1):
        """Retorna os últimos n estados"""
        return self.history[-n:] if len(self.history) >= n else self.history
    
    def get_state_duration(self, state):
        """Retorna quanto tempo ficou em um determinado estado"""
        if not self.history:
            return 0
        
        total_time = 0
        last_timestamp = None
        
        for entry in self.history:
            if entry['state'] == state:
                if last_timestamp is not None:
                    total_time += entry['timestamp'] - last_timestamp
                last_timestamp = entry['timestamp']
        
        return total_time
    
    def print_summary(self):
        """Imprime resumo do histórico"""
        if not self.history:
            print("Sem histórico disponível")
            return
        
        states = {}
        for entry in self.history:
            state = entry['state']
            states[state] = states.get(state, 0) + 1
        
        total = len(self.history)
        print("\n" + "="*50)
        print("RESUMO DE ESTADOS")
        print("="*50)
        for state, count in sorted(states.items(), key=lambda x: x[1], reverse=True):
            percentage = (count / total) * 100
            print(f"{state}: {count} vezes ({percentage:.1f}%)")


def format_time(seconds):
    """Formata segundos em formato legível"""
    if seconds < 60:
        return f"{seconds:.1f}s"
    elif seconds < 3600:
        minutes = int(seconds / 60)
        secs = seconds % 60
        return f"{minutes}m {secs:.0f}s"
    else:
        hours = int(seconds / 3600)
        minutes = int((seconds % 3600) / 60)
        return f"{hours}h {minutes}m"


if __name__ == "__main__":
    # Testes das funções utilitárias
    print("Testando utilitários...\n")
    
    # Teste do Timer
    print("1. Teste do Timer:")
    timer = Timer()
    timer.start()
    time.sleep(0.5)
    print(f"   Tempo decorrido: {timer.elapsed():.2f}s")
    
    # Teste da Moving Average
    print("\n2. Teste da Moving Average:")
    avg = MovingAverage(window_size=3)
    values = [10, 15, 20, 25, 30]
    for val in values:
        result = avg.add(val)
        print(f"   Valor: {val}, Média: {result:.2f}")
    
    # Teste do clamp
    print("\n3. Teste do clamp:")
    print(f"   clamp(150, 0, 100) = {clamp(150, 0, 100)}")
    print(f"   clamp(-10, 0, 100) = {clamp(-10, 0, 100)}")
    
    # Teste do map_range
    print("\n4. Teste do map_range:")
    print(f"   map_range(50, 0, 100, 0, 255) = {map_range(50, 0, 100, 0, 255):.0f}")
    
    print("\n✓ Todos os testes concluídos!")