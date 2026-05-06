# PNCP API - Guia de Integração

Ferramentas Python para buscar editais, contratos e atas do Portal Nacional de Contratações Públicas (PNCP) e integrá-los com sua aplicação Flask ou Microsoft Dynamics 365.

---

## 📋 Conteúdo

1. **pncp_api_client.py** - Cliente Python para consumir API do PNCP
2. **flask_pncp_api.py** - Endpoints Flask para expor API do PNCP
3. **pncp_dynamics_sync.py** - Sincronização com Microsoft Dynamics 365
4. **requirements.txt** - Dependências Python

---

## 🚀 Instalação Rápida

### 1. Criar ambiente virtual (recomendado)

```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate  # Windows
```

### 2. Instalar dependências

```bash
pip install requests flask
```

---

## 💻 Uso 1: Cliente Python Direto

### Importar e usar

```python
from pncp_api_client import PNCPClient

# Criar cliente
client = PNCPClient()

# Buscar editais dos últimos 7 dias
editais = client.buscar_editais(
    dias=7,
    quantidade=20
)

# Buscar contratos
contratos = client.buscar_contratos(
    data_inicio="2024-01-01",
    data_fim="2024-12-31"
)

# Buscar atas de registro de preço
atas = client.buscar_atas(
    quantidade=10
)

# Fechar conexão
client.fechar()
```

### Métodos disponíveis

#### `buscar_editais()`
```python
editais = client.buscar_editais(
    pagina=1,                          # Número da página (padrão: 1)
    quantidade=10,                     # Registros por página (máx: 100)
    data_inicio="2024-01-01",         # Data inicial
    data_fim="2024-12-31",            # Data final
    situacao="DIVULGADA",             # Situação do edital
    orgao="Ministério da Educação"    # Nome/CNPJ do órgão
)
```

#### `buscar_contratos()`
```python
contratos = client.buscar_contratos(
    pagina=1,
    quantidade=10,
    data_inicio="2024-01-01",
    data_fim="2024-12-31",
    orgao="Ministério da Educação"
)
```

#### `buscar_atas()`
```python
atas = client.buscar_atas(
    pagina=1,
    quantidade=10,
    data_inicio="2024-01-01",
    data_fim="2024-12-31"
)
```

#### `buscar_planos_contratacao()`
```python
planos = client.buscar_planos_contratacao(
    pagina=1,
    quantidade=10,
    ano=2024,
    orgao="Ministério da Educação"
)
```

---

## 🌐 Uso 2: API Flask

### Iniciar servidor

```bash
python flask_pncp_api.py
```

O servidor estará disponível em `http://localhost:5000`

### Endpoints disponíveis

#### GET `/api/pncp/editais`

Buscar editais

**Query Parameters:**
```
pagina=1                    # Número da página
quantidade=10              # Registros por página
data_inicio=2024-01-01    # Data inicial
data_fim=2024-12-31       # Data final
dias=7                     # Alternativamente, últimos N dias
situacao=DIVULGADA         # Situação
orgao=Ministério           # Órgão
```

**Exemplos:**

```bash
# Últimos 7 dias, 20 registros
curl "http://localhost:5000/api/pncp/editais?dias=7&quantidade=20"

# Data específica
curl "http://localhost:5000/api/pncp/editais?data_inicio=2024-01-01&data_fim=2024-01-31"

# Por órgão
curl "http://localhost:5000/api/pncp/editais?orgao=Ministério%20da%20Educação&quantidade=50"

# Paginação
curl "http://localhost:5000/api/pncp/editais?pagina=2&quantidade=100"
```

**Resposta:**
```json
{
  "sucesso": true,
  "quantidade": 20,
  "pagina": 1,
  "data_consulta": "2024-05-06T15:30:00",
  "filtros": {
    "data_inicio": "2024-04-29",
    "data_fim": "2024-05-06",
    "situacao": null,
    "orgao": null
  },
  "dados": [
    {
      "id": "12345...",
      "numero": "001/2024",
      "objeto": "Aquisição de material de consumo",
      "orgao": {
        "nome": "Ministério da Educação",
        "cnpj": "00.000.000/0000-00"
      },
      "valor": 50000.00,
      "dataPublicacao": "2024-05-06",
      "situacao": "DIVULGADA"
    }
  ]
}
```

