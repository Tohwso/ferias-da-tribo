# Diagramas de Sequência — ferias

> **Artefato RUP:** Diagramas de Sequência (Análise & Design)
> **Proprietário:** [RUP] Arquiteto
> **Status:** Completo
> **Última atualização:** 2026-07-17

---

## 1. UC-004: Consultar Agenda de Férias (Tela Inicial)

O fluxo principal do sistema — carrega a tela inicial com férias futuras, filtro por time e detecção de sobreposição.

```mermaid
sequenceDiagram
    actor U as Usuário
    participant B as Navegador
    participant P as Pages Router
    participant S as VacationService
    participant DB as SQLite

    U->>B: Acessa http://localhost:8000/
    B->>P: GET /
    P->>S: listar_ferias(include_past=false)
    S->>DB: SELECT v.*, p.name, p.team_id, t.name<br/>FROM vacation v<br/>JOIN person p ON v.person_id = p.id<br/>JOIN team t ON p.team_id = t.id<br/>WHERE v.end_date >= date('now')<br/>ORDER BY v.start_date ASC
    DB-->>S: Lista de eventos
    S->>S: Calcula sobreposições por time<br/>(RF-20, ADR-007)
    S->>DB: SELECT id, name FROM team
    DB-->>S: Lista de times (para filtro)
    S-->>P: vacations + teams + overlap_ids
    P->>P: Renderiza template Jinja2<br/>com has_overlap em cada card
    P-->>B: HTML completo
    B-->>U: Tela inicial com férias futuras
```

### 1.1 Fluxo Alternativo — Filtrar por Time (RF-18)

```mermaid
sequenceDiagram
    actor U as Usuário
    participant B as Navegador
    participant A as API Router
    participant S as VacationService
    participant DB as SQLite

    U->>B: Seleciona time "Backend" no filtro
    B->>A: GET /api/v1/vacations?team_id=1
    A->>S: listar_ferias(team_id=1, include_past=false)
    S->>DB: SELECT ... WHERE p.team_id = 1<br/>AND v.end_date >= date('now')<br/>ORDER BY v.start_date ASC
    DB-->>S: Eventos filtrados
    S->>S: Calcula sobreposições<br/>(apenas dentro do time 1)
    S-->>A: vacations + teams + overlap_ids
    A-->>B: JSON response
    B->>B: JavaScript atualiza DOM<br/>com novos cards
    B-->>U: Lista atualizada
```

### 1.2 Fluxo Alternativo — Toggle Férias Passadas (RF-19)

```mermaid
sequenceDiagram
    actor U as Usuário
    participant B as Navegador
    participant A as API Router
    participant S as VacationService
    participant DB as SQLite

    U->>B: Ativa toggle "Mostrar passadas"
    B->>A: GET /api/v1/vacations?include_past=true
    A->>S: listar_ferias(include_past=true)
    S->>DB: SELECT ... (sem filtro de end_date)<br/>ORDER BY v.start_date ASC
    DB-->>S: Todos os eventos
    S->>S: Calcula sobreposições
    S-->>A: vacations + teams + overlap_ids
    A-->>B: JSON response
    B->>B: Atualiza DOM
    B-->>U: Lista com férias passadas e futuras
```

---

## 2. UC-003: Criar Evento de Férias (Happy Path)

```mermaid
sequenceDiagram
    actor U as Usuário
    participant B as Navegador
    participant A as API Router
    participant Sc as Pydantic Schema
    participant S as VacationService
    participant DB as SQLite

    U->>B: Preenche formulário de férias<br/>(pessoa, início, fim, dias)
    B->>A: POST /api/v1/vacations<br/>{"person_id": 1, "start_date": "2026-08-01",<br/>"end_date": "2026-08-15", "days": 15}
    A->>Sc: Valida VacationCreate
    Sc->>Sc: Verifica start_date <= end_date (BR-002)<br/>Verifica days > 0 (BR-003)
    Sc-->>A: ✅ Válido
    A->>S: criar_ferias(data)
    S->>DB: SELECT id FROM person WHERE id = 1
    DB-->>S: ✅ Pessoa existe
    S->>DB: INSERT INTO vacation (person_id, start_date, end_date, days)<br/>VALUES (1, '2026-08-01', '2026-08-15', 15)
    DB-->>S: ✅ id = 42
    S-->>A: Vacation criada (id=42)
    A-->>B: 201 Created + JSON
    B->>B: Exibe confirmação,<br/>atualiza lista
    B-->>U: "Férias registradas com sucesso"
```

### 2.1 Fluxo de Exceção — Data Inválida (BR-002)

```mermaid
sequenceDiagram
    actor U as Usuário
    participant B as Navegador
    participant A as API Router
    participant Sc as Pydantic Schema

    U->>B: Preenche formulário com<br/>início=2026-08-15, fim=2026-08-01
    B->>A: POST /api/v1/vacations<br/>{"start_date": "2026-08-15", "end_date": "2026-08-01", ...}
    A->>Sc: Valida VacationCreate
    Sc->>Sc: start_date > end_date ❌
    Sc-->>A: Erro de validação
    A-->>B: 422 Unprocessable Entity<br/>{"detail": "Data de início deve ser<br/>anterior ou igual à data de fim"}
    B->>B: Exibe mensagem de erro
    B-->>U: Formulário com erro destacado
```

---

## 3. UC-002: Criar Pessoa (Happy Path + Exceção)

```mermaid
sequenceDiagram
    actor U as Usuário
    participant B as Navegador
    participant A as API Router
    participant S as PersonService
    participant DB as SQLite

    U->>B: Preenche formulário<br/>(nome, email, time)
    B->>A: POST /api/v1/people<br/>{"name": "Maria", "email": "maria@emp.com", "team_id": 1}
    A->>S: criar_pessoa(data)
    S->>DB: SELECT id FROM team WHERE id = 1
    DB-->>S: ✅ Time existe
    S->>DB: SELECT id FROM person WHERE email = 'maria@emp.com'
    DB-->>S: ∅ Nenhum resultado
    S->>DB: INSERT INTO person (name, email, team_id)<br/>VALUES ('Maria', 'maria@emp.com', 1)
    DB-->>S: ✅ id = 7
    S-->>A: Person criada
    A-->>B: 201 Created + JSON
    B-->>U: "Pessoa cadastrada"
```

### 3.1 Fluxo de Exceção — Email Duplicado (BR-011)

```mermaid
sequenceDiagram
    actor U as Usuário
    participant B as Navegador
    participant A as API Router
    participant S as PersonService
    participant DB as SQLite

    U->>B: Preenche formulário com email existente
    B->>A: POST /api/v1/people<br/>{"name": "Outro", "email": "maria@emp.com", "team_id": 2}
    A->>S: criar_pessoa(data)
    S->>DB: SELECT id FROM person WHERE email = 'maria@emp.com'
    DB-->>S: id = 7 (já existe!)
    S-->>A: ❌ Erro: email duplicado
    A-->>B: 409 Conflict<br/>{"detail": "Já existe uma pessoa com este email"}
    B->>B: Exibe erro no campo email
    B-->>U: Formulário com erro
```

---

## 4. UC-001: Excluir Time (Happy Path + Exceção BR-010)

```mermaid
sequenceDiagram
    actor U as Usuário
    participant B as Navegador
    participant A as API Router
    participant S as TeamService
    participant DB as SQLite

    U->>B: Clica "Excluir" no time "QA"
    B->>B: Exibe confirmação
    U->>B: Confirma exclusão
    B->>A: DELETE /api/v1/teams/3
    A->>S: excluir_time(id=3)
    S->>DB: SELECT COUNT(*) FROM person WHERE team_id = 3
    DB-->>S: count = 0
    S->>DB: DELETE FROM team WHERE id = 3
    DB-->>S: ✅ Excluído
    S-->>A: Sucesso
    A-->>B: 204 No Content
    B->>B: Remove card do time da lista
    B-->>U: Time removido
```

### 4.1 Fluxo de Exceção — Time com Pessoas (BR-010)

```mermaid
sequenceDiagram
    actor U as Usuário
    participant B as Navegador
    participant A as API Router
    participant S as TeamService
    participant DB as SQLite

    U->>B: Clica "Excluir" no time "Backend"
    B->>B: Exibe confirmação
    U->>B: Confirma exclusão
    B->>A: DELETE /api/v1/teams/1
    A->>S: excluir_time(id=1)
    S->>DB: SELECT COUNT(*) FROM person WHERE team_id = 1
    DB-->>S: count = 5 (tem pessoas!)
    S-->>A: ❌ Erro: time possui pessoas
    A-->>B: 409 Conflict<br/>{"detail": "Não é possível excluir:<br/>existem pessoas vinculadas"}
    B->>B: Exibe mensagem de erro
    B-->>U: "Remova as pessoas antes de excluir o time"
```

---

## 5. UC-002: Excluir Pessoa com Cascata (BR-009)

```mermaid
sequenceDiagram
    actor U as Usuário
    participant B as Navegador
    participant A as API Router
    participant S as PersonService
    participant DB as SQLite

    U->>B: Clica "Excluir" na pessoa "João"
    B->>B: Exibe confirmação<br/>"João e todas as suas férias serão excluídos"
    U->>B: Confirma
    B->>A: DELETE /api/v1/people/1
    A->>S: excluir_pessoa(id=1)
    S->>DB: DELETE FROM person WHERE id = 1
    Note over DB: ON DELETE CASCADE<br/>remove automaticamente<br/>todos os registros de vacation<br/>com person_id = 1
    DB-->>S: ✅ Excluído (pessoa + férias)
    S-->>A: Sucesso
    A-->>B: 204 No Content
    B->>B: Remove pessoa da lista
    B-->>U: Pessoa e férias removidos
```

---

## 6. Resumo de Cobertura

| UC | Diagramas | Fluxos Cobertos |
|----|-----------|-----------------|
| UC-001 | §4, §4.1 | Excluir time (happy path + BR-010) |
| UC-002 | §3, §3.1, §5 | Criar pessoa (happy + email duplicado), Excluir com cascata |
| UC-003 | §2, §2.1 | Criar férias (happy + data inválida) |
| UC-004 | §1, §1.1, §1.2 | Tela inicial, filtro por time, toggle passadas |
