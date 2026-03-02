# hw-cotacao-brasil 🏎️

Site de catálogo e cotação de carrinhos **Hot Wheels** para o mercado brasileiro, inspirado na interface da [LigaPokémon](https://www.ligapokemon.com.br).

## Funcionalidades

- 🔍 Busca e filtragem por nome, ano e série
- 📸 Galeria de imagens dos carrinhos
- 📈 "Mais Visualizados" — ranking baseado em visualizações
- 🤖 Scraper automático do Fandom Hot Wheels Wiki
- 📱 Layout responsivo (mobile-first)

## Tecnologias

| Camada    | Tecnologia                  |
|-----------|-----------------------------|
| Backend   | Python 3.11, FastAPI, SQLite |
| Frontend  | React 18, Vite               |
| Scraper   | requests, BeautifulSoup4     |
| DevOps    | Docker, GitHub Actions       |

## Início Rápido

```bash
# 1. Clone o repositório
git clone https://github.com/SEU_USER/hw-cotacao-brasil.git
cd hw-cotacao-brasil

# 2. Suba com Docker Compose
docker-compose up --build
```

Ou consulte o [CLAUDE.md](CLAUDE.md) para instruções detalhadas de execução local.

## Estrutura do Projeto

```
hw_site/
├── api/          # Backend FastAPI
├── scraper/      # Scraper do Fandom Wiki
├── web/          # Frontend React
├── tests/        # Testes pytest
└── .github/      # GitHub Actions workflows
```

## Licença

MIT