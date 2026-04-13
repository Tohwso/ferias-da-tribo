# Diário de Bordo — ferias

> **Artefato RUP:** Diário de Bordo (Governança)
> **Proprietário:** [RUP] Governante (👑)
> **Status:** Em Progresso
> **Última atualização:** 2026-07-17

---

## Status do Pipeline

| Fase | Agente | Status | Artefatos | Confiança |
|------|--------|--------|-----------|-----------|
| Modelagem de Negócios | 📋 AN | ✅ Completo | 5/5 | — |
| Requisitos | 📋 AR | ✅ Completo | 2/2 | — |
| Design | 🏛️ Arq | ✅ Completo | 4/4 | — |
| Implementação | 🔀 Dev | ✅ Completo | 4/4 | — |
| Qualidade | 🧪 QA | ✅ Completo | 3/3 | — |
| Deployment | 🏛️ Arq + 🔀 Dev | ✅ Completo | 2/2 | — |

---

## Perguntas em Aberto

| ID | Levantada por | Fase | Pergunta | Status | Resolução |
|----|---------------|------|----------|--------|-----------|
| UQ-001 | 📋 AN | Negócios | Validação de sobreposição de férias no mesmo time? | ✅ RESOLVIDA | Só visual — o calendário já mostra, sem alerta extra |
| UQ-002 | 📋 AN | Negócios | Exclusão de pessoa com férias — cascata ou bloqueio? | ✅ RESOLVIDA | Cascata — exclui pessoa e todas as férias dela |
| UQ-003 | 📋 AN | Negócios | Tela inicial mostra férias passadas ou só futuras? | ✅ RESOLVIDA | Futuras por padrão, toggle pra ver passadas |

---

## Premissas

| ID | Feita por | Fase | Premissa | Risco | Validada? |
|----|-----------|------|----------|-------|-----------|
| AS-01 | 📋 AN | Negócios | Máximo ~30 pessoas | Baixo | Pendente |
| AS-02 | 📋 AN | Negócios | Sem histórico/auditoria | Baixo | Pendente |
| AS-03 | 📋 AN | Negócios | Dias de férias informados manualmente | Baixo | Pendente |
| AS-04 | 📋 AN | Negócios | Todos com acesso igual (sem papéis) | Baixo | Pendente |

---

## Log de Handoffs

<!-- Entradas adicionadas conforme o pipeline avança -->

### [2026-07-17] 📋 Analista de Negócios → 📋 Analista de Requisitos

**Entregue:**
- spec/docs/01-business/vision.md (4.3KB) — 3 objetivos de negócio, escopo in/out
- spec/docs/01-business/glossary.md (2.4KB) — 10 termos, 4 siglas
- spec/docs/01-business/stakeholders.md (2.4KB) — 3 humanos + 2 sistema
- spec/docs/01-business/business-rules.md (3.7KB) — 15 regras BR-001 a BR-015
- spec/docs/01-business/business-processes.md (6.0KB) — 4 processos com Mermaid

**Decisões-chave:**
- Sistema simples para ~30 pessoas, sem autenticação, sem papéis
- Dias de férias informados manualmente (não calculados)
- Não há workflow de aprovação — quem cadastra já está confirmado

**Alternativas descartadas:**
- Validação de sobreposição de férias (complexidade desproporcional — visibilidade resolve)
- Modelagem de dia útil vs dia corrido (overcomplexity)

**Armadilhas para agentes downstream:**
- ⚠️ BR-009: exclusão de pessoa com férias — cascata ou bloqueio? Precisa decisão
- ⚠️ AS-01: se escalar além de 30 pessoas, UI precisa paginação
- ⚠️ BR-005/BR-006: filtro por time precisa de estado default "Todos"

**Avaliação de confiança:**
- 🟢 Visão e escopo: alta confiança — stakeholder foi claro
- 🟢 Regras de negócio: alta confiança — domínio simples
- 🟡 Processos: média confiança — stakeholder não mencionou edição/exclusão detalhada

**Perguntas em aberto:**
- ❓ UQ-001: Validação de sobreposição de férias no mesmo time?
- ❓ UQ-002: Exclusão de pessoa com férias — cascata ou bloqueio?
- ❓ UQ-003: Tela inicial mostra férias passadas ou só futuras?

**Premissas:**
- 💭 AS-01: Máximo ~30 pessoas
- 💭 AS-02: Sem histórico/auditoria
- 💭 AS-03: Dias de férias informados manualmente
- 💭 AS-04: Todos com acesso igual

### [2026-07-17] 📋 Analista de Requisitos → 🏛️ Arquiteto

**Entregue:**
- spec/docs/02-requirements/requirements.md (9.0KB) — 20 RFs, 8 NFRs, rastreabilidade completa
- spec/docs/02-requirements/use_cases.md (8.9KB) — 4 UCs com fluxos, matriz UC×RF×NFR×BR

**Decisões-chave:**
- 15/15 BRs mapeadas, 3/3 UQs incorporadas
- RF-20 (sobreposição visual) classificado como Should Have
- 4 UCs agrupados (CRUD agrupado por entidade em vez de 1 UC por operação)

**Alternativas descartadas:**
- 9 UCs separados (1 por operação CRUD) — desproporcional, agrupou em 4

**Armadilhas para agentes downstream:**
- ⚠️ RF-20: como mostrar sobreposição — calendário ou highlight na lista?
- ⚠️ BR-010 vs BR-009: exclusão de time bloqueia, de pessoa faz cascata
- ⚠️ NFR-05/BR-015: assets CSS/fontes devem ser 100% locais

**Avaliação de confiança:**
- 🟢 Requisitos funcionais: alta — domínio simples e bem definido
- 🟢 Casos de uso: alta — fluxos claros
- 🟡 NFRs: média — performance/escalabilidade baseada em premissa AS-01

**Perguntas em aberto:**
- Nenhuma nova

**Premissas:**
- 💭 AS-05: Validação de email é formato-independente (qualquer string única)

### [2026-07-17] 🏛️ Arquiteto → 🔀 Desenvolvedor

**Entregue:**
- spec/docs/03-design/architecture.md (11.7KB) — C4 (3 níveis), 7 ADRs
- spec/docs/03-design/domain_model.md (8.4KB) — 3 entidades, ER, constraints
- spec/docs/03-design/api_spec.md (10.2KB) — 12 endpoints REST
- spec/docs/03-design/sequence_diagrams.md (8.5KB) — 10 diagramas Mermaid
- spec/docs/06-deployment/ci_cd_pipeline.md (2.9KB) — setup local
- spec/docs/06-deployment/infrastructure.md (7.8KB) — estrutura de diretórios, DDL

**Decisões-chave:**
- ADR-007: sobreposição via highlight na lista (não calendário)
- Layered architecture (não hexagonal — desproporcional pra 3 entidades)
- Jinja2 templates + vanilla JS (não SPA)
- ON DELETE CASCADE pra person→vacation, validação em service pra team→person

**Armadilhas para o Dev:**
- ⚠️ Sobreposição é query no service, não entidade — algoritmo no domain_model.md §5
- ⚠️ updated_at precisa de onupdate=func.now() no SQLAlchemy
- ⚠️ GET /api/v1/vacations retorna has_overlap e teams junto

**Avaliação de confiança:**
- 🟢 Modelo de dados, API, stack: alta
- 🟡 Sobreposição visual (RF-20): média — implementação precisa atenção

**Premissas novas:**
- 💭 AS-06: ruff como linter/formatter
- 💭 AS-07: Schema SQLAlchemy ≈ DDL documentado

### [2026-07-17] 🔀 Desenvolvedor → 🧪 Analista de Qualidade

**Entregue:**
- Backend completo: 23 arquivos Python, ~1.500 linhas
- Frontend: index.html + style.css + app.js (~1.300 linhas)
- Testes: 25 testes, todos passando ✅
- spec/docs/04-implementation/ (4 artefatos)
- README.md com instruções de setup

**Decisões-chave:**
- Layered architecture: routers → services → models
- Vacation.days auto-calculado (end_date - start_date + 1)
- Overlap detection via query SQL no service
- Frontend single-page com 4 abas (Agenda, Times, Pessoas, Férias)

**Armadilhas para o QA:**
- ⚠️ Verificar se overlap highlight funciona visualmente no frontend
- ⚠️ Verificar cascata real (BR-009) além do teste unitário
- ⚠️ Verificar filtro de férias passadas (toggle)

**Avaliação de confiança:**
- 🟢 Backend: alta — 25 testes passando, regras implementadas
- 🟢 API: alta — 12 endpoints conforme spec
- 🟡 Frontend: média — funcional mas não testado end-to-end

### [2026-07-17] 🧪 Analista de Qualidade → 👑 Governante (Pipeline Completo)

**Entregue:**
- spec/docs/05-test/test_strategy.md (8.7KB)
- spec/docs/05-test/test_coverage_map.md (23.6KB)
- spec/docs/05-test/test_patterns.md (10KB)
- spec/docs/07-change-management/technical_debt.md (7KB)
- spec/docs/07-change-management/risks_and_limitations.md (9.5KB)

**Veredicto: CONDITIONAL_GO** ✅🟡

**Findings críticos resolvidos:**
- ✅ ARCH-001: routes/api.py deletado (endpoints duplicados com bugs)

**Findings pendentes (não-bloqueantes):**
- RF-20: teste de overlap visual não coberto (E2E pendente)
- RF-16: ordenação assertada indiretamente
- BR-003: spec diz "manual", código calcula automaticamente (melhoria)

**Premissas validadas:** 5/7 confirmadas, 1 violada (AS-03, intencional), 1 parcial (AS-06)
