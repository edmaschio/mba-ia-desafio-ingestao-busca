# Desafio MBA Engenharia de Software com IA - Full Cycle

Um sistema **RAG (Retrieval-Augmented Generation)** que ingere documentos PDF em um banco de dados vetorial e responde perguntas com base no conteúdo ingerido usando Google Generative AI.

## 🎯 Visão Geral do Projeto

Esta solução implementa um pipeline completo de ingestão de documentos e busca:

- **Ingestão de PDF**: Carrega e divide documentos PDF em partes, gera embeddings e armazena no PostgreSQL
- **Busca Vetorial**: Recupera trechos relevantes do documento usando similaridade semântica
- **RAG Chain**: Combina recuperação com LLM para responder às perguntas com contexto
- **Chat Interativo**: Interface CLI para consultar o sistema

**Stack**: Python 3.x | LangChain | Google Generative AI (Gemini) | PostgreSQL + pgvector | Docker

## 📋 Pré-requisitos

- Python 3.8+
- Docker e Docker Compose
- Chave de API do Google Generative AI ([obtenha aqui](https://ai.google.dev/))
- Um arquivo PDF para ingestão

## 🚀 Início Rápido

### 1. Clonar e Configurar

```bash
# Criar ambiente virtual (recomendado)
python -m venv venv

# Ativar ambiente virtual
# No Windows:
venv\Scripts\activate
# No macOS/Linux:
source venv/bin/activate

# Instalar dependências
pip install -r requirements.txt
```

### 2. Configurar o Ambiente

Crie um arquivo `.env` na raiz do projeto:

```env
# Configuração do Banco de Dados
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/rag
PG_VECTOR_COLLECTION_NAME=documents

# Chaves de API (escolha uma)
GOOGLE_API_KEY=sua_chave_google_aqui
# OPENAI_API_KEY=sua_chave_openai_aqui (alternativa)

# Modelo de Embeddings
GOOGLE_EMBEDDING_MODEL=models/embedding-001

# Caminho para o Documento PDF
PDF_PATH=./data/document.pdf
```

### 3. Iniciar PostgreSQL com Suporte a Vetores

```bash
docker-compose up -d
```

Aguarde até o PostgreSQL ficar saudável (verifique os logs do healthcheck):

```bash
docker-compose logs -f postgres
```

### 4. Ingerir o Documento

Coloque seu arquivo PDF no caminho especificado em `PDF_PATH`, e então execute:

```bash
python src/ingest.py
```

Saída esperada:
```
Added N documents to PGVector collection documents
```

### 5. Iniciar o Chat Interativo

```bash
python src/chat.py
```

Exemplo de interação:
```
Chat iniciado. Digite 'quit', 'exit' ou 'sair' para encerrar.

Faça sua pergunta: What is the main topic of the document?

RESPOSTA: O documento aborda [resposta com base no contexto do PDF]
```

Digite `quit`, `exit` ou `sair` para encerrar o chat.

## 📁 Estrutura do Projeto

```
├── src/
│   ├── ingest.py          # Pipeline de ingestão de PDF
│   ├── search.py          # Lógica da RAG chain e busca
│   └── chat.py            # Interface CLI interativa
├── docker-compose.yml     # Configuração do PostgreSQL + pgvector
├── requirements.txt       # Dependências Python
├── .env                   # Configuração de ambiente (crie localmente)
└── README.md              # Este arquivo
```

## 🔍 Como Funciona

### Fluxo de Ingestão de Documentos

1. **Load**: PyPDFLoader lê o arquivo PDF
2. **Chunk**: RecursiveCharacterTextSplitter divide o documento em blocos de 1000 tokens com sobreposição de 150
3. **Embed**: Gera embeddings usando o modelo do Google
4. **Store**: Salva os blocos e embeddings no PostgreSQL (coleção pgvector)

### Fluxo de Busca e Resposta

1. **Retrieve**: Usa `similarity_search_with_score` para obter os 10 blocos mais semelhantes com pontuações
2. **Format**: Combina os blocos recuperados como contexto
3. **Prompt**: Envia contexto + pergunta para o LLM com instruções rígidas
4. **Response**: O LLM responde APENAS com base no contexto fornecido

### Design de Segurança

O sistema foi projetado para evitar alucinações:
- Os prompts proíbem explicitamente conhecimento externo
- Temperatura do modelo definida como 0 (determinístico)
- Perguntas fora do contexto recebem resposta de rejeição padrão
- Enriquecimento de metadados remove valores vazios/nulos

## 🛠️ Configuração Avançada

### Alternar para Embeddings do OpenAI

Edite `src/ingest.py` e descomente os embeddings do OpenAI (já presente como código comentado):

```python
# embeddings = GoogleGenerativeAIEmbeddings(...)
embeddings = OpenAIEmbeddings(model=os.getenv("OPENAI_MODEL","text-embedding-3-small"))
```

### Ajustar Estratégia de Divisão de Texto

Em `src/ingest.py`, modifique `RecursiveCharacterTextSplitter`:

```python
RecursiveCharacterTextSplitter(
    chunk_size=1500,      # Aumenta para blocos maiores
    chunk_overlap=200,    # Ajusta a sobreposição
    add_start_index=True  # Rastreia posição original
)
```

### Alterar Configurações da Busca Vetorial

Em `src/search.py`, ajuste a configuração da busca:

```python
results = store.similarity_search_with_score(question, k=20)  # Obtém top 20 em vez de 10
```

## ⚠️ Solução de Problemas

| Problema | Solução |
|---------|----------|
| `RuntimeError: Environment variable X is not set` | Verifique se o arquivo `.env` está configurado corretamente com todas as variáveis necessárias |
| `DatabaseError: connection refused` | PostgreSQL não está em execução. Execute `docker-compose up -d` |
| `PDF_PATH does not exist` | Verifique se o caminho do PDF em `.env` existe e está acessível |
| `No splits were created` | O PDF pode estar vazio ou corrompido. Tente outro arquivo PDF |
| `ModuleNotFoundError` | Ative o ambiente virtual e reinstale: `pip install -r requirements.txt` |

## 📚 Dependências Principais

- **langchain**: Framework RAG e orquestração de LLM
- **langchain-google-genai**: Integração com Google Generative AI
- **langchain-postgres**: Backend de armazenamento PGVector
- **pgvector**: Extensão vetorial para PostgreSQL
- **python-dotenv**: Configuração de ambiente

Veja `requirements.txt` para a lista completa de dependências.

## 🔗 Recursos Adicionais

- [Documentação LangChain](https://python.langchain.com/)
- [Documentação Google Generative AI](https://ai.google.dev/)
- [GitHub do pgvector](https://github.com/pgvector/pgvector)
- [Documentação PostgreSQL](https://www.postgresql.org/docs/)

## 📝 Observações

- A ingestão de documentos não é idempotente (executar várias vezes adiciona blocos duplicados)
- Limpe a coleção excluindo e recriando o volume do PostgreSQL: `docker-compose down -v`
- O histórico do chat não é persistido (cada sessão é independente)
- Segurança de chave de API: Nunca comite o arquivo `.env` no controle de versão
- A busca vetorial usa `similarity_search_with_score` para obter pontuações de relevância, permitindo controle fino sobre os resultados