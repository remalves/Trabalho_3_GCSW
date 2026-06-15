import psycopg2
from datetime import datetime
from conexao import conectar

# =========================
# UTILITÁRIO DE CONEXÃO
# =========================

def get_cursor():
    # 1. Tenta se conectar ao banco de dados
    conexao = conectar()
    
    # 2. Se a conexão falhou (não existe), avisa que deu erro devolvendo valores vazios
    if not conexao:
        return None, None
        
    # 3. Se deu certo, cria o objeto que executa os comandos SQL
    gerenciador_de_comandos = conexao.cursor()
    
    # 4. Devolve a conexão e o gerenciador prontos para uso
    return conexao, gerenciador_de_comandos

# ==================== GERENCIAMENTO DE CLIENTES ====================

def listar_todos_clientes():
    try:
        conexao, comando = get_cursor()
        if not conexao:
            return

        # Busca todos os CPFs para sabermos quem listar
        comando.execute("SELECT cpf FROM clientes ORDER BY cpf")
        lista_de_cpfs = comando.fetchall()

        if not lista_de_cpfs:
            print("\nNão há clientes cadastrados!")
            return

        # Para cada CPF encontrado, busca os dados completos
        for (cpf_atual,) in lista_de_cpfs:
            comando.execute("""
                SELECT nome, data_nascimento, sexo, salario
                FROM clientes WHERE cpf = %s
            """, (cpf_atual,))
            dados_pessoais = comando.fetchone()

            # CORREÇÃO: Busca e isola os e-mails corretamente
            comando.execute("SELECT email FROM cliente_emails WHERE cpf = %s ORDER BY email", (cpf_atual,))
            lista_emails = ", ".join([linha[0] for linha in comando.fetchall()])

            # CORREÇÃO CRUCIAL: Busca e isola todos os telefones de forma limpa
            comando.execute("SELECT telefone FROM cliente_telefones WHERE cpf = %s ORDER BY telefone", (cpf_atual,))
            lista_telefones = ", ".join([linha[0] for linha in comando.fetchall()])

            # Formata a data de nascimento vinda do banco de dados para o padrão PT-BR (dd/mm/aaaa)
            data_nasc = dados_pessoais[1]
            data_nasc_formatada = data_nasc.strftime("%d/%m/%Y") if hasattr(data_nasc, 'strftime') else data_nasc

            # Mostra os dados organizados na tela
            print(f"\nCPF: {cpf_atual}")
            print(f"Nome: {dados_pessoais[0]}")
            print(f"Nascimento: {data_nasc_formatada}")
            print(f"Sexo: {dados_pessoais[2]}")
            print(f"Salário: R$ {dados_pessoais[3]:.2f}")
            print(f"E-mails: {lista_emails if lista_emails else 'Nenhum'}")
            print(f"Telefones: {lista_telefones if lista_telefones else 'Nenhum'}")
            print("-" * 40)

        conexao.close()

    except Exception as erro:
        print(f"Erro ao listar clientes: {erro}")

def incluir_cliente(cpf):
    conexao = None
    try:
        conexao, comando = get_cursor()
        if not conexao:
            return False

        # 1. CAPTURA DOS DADOS PRINCIPAIS
        nome = input("Nome do cliente: ").strip()
        
        # --- TRATAMENTO DA DATA DE NASCIMENTO ---
        data_texto = input("Data de Nascimento (dd/mm/aaaa): ").strip()
        try:
            data_objeto = datetime.strptime(data_texto, "%d/%m/%Y").date()
        except ValueError:
            print("\n[ERRO] Formato de data inválido! Use o padrão dd/mm/aaaa (Ex: 23/01/1981).")
            return False
        # ----------------------------------------

        sexo = input("Sexo (M/F): ").strip().upper()
        salario = float(input("Salário: R$ ").strip())

        # Insere o cliente na tabela principal
        comando.execute("""
            INSERT INTO clientes (cpf, nome, data_nascimento, sexo, salario)
            VALUES (%s, %s, %s, %s, %s)
        """, (cpf, nome, data_objeto, sexo, salario))

        # 2. CAPTURA DE TELEFONES (Pode adicionar vários)
        print("\n--- Cadastro de Telefones ---")
        while True:
            telefone = input("Digite um telefone (ou pressione Enter para pular/encerrar): ").strip()
            if not telefone:
                break  # Se o usuário só apertar Enter, sai do loop de telefones
            
            comando.execute("""
                INSERT INTO cliente_telefones (cpf, telefone)
                VALUES (%s, %s)
            """, (cpf, telefone))
            print(f"Telefone {telefone} adicionado!")

        # 3. CAPTURA DE E-MAILS (Pode adicionar vários)
        print("\n--- Cadastro de E-mails ---")
        while True:
            email = input("Digite um e-mail (ou pressione Enter para pular/encerrar): ").strip()
            if not email:
                break  # Se o usuário só apertar Enter, sai do loop de e-mails
            
            comando.execute("""
                INSERT INTO cliente_emails (cpf, email)
                VALUES (%s, %s)
            """, (cpf, email))
            print(f"E-mail {email} adicionado!")

        # Salva todas as inserções de uma vez só no banco de dados
        conexao.commit()
        print(f"\n[OK] Cliente '{nome}' e seus contatos foram salvos com sucesso!")
        return True

    except Exception as erro:
        if conexao:
            conexao.rollback()
        print(f"Erro ao incluir cliente: {erro}")
        return False
    finally:
        if conexao:
            conexao.close()


