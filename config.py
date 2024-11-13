import json
from pathlib import Path
from typing import Any, Dict, Optional, Union
from datetime import datetime
import shutil
import logging
from dataclasses import dataclass
import os

class ConfigurationError(Exception):
    pass

@dataclass
class DatabaseConfig:
    path: str
    backup_dir: str
    auto_backup: bool = True
    backup_interval_days: int = 1
    max_backups: int = 30

@dataclass
class LogConfig:
    path: str
    level: str = "INFO"
    max_size_mb: int = 10
    backup_count: int = 5

@dataclass
class ThemeConfig:
    name: str = "litera"
    dark_mode: bool = False
    font_size: int = 12

class ConfigManager:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if not hasattr(self, 'initialized'):
            self.logger = logging.getLogger('austral.config')
            self.base_dir = Path.home() / '.austral'
            self.config_file = self.base_dir / 'config.json'
            self.config: Dict[str, Any] = {}
            self._load_default_config()
            self._ensure_directories()
            self.initialized = True

    def _load_default_config(self) -> None:
        self.default_config = {
            'version': '1.0.0',
            'theme': {
                'name': 'litera',
                'dark_mode': False,
                'font_size': 12
            },
            'data_dir': str(Path.home() / 'Documents' / 'Austral'),
            'database': {
                'path': str(self.base_dir / 'austral.db'),
                'backup_dir': str(self.base_dir / 'backups'),
                'auto_backup': True,
                'backup_interval_days': 1,
                'max_backups': 30
            },
            'logs': {
                'path': str(self.base_dir / 'logs' / 'austral.log'),
                'level': 'INFO',
                'max_size_mb': 10,
                'backup_count': 5
            },
            'email': {
                'templates_dir': str(self.base_dir / 'templates'),
                'signature_file': str(self.base_dir / 'signature.txt')
            },
            'security': {
                'session_timeout_minutes': 30,
                'max_login_attempts': 3,
                'password_expiry_days': 90
            },
            'performance': {
                'cache_size_mb': 100,
                'max_concurrent_operations': 5
            },
            'last_values': {
                'email_generator': {},
                'mix_diario': {},
                'etiqueta_clientes': {},
                'etiqueta_transferencia': {}
            }
        }
        self._load_config()

    def _load_config(self) -> None:
        try:
            if self.config_file.exists():
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    loaded_config = json.load(f)
                    self.config = self.default_config.copy()
                    self._validate_and_update_config(loaded_config)
            else:
                self.config = self.default_config.copy()
                self._save_config()
        except Exception as e:
            self.logger.error(f"Erro ao carregar configurações: {e}")
            raise ConfigurationError(f"Erro ao carregar configurações: {e}")

    def _validate_and_update_config(self, new_config: Dict) -> None:
        def update_recursive(base: Dict, updates: Dict) -> None:
            for key, value in updates.items():
                if key in base:
                    if isinstance(base[key], dict) and isinstance(value, dict):
                        update_recursive(base[key], value)
                    else:
                        if type(base[key]) == type(value):
                            base[key] = value
                        else:
                            self.logger.warning(
                                f"Tipo inválido para configuração '{key}': "
                                f"esperado {type(base[key])}, recebido {type(value)}"
                            )

        update_recursive(self.config, new_config)

    def _save_config(self) -> None:
        try:
            self.config_file.parent.mkdir(parents=True, exist_ok=True)
            temp_file = self.config_file.with_suffix('.tmp')
            
            with open(temp_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=4, ensure_ascii=False)
            
            temp_file.replace(self.config_file)
            
        except Exception as e:
            self.logger.error(f"Erro ao salvar configurações: {e}")
            raise ConfigurationError(f"Erro ao salvar configurações: {e}")

    def _ensure_directories(self) -> None:
        try:
            dirs = [
                self.base_dir,
                Path(self.config['data_dir']),
                Path(self.config['database']['backup_dir']),
                Path(self.config['logs']['path']).parent,
                Path(self.config['email']['templates_dir'])
            ]
            
            for directory in dirs:
                directory.mkdir(parents=True, exist_ok=True)
                
        except Exception as e:
            self.logger.error(f"Erro ao criar diretórios: {e}")
            raise ConfigurationError(f"Erro ao criar diretórios: {e}")

    def get(self, key_path: str, default: Any = None) -> Any:
        try:
            value = self.config
            for key in key_path.split('.'):
                value = value[key]
            return value
        except (KeyError, TypeError):
            return default

    def set(self, key_path: str, value: Any, save: bool = True) -> None:
        try:
            keys = key_path.split('.')
            config = self.config
            
            for key in keys[:-1]:
                config = config.setdefault(key, {})
            
            config[keys[-1]] = value
            
            if save:
                self._save_config()
                
        except Exception as e:
            self.logger.error(f"Erro ao definir configuração '{key_path}': {e}")
            raise ConfigurationError(f"Erro ao definir configuração '{key_path}': {e}")

    def backup_config(self) -> None:
        try:
            backup_dir = self.base_dir / 'backups' / 'config'
            backup_dir.mkdir(parents=True, exist_ok=True)
            
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            backup_file = backup_dir / f'config_{timestamp}.json'
            
            shutil.copy2(self.config_file, backup_file)
            
            self._cleanup_old_backups(backup_dir)
            
        except Exception as e:
            self.logger.error(f"Erro ao fazer backup das configurações: {e}")

    def _cleanup_old_backups(self, backup_dir: Path, keep: int = 10) -> None:
        try:
            backups = sorted(backup_dir.glob('*.json'), key=os.path.getmtime)
            for backup in backups[:-keep]:
                backup.unlink()
        except Exception as e:
            self.logger.error(f"Erro ao limpar backups antigos: {e}")

    def reset_to_default(self) -> None:
        try:
            self.config = self.default_config.copy()
            self._save_config()
            self._ensure_directories()
        except Exception as e:
            self.logger.error(f"Erro ao resetar configurações: {e}")
            raise ConfigurationError(f"Erro ao resetar configurações: {e}")

    def validate_database_config(self) -> bool:
        try:
            db_config = DatabaseConfig(**self.config['database'])
            return (
                Path(db_config.path).parent.exists() and
                Path(db_config.backup_dir).exists()
            )
        except Exception:
            return False

    def validate_log_config(self) -> bool:
        try:
            log_config = LogConfig(**self.config['logs'])
            return (
                Path(log_config.path).parent.exists() and
                log_config.level in logging._nameToLevel
            )
        except Exception:
            return False

    def get_database_config(self) -> DatabaseConfig:
        return DatabaseConfig(**self.config['database'])

    def get_log_config(self) -> LogConfig:
        return LogConfig(**self.config['logs'])

    def get_theme_config(self) -> ThemeConfig:
        return ThemeConfig(**self.config['theme'])

    def __str__(self) -> str:
        return json.dumps(self.config, indent=2)

config_manager = ConfigManager()