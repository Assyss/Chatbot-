# DB2 - provisionamento e carga dos dados

Este guia segue a atividade AV-01-ICL-Chatbot usando IBM Db2 on Cloud e a API REST do Db2.

## 1. Criar o servico DB2

1. Acesse o catalogo da IBM Cloud: <https://cloud.ibm.com/catalog#all_products>.
2. Pesquise por **DB2**.
3. Instancie o servico relacional DB2.
4. Aguarde o provisionamento em <https://cloud.ibm.com/resources>.
5. Abra o recurso DB2 provisionado na secao de bancos de dados.

## 2. Obter credenciais

1. No menu lateral do DB2, abra **Credenciais de servicos**.
2. Clique em **Criar credencial**.
3. Copie os valores:
   - `username`
   - `password`
4. No menu lateral, abra **Gerenciar**.
5. Clique em **Ir para UI**.
6. Na UI do DB2, abra **Administracao** pelo icone de chave.
7. Copie:
   - nome do host da API REST
   - deployment ID usado no header `x-deployment-id`

> Nunca publique `username`, `password`, `DB2_TOKEN` ou `deployment ID` real em commits.

## 3. Configurar ambiente local

Copie o arquivo de exemplo:

```bash
cp .env.example .env
```

Edite `.env` com os dados reais do DB2:

```env
DB2_HOSTNAME=seu-host.db2.cloud.ibm.com
DB2_DEPLOYMENT_ID=seu-deployment-id
DB2_USERNAME=seu-username
DB2_PASSWORD=sua-senha
```

## 4. Criar tabelas e carregar dados

Execute:

```bash
python3 scripts/load_db2_rest.py
```

O script faz:

1. POST em `/dbapi/v4/auth/tokens` para gerar o token.
2. POST em `/dbapi/v4/sql_jobs` para executar `sql/reset.sql` com `stop_on_error=no`.
3. POST em `/dbapi/v4/sql_jobs` para executar `sql/schema_and_seed.sql` com `stop_on_error=yes`.
4. GET em `/dbapi/v4/sql_jobs/{job_id}` ate cada job terminar.

Se quiser carregar sem derrubar tabelas existentes, execute:

```bash
python3 scripts/load_db2_rest.py --skip-reset
```

As tabelas criadas sao:

- `ALUNOS`
- `DISCIPLINAS`
- `MATRICULAS`

Os CSVs originais estao versionados em:

- `data/alunos.csv`
- `data/disciplinas.csv`
- `data/matriculas.csv`

## 5. Consultas de validacao

Depois da carga, valide no DB2 com:

```sql
SELECT COUNT(*) AS TOTAL_ALUNOS FROM ALUNOS;
SELECT COUNT(*) AS TOTAL_DISCIPLINAS FROM DISCIPLINAS;
SELECT COUNT(*) AS TOTAL_MATRICULAS FROM MATRICULAS;
```

Valores esperados:

- `ALUNOS`: 10
- `DISCIPLINAS`: 32
- `MATRICULAS`: 1
