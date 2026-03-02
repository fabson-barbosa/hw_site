# CLAUDE.md — hw-cotacao-brasil

## Visão Geral

**hw-cotacao-brasil** é um site de catálogo e cotação de carrinhos Hot Wheels para o mercado brasileiro. Ele foi inspirado na interface e funcionalidades da LigaPokémon.

### Módulos Principais

```
hw_site/
├── api/          # Backend FastAPI + SQLite
├── scraper/      # Scraper do Fandom Hot Wheels Wiki
├── web/          # Frontend React
├── tests/        # Testes pytest para a API
└── .github/      # Workflows do GitHub Actions
```

---

## Arquitetura

```
Fandom Wiki (scraper) → SQLite (database) → FastAPI (api) → React (web)
```

### Fluxo de Dados

1. **Scraper** (`scraper/hotwheels_scraper.py`) extrai dados de carrinhos mainline do Fandom Hot Wheels Wiki.
2. Os dados são persistidos no banco **SQLite** via `api/database.py`.
3. A **API FastAPI** (`api/main.py`) expõe endpoints REST para consulta.
4. O **frontend React** (`web/src/App.jsx`) consome a API e exibe os carrinhos.

---

## Como Executar Localmente

### Pré-requisitos
- Python 3.11+
- Node.js 18+
- pip / npm

### 1. API FastAPI

```bash
cd api
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

### 2. Scraper (popular o banco)

```bash
cd scraper
pip install -r requirements.txt
python hotwheels_scraper.py
```

### 3. Frontend React

```bash
cd web
npm install
npm start
```

A aplicação estará disponível em `http://localhost:3000`.

---

## Endpoints da API

| Método | Rota                  | Descrição                              |
|--------|-----------------------|----------------------------------------|
| GET    | `/api/v1/cars`        | Lista carrinhos com filtros opcionais  |
| GET    | `/api/v1/cars/{id}`   | Detalhe de um carrinho                 |
| GET    | `/api/v1/years`       | Lista anos disponíveis                 |
| GET    | `/api/v1/series`      | Lista séries disponíveis               |
| POST   | `/api/v1/cars/{id}/view` | Registra visualização de um carrinho |

### Parâmetros de Filtro para `/api/v1/cars`

- `year` — filtra por ano (ex: `?year=2023`)
- `series` — filtra por série (ex: `?series=Mainline`)
- `search` — busca por nome (ex: `?search=camaro`)
- `skip` — paginação offset (padrão: 0)
- `limit` — número de resultados (padrão: 20, máx: 100)

---

## Banco de Dados

**Arquivo:** `api/hw_cars.db` (SQLite)

### Tabela `cars`

| Coluna        | Tipo    | Descrição                     |
|---------------|---------|-------------------------------|
| id            | INTEGER | Chave primária                |
| name          | TEXT    | Nome do carrinho              |
| year          | INTEGER | Ano da série                  |
| series        | TEXT    | Nome da série                 |
| series_number | TEXT    | Número na série               |
| color         | TEXT    | Cor do carrinho               |
| tampo         | TEXT    | Tampo/decal                   |
| base_color    | TEXT    | Cor da base                   |
| window_color  | TEXT    | Cor das janelas               |
| interior_color| TEXT    | Cor do interior               |
| wheel_type    | TEXT    | Tipo de roda                  |
| toy_number    | TEXT    | Número do brinquedo           |
| country       | TEXT    | País de origem                |
| image_url     | TEXT    | URL da imagem                 |
| fandom_url    | TEXT    | URL da página no Fandom       |
| view_count    | INTEGER | Contador de visualizações     |
| created_at    | TEXT    | Data de criação do registro   |

---

## Docker

```bash
docker-compose up --build
```

- API disponível em `http://localhost:8000`
- Frontend disponível em `http://localhost:3000`

---

## GitHub Actions

O workflow `.github/workflows/weekly-scraper.yml` executa o scraper automaticamente todo domingo às 00:00 UTC para manter o banco atualizado.

---

## Testes

```bash
cd tests
pip install pytest httpx
pytest -v
```
