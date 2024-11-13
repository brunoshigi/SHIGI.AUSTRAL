import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional, Dict, Any, List
from functools import wraps
import inspect
import json
import pandas as pd  # pip install pandas
from config import ConfigManager

class AustralLogger:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if not hasattr(self, 'initialized'):
            self.config = ConfigManager()
            self.setup_logger()
            self.initialized = True

    def setup_logger(self) -> None:
        """Configura o sistema de logs"""
        log_path = Path(self.config.get('logs.path'))
        log_path.parent.mkdir(parents=True, exist_ok=True)

        self.logger = logging.getLogger('austral')
        self.logger.setLevel(self.config.get('logs.level', 'INFO'))

        if not self.logger.handlers:
            file_handler = logging.FileHandler(log_path, encoding='utf-8')
            file_formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            file_handler.setFormatter(file_formatter)
            self.logger.addHandler(file_handler)

    def log_action(self, action: str, user: str, details: Optional[Dict] = None) -> None:
        """Registra uma ação no sistema"""
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'action': action,
            'user': user,
            'details': details or {}
        }
        self.logger.info(json.dumps(log_entry, ensure_ascii=False))

    def get_recent_activity(self, days: int = 7) -> List[Dict[str, Any]]:
        """Retorna atividades recentes do sistema"""
        cutoff_date = datetime.now() - timedelta(days=days)
        activities = []
        
        try:
            log_path = Path(self.config.get('logs.path'))
            if log_path.exists():
                with open(log_path, 'r', encoding='utf-8') as f:
                    for line in f:
                        try:
                            timestamp_str = line.split(' - ')[0]
                            timestamp = datetime.strptime(timestamp_str, '%Y-%m-%d %H:%M:%S,%f')
                            if timestamp >= cutoff_date:
                                log_data = json.loads(line.split(' - ')[-1])
                                activities.append({
                                    'timestamp': timestamp,
                                    'user': log_data['user'],
                                    'action': log_data['action'],
                                    'details': log_data['details']
                                })
                        except:
                            continue
        except Exception as e:
            self.logger.error(f"Erro ao ler atividades recentes: {e}")
        
        return sorted(activities, key=lambda x: x['timestamp'], reverse=True)

    def export_activity_report(self, output_file: str, days: int = 30) -> bool:
        """Exporta relatório de atividades para Excel"""
        try:
            activities = self.get_recent_activity(days)
            if activities:
                df = pd.DataFrame(activities)
                df.to_excel(output_file, index=False)
                return True
        except Exception as e:
            self.logger.error(f"Erro ao exportar relatório: {e}")
        return False

def log_action(action: str):
    """Decorador para logging automático de ações"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            instance = args[0] if args and hasattr(args[0], '__class__') else None
            user = getattr(instance, 'username', 'system') if instance else 'system'
            
            sig = inspect.signature(func)
            bound_args = sig.bind(*args, **kwargs)
            bound_args.apply_defaults()
            
            # Remove argumentos sensíveis
            safe_args = {
                k: v for k, v in bound_args.arguments.items() 
                if k not in ['password', 'senha', 'token']
            }
            
            logger = AustralLogger()
            logger.log_action(
                action=action,
                user=user,
                details={
                    'function': func.__name__,
                    'arguments': str(safe_args)
                }
            )
            
            try:
                result = func(*args, **kwargs)
                return result
            except Exception as e:
                logger.logger.error(
                    f"Erro em {action}: {str(e)}",
                    exc_info=True
                )
                raise
            
        return wrapper
    return decorator
