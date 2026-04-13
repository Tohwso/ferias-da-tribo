# Regras de Negócio — ferias

> **Artefato RUP:** Catálogo de Regras de Negócio (Modelagem de Negócios)
> **Proprietário:** [RUP] Analista de Negócios (📋)
> **Status:** Completo
> **Última atualização:** 2026-07-17

---

## Catálogo de Regras

### Regras Operacionais

| ID | Regra | Classificação | Fonte | Impacto se Violada |
|----|-------|---------------|-------|--------------------|
| BR-001 | Toda pessoa deve estar vinculada a exatamente um time | Operacional | Decisão de negócio | Impossibilidade de filtrar férias por time |
| BR-002 | Um evento de férias deve ter data de início anterior ou igual à data de fim | Operacional | Lógica de domínio | Dados inconsistentes — período negativo |
| BR-003 | A quantidade de dias de férias é informada manualmente pelo usuário, sem cálculo automático | Operacional | Decisão de escopo | — (simplificação deliberada) |
| BR-004 | A tela inicial exibe os eventos de férias ordenados por data de início (mais próximo primeiro) | Operacional | Requisito do stakeholder | Perda de usabilidade — eventos desordenados |
| BR-005 | O filtro por time na tela inicial mostra apenas os eventos de férias das pessoas pertencentes ao time selecionado | Operacional | Requisito do stakeholder | Visibilidade incorreta — dados misturados |
| BR-006 | Sem filtro aplicado, a tela inicial exibe eventos de férias de todos os times | Operacional | Comportamento padrão | — |
| BR-007 | Uma pessoa pode ter múltiplos eventos de férias cadastrados (férias parceladas, períodos distintos) | Operacional | Regra trabalhista implícita | Restrição artificial que impediria cenários reais |
| BR-008 | Um time pode existir sem pessoas vinculadas (time recém-criado) | Operacional | Flexibilidade operacional | — |
| BR-009 | Uma pessoa não pode ser excluída se possuir eventos de férias cadastrados, ou os eventos devem ser excluídos junto | Operacional | Integridade de dados | Eventos órfãos no sistema |
| BR-010 | Um time não pode ser excluído se possuir pessoas vinculadas, ou as pessoas devem ser realocadas/removidas antes | Operacional | Integridade de dados | Pessoas e eventos órfãos |
| BR-011 | O email de uma pessoa deve ser único no sistema — não podem existir duas pessoas com o mesmo email | Operacional | Identificação unívoca | Duplicação de cadastro, confusão na visualização |
| BR-012 | A tela inicial deve exibir: nome da pessoa, quantidade de dias, data de início e data de fim de cada evento | Operacional | Requisito do stakeholder | Interface incompleta |

### Regras de Controle Interno

| ID | Regra | Classificação | Fonte | Impacto se Violada |
|----|-------|---------------|-------|--------------------|
| BR-013 | O sistema não implementa autenticação — qualquer pessoa com acesso à rede pode utilizá-lo | Controle Interno | Decisão de escopo | — (risco aceito) |
| BR-014 | Qualquer usuário pode criar, editar e excluir qualquer registro (pessoa, time, férias) | Controle Interno | Decisão de escopo | Alterações indevidas — risco aceito pela simplicidade |
| BR-015 | O sistema opera 100% localmente, sem dependências de serviços externos | Controle Interno | Restrição do stakeholder | Indisponibilidade se dependência externa falhar |

---

## Observações

- Não existem regras regulatórias neste contexto — o sistema não interage com órgãos externos, RH ou legislação trabalhista.
- As regras BR-013 e BR-014 são riscos conscientemente aceitos pelo stakeholder em favor da simplicidade.
- A regra BR-003 (dias manuais) é uma simplificação deliberada — o cálculo de dias úteis/corridos envolveria complexidade desproporcional ao problema.
