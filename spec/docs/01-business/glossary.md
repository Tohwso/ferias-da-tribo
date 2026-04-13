# Glossário — ferias

> **Artefato RUP:** Glossário (Modelagem de Negócios)
> **Proprietário:** [RUP] Analista de Negócios (📋)
> **Status:** Completo
> **Última atualização:** 2026-07-17

---

## Termos de Domínio

| Termo | Definição | Contexto |
|-------|-----------|----------|
| Evento de Férias | Registro de um período de ausência de uma pessoa por motivo de férias. Composto por: pessoa, data de início, data de fim e quantidade de dias | Unidade central do sistema — o que é visualizado na tela inicial |
| Pessoa | Membro de um time que pode ter eventos de férias cadastrados. Identificada por nome, email e vínculo a um time | Entidade base para associação de férias |
| Time | Agrupamento organizacional de pessoas (ex.: squad, tribo, célula). Possui nome e descrição | Usado para filtrar eventos de férias na tela inicial |
| Data de Início | Primeiro dia útil em que a pessoa estará de férias | Define o início da ausência |
| Data de Fim | Último dia do período de férias (a pessoa retorna no dia seguinte) | Define o fim da ausência |
| Dias de Férias | Quantidade total de dias do período de férias, informada manualmente pelo usuário | Não é calculada automaticamente — o usuário digita |
| Tela Inicial | Página principal do sistema que exibe todos os eventos de férias cadastrados, ordenados por data de início | Ponto de entrada e principal interface de consulta |
| Filtro por Time | Funcionalidade que permite ao usuário selecionar um time na tela inicial para exibir apenas os eventos de férias das pessoas daquele time | Facilita a consulta em organizações com múltiplos times |
| Visibilidade | Capacidade de qualquer membro do time consultar quando seus colegas estarão de férias | Objetivo principal do sistema |
| Sobreposição de Férias | Situação em que dois ou mais membros do mesmo time possuem períodos de férias coincidentes (total ou parcialmente) | Problema que o sistema ajuda a identificar visualmente |

---

## Siglas e Abreviações

| Sigla | Significado |
|-------|-------------|
| CRUD | Create, Read, Update, Delete — operações básicas de cadastro |
| API | Application Programming Interface |
| SQLite | Banco de dados relacional embutido, armazenado em arquivo local |
| FastAPI | Framework web Python para construção de APIs REST |
