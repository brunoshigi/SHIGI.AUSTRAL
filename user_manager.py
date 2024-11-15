import sqlite3
import hashlib
import argparse
from config import ConfigManager
from logger import AustralLogger

class UserManager:
    def __init__(self):
        self.config = ConfigManager()
        self.logger = AustralLogger()
        self.db_path = self.config.get('database.path')

    def create_user(self, username: str, password: str, role: str = 'user'):
        """Cria um novo usuário"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Hash da senha
            hashed_password = hashlib.sha256(password.encode()).hexdigest()
            
            cursor.execute('''
                INSERT INTO users (username, password, role)
                VALUES (?, ?, ?)
            ''', (username, hashed_password, role))
            
            conn.commit()
            print(f"Usuário '{username}' criado com sucesso!")
            
        except sqlite3.IntegrityError:
            print(f"ERRO: Usuário '{username}' já existe!")
        except Exception as e:
            print(f"ERRO ao criar usuário: {str(e)}")
        finally:
            conn.close()

    def list_users(self):
        """Lista todos os usuários"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('SELECT username, role, created_at, last_login FROM users')
            users = cursor.fetchall()
            
            print("\nUsuários cadastrados:")
            print("-" * 80)
            print(f"{'Username':<20} {'Role':<10} {'Created At':<20} {'Last Login':<20}")
            print("-" * 80)
            
            for user in users:
                print(f"{user[0]:<20} {user[1]:<10} {user[2]:<20} {user[3] or 'Never':<20}")
                
        except Exception as e:
            print(f"ERRO ao listar usuários: {str(e)}")
        finally:
            conn.close()

    def delete_user(self, username: str):
        """Remove um usuário"""
        if username.lower() == 'admin':
            print("ERRO: Não é permitido remover o usuário admin!")
            return
            
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('DELETE FROM users WHERE username = ?', (username,))
            
            if cursor.rowcount > 0:
                conn.commit()
                print(f"Usuário '{username}' removido com sucesso!")
            else:
                print(f"Usuário '{username}' não encontrado!")
                
        except Exception as e:
            print(f"ERRO ao remover usuário: {str(e)}")
        finally:
            conn.close()

    def change_password(self, username: str, new_password: str):
        """Altera a senha de um usuário"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            hashed_password = hashlib.sha256(new_password.encode()).hexdigest()
            
            cursor.execute('''
                UPDATE users 
                SET password = ? 
                WHERE username = ?
            ''', (hashed_password, username))
            
            if cursor.rowcount > 0:
                conn.commit()
                print(f"Senha do usuário '{username}' alterada com sucesso!")
            else:
                print(f"Usuário '{username}' não encontrado!")
                
        except Exception as e:
            print(f"ERRO ao alterar senha: {str(e)}")
        finally:
            conn.close()

def main():
    parser = argparse.ArgumentParser(description='Gerenciador de Usuários Austral')
    parser.add_argument('action', choices=['create', 'list', 'delete', 'change-password'],
                      help='Ação a ser executada')
    parser.add_argument('--username', help='Nome do usuário')
    parser.add_argument('--password', help='Senha do usuário')
    parser.add_argument('--role', choices=['admin', 'user'], default='user',
                      help='Papel do usuário (admin ou user)')

    args = parser.parse_args()
    manager = UserManager()

    if args.action == 'create':
        if not args.username or not args.password:
            print("ERRO: Username e password são obrigatórios para criar usuário!")
            return
        manager.create_user(args.username, args.password, args.role)
        
    elif args.action == 'list':
        manager.list_users()
        
    elif args.action == 'delete':
        if not args.username:
            print("ERRO: Username é obrigatório para remover usuário!")
            return
        manager.delete_user(args.username)
        
    elif args.action == 'change-password':
        if not args.username or not args.password:
            print("ERRO: Username e password são obrigatórios para alterar senha!")
            return
        manager.change_password(args.username, args.password)

if __name__ == "__main__":
    main()