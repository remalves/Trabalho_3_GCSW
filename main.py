import time
# Importamos a função de esperar o banco diretamente do conexao.py para não repetir código
from conexao import esperar_banco
from funcoes import (
    submenu_clientes,
    submenu_compra_venda,
    submenu_produtos,
    submenu_relatorios,
)


def main():
    # 1. Aguarda o banco de dados inicializar de forma segura no Docker
    # função já está pronta e configurada em conexao.py
    if not esperar_banco():
        print("\n[ERRO] O banco de dados não respondeu a tempo. Encerrando o sistema.")
        return

    print("\n====================================")
    print("   SISTEMA INICIADO COM SUCESSO!    ")
    print("====================================")

    # 2. Loop principal do sistema
    while True:
        print("\n========== MENU PRINCIPAL ==========")
        print("1. Gerenciar Clientes")
        print("2. Gerenciar Produtos")
        print("3. Operações de Compra/Venda")
        print("4. Relatórios do Sistema")
        print("5. Sair")
        print("====================================")

        # Captura a opção digitada e remove espaços vazios nas pontas
        opcao = input("Escolha uma opção: ").strip()

        # Direcionamento dos submenus
        if opcao == "1":
            submenu_clientes()

        elif opcao == "2":
            submenu_produtos()

        elif opcao == "3":
            submenu_compra_venda()

        elif opcao == "4":
            submenu_relatorios()

        elif opcao == "5":
            print("\nObrigado por utilizar o sistema! Encerrando...")
            break  # Quebra o loop while e finaliza o programa de forma limpa

        else:
            print("\nOpção inválida! Por favor, escolha um número de 1 a 5.")


# Ponto de entrada do programa
if __name__ == "__main__":
    main()