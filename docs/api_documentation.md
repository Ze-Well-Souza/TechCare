# Documentação da API TechCare

Esta documentação descreve todas as APIs disponíveis no sistema TechCare, incluindo endpoints, parâmetros, respostas esperadas e exemplos de uso.

## Índice

1. [Autenticação](#autenticação)
   - [Login](#login)
   - [Logout](#logout)
   - [Registro](#registro)

2. [Diagnóstico](#diagnóstico)
   - [Executar Diagnóstico](#executar-diagnóstico)
   - [Histórico de Diagnósticos](#histórico-de-diagnósticos)
   - [Detalhes de um Diagnóstico](#detalhes-de-um-diagnóstico)
   - [Métricas do Sistema](#métricas-do-sistema)

3. [Reparo](#reparo)
   - [Criar Plano de Reparo](#criar-plano-de-reparo)
   - [Listar Planos de Reparo](#listar-planos-de-reparo)
   - [Detalhes do Plano de Reparo](#detalhes-do-plano-de-reparo)
   - [Executar Passo de Reparo](#executar-passo-de-reparo)

4. [Drivers](#drivers)
   - [Escanear Drivers](#escanear-drivers)
   - [Baixar Driver](#baixar-driver)
   - [Instalar Driver](#instalar-driver)

5. [Limpeza](#limpeza)
   - [Análise de Armazenamento](#análise-de-armazenamento)
   - [Limpar Arquivos Temporários](#limpar-arquivos-temporários)
   - [Limpar Cache do Sistema](#limpar-cache-do-sistema)

## Autenticação

### Login

**Endpoint:** `POST /auth/login`

**Descrição:** Realiza a autenticação do usuário no sistema.

**Parâmetros de Requisição:**
```
{
    "username": "nome_de_usuario",
    "password": "senha123",
    "remember_me": true|false
}
```

**Respostas:**
- `200 OK`: Login bem-sucedido, redireciona para a página inicial
- `401 Unauthorized`: Credenciais inválidas

**Exemplo de Uso:**
```javascript
fetch('/auth/login', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    username: 'usuario',
    password: 'senha123',
    remember_me: true
  }),
})
.then(response => {
  if (response.redirected) {
    window.location.href = response.url;
  }
});
```

### Logout

**Endpoint:** `GET /auth/logout`

**Descrição:** Encerra a sessão do usuário.

**Respostas:**
- `302 Found`: Redireciona para a página de login

### Registro

**Endpoint:** `POST /auth/register`

**Descrição:** Registra um novo usuário no sistema.

**Parâmetros de Requisição:**
```
{
    "username": "novo_usuario",
    "name": "Nome Completo",
    "email": "email@exemplo.com",
    "password": "senha123",
    "password_confirm": "senha123"
}
```

**Respostas:**
- `200 OK`: Registro bem-sucedido, redireciona para a página de login
- `400 Bad Request`: Parâmetros de requisição inválidos
- `409 Conflict`: Nome de usuário ou email já existente

## Diagnóstico

### Executar Diagnóstico

**Endpoint:** `POST /api/diagnostic/run`

**Descrição:** Executa um diagnóstico completo do sistema.

**Respostas:**
- `200 OK`: Diagnóstico executado com sucesso
  ```json
  {
    "success": true,
    "results": {
      "id": "diag-123456",
      "score": 85,
      "cpu": {"usage": 35, "status": "good"},
      "memory": {"usage": 60, "status": "good"},
      "disk": {"usage": 75, "status": "warning"},
      "problems": [
        {
          "id": "prob-001",
          "category": "disk",
          "title": "Disco com espaço moderado",
          "description": "Seu disco está com espaço moderado.",
          "severity": "warning"
        }
      ]
    }
  }
  ```

**Exemplo de Uso:**
```javascript
fetch('/api/diagnostic/run', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  }
})
.then(response => response.json())
.then(data => console.log(data));
```

### Histórico de Diagnósticos

**Endpoint:** `GET /api/diagnostic/history`

**Descrição:** Retorna o histórico de diagnósticos do usuário.

**Respostas:**
- `200 OK`: Lista de diagnósticos
  ```json
  {
    "success": true,
    "history": [
      {
        "id": "diag-123456",
        "timestamp": "2023-10-01T14:30:00",
        "score": 85,
        "problems_count": 1
      },
      {
        "id": "diag-123457",
        "timestamp": "2023-10-02T16:45:00",
        "score": 70,
        "problems_count": 3
      }
    ]
  }
  ```

### Detalhes de um Diagnóstico

**Endpoint:** `GET /api/diagnostic/{diagnostic_id}`

**Descrição:** Retorna os detalhes de um diagnóstico específico.

**Parâmetros de URL:**
- `diagnostic_id`: ID do diagnóstico

**Respostas:**
- `200 OK`: Detalhes do diagnóstico
  ```json
  {
    "diagnostic": {
      "id": "diag-123456",
      "timestamp": "2023-10-01T14:30:00",
      "score": 85,
      "cpu": {"usage": 35, "status": "good"},
      "memory": {"usage": 60, "status": "good"},
      "disk": {"usage": 75, "status": "warning"},
      "problems": [
        {
          "id": "prob-001",
          "category": "disk",
          "title": "Disco com espaço moderado",
          "description": "Seu disco está com espaço moderado.",
          "severity": "warning"
        }
      ]
    }
  }
  ```
- `404 Not Found`: Diagnóstico não encontrado

### Métricas do Sistema

**Endpoint:** `GET /api/diagnostic/metrics`

**Descrição:** Retorna as métricas atuais do sistema.

**Respostas:**
- `200 OK`: Métricas do sistema
  ```json
  {
    "metrics": {
      "cpu": {
        "usage": 30,
        "status": "good"
      },
      "memory": {
        "total": 8589934592,
        "available": 4294967296,
        "used": 4294967296,
        "percent": 50,
        "status": "good"
      },
      "disk": {
        "total": 107374182400,
        "free": 53687091200,
        "used": 53687091200,
        "percent": 50,
        "status": "good"
      }
    }
  }
  ```

## Reparo

### Criar Plano de Reparo

**Endpoint:** `POST /api/repair/plan/{diagnostic_id}`

**Descrição:** Cria um plano de reparo baseado em um diagnóstico.

**Parâmetros de URL:**
- `diagnostic_id`: ID do diagnóstico

**Respostas:**
- `200 OK`: Plano de reparo criado
  ```json
  {
    "success": true,
    "plan": {
      "plan_id": "plan-123456",
      "diagnostic_id": "diag-123456",
      "total_steps": 2,
      "steps": [
        {
          "id": "step-001",
          "problem_id": "prob-001",
          "title": "Liberar espaço em disco",
          "description": "Remover arquivos temporários para liberar espaço.",
          "status": "pending"
        },
        {
          "id": "step-002",
          "problem_id": "prob-002",
          "title": "Otimizar memória",
          "description": "Fechar aplicativos que consomem muita memória.",
          "status": "pending"
        }
      ]
    }
  }
  ```
- `404 Not Found`: Diagnóstico não encontrado

### Listar Planos de Reparo

**Endpoint:** `GET /api/repair/plans`

**Descrição:** Lista todos os planos de reparo do usuário.

**Respostas:**
- `200 OK`: Lista de planos de reparo
  ```json
  {
    "success": true,
    "plans": [
      {
        "plan_id": "plan-123456",
        "diagnostic_id": "diag-123456",
        "created_at": "2023-10-01T15:00:00",
        "status": "in_progress",
        "completed_steps": 1,
        "total_steps": 2
      },
      {
        "plan_id": "plan-123457",
        "diagnostic_id": "diag-123457",
        "created_at": "2023-10-02T17:00:00",
        "status": "completed",
        "completed_steps": 3,
        "total_steps": 3
      }
    ]
  }
  ```

### Detalhes do Plano de Reparo

**Endpoint:** `GET /api/repair/plan/{plan_id}`

**Descrição:** Retorna os detalhes de um plano de reparo específico.

**Parâmetros de URL:**
- `plan_id`: ID do plano de reparo

**Respostas:**
- `200 OK`: Detalhes do plano de reparo
  ```json
  {
    "success": true,
    "plan": {
      "plan_id": "plan-123456",
      "diagnostic_id": "diag-123456",
      "created_at": "2023-10-01T15:00:00",
      "status": "in_progress",
      "steps": [
        {
          "id": "step-001",
          "problem_id": "prob-001",
          "title": "Liberar espaço em disco",
          "description": "Remover arquivos temporários para liberar espaço.",
          "status": "completed",
          "completed_at": "2023-10-01T15:10:00",
          "result": "Liberado 500MB de espaço"
        },
        {
          "id": "step-002",
          "problem_id": "prob-002",
          "title": "Otimizar memória",
          "description": "Fechar aplicativos que consomem muita memória.",
          "status": "pending"
        }
      ]
    }
  }
  ```
- `404 Not Found`: Plano de reparo não encontrado

### Executar Passo de Reparo

**Endpoint:** `POST /api/repair/execute/{plan_id}/{step_id}`

**Descrição:** Executa um passo específico de um plano de reparo.

**Parâmetros de URL:**
- `plan_id`: ID do plano de reparo
- `step_id`: ID do passo a ser executado

**Respostas:**
- `200 OK`: Passo executado com sucesso
  ```json
  {
    "success": true,
    "result": {
      "step_id": "step-002",
      "new_status": "completed",
      "message": "Memória otimizada com sucesso. Liberado 1.2GB de RAM."
    }
  }
  ```
- `404 Not Found`: Plano ou passo não encontrado
- `400 Bad Request`: O passo não pode ser executado (já completado, etc.)

## Drivers

### Escanear Drivers

**Endpoint:** `GET /api/drivers/scan`

**Descrição:** Escaneia os drivers do sistema para atualizações.

**Respostas:**
- `200 OK`: Resultado do escaneamento
  ```json
  {
    "success": true,
    "results": {
      "total_drivers": 10,
      "outdated_drivers": [
        {
          "device_id": "PCI\\VEN_8086&DEV_0046",
          "name": "Intel HD Graphics",
          "version": "10.18.10.3960",
          "update_available": true,
          "update_info": {
            "latest_version": "27.20.100.9030",
            "download_url": "https://example.com/driver.exe"
          }
        }
      ],
      "problematic_drivers": [],
      "up_to_date_drivers": 9
    }
  }
  ```

### Baixar Driver

**Endpoint:** `POST /api/drivers/download/{driver_id}`

**Descrição:** Inicia o download de um driver específico.

**Parâmetros de URL:**
- `driver_id`: ID do driver

**Respostas:**
- `200 OK`: Download iniciado com sucesso
  ```json
  {
    "success": true,
    "result": {
      "driver_id": "PCI\\VEN_8086&DEV_0046",
      "file_path": "C:\\data\\drivers\\intel_graphics_27.20.100.9030.exe",
      "download_progress": 0
    }
  }
  ```
- `404 Not Found`: Driver não encontrado

### Instalar Driver

**Endpoint:** `POST /api/drivers/install/{driver_id}`

**Descrição:** Instala um driver previamente baixado.

**Parâmetros de URL:**
- `driver_id`: ID do driver

**Respostas:**
- `200 OK`: Instalação bem-sucedida
  ```json
  {
    "success": true,
    "result": {
      "driver_id": "PCI\\VEN_8086&DEV_0046",
      "version": "27.20.100.9030",
      "message": "Driver instalado com sucesso."
    }
  }
  ```
- `404 Not Found`: Driver não encontrado
- `400 Bad Request`: Driver não baixado ou erro na instalação

## Limpeza

### Análise de Armazenamento

**Endpoint:** `GET /api/cleaner/analyze`

**Descrição:** Analisa o armazenamento do sistema e identifica arquivos que podem ser removidos.

**Respostas:**
- `200 OK`: Resultado da análise
  ```json
  {
    "success": true,
    "analysis": {
      "total_disk_space": 107374182400,
      "free_space": 53687091200,
      "categories": [
        {
          "name": "temp_files",
          "size": 2147483648,
          "count": 1500,
          "description": "Arquivos temporários"
        },
        {
          "name": "cache",
          "size": 1073741824,
          "count": 500,
          "description": "Arquivos de cache"
        },
        {
          "name": "logs",
          "size": 536870912,
          "count": 100,
          "description": "Arquivos de log"
        }
      ]
    }
  }
  ```

### Limpar Arquivos Temporários

**Endpoint:** `POST /api/cleaner/cleanup/temp_files`

**Descrição:** Remove arquivos temporários do sistema.

**Respostas:**
- `200 OK`: Limpeza bem-sucedida
  ```json
  {
    "success": true,
    "result": {
      "space_freed": 2147483648,
      "files_removed": 1500,
      "message": "Arquivos temporários removidos com sucesso."
    }
  }
  ```

### Limpar Cache do Sistema

**Endpoint:** `POST /api/cleaner/cleanup/cache`

**Descrição:** Remove arquivos de cache do sistema.

**Respostas:**
- `200 OK`: Limpeza bem-sucedida
  ```json
  {
    "success": true,
    "result": {
      "space_freed": 1073741824,
      "files_removed": 500,
      "message": "Cache do sistema limpo com sucesso."
    }
  }
  ``` 