# Stakeholders — ferias

> **Artefato RUP:** Registro de Stakeholders (Modelagem de Negócios)
> **Proprietário:** [RUP] Analista de Negócios (📋)
> **Status:** Completo
> **Última atualização:** 2026-07-17

---

## Registro de Stakeholders

### Stakeholders Humanos

| # | Papel | Interesse | Influência | Expectativas |
|---|-------|-----------|------------|--------------|
| 1 | **Tech Manager** (Ricardo Costa) | Visibilidade das férias para planejar entregas e garantir cobertura técnica | 🔴 Alta | Sistema simples, funcional, que resolva o problema sem burocracia |
| 2 | **Membros do Time** | Saber quando colegas saem de férias para evitar conflitos e se organizar | 🟡 Média | Interface fácil de usar, cadastro rápido, consulta imediata |
| 3 | **Tech Leads / Coordenadores** | Planejar sprints e alocação de pessoas considerando ausências | 🟡 Média | Filtro por time funcional, visão cronológica clara |

### Atores de Sistema

| # | Sistema/Ator | Papel no Contexto | Tipo |
|---|--------------|-------------------|------|
| 4 | **Navegador Web** | Interface de acesso ao sistema — o usuário interage via browser | Ator externo |
| 5 | **Banco de Dados SQLite** | Persistência local dos dados de pessoas, times e férias | Componente interno |

---

## Matriz de Influência × Interesse

```
            INTERESSE
            Baixo          Alto
          ┌──────────────┬──────────────┐
  Alta    │              │ Tech Manager │
INFLUÊNCIA│              │              │
          ├──────────────┼──────────────┤
  Baixa   │              │ Membros do   │
          │              │ Time / Leads │
          └──────────────┴──────────────┘
```

**Leitura:** O Tech Manager é o principal stakeholder — alta influência (dono do produto) e alto interesse (resolve a dor dele diretamente). Membros e Leads têm interesse alto (são usuários diretos) mas influência menor nas decisões de produto.

---

## Observações

- Não há stakeholders de áreas externas (RH, financeiro, jurídico) — o sistema é autocontido dentro do time de tecnologia.
- Não existe figura de "administrador" — todos os usuários possuem o mesmo nível de acesso.
