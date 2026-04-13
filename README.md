# 🏖️ Férias da Tribo

Sistema de gestão de férias para dar visibilidade das agendas de férias do time.

## Funcionalidades

- Cadastro de times e pessoas
- Cadastro de férias com validação de datas e sobreposição
- Agenda com filtro por time e toggle de férias passadas
- Destaque visual de sobreposições de férias no mesmo time

## Quick Start (local)

```bash
# Com SQLite (zero config)
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
# → http://localhost:8000
```

## Docker Compose (local com PostgreSQL)

```bash
docker compose up --build
# → http://localhost:8000
```

## Deploy (K8s PicPay)

### Pré-requisitos
- Namespace `feriasdatribo` criado no cluster
- PostgreSQL disponível (RDS ou Aurora)
- Secret com a connection string

### Passos

```bash
# 1. Criar o secret com a URL do banco
kubectl create secret generic ferias-da-tribo-db \
  --namespace=feriasdatribo \
  --from-literal=url='postgresql://USER:PASS@HOST:5432/ferias_db'

# 2. Build e push da imagem
docker build -t registry.picpay.com/ferias-da-tribo:latest .
docker push registry.picpay.com/ferias-da-tribo:latest

# 3. Aplicar manifests
kubectl apply -f k8s/deployment.yaml
```

O app cria as tabelas automaticamente no startup (SQLAlchemy `create_all`).

## Variáveis de Ambiente

| Variável | Default | Descrição |
|----------|---------|-----------|
| `DATABASE_URL` | `sqlite:///ferias.db` | Connection string do banco |
| `HOST` | `127.0.0.1` | Host do servidor |
| `PORT` | `8000` | Porta do servidor |
| `LOG_LEVEL` | `INFO` | Nível de log |

## Testes

```bash
pytest -v          # Roda todos (usa SQLite in-memory)
pytest --cov=app   # Com cobertura
```

## Stack

- **Backend:** Python 3.12 + FastAPI + SQLAlchemy
- **Frontend:** HTML + CSS + JavaScript (vanilla, zero CDN)
- **Banco:** PostgreSQL (prod) / SQLite (dev)
- **Infra:** Docker + K8s

## Estrutura

```
ferias/
├── app/
│   ├── main.py              ← Entry point FastAPI
│   ├── database.py          ← Engine, sessão, Base
│   ├── config.py            ← Variáveis de ambiente
│   ├── models/              ← SQLAlchemy models
│   ├── schemas/             ← Pydantic schemas
│   ├── services/            ← Lógica de negócio
│   ├── routers/             ← Endpoints REST (/api/v1/*)
│   ├── routes/              ← Páginas HTML
│   ├── templates/           ← Jinja2 (index.html)
│   └── static/              ← CSS + JS
├── tests/                   ← 25 testes
├── k8s/                     ← Manifests Kubernetes
├── spec/                    ← Documentação SDD (24 artefatos)
├── Dockerfile
├── docker-compose.yaml
└── requirements.txt
```
