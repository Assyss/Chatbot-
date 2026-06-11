# Atividade ChatBot

Atividade ChatBot de matricula usando IBM Db2 e Watsonx Assistant.

Este repositorio contem os artefatos da atividade:

- dados CSV para `ALUNOS`, `DISCIPLINAS` e `MATRICULAS`;
- SQL para criar e popular as tabelas no Db2;
- script Python para carregar o banco via Db2 REST API;
- especificacoes OpenAPI para integracoes customizadas do Watsonx Assistant;
- guias de configuracao do DB2 e do Watsonx Assistant.

> Credenciais reais da IBM Cloud nao devem ser versionadas. Use `.env.example` como modelo e mantenha o arquivo `.env` local fora do Git.

## Estrutura

```text
.
├── data/
│   ├── alunos.csv
│   ├── disciplinas.csv
│   └── matriculas.csv
├── docs/
│   ├── db2.md
│   └── watsonx-assistant.md
├── integrations/
│   └── watsonx-assistant/
│       ├── get-db2-sql-job.openapi.json
│       ├── get-db2-token.openapi.json
│       └── run-db2-sql-job.openapi.json
├── scripts/
│   ├── download_assistant_template.sh
│   └── load_db2_rest.py
├── sql/
│   ├── reset.sql
│   └── schema_and_seed.sql
├── .env.example
└── README.md
```

## Execucao rapida

1. Provisione o DB2 seguindo `docs/db2.md`.
2. Copie as variaveis de ambiente:

   ```bash
   cp .env.example .env
   ```

3. Preencha `.env` com os dados obtidos no IBM Cloud.
4. Carregue as tabelas:

   ```bash
   python3 scripts/load_db2_rest.py
   ```

   Por padrao, o script executa `sql/reset.sql` antes da carga para recriar as tabelas. Para apenas executar `sql/schema_and_seed.sql`, use `--skip-reset`.

5. Provisione e configure o Watsonx Assistant seguindo `docs/watsonx-assistant.md`.
6. Importe as integracoes OpenAPI de `integrations/watsonx-assistant/`.

## Integracao principal solicitada

O arquivo abaixo contem a integracao `GetDB2Token` solicitada na atividade:

```text
integrations/watsonx-assistant/get-db2-token.openapi.json
```

Ela chama:

```text
POST https://{HOSTNAME}/dbapi/v4/auth/tokens
```

com:

- header `x-deployment-id`;
- body `userid`;
- body `password`.

O token retornado deve ser armazenado na variavel de sessao `DB2_TOKEN`.

## Dados carregados

| Tabela | Arquivo | Registros |
| --- | --- | ---: |
| `ALUNOS` | `data/alunos.csv` | 10 |
| `DISCIPLINAS` | `data/disciplinas.csv` | 32 |
| `MATRICULAS` | `data/matriculas.csv` | 1 |

## Observacoes de seguranca

- Nao committe `.env`.
- Nao publique `DB2_PASSWORD`.
- Nao publique `DB2_TOKEN`.
- Se o token expirar, execute novamente `GetDB2Token`.
