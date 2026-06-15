import psycopg2
import os
import time
from dotenv import load_dotenv

# Carrega as variáveis de ambiente do arquivo .env
load_dotenv()

# =========================
# CONFIGURAÇÃO DO BANCO
# =========================

DB_HOST = os.getenv('DB_HOST', 'postgres')  # Nome do serviço no docker-compose
DB_PORT = os.getenv('DB_PORT', '5432')
DB_NAME = os.getenv('POSTGRES_DB')        
DB_USER = os.getenv('POSTGRES_USER')      
DB_PASSWORD = os.getenv('POSTGRES_PASSWORD')  


# =========================
# CONEXÃO PRINCIPAL
# =========================

def conectar(exibir_erro=True):
    try:
        return psycopg2.connect(
            host=DB_HOST,
            port=DB_PORT,
            database=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD
        )
    except psycopg2.Error as erro:
        # Só exibe o erro se não estivermos na fase de espera inicial do Docker
        if exibir_erro:
            print(f"\nErro ao conectar ao banco de dados: {erro}")
        return None


# =========================
# TESTE DE CONEXÃO
# =========================

def testar_conexao():
    conexao = conectar()
    if conexao:
        conexao.close()
        print("Conexão com o banco de dados realizada com sucesso!")
        return True
    return False


# =========================
# ESPERAR BANCO SUBIR (DOCKER)
# =========================

def esperar_banco():
    print("Aguardando o banco de dados inicializar...")

    for tentativa in range(10):
        # Passamos exibir_erro=False para não inundar a tela com mensagens de erro enquanto o banco liga
        conexao = conectar(exibir_erro=False)
        if conexao:
            conexao.close()
            print("\n[OK] Banco de dados disponível e pronto para uso!")
            return True

        print(f"Banco ainda não respondeu. Tentativa {tentativa + 1}/10... Aguardando 3 segundos.")
        time.sleep(3)

    print("\n[ERRO] Não foi possível conectar ao banco de dados após 10 tentativas.")
    return False