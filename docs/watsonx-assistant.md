# Watsonx Assistant - configuracao

Este guia descreve como configurar o Watsonx Assistant para consumir os dados do DB2 da atividade.

## 1. Criar o servico Watsonx Assistant

1. Acesse o catalogo da IBM Cloud: <https://cloud.ibm.com/catalog#all_products>.
2. Pesquise por **Assistant**.
3. Instancie o servico.
4. Aguarde o provisionamento em <https://cloud.ibm.com/resources>.
5. Abra o servico provisionado.
6. Clique em **Launch watsonx Assistant**.

## 2. Importar template do assistente

Baixe o template da atividade:

```bash
curl -L \
  -o assistente-modelo.zip \
  https://github.com/esensato/icl-2026-01/raw/main/assistente-modelo.zip
```

No Watsonx Assistant:

1. Abra o assistente.
2. Use a opcao de importar/upload de skill ou template.
3. Selecione `assistente-modelo.zip`.
4. Confirme a importacao.

## 3. Criar variaveis de sessao

Crie as variaveis de sessao abaixo e preencha com os dados do DB2:

| Variavel | Valor |
| --- | --- |
| `DB2_DEPLOYMENT_ID` | Deployment ID do DB2 usado no header `x-deployment-id` |
| `DB2_PASSWORD` | `password` da credencial de servico DB2 |
| `DB2_TOKEN` | Token retornado por `GetDB2Token`; pode iniciar vazio |
| `DB2_USERNAME` | `username` da credencial de servico DB2 |

O host da API REST e configurado como variavel do servidor nas integracoes OpenAPI. Use o valor anotado na UI do DB2 em **Administracao**.

## 4. Criar integracoes customizadas

No Watsonx Assistant, crie extensoes/integracoes customizadas importando os arquivos:

1. `integrations/watsonx-assistant/get-db2-token.openapi.json`
2. `integrations/watsonx-assistant/run-db2-sql-job.openapi.json`
3. `integrations/watsonx-assistant/get-db2-sql-job.openapi.json`

### GetDB2Token

Mapeie:

- Header `x-deployment-id`: `DB2_DEPLOYMENT_ID`
- Body `userid`: `DB2_USERNAME`
- Body `password`: `DB2_PASSWORD`

Salve o campo `token` retornado na variavel de sessao `DB2_TOKEN`.

### RunDB2SQLJob

Mapeie:

- Header `authorization`: `Bearer <DB2_TOKEN>`
- Header `x-deployment-id`: `DB2_DEPLOYMENT_ID`
- Body `commands`: SQL que sera executado
- Body `separator`: `;`
- Body `limit`: `100`
- Body `stop_on_error`: `yes`

Salve o campo `id` retornado para consultar o resultado.

### GetDB2SQLJob

Mapeie:

- Path `job_id`: id retornado por `RunDB2SQLJob`
- Header `authorization`: `Bearer <DB2_TOKEN>`
- Header `x-deployment-id`: `DB2_DEPLOYMENT_ID`

Use o retorno para montar a resposta ao usuario.

## 5. Consultas SQL uteis para a conversa

Aluno por codigo:

```sql
SELECT ID, NOME_ALUNO, CREDITOS
FROM ALUNOS
WHERE UPPER(ID) = UPPER('A001');
```

Disciplinas por semestre:

```sql
SELECT ID, NOME_DISCIPLINA, SEMESTRE, CREDITOS
FROM DISCIPLINAS
WHERE SEMESTRE = 1
ORDER BY ID;
```

Matriculas de um aluno:

```sql
SELECT M.ID_ALUNO, A.NOME_ALUNO, M.ID_DISCIPLINA, D.NOME_DISCIPLINA, D.CREDITOS
FROM MATRICULAS M
JOIN ALUNOS A ON A.ID = M.ID_ALUNO
JOIN DISCIPLINAS D ON D.ID = M.ID_DISCIPLINA
WHERE UPPER(M.ID_ALUNO) = UPPER('A001')
ORDER BY M.ID_DISCIPLINA;
```

Creditos restantes de um aluno:

```sql
SELECT
    A.ID,
    A.NOME_ALUNO,
    A.CREDITOS AS CREDITOS_DISPONIVEIS,
    COALESCE(SUM(D.CREDITOS), 0) AS CREDITOS_MATRICULADOS,
    A.CREDITOS - COALESCE(SUM(D.CREDITOS), 0) AS CREDITOS_RESTANTES
FROM ALUNOS A
LEFT JOIN MATRICULAS M ON M.ID_ALUNO = A.ID
LEFT JOIN DISCIPLINAS D ON D.ID = M.ID_DISCIPLINA
WHERE UPPER(A.ID) = UPPER('A001')
GROUP BY A.ID, A.NOME_ALUNO, A.CREDITOS;
```
