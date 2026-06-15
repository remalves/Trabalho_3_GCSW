CREATE TABLE clientes (
    cpf VARCHAR(14) PRIMARY KEY,
    nome VARCHAR(100) NOT NULL,
    data_nascimento DATE NOT NULL,
    sexo CHAR(1),
    salario NUMERIC(10,2)
);

CREATE TABLE cliente_emails (
    id SERIAL PRIMARY KEY,
    cpf VARCHAR(14)
        REFERENCES clientes(cpf)
        ON DELETE CASCADE,
    email VARCHAR(100)
);

CREATE TABLE cliente_telefones (
    id SERIAL PRIMARY KEY,
    cpf VARCHAR(14)
        REFERENCES clientes(cpf)
        ON DELETE CASCADE,
    telefone VARCHAR(20)
);

CREATE TABLE produtos (
    codigo SERIAL PRIMARY KEY,
    descricao VARCHAR(200),
    peso NUMERIC(10,2),
    preco NUMERIC(10,2),
    desconto NUMERIC(5,2),
    data_validade DATE,
    estoque INTEGER DEFAULT 0
);

CREATE TABLE vendas (
    id SERIAL PRIMARY KEY,
    cpf_cliente VARCHAR(14)
        REFERENCES clientes(cpf),
    codigo_produto INTEGER
        REFERENCES produtos(codigo),
    quantidade INTEGER NOT NULL,
    data_venda TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    valor_total NUMERIC(10,2)
);