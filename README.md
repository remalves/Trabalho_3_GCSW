# Trabalho Prático: Sistema de vendas e cadastro de clientes utilizando Docker Compose

Este é um projeto de sistema de vendas e cadastro de clientes que funciona totalmente dentro do Docker. Ele foi feito para ser fácil de rodar em qualquer computador, sem precisar instalar banco de dados ou o Python na sua máquina física.

---
## Checklist de Requisitos Atendidos (O que foi feito)
Para garantir que o projeto seguiu exatamente o passo a passo solicitado pelo professor, aqui está o resumo do que foi implementado:

[✔] Infraestrutura com 3 Serviços Distintos:

    - O Sistema (Python): Programa próprio que roda o menu e valida os dados na tela.

    - O Banco de Dados (PostgreSQL): Responsável por salvar os dados de verdade.

    - O Adminer (Visualizador): Interface gráfica de internet para gerenciar o banco com o mouse.

[✔] Orquestração com Docker Compose: Todos os serviços são iniciados, parados e conectados de forma unificada por um único arquivo de configuração.

[✔] Sincronismo Inteligente (Healthcheck): O sistema em Python foi configurado para esperar o Banco de Dados estar 100% pronto e "saudável" antes de abrir, evitando erros de conexão travada.

[✔] Uso de Variáveis de Ambiente (.env): Nenhuma senha ou credencial do banco ficou exposta direto no código. Tudo é puxado de forma segura e isolada.

[✔] Persistência com Volumes Docker: Configuração de um volume para o banco de dados (os dados dos clientes não somem ao desligar) e de espelhamento para o código Python (atualizações no código entram na hora).

---
## 🚀 Como Executar o Projeto

### 1. Baixar o Projeto
Abra o seu terminal na pasta onde quer salvar e baixe os arquivos:

```bash
git clone <https://github.com/remalves/Trabalho_3_GCSW.git>
```

### 2. Ligar as Máquinas (Docker)
Com o Docker aberto no seu computador, digite o comando abaixo para ligar o banco de dados, o visualizador e o sistema de uma vez só:

```bash
docker compose up -d
```

### 3. Abrir o Menu do Sistema

Para mexer no menu de cadastros, vendas e relatórios pelo seu terminal, digite:

```bash
docker attach sistema_vendas
```
Caso o menu de opções não aparecer, aperte ENTER.

### 4. Abrir o Visualizador do Banco (Adminer)
Se quiser ver os clientes aparecendo no banco de dados pelo navegador de internet:

- Abra o seu navegador e entre no endereço: http://localhost:8080

- Na tela de login, escolha PostgreSQL no primeiro campo.

- No campo Servidor, digite apenas: postgres

- Nos campos de Usuário, Senha e Banco, use as mesmas informações que estão salvas no arquivo .env do projeto.



## ⚠️ AVISO IMPORTANTE SOBRE O ADMINER
O Adminer serve para você olhar, adicionar, editar ou apagar dados (como mudar o nome de um cliente ou o valor de um salário). Isso funciona perfeitamente e atualiza em tempo real no sistema!

O que NÃO fazer: Não apague tabelas e não mude o nome das colunas (como mudar data_nascimento para apenas nascimento). Se você alterar a estrutura das tabelas por lá, o código do programa em Python vai se perder e o sistema vai dar erro na tela.

---
## 🛑 Como Desligar Tudo

Quando terminar de usar e quiser desligar os serviços com segurança sem gastar memória do computador, digite:

```bash
docker compose down
```

