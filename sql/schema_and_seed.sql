CREATE TABLE ALUNOS (
    ID VARCHAR(10) NOT NULL PRIMARY KEY,
    NOME_ALUNO VARCHAR(100) NOT NULL,
    CREDITOS INTEGER NOT NULL
);

CREATE TABLE DISCIPLINAS (
    ID VARCHAR(10) NOT NULL PRIMARY KEY,
    NOME_DISCIPLINA VARCHAR(150) NOT NULL,
    SEMESTRE INTEGER NOT NULL,
    CREDITOS INTEGER NOT NULL
);

CREATE TABLE MATRICULAS (
    ID_ALUNO VARCHAR(10) NOT NULL,
    ID_DISCIPLINA VARCHAR(10) NOT NULL,
    NOME_DISCIPLINA VARCHAR(150) NOT NULL,
    PRIMARY KEY (ID_ALUNO, ID_DISCIPLINA),
    CONSTRAINT FK_MATRICULAS_ALUNOS
        FOREIGN KEY (ID_ALUNO) REFERENCES ALUNOS (ID),
    CONSTRAINT FK_MATRICULAS_DISCIPLINAS
        FOREIGN KEY (ID_DISCIPLINA) REFERENCES DISCIPLINAS (ID)
);

INSERT INTO ALUNOS (ID, NOME_ALUNO, CREDITOS) VALUES
('A001', 'Lucas Almeida', 14),
('A002', 'Pedro Santos', 18),
('A003', 'Gabriel Oliveira', 12),
('A004', 'Rafael Costa', 17),
('A005', 'Mateus Ferreira', 10),
('A006', 'Ana Souza', 19),
('A007', 'Mariana Lima', 13),
('A008', 'Juliana Pereira', 16),
('A009', 'Camila Rodrigues', 11),
('A010', 'Beatriz Carvalho', 20);

INSERT INTO DISCIPLINAS (ID, NOME_DISCIPLINA, SEMESTRE, CREDITOS) VALUES
('D001', 'Algoritmos e Lógica de Programação', 1, 4),
('D002', 'Fundamentos de Sistemas de Informação', 1, 4),
('D003', 'Matemática Discreta', 1, 4),
('D004', 'Introdução à Computação', 1, 2),
('D005', 'Programação Orientada a Objetos', 2, 6),
('D006', 'Arquitetura de Computadores', 2, 4),
('D007', 'Engenharia de Software I', 2, 4),
('D008', 'Banco de Dados I', 2, 4),
('D009', 'Estruturas de Dados', 3, 6),
('D010', 'Sistemas Operacionais', 3, 4),
('D011', 'Análise e Projeto de Sistemas', 3, 4),
('D012', 'Probabilidade e Estatística', 3, 2),
('D013', 'Banco de Dados II', 4, 4),
('D014', 'Redes de Computadores', 4, 6),
('D015', 'Engenharia de Software II', 4, 4),
('D016', 'Interação Humano-Computador', 4, 2),
('D017', 'Desenvolvimento Web I', 5, 4),
('D018', 'Computação em Nuvem', 5, 4),
('D019', 'Segurança da Informação', 5, 6),
('D020', 'Governança de TI', 5, 2),
('D021', 'Desenvolvimento Mobile', 6, 4),
('D022', 'Inteligência Artificial', 6, 6),
('D023', 'Sistemas Distribuídos', 6, 4),
('D024', 'Gestão de Projetos de TI', 6, 2),
('D025', 'Big Data e Analytics', 7, 4),
('D026', 'Mineração de Dados', 7, 4),
('D027', 'Internet das Coisas', 7, 6),
('D028', 'Empreendedorismo em Tecnologia', 7, 2),
('D029', 'Arquitetura de Software', 8, 4),
('D030', 'Auditoria e Perícia em TI', 8, 4),
('D031', 'Tópicos Avançados em Sistemas de Informação', 8, 6),
('D032', 'Trabalho de Conclusão de Curso', 8, 6);

INSERT INTO MATRICULAS (ID_ALUNO, ID_DISCIPLINA, NOME_DISCIPLINA) VALUES
('A001', 'D001', 'Algoritmos e Lógica de Programação');

SELECT 'ALUNOS' AS TABELA, COUNT(*) AS TOTAL FROM ALUNOS;
SELECT 'DISCIPLINAS' AS TABELA, COUNT(*) AS TOTAL FROM DISCIPLINAS;
SELECT 'MATRICULAS' AS TABELA, COUNT(*) AS TOTAL FROM MATRICULAS;