#### GET `/api/pncp/contratos`

Buscar contratos

```bash
curl "http://localhost:5000/api/pncp/contratos?dias=30&quantidade=10"
```

#### GET `/api/pncp/atas`

Buscar atas de registro de preço

```bash
curl "http://localhost:5000/api/pncp/atas?quantidade=5"
```

#### GET `/api/pncp/planos`

Buscar planos de contratação

```bash
curl "http://localhost:5000/api/pncp/planos?ano=2024&quantidade=20"
```

#### GET `/api/pncp/status`

Verificar status da API

```bash
curl "http://localhost:5000/api/pncp/status"
```

---

## 🔄 Uso 3: Sincronização com Dynamics 365

### Configuração

1. Criar aplicação no Azure AD
2. Obter credentials (Client ID, Tenant ID, Client Secret)
3. Configurar as credenciais no script

### Usar sincronização

```python
from pncp_dynamics_sync import PNCPDynamicsSync

# Configurar sincronização
sync = PNCPDynamicsSync(
    client_id='seu_client_id',
    tenant_id='seu_tenant_id',
    client_secret='seu_client_secret',
    instance_url='https://seu-org.crm.dynamics.com'
)

# Sincronizar editais dos últimos 7 dias
resultado = sync.sincronizar_editais(
    dias=7,
    quantidade_pagina=50,
    limite_registros=100  # Opcional: limitar registros
)

# Ver resultado
print(f"Criados: {resultado['total_criado']}")
print(f"Erros: {resultado['total_erro']}")
```

### O que acontece na sincronização

1. **Busca editais** no PNCP dos últimos N dias
2. **Cria Accounts** para órgãos não cadastrados no Dynamics
3. **Cria Opportunities** com informações dos editais
4. **Mapeia campos** relevantes (número, objeto, valor, órgão, etc.)
5. **Retorna relatório** com quantidade de sucessos e erros

### Mapeamento de campos (Dynamics)

| Campo PNCP | Campo Dynamics |
|---|---|
| número | new_pncp_numero_edital |
| objeto | description |
| valor | estimatedvalue |
| órgão | new_pncp_orgao |
| data publicação | new_pncp_data_publicacao |
| situação | stagecode |

---

## 📊 Exemplos Práticos

### Exemplo 1: Buscar editais de um órgão específico

```python
from pncp_api_client import PNCPClient

client = PNCPClient()

editais = client.buscar_editais(
    orgao="Ministério da Educação",
    quantidade=50
)

for edital in editais:
    print(f"{edital['numero']}: R$ {edital.get('valor', 0):,.2f}")
```

### Exemplo 2: Exportar editais para CSV

```python
import csv
from pncp_api_client import PNCPClient

client = PNCPClient()

editais = client.buscar_editais(
    dias=30,
    quantidade=100
)

with open('editais.csv', 'w', newline='', encoding='utf-8') as f:
    writer = csv.writer(f)
    writer.writerow(['Número', 'Órgão', 'Objeto', 'Valor', 'Data'])
    
    for edital in editais:
        writer.writerow([
            edital.get('numero', ''),
            edital.get('orgao', {}).get('nome', ''),
            edital.get('objeto', '')[:100],
            edital.get('valor', 0),
            edital.get('dataPublicacao', '')
        ])

print(f"Exportados {len(editais)} editais para editais.csv")
```

### Exemplo 3: Integrar ao Flask existente

```python
from flask import Flask, jsonify
from pncp_api_client import PNCPClient

app = Flask(__name__)
pncp = PNCPClient()

@app.route('/oportunidades')
def oportunidades():
    editais = pncp.buscar_editais(dias=7, quantidade=20)
    return jsonify(editais)

if __name__ == '__main__':
    app.run()
```

### Exemplo 4: Buscar contratações por período

```python
from pncp_api_client import PNCPClient
from datetime import datetime

client = PNCPClient()

# Buscar contratações do mês anterior
hoje = datetime.now()
primeiro_dia = toda.replace(day=1)
ultimo_dia = (primeiro_dia - timedelta(days=1)).replace(day=1)

editais = client.buscar_editais(
    data_inicio=ultimo_dia.strftime("%Y-%m-%d"),
    data_fim=primeiro_dia.strftime("%Y-%m-%d"),
    quantidade=100
)

total = sum(e.get('valor', 0) for e in editais)
print(f"Total em editais do mês anterior: R$ {total:,.2f}")
```

---

## 🔍 Tratamento de Erros

Os métodos retornam listas vazias em caso de erro:

```python
from pncp_api_client import PNCPClient
import logging

# Ativar logging para ver erros
logging.basicConfig(level=logging.INFO)

client = PNCPClient(timeout=10)

editais = client.buscar_editais(dias=7)

if not editais:
    print("Erro ao buscar editais ou nenhum resultado encontrado")
else:
    print(f"Encontrados {len(editais)} editais")
```

---

## ⚙️ Configuração Avançada

### Aumentar timeout

```python
client = PNCPClient(timeout=60)  # 60 segundos
```

### Customizar headers

```python
client = PNCPClient()
client.session.headers.update({
    'User-Agent': 'MeuApp/1.0'
})
```

### Usar proxy

```python
proxies = {
    'http': 'http://seu-proxy:8080',
    'https': 'https://seu-proxy:8080'
}

client = PNCPClient()
client.session.proxies.update(proxies)
```

---

## 📝 Estrutura de resposta típica (Edital)

```json
{
  "id": "00509968000148-1-000113/2024",
  "numero": "113/2024",
  "objeto": "Aquisição de material de consumo para o exercício de 2024",
  "orgao": {
    "id": "00509968000148",
    "nome": "TRIBUNAL SUPERIOR DO TRABALHO",
    "cnpj": "00.509.968/0000-48"
  },
  "valor": 50000.00,
  "dataPublicacao": "2024-05-06",
  "dataAbertura": "2024-05-20",
  "situacao": "DIVULGADA",
  "modalidade": "Pregão Eletrônico",
  "tipo": "Edital"
}
```

---

## 🆘 Troubleshooting

### Erro: "Connection refused"
- Verificar se servidor PNCP está acessível
- Verificar conexão de internet

### Erro: "Timeout"
- Aumentar timeout: `PNCPClient(timeout=60)`
- Reduzir quantidade de registros por página

### Sem resultados
- Verificar datas (API é sensível a formato)
- Tentar aumentar período (dias ou datas)
- Verificar parametrização (orgão, situação, etc.)

### Rate limit
- API PNCP não tem rate limit documentado
- Adicionar pequenos delays entre requisições se necessário

```python
import time

for pagina in range(1, 11):
    editais = client.buscar_editais(pagina=pagina, quantidade=50)
    print(f"Página {pagina}: {len(editais)} registros")
    time.sleep(1)  # 1 segundo entre requisições
```

---

## 📚 Documentação Oficial

- **PNCP Portal**: https://www.gov.br/pncp/pt-br
- **API Swagger**: https://pncp.gov.br/api/consulta/swagger-ui/index.html
- **Dados Abertos**: https://www.gov.br/pncp/pt-br/acesso-a-informacao/dados-abertos
- **Manual de Integração**: https://www.gov.br/pncp/pt-br/central-de-conteudo/manuais

---

## 📄 Licença

Código fornecido como-é para fins de integração com PNCP.

---

## 💡 Dicas

1. **Caching**: Implemente cache local para evitar requisições repetidas
2. **Agendamento**: Use `schedule` ou `APScheduler` para sincronizações automáticas
3. **Logging**: Mantenha logs detalhados de todas as sincronizações
4. **Validação**: Validar dados antes de enviar para Dynamics
5. **Backup**: Fazer backup de dados antes de sincronizações em larga escala

---

**Criado em**: Maio 2024  
**Última atualização**: Maio 2024
