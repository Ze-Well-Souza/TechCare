# Guia do Banco de Dados TechCare

Este documento fornece instruções detalhadas sobre como configurar, utilizar e gerenciar o banco de dados do sistema TechCare, baseado no Supabase (PostgreSQL).

## Índice
1. [Visão Geral do Banco de Dados](#visão-geral-do-banco-de-dados)
2. [Configuração do Supabase](#configuração-do-supabase)
3. [Estrutura de Tabelas](#estrutura-de-tabelas)
4. [Integração com o TechCare](#integração-com-o-techcare)
5. [Operações Comuns](#operações-comuns)
6. [Backup e Segurança](#backup-e-segurança)
7. [Solução de Problemas](#solução-de-problemas)

## Visão Geral do Banco de Dados

O TechCare utiliza o Supabase como plataforma de banco de dados. O Supabase é uma alternativa open source ao Firebase, oferecendo:

- Banco de dados PostgreSQL
- Autenticação de usuários
- API RESTful automática
- Armazenamento de arquivos
- Funções serverless
- Tempo real via websockets

O banco de dados armazena:
- Informações de clientes
- Dados de dispositivos
- Resultados de diagnósticos
- Histórico de reparos
- Informações sobre o sistema operacional
- Logs de ações realizadas

## Configuração do Supabase

### 1. Criação de Conta e Projeto

1. Acesse [supabase.com](https://supabase.com) e crie uma conta gratuita
2. Após o login, clique em "New Project"
3. Preencha as informações do projeto:
   - Nome: TechCare (ou o nome da sua marca)
   - Senha do banco de dados: crie uma senha forte
   - Região: escolha a mais próxima dos seus usuários
4. Clique em "Create new project" e aguarde a criação (pode levar alguns minutos)

### 2. Obtenção das Credenciais

Após a criação do projeto, você precisará de duas informações principais:

1. **URL do Projeto**: Na página inicial do seu projeto, clique em "Settings" (ícone de engrenagem) no menu lateral, depois em "API". Copie o valor de "URL" (exemplo: `https://abcdefghijklm.supabase.co`)

2. **Chave de API**: Na mesma página, copie o valor de "anon public" em "Project API keys" (exemplo: `eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...`)

Estas credenciais serão usadas para conectar o TechCare ao seu banco de dados.

### 3. Criação das Tabelas

Execute os seguintes comandos SQL no Editor SQL do Supabase (menu "SQL Editor"):

```sql
-- Tabela de clientes
CREATE TABLE clientes (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  nome TEXT NOT NULL,
  email TEXT UNIQUE NOT NULL,
  telefone TEXT,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Tabela de dispositivos
CREATE TABLE dispositivos (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  cliente_id UUID REFERENCES clientes(id),
  nome TEXT NOT NULL,
  sistema_operacional TEXT,
  processador TEXT,
  memoria TEXT,
  armazenamento TEXT,
  sistema_original BOOLEAN,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Tabela de diagnósticos
CREATE TABLE diagnosticos (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  dispositivo_id UUID REFERENCES dispositivos(id),
  data TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  resultado JSONB NOT NULL,
  score_geral INTEGER,
  problemas JSONB
);

-- Tabela de reparos
CREATE TABLE reparos (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  diagnostico_id UUID REFERENCES diagnosticos(id),
  data TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  acoes_realizadas JSONB NOT NULL,
  backup_realizado BOOLEAN DEFAULT FALSE,
  resultado TEXT
);

-- Tabela de logs
CREATE TABLE logs (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  tipo TEXT NOT NULL,
  descricao TEXT NOT NULL,
  data TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  dispositivo_id UUID REFERENCES dispositivos(id),
  dados_adicionais JSONB
);
```

### 4. Configuração de Políticas de Segurança

Para proteger seus dados, configure políticas de acesso no Supabase:

1. Acesse "Authentication" > "Policies" no menu lateral
2. Para cada tabela, clique em "New Policy"
3. Configure políticas adequadas, por exemplo:

```sql
-- Política para tabela clientes (apenas usuários autenticados podem ler)
CREATE POLICY "Usuários autenticados podem ler clientes" 
ON clientes FOR SELECT 
TO authenticated 
USING (true);

-- Política para inserção de diagnósticos
CREATE POLICY "Inserção de diagnósticos permitida" 
ON diagnosticos FOR INSERT 
TO authenticated 
WITH CHECK (true);
```

## Estrutura de Tabelas

### Tabela: clientes

Armazena informações sobre os clientes que utilizam o serviço.

| Coluna | Tipo | Descrição |
|--------|------|-----------|
| id | UUID | Identificador único do cliente (chave primária) |
| nome | TEXT | Nome completo do cliente |
| email | TEXT | Email do cliente (único) |
| telefone | TEXT | Número de telefone do cliente |
| created_at | TIMESTAMP | Data e hora de cadastro do cliente |

### Tabela: dispositivos

Armazena informações sobre os dispositivos dos clientes.

| Coluna | Tipo | Descrição |
|--------|------|-----------|
| id | UUID | Identificador único do dispositivo (chave primária) |
| cliente_id | UUID | Referência ao cliente proprietário (chave estrangeira) |
| nome | TEXT | Nome do dispositivo (ex: "Notebook Dell") |
| sistema_operacional | TEXT | Sistema operacional instalado |
| processador | TEXT | Modelo do processador |
| memoria | TEXT | Quantidade e tipo de memória RAM |
| armazenamento | TEXT | Tipo e capacidade de armazenamento |
| sistema_original | BOOLEAN | Indica se o sistema operacional é original |
| created_at | TIMESTAMP | Data e hora de cadastro do dispositivo |

### Tabela: diagnosticos

Armazena os resultados dos diagnósticos realizados.

| Coluna | Tipo | Descrição |
|--------|------|-----------|
| id | UUID | Identificador único do diagnóstico (chave primária) |
| dispositivo_id | UUID | Referência ao dispositivo diagnosticado (chave estrangeira) |
| data | TIMESTAMP | Data e hora do diagnóstico |
| resultado | JSONB | Resultado completo do diagnóstico em formato JSON |
| score_geral | INTEGER | Pontuação geral do sistema (0-100) |
| problemas | JSONB | Lista de problemas encontrados em formato JSON |

### Tabela: reparos

Armazena informações sobre os reparos realizados após diagnósticos.

| Coluna | Tipo | Descrição |
|--------|------|-----------|
| id | UUID | Identificador único do reparo (chave primária) |
| diagnostico_id | UUID | Referência ao diagnóstico relacionado (chave estrangeira) |
| data | TIMESTAMP | Data e hora do reparo |
| acoes_realizadas | JSONB | Lista de ações realizadas em formato JSON |
| backup_realizado | BOOLEAN | Indica se foi realizado backup antes do reparo |
| resultado | TEXT | Resultado final do reparo |

### Tabela: logs

Armazena logs de ações e eventos do sistema.

| Coluna | Tipo | Descrição |
|--------|------|-----------|
| id | UUID | Identificador único do log (chave primária) |
| tipo | TEXT | Tipo de log (ex: "erro", "info", "aviso") |
| descricao | TEXT | Descrição do evento |
| data | TIMESTAMP | Data e hora do evento |
| dispositivo_id | UUID | Referência ao dispositivo relacionado (opcional) |
| dados_adicionais | JSONB | Dados adicionais em formato JSON |

## Integração com o TechCare

### Atualização das Credenciais

Para conectar o TechCare ao seu banco de dados Supabase, edite o arquivo `/js/database.js`:

```javascript
class DatabaseManager {
  constructor() {
    // Substitua com suas credenciais do Supabase
    this.supabaseUrl = 'https://seu-projeto.supabase.co';
    this.supabaseKey = 'sua-chave-anon-public';
    this.supabase = null;
    this.inicializado = false;
  }
  
  // Resto do código...
}
```

### Verificação da Conexão

Para verificar se a conexão com o banco de dados está funcionando corretamente:

1. Abra o console do navegador (F12) enquanto usa o TechCare
2. Verifique se há mensagens de erro relacionadas ao Supabase
3. Você deve ver mensagens como "Conexão com banco de dados inicializada com sucesso"

## Operações Comuns

### Consulta de Histórico de Diagnósticos

Para consultar o histórico de diagnósticos de um cliente:

```javascript
// Exemplo de código para consultar histórico
async function consultarHistorico(clienteId) {
  try {
    // Inicializar conexão com Supabase
    const { createClient } = supabase;
    const supabaseClient = createClient(supabaseUrl, supabaseKey);
    
    // Consultar dispositivos do cliente
    const { data: dispositivos, error: erroDispositivos } = await supabaseClient
      .from('dispositivos')
      .select('id, nome')
      .eq('cliente_id', clienteId);
      
    if (erroDispositivos) throw erroDispositivos;
    
    // Consultar diagnósticos para cada dispositivo
    const historico = [];
    for (const dispositivo of dispositivos) {
      const { data: diagnosticos, error: erroDiagnosticos } = await supabaseClient
        .from('diagnosticos')
        .select('id, data, score_geral, problemas')
        .eq('dispositivo_id', dispositivo.id)
        .order('data', { ascending: false });
        
      if (erroDiagnosticos) throw erroDiagnosticos;
      
      historico.push({
        dispositivo: dispositivo.nome,
        diagnosticos: diagnosticos
      });
    }
    
    return historico;
  } catch (erro) {
    console.error('Erro ao consultar histórico:', erro);
    return null;
  }
}
```

### Registro de Novo Cliente e Dispositivo

Para registrar um novo cliente e seu dispositivo:

```javascript
// Exemplo de código para registrar cliente e dispositivo
async function registrarClienteDispositivo(dadosCliente, dadosDispositivo) {
  try {
    // Inicializar conexão com Supabase
    const { createClient } = supabase;
    const supabaseClient = createClient(supabaseUrl, supabaseKey);
    
    // Inserir cliente
    const { data: cliente, error: erroCliente } = await supabaseClient
      .from('clientes')
      .insert([
        {
          nome: dadosCliente.nome,
          email: dadosCliente.email,
          telefone: dadosCliente.telefone
        }
      ])
      .select();
      
    if (erroCliente) throw erroCliente;
    
    // Inserir dispositivo
    const { data: dispositivo, error: erroDispositivo } = await supabaseClient
      .from('dispositivos')
      .insert([
        {
          cliente_id: cliente[0].id,
          nome: dadosDispositivo.nome,
          sistema_operacional: dadosDispositivo.sistema,
          processador: dadosDispositivo.processador,
          memoria: dadosDispositivo.memoria,
          armazenamento: dadosDispositivo.armazenamento,
          sistema_original: dadosDispositivo.original
        }
      ])
      .select();
      
    if (erroDispositivo) throw erroDispositivo;
    
    return {
      cliente: cliente[0],
      dispositivo: dispositivo[0]
    };
  } catch (erro) {
    console.error('Erro ao registrar cliente e dispositivo:', erro);
    return null;
  }
}
```

### Salvamento de Resultados de Diagnóstico

Para salvar os resultados de um diagnóstico:

```javascript
// Exemplo de código para salvar resultados de diagnóstico
async function salvarDiagnostico(dispositivoId, resultados) {
  try {
    // Inicializar conexão com Supabase
    const { createClient } = supabase;
    const supabaseClient = createClient(supabaseUrl, supabaseKey);
    
    // Inserir diagnóstico
    const { data: diagnostico, error: erroDiagnostico } = await supabaseClient
      .from('diagnosticos')
      .insert([
        {
          dispositivo_id: dispositivoId,
          resultado: resultados,
          score_geral: resultados.scoreGeral,
          problemas: resultados.problemas
        }
      ])
      .select();
      
    if (erroDiagnostico) throw erroDiagnostico;
    
    return diagnostico[0];
  } catch (erro) {
    console.error('Erro ao salvar diagnóstico:', erro);
    return null;
  }
}
```

### Registro de Reparos

Para registrar os reparos realizados:

```javascript
// Exemplo de código para registrar reparos
async function registrarReparo(diagnosticoId, acoes, backupRealizado, resultado) {
  try {
    // Inicializar conexão com Supabase
    const { createClient } = supabase;
    const supabaseClient = createClient(supabaseUrl, supabaseKey);
    
    // Inserir reparo
    const { data: reparo, error: erroReparo } = await supabaseClient
      .from('reparos')
      .insert([
        {
          diagnostico_id: diagnosticoId,
          acoes_realizadas: acoes,
          backup_realizado: backupRealizado,
          resultado: resultado
        }
      ])
      .select();
      
    if (erroReparo) throw erroReparo;
    
    return reparo[0];
  } catch (erro) {
    console.error('Erro ao registrar reparo:', erro);
    return null;
  }
}
```

## Backup e Segurança

### Backup do Banco de Dados

O Supabase oferece backups automáticos, mas você também pode realizar backups manuais:

1. Acesse "Database" > "Backups" no menu lateral do Supabase
2. Clique em "Create backup" para criar um backup manual
3. Para restaurar um backup, clique em "Restore" ao lado do backup desejado

Para exportar dados específicos:

1. Acesse "SQL Editor" no menu lateral
2. Execute um comando como:
   ```sql
   COPY (SELECT * FROM diagnosticos) TO STDOUT WITH CSV HEADER;
   ```
3. Salve o resultado como arquivo CSV

### Segurança de Dados

Para garantir a segurança dos dados:

1. **Nunca compartilhe** suas credenciais do Supabase
2. Configure **políticas de acesso** adequadas para cada tabela
3. Use **autenticação** para proteger o acesso aos dados
4. Ative o **Row Level Security (RLS)** para todas as tabelas
5. Considere **criptografar dados sensíveis** antes de armazená-los
6. Implemente **validação de dados** no lado do cliente e do servidor

## Solução de Problemas

### Problemas Comuns e Soluções

1. **Erro de conexão com o banco de dados**
   - Verifique se as credenciais (URL e chave) estão corretas
   - Confirme se o projeto Supabase está ativo
   - Verifique se há restrições de CORS nas configurações do Supabase

2. **Erro ao inserir dados**
   - Verifique se todos os campos obrigatórios estão sendo preenchidos
   - Confirme se os tipos de dados estão corretos
   - Verifique se há violações de chave única (ex: email duplicado)

3. **Dados não aparecem após inserção**
   - Verifique se a consulta está usando os parâmetros corretos
   - Confirme se as políticas de segurança permitem a leitura dos dados
   - Verifique se há erros no console do navegador

### Logs e Depuração

Para facilitar a depuração de problemas com o banco de dados:

1. Adicione logs detalhados nas operações de banco de dados:
   ```javascript
   console.log('Iniciando operação de banco de dados:', {
     operacao: 'inserir',
     tabela: 'diagnosticos',
     dados: { dispositivo_id, resultado }
   });
   ```

2. Registre erros de banco de dados na tabela de logs:
   ```javascript
   // Registrar erro no banco de dados
   await supabaseClient
     .from('logs')
     .insert([
       {
         tipo: 'erro',
         descricao: `Erro ao salvar diagnóstico: ${erro.message}`,
         dados_adicionais: { erro: erro.toString(), stack: erro.stack }
       }
     ]);
   ```

3. Implemente um sistema de monitoramento para detectar problemas:
   ```javascript
   // Verificar saúde do banco de dados
   async function verificarSaudeBancoDados() {
     try {
       const inicio = Date.now();
       const { data, error } = await supabaseClient
         .from('logs')
         .select('id')
         .limit(1);
         
       const tempo = Date.now() - inicio;
       
       if (error) throw error;
       
       console.log(`Banco de dados respondeu em ${tempo}ms`);
       return tempo < 1000; // Saudável se responder em menos de 1 segundo
     } catch (erro) {
       console.error('Erro ao verificar saúde do banco de dados:', erro);
       return false;
     }
   }
   ```

## Considerações Finais

O banco de dados é um componente crítico do sistema TechCare, armazenando informações importantes sobre clientes, dispositivos, diagnósticos e reparos. Ao configurar e gerenciar corretamente o banco de dados, você garante que o sistema funcione de maneira eficiente e segura.

Lembre-se de:
- Manter suas credenciais seguras
- Realizar backups regulares
- Monitorar o desempenho do banco de dados
- Atualizar as políticas de segurança conforme necessário
- Implementar validação adequada de dados

Para suporte adicional, consulte a [documentação oficial do Supabase](https://supabase.com/docs).
