# Guia de Configuração — ferias

> **Artefato RUP:** Guia de Configuração (Implementação)
> **Proprietário:** [RUP] Desenvolvedor
> **Status:** Completo
> **Última atualização:** 2026-07-18

---

## 1. Banco de Dados

| Parâmetro | Valor |
|-----------|-------|
| Engine | SQLite 3 |
| Arquivo | `ferias.db` (raiz do projeto) |
| URL | `sqlite:///./ferias.db` |
| Criação | Automática via `create_tables()` no lifespan |

Nenhuma configuração externa necessária — o banco é criado na primeira execução.

## 2. Execução

```bash
# Criar virtualenv e instalar dependências
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Rodar a aplicação
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Acesse:
- API docs (Swagger): http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc
- Healthcheck: http://localhost:8000/health

## 3. CORS

Configurado para aceitar todas as origens (`allow_origins=["*"]`), conforme NFR-08 (sem autenticação, app local).

## 4. Variáveis de Ambiente

Nenhuma variável de ambiente é necessária. Toda configuração está hardcoded para simplicidade (NFR-05, BR-015).