def excluir_cliente(cpf):
    conexao = None
    try:
        conexao, comando = get_cursor()
        if not conexao:
            return

        # Verifica se o cliente realmente existe antes de tentar deletar
        comando.execute("SELECT cpf FROM clientes WHERE cpf = %s", (cpf,))
        if not comando.fetchone():
            print("Cliente não encontrado!")
            return

        # Deleta o cliente
        comando.execute("DELETE FROM clientes WHERE cpf = %s", (cpf,))
        conexao.commit()
        print("Cliente e todos os seus contatos foram excluídos!")

    except Exception as erro:
        if conexao:
            conexao.rollback()
        print(f"Erro ao excluir cliente: {erro}")

    finally:
        if conexao:
            conexao.close()

# ==================== GERENCIAMENTO DE PRODUTOS ====================

def listar_todos_produtos():
    try:
        # Abre a conexão usando o padrão unificado
        conexao, comando = get_cursor()
        if not conexao:
            return

        # Busca todos os produtos cadastrados
        comando.execute("SELECT codigo, descricao, peso, preco, desconto, data_validade, estoque FROM produtos ORDER BY codigo")
        lista_de_produtos = comando.fetchall()

        # Mensagem caso a tabela esteja vazia
        if not lista_de_produtos:
            print("\nNão há produtos cadastrados no sistema!")
            return

        print("\n--- LISTA DE PRODUTOS ---")
        for produto in lista_de_produtos:
            codigo, descricao, peso, preco, desconto, data_validade, estoque = produto
            print(f"Código: {codigo}")
            print(f"Descrição: {descricao}")
            print(f"Peso: {peso}kg")
            print(f"Preço: R$ {preco:.2f}")
            print(f"Desconto: {desconto}%")
            print(f"Validade: {data_validade}")
            print(f"Estoque: {estoque} unidades")
            print("-" * 30)

        conexao.close()

    except Exception as erro:
        print(f"Erro ao listar produtos: {erro}")


def incluir_produto(codigo):
    conexao = None
    try:
        conexao, comando = get_cursor()
        if not conexao:
            return False

        # Verifica se o código informado já existe no banco
        comando.execute("SELECT codigo FROM produtos WHERE codigo = %s", (int(codigo),))
        if comando.fetchone():
            print(f"\nErro: O produto com código {codigo} já está cadastrado!")
            return False

        # Coleta os dados do novo produto pelo terminal
        descricao = input("Descrição do produto: ")
        peso = float(input("Peso (em kg): ").replace(",", "."))
        preco = float(input("Preço: R$ ").replace(",", "."))
        desconto = float(input("Desconto (em %): ").replace(",", "."))
        data_validade = input("Data de Validade (aaaa-mm-dd): ")
        estoque = int(input("Quantidade inicial em Estoque: "))

        # Insere especificando as colunas certas do init.sql
        comando.execute("""
            INSERT INTO produtos (codigo, descricao, peso, preco, desconto, data_validade, estoque)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (int(codigo), descricao, peso, preco, desconto, data_validade, estoque))

        conexao.commit()
        print(f"\nProduto '{descricao}' cadastrado com sucesso!")
        return True

    except Exception as erro:
        if conexao:
            conexao.rollback()
        print(f"Erro ao incluir produto: {erro}")
        return False

    finally:
        if conexao:
            conexao.close()


def excluir_produto(codigo):
    conexao = None
    try:
        conexao, comando = get_cursor()
        if not conexao:
            return

        # Verifica se o produto realmente existe antes de tentar deletar
        comando.execute("SELECT codigo, descricao FROM produtos WHERE codigo = %s", (int(codigo),))
        produto_encontrado = comando.fetchone()

        if not produto_encontrado:
            print(f"\nErro: Nenhum produto encontrado com o código {codigo}!")
            return

        # Deleta o produto se ele existir
        comando.execute("DELETE FROM produtos WHERE codigo = %s", (int(codigo),))
        conexao.commit()
        print(f"\nProduto '{produto_encontrado[1]}' (Código {codigo}) excluído com sucesso!")

    except Exception as erro:
        if conexao:
            conexao.rollback()
        print(f"Erro ao excluir produto: {erro}")

    finally:
        if conexao:
            conexao.close()

# ==================== GERENCIAMENTO DE VENDAS ====================

def registrar_compra(cpf, codigo):
    conexao = None
    try:
        conexao, comando = get_cursor()
        if not conexao:
            return False

        # 1. VERIFICAÇÃO: O cliente existe?
        comando.execute("SELECT nome FROM clientes WHERE cpf = %s", (cpf,))
        cliente_encontrado = comando.fetchone()
        if not cliente_encontrado:
            print(f"\nErro: Nenhum cliente cadastrado com o CPF '{cpf}'!")
            return False

        # 2. VERIFICAÇÃO: O produto existe e qual o preço/estoque atual?
        comando.execute("SELECT descricao, preco, estoque FROM produtos WHERE codigo = %s", (int(codigo),))
        produto_encontrado = comando.fetchone()

        if not produto_encontrado:
            print(f"\nErro: O produto com código {codigo} não existe!")
            return False

        descricao_produto, preco_unitario, estoque_atual = produto_encontrado

        # Solicita a quantidade desejada
        quantidade = int(input(f"Quantidade de '{descricao_produto}' (Estoque atual: {estoque_atual}): "))

        if quantidade <= 0:
            print("\nErro: A quantidade deve ser maior que zero!")
            return False

        # 3. VERIFICAÇÃO: Tem estoque suficiente?
        if quantidade > estoque_atual:
            print(f"\nErro: Estoque insuficiente! Você tentou vender {quantidade}, mas só existem {estoque_atual} em estoque.")
            return False

        # Calcula o valor final da venda
        valor_total = preco_unitario * quantidade

        # 4. AÇÃO: Insere o registro na tabela de vendas
        comando.execute("""
            INSERT INTO vendas (cpf_cliente, codigo_produto, quantidade, valor_total)
            VALUES (%s, %s, %s, %s)
        """, (cpf, int(codigo), quantidade, valor_total))

        # 5. AÇÃO: Atualiza (diminui) o estoque do produto vendido
        comando.execute("""
            UPDATE produtos SET estoque = estoque - %s WHERE codigo = %s
        """, (quantidade, int(codigo)))

        # Salva as duas ações juntas no banco de dados
        conexao.commit()
        print(f"\nVenda realizada com sucesso!")
        print(f"Cliente: {cliente_encontrado[0]} | Produto: {descricao_produto}")
        print(f"Quantidade: {quantidade} | Total: R$ {valor_total:.2f}")
        return True

    except Exception as erro:
        # Se falhar no insert ou no update, desfaz tudo para não bagunçar o estoque
        if conexao:
            conexao.rollback()
        print(f"Erro ao registrar venda: {erro}")
        return False
    finally:
        if conexao:
            conexao.close()

def listar_todas_compras():
    try:
        conexao, comando = get_cursor()
        if not conexao:
            return

        # Busca todas as vendas trazendo os nomes e descrições relacionados de forma organizada
        comando.execute("""
            SELECT v.id, c.nome, p.descricao, v.quantidade, v.data_venda, v.valor_total 
            FROM vendas v
            JOIN clientes c ON v.cpf_cliente = c.cpf
            JOIN produtos p ON v.codigo_produto = p.codigo
            ORDER BY v.id
        """)
        lista_de_vendas = comando.fetchall()
        
        # Mensagem caso não existam vendas no banco
        if not lista_de_vendas:
            print("\nNenhuma venda foi registrada no sistema até o momento!")
            return

        print("\n--- HISTÓRICO DE VENDAS REGISTRADAS ---")
        for venda in lista_de_vendas:
            id_venda, nome_cliente, descricao_prod, qtd, data, total = venda
            # Formata a data para exibir bonito na tela (se ela vier como objeto do banco)
            data_formatada = data.strftime("%d/%m/%Y %H:%M:%S") if hasattr(data, 'strftime') else data
            
            print(f"ID da Venda: {id_venda}")
            print(f"Cliente: {nome_cliente}")
            print(f"Produto: {descricao_prod} (Qtd: {qtd})")
            print(f"Data/Hora: {data_formatada}")
            print(f"Valor Total: R$ {total:.2f}")
            print("-" * 40)

        conexao.close()
    except Exception as erro:
        print(f"Erro ao listar vendas: {erro}")

# ==================== SUBMENUS DE NAVEGAÇÃO ====================

def submenu_clientes():
    while True:
        print("\n--- MENU: GERENCIAR CLIENTES ---")
        print("1. Listar todos os clientes")
        print("2. Incluir novo cliente")
        print("3. Excluir um cliente")
        print("4. Voltar ao Menu Principal")
        
        opcao = input("Escolha uma opção: ").strip()

        if opcao == "1":
            listar_todos_clientes()
        elif opcao == "2":
            cpf_informado = input("Digite o CPF do cliente: ")
            incluir_cliente(cpf_informado)
        elif opcao == "3":
            cpf_informado = input("Digite o CPF do cliente que deseja excluir: ")
            excluir_cliente(cpf_informado)
        elif opcao == "4":
            print("\nVoltando ao menu principal...")
            break
        else:
            print("\nOpção inválida! Por favor, escolha um número de 1 a 4.")


def submenu_produtos():
    while True:
        print("\n--- MENU: GERENCIAR PRODUTOS ---")
        print("1. Listar todos os produtos")
        print("2. Incluir novo produto")
        print("3. Excluir um produto")
        print("4. Voltar ao Menu Principal")
        
        opcao = input("Escolha uma opção: ").strip()

        if opcao == "1":
            listar_todos_produtos()
        elif opcao == "2":
            codigo_informado = input("Digite o Código do novo produto: ")
            incluir_produto(codigo_informado)
        elif opcao == "3":
            codigo_informado = input("Digite o Código do produto que deseja excluir: ")
            excluir_produto(codigo_informado)
        elif opcao == "4":
            print("\nVoltando ao menu principal...")
            break
        else:
            print("\nOpção inválida! Por favor, escolha um número de 1 a 4.")


def submenu_compra_venda():
    while True:
        print("\n--- MENU: OPERAÇÕES DE VENDAS ---")
        print("1. Registrar uma nova venda")
        print("2. Listar histórico de vendas")
        print("3. Voltar ao Menu Principal")
        
        opcao = input("Escolha uma opção: ").strip()

        if opcao == "1":
            cpf_cliente = input("Digite o CPF do cliente comprador: ")
            codigo_produto = input("Digite o Código do produto vendido: ")
            registrar_compra(cpf_cliente, codigo_produto)
        elif opcao == "2":
            listar_todas_compras()
        elif opcao == "3":
            print("\nVoltando ao menu principal...")
            break
        else:
            print("\nOpção inválida! Por favor, escolha um número de 1 a 3.")

# ==================== FUNÇÕES DE RELATÓRIOS ====================

def relatorio_clientes_por_telefones():
    try:
        conexao, comando = get_cursor()
        if not conexao:
            return

        print("\n--- Relatório: Clientes por Quantidade de Telefones ---")
        
        # Captura e valida a quantidade mínima informada pelo usuário
        try:
            min_telefones = int(input("Digite a quantidade mínima de telefones: ").strip())
        except ValueError:
            print("\n[ERRO] Por favor, digite um número inteiro válido.")
            return

        # QUERY CORRIGIDA: Agrupa por cliente e conta quantos telefones reais ele possui
        comando.execute("""
            SELECT c.cpf, c.nome, COUNT(t.telefone) AS qtd_telefones
            FROM clientes c
            INNER JOIN cliente_telefones t ON c.cpf = t.cpf
            GROUP BY c.cpf, c.nome
            HAVING COUNT(t.telefone) >= %s
            ORDER BY qtd_telefones DESC, c.nome
        """, (min_telefones,))
        
        clientes_encontrados = comando.fetchall()

        if not clientes_encontrados:
            print(f"\nNenhum cliente encontrado com {min_telefones} ou mais telefones.")
            conexao.close()
            return

        print(f"\nClientes encontrados com pelo menos {min_telefones} telefone(s):")
        print("=" * 60)
        
        # Exibe os clientes filtrados de forma organizada
        for cpf, nome, qtd in clientes_encontrados:
            # Busca os telefones específicos desse cliente para listar na tela
            comando.execute("SELECT telefone FROM cliente_telefones WHERE cpf = %s", (cpf,))
            # Correção na leitura dos telefones para evitar listas duplicadas
            telefones_lista = [linha[0] for linha in comando.fetchall()]
            telefones_texto = ", ".join(telefones_lista)

            print(f"CPF: {cpf}")
            print(f"Nome: {nome}")
            print(f"Quantidade de Telefones: {qtd}")
            print(f"Telefone(s): {telefones_texto}")
            print("-" * 60)

        conexao.close()
        
    except Exception as erro:
        print(f"\nErro ao gerar relatório de telefones: {erro}")


def relatorio_produtos_vencidos():
    """Gera relatório de produtos com validade vencida direto pelo banco"""
    try:
        conexao, comando = get_cursor()
        if not conexao:
            return
        
        # O banco de dados já faz o filtro trazendo apenas o que venceu antes de hoje (CURRENT_DATE)
        comando.execute("""
            SELECT codigo, descricao, peso, preco, desconto, data_validade 
            FROM produtos 
            WHERE data_validade < CURRENT_DATE
            ORDER BY data_validade
        """)
        lista_de_vencidos = comando.fetchall()
        
        print('\n--- RELATÓRIO: Produtos com validade vencida ---')
        
        if not lista_de_vencidos:
            print('Excelente! Nenhum produto vencido encontrado no estoque.')
            conexao.close()
            return
            
        for codigo, descricao, peso, preco, desconto, data_validade in lista_de_vencidos:
            # Formata a data de validade para exibir bonito (dd/mm/aaaa)
            validade_formatada = data_validade.strftime("%d/%m/%Y") if hasattr(data_validade, 'strftime') else data_validade
            
            print(f'Código: {codigo}')
            print(f'Descrição: {descricao}')
            print(f'Preço original: R$ {preco:.2f}')
            print(f'Desconto aplicado: {desconto}%')
            print(f'Data de Vencimento: {validade_formatada}')
            print('-' * 40)
        
        conexao.close()
    except Exception as erro:
        print(f"Erro ao gerar relatório de produtos vencidos: {erro}")


def relatorio_vendas_periodo():
    """Gera relatório de vendas em um período específico"""
    try:
        conexao, comando = get_cursor()
        if not conexao:
            return
        
        data_inicio = input('Data inicial (aaaa-mm-dd): ').strip()
        data_fim = input('Data final (aaaa-mm-dd): ').strip()
        
        # Filtra as vendas agrupando no período selecionado
        comando.execute("""
            SELECT v.id, c.nome, p.descricao, v.quantidade, v.data_venda, v.valor_total
            FROM vendas v
            JOIN clientes c ON v.cpf_cliente = c.cpf
            JOIN produtos p ON v.codigo_produto = p.codigo
            WHERE v.data_venda::DATE >= %s AND v.data_venda::DATE <= %s
            ORDER BY v.data_venda
        """, (data_inicio, data_fim))
        
        lista_de_vendas = comando.fetchall()
        
        if not lista_de_vendas:
            print(f"\nNenhuma venda encontrada entre as datas {data_inicio} e {data_fim}.")
            conexao.close()
            return
        
        print(f'\n--- RELATÓRIO: Vendas de {data_inicio} até {data_fim} ---')
        faturamento_total = 0
        
        for id_venda, nome_cliente, descricao_produto, qtd, data_venda, valor_total in lista_de_vendas:
            # Formata a data e hora da venda para o padrão brasileiro
            data_formatada = data_venda.strftime("%d/%m/%Y %H:%M:%S") if hasattr(data_venda, 'strftime') else data_venda
            
            print(f'ID da Venda: {id_venda}')
            print(f'Cliente: {nome_cliente}')
            print(f'Produto: {descricao_produto} (Qtd: {qtd})')
            print(f'Data/Hora: {data_formatada}')
            print(f'Valor Total da Venda: R$ {valor_total:.2f}')
            print('-' * 40)
            faturamento_total += valor_total
        
        print(f'\nFATURAMENTO TOTAL NO PERÍODO: R$ {faturamento_total:.2f}')
        conexao.close()
    except Exception as erro:
        print(f"Erro ao gerar relatório de vendas: {erro}")


def submenu_relatorios():
    """Submenu para gerenciamento e escolha de relatórios"""
    while True:
        print("\n--- MENU: RELATÓRIOS DO SISTEMA ---")
        print("1. Clientes com X ou mais telefones")
        print("2. Verificar produtos vencidos")
        print("3. Faturamento de vendas por período")
        print("4. Voltar ao Menu Principal")
        
        opcao = input("Escolha uma opção: ").strip()
        
        if opcao == "1":
            relatorio_clientes_por_telefones()
        elif opcao == "2":
            relatorio_produtos_vencidos()
        elif opcao == "3":
            relatorio_vendas_periodo()
        elif opcao == "4":
            print("\nVoltando ao menu principal...")
            break
        else:
            print('\nOpção inválida! Por favor, escolha um número de 1 a 4.')
