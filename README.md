# 🚀 API Mockup System

## 🎯 O que é e para que serve?

Esta API nasceu para resolver um dos maiores gargalos no desenvolvimento de software moderno: a **dependência entre Front-end e Back-end**.

### 🛑 O Problema

Muitas vezes, a equipe de Front-end precisa criar telas e funcionalidades, mas a API real ainda não está pronta ou é instável. Além disso, é difícil simular cenários de erro específicos (como um "Cartão Bloqueado" ou "Saldo Insuficiente") usando apenas dados reais de teste, pois isso exige manipulação complexa em bancos de produção/homologação.

### ✨ A Solução

O **API Mockup System** funciona como um simulador fidedigno. Ele permite:

1. **Independência Total**: O Front-end pode trabalhar com dados reais simulados antes mesmo do Back-end começar a codar.
2. **Mocks Sob Demanda**: Você cria uma "Regra" (Template) e depois gera "Casos" (Mocks) específicos para cada teste (ex: um CPF que retorna sucesso, outro que retorna erro 404).
3. **Simulação Realista**: Ele se comporta exatamente como uma API real, interceptando rotas e respondendo JSONs baseados em campos de identidade (como CPF, ID ou E-mail).

---

## 🛠️ Tecnologias Utilizadas

* **Python 3.11+**
* **FastAPI**: Framework web de alta performance.
* **MongoDB**: Banco de dados NoSQL para armazenamento dos mocks.
* **JWT (JSON Web Tokens)**: Sistema de autenticação seguro.
* **Docker** (Opcional): Para rodar o banco de dados.

---

## 🏃 Como Rodar o Projeto

1. **Crie e ative o ambiente virtual**:
   ```powershell
   # Cria o ambiente
   python -m venv .venv

   # Ativa no PowerShell
   .\.venv\Scripts\Activate.ps1
   ```
2. **Instale as dependências**:
   ```powershell
   pip install -r requirements.txt
   ```
2. **Configure o `.env`**:
   Crie um arquivo `.env` na raiz seguindo o `.env.example`.
3. **Inicie o Servidor**:
   ```powershell
   python -m app.main
   ```
4. **Acesse a Documentação**:
   Abra `http://localhost:8000/swagger` no seu navegador.

---

## 🔐 1. Autenticação e Segurança (Dashboard)

### 1.1 Criar o primeiro usuário (Admin)

No Swagger, procure a seção **Autenticação**:

1. **Abra o endpoint** `POST /api/v1/auth/register`.
2. **Preencha** seu `username`, `email` e `password`.
3. **Clique em Execute**.

### 1.2 Fazer Login e Autorizar o Swagger (Modo Fácil)

1. **Clique no botão verde Authorize** no topo da página.
2. **Digite o seu username e password**.
3. **Clique em Authorize**.

---

## 🛠 2. Gerenciamento de Templates (As Regras)

O **Template** é a regra principal de uma API.

1.  Acesse `POST /api/v1/register-template`.
2.  Informe o `endpoint` (ex: `v1/usuarios`), `identity_field` (ex: `cpf`) e as tags organizacionais (`tag_squad`).
3.  No Body, defina o `payload_padrao` (o JSON fidedigno que você quer simular).

---

## ✨ 3. Gerando um Mock Customizado (Cenários)

Se você precisa de um dado específico para um teste (ex: um CPF que retorna status BLOQUEADO):

1.  Acesse `POST /api/v1/generate-mock`.
2.  Informe o `endpoint` do template e o `identity_value` (ex: o CPF real).
3.  No campo `modified_fields`, coloque apenas o que você quer sobrescrever do original.

---

## 🔍 4. Pesquisa e Metadados (Para o Front-end)

O sistema oferece dois endpoints principais para gerenciar a informação:

*   **`GET /api/v1/search`**: Pesquisa geral em templates e mocks. Filtra por URL, Endpoint ou **`identity_value`**.
*   **`GET /api/v1/templates-metadata`**: Retorna apenas os dados técnicos dos templates (endpoint, método, campos editáveis). **Ideal para montar formulários dinâmicos no Front-end.**

---

## 🪄 5. Funcionalidades de Autopreenchimento

Se um template tiver os campos abaixo na lista de `campos_editaveis`, mas você **não** os informar ao criar um mock, o sistema os gerará automaticamente:

*   **CPF**: Gera um CPF válido aleatório.
*   **Código de Associado**: Gera um código no formato `XXXXXX`.

---

## 🚀 6. Usando o Simulador (A Chamada Real)

O simulador intercepta qualquer chamada que não seja administrativa. 

*   **Exemplo**: Se você cadastrou o endpoint `v1/busca-cpf`.
*   **Chamada**: `POST http://localhost:8000/v1/busca-cpf`
*   **Identificação**: Envie o campo de identidade no Body do JSON:
    ```json
    { "cpf": "57462" }
    ```
*   O sistema retornará os dados da instância customizada se ela existir, ou o template padrão caso contrário.

---

## 📦 7. Estrutura do Projeto
*   `app/core/domain/models`: Modelos Pydantic (Esquemas de dados).
*   `app/core/use_cases`: Lógica de negócio e serviços.
*   `app/adapters/inbound/controllers`: Pontos de entrada (API/Swagger).
*   `app/adapters/outbound`: Persistência (MongoDB).