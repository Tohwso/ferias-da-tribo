# Visão do Produto — ferias

> **Artefato RUP:** Documento de Visão (Modelagem de Negócios)
> **Proprietário:** [RUP] Analista de Negócios (📋)
> **Status:** Completo
> **Última atualização:** 2026-07-17

---

## 1. Declaração do Problema

| Dimensão | Descrição |
|----------|-----------|
| **O problema** | Falta de visibilidade sobre as agendas de férias dos membros do time, levando a conflitos de datas e ausência de planejamento |
| **Afeta** | Membros do time, Tech Managers e líderes técnicos |
| **Impacto** | Desencontros nas marcações (ex.: duas pessoas-chave saindo no mesmo período), dificuldade de planejamento de entregas e cobertura |
| **Uma solução adequada** | Um sistema simples e local onde qualquer pessoa do time pode cadastrar e visualizar as férias de todos, com filtro por time |

---

## 2. Posicionamento do Produto

| Dimensão | Descrição |
|----------|-----------|
| **Para** | Membros de times de tecnologia que precisam coordenar férias |
| **Que necessitam de** | Visibilidade compartilhada sobre quem sai e quando volta de férias |
| **O produto** | É uma aplicação web local de gestão de férias |
| **Que** | Permite cadastrar pessoas, times e períodos de férias, exibindo uma visão consolidada ordenada por data |
| **Diferente de** | Planilhas compartilhadas ou comunicação informal via chat |
| **Nosso produto** | Oferece uma interface dedicada com filtro por time e visão cronológica imediata, sem depender de serviços cloud |

---

## 3. Objetivos de Negócio

| ID | Objetivo | Métrica de Sucesso |
|----|----------|--------------------|
| OBJ-01 | Eliminar conflitos de férias no time | Zero sobreposições não-planejadas após adoção |
| OBJ-02 | Dar visibilidade imediata da agenda de férias | Qualquer membro consulta férias do time em menos de 10 segundos |
| OBJ-03 | Centralizar informações de férias em um único lugar | 100% das férias do time registradas no sistema (em vez de planilhas ou chat) |

---

## 4. Escopo

### 4.1 Dentro do Escopo (IN)

- Cadastro e gestão de pessoas (nome, email, time)
- Cadastro e gestão de times (nome, descrição)
- Cadastro e gestão de períodos de férias (pessoa, data início, data fim, quantidade de dias)
- Tela inicial com listagem cronológica dos eventos de férias
- Filtro por time na tela inicial
- Execução 100% local (sem dependência de cloud)

### 4.2 Fora do Escopo (OUT)

- Autenticação e controle de acesso (qualquer pessoa acessa)
- Workflow de aprovação de férias (não é um sistema de RH)
- Integração com sistemas de RH, folha de pagamento ou calendários externos
- Cálculo de saldo de dias de férias ou regras trabalhistas (CLT)
- Notificações por email ou push
- Multi-tenant (múltiplas empresas)
- Deploy em cloud ou containerização

---

## 5. Restrições

| ID | Restrição | Razão |
|----|-----------|-------|
| R-01 | Sistema deve rodar 100% local, sem serviços externos | Decisão do stakeholder — simplicidade e independência |
| R-02 | Stack fixa: Python + FastAPI + SQLite + HTML/CSS/JS | Decisão técnica já tomada pelo stakeholder |
| R-03 | Sem autenticação — acesso aberto na rede local | Escopo deliberadamente simples |

---

## 6. Riscos Iniciais

| ID | Risco | Probabilidade | Impacto | Mitigação |
|----|-------|---------------|---------|-----------|
| RI-01 | Dados ficarem desatualizados se as pessoas não cadastrarem as férias | Alta | Alto | Simplicidade do sistema reduz atrito de cadastro |
| RI-02 | Perda de dados por falta de backup do SQLite | Média | Alto | Documentar procedimento de backup do arquivo `.db` |
| RI-03 | Sem validação de sobreposição, duas pessoas podem cadastrar férias conflitantes sem aviso | Baixa | Médio | A visibilidade na tela inicial já mitiga parcialmente — avaliação futura de alertas |

---

## 7. Premissas

| ID | Premissa |
|----|----------|
| AS-01 | O sistema será acessado por um grupo pequeno (até ~30 pessoas de um mesmo time ou tribo) |
| AS-02 | Não existe necessidade de histórico formal ou auditoria — é uma ferramenta de visibilidade |
| AS-03 | A quantidade de dias de férias é informada manualmente, sem cálculo automático |
| AS-04 | Todos os usuários têm acesso igual — não há papéis diferenciados |
