"""
PNCP API Client - Busca de Editais
Portal Nacional de Contratações Públicas

Uso:
    client = PNCPClient()
    editais = client.buscar_editais(
        pagina=1,
        quantidade=10,
        data_inicio="2024-01-01",
        data_fim="2024-12-31"
    )
"""

import requests
import json
from datetime import datetime
from typing import List, Dict, Optional
import logging

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class PNCPClient:
    """Cliente para consumir API do Portal Nacional de Contratações Públicas"""
    
    # URLs base da API
    BASE_URL = "https://pncp.gov.br/api/consulta"
    
    # Endpoints disponíveis
    ENDPOINTS = {
        'editais': '/compras',
        'contratos': '/contratos',
        'atas': '/atas',
        'planos': '/planos-contratacoes-anual'
    }
    
    def __init__(self, timeout: int = 30):
        """
        Inicializa o cliente PNCP
        
        Args:
            timeout: Timeout para requisições em segundos
        """
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers.update({
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        })
    
    def _fazer_requisicao(self, endpoint: str, params: Dict) -> Optional[Dict]:
        """
        Faz uma requisição à API PNCP
        
        Args:
            endpoint: Endpoint a chamar
            params: Parâmetros da requisição
            
        Returns:
            Resposta JSON ou None em caso de erro
        """
        url = f"{self.BASE_URL}{endpoint}"
        
        try:
            logger.info(f"Buscando: {url} com params: {params}")
            response = self.session.get(url, params=params, timeout=self.timeout)
            response.raise_for_status()
            
            data = response.json()
            logger.info(f"Status: {response.status_code} - {len(data.get('content', []))} registros retornados")
            return data
            
        except requests.exceptions.Timeout:
            logger.error(f"Timeout na requisição a {url}")
            return None
        except requests.exceptions.ConnectionError:
            logger.error(f"Erro de conexão com {url}")
            return None
        except requests.exceptions.HTTPError as e:
            logger.error(f"Erro HTTP {e.response.status_code}: {e}")
            return None
        except json.JSONDecodeError:
            logger.error(f"Resposta não é JSON válido")
            return None
        except Exception as e:
            logger.error(f"Erro inesperado: {e}")
            return None
    
    def buscar_editais(
        self,
        pagina: int = 1,
        quantidade: int = 10,
        data_inicio: Optional[str] = None,
        data_fim: Optional[str] = None,
        situacao: Optional[str] = None,
        orgao: Optional[str] = None,
        **kwargs
    ) -> List[Dict]:
        """
        Busca editais no PNCP
        
        Args:
            pagina: Número da página (padrão: 1)
            quantidade: Quantidade de registros por página (padrão: 10, máx: 100)
            data_inicio: Data inicial (formato: YYYY-MM-DD)
            data_fim: Data final (formato: YYYY-MM-DD)
            situacao: Situação do edital (ex: "DIVULGADA", "EM_ANDAMENTO")
            orgao: CNPJ ou nome do órgão
            **kwargs: Parâmetros adicionais
            
        Returns:
            Lista de editais encontrados
        """
        
        # Validar e limitar quantidade
        quantidade = min(max(quantidade, 1), 100)
        
        params = {
            'page': pagina - 1,  # API usa page zero-indexed
            'size': quantidade,
        }
        
        # Adicionar filtros opcionais
        if data_inicio:
            params['dataInicio'] = data_inicio
        if data_fim:
            params['dataFim'] = data_fim
        if situacao:
            params['situacao'] = situacao
        if orgao:
            params['orgao'] = orgao
        
        # Adicionar kwargs
        params.update(kwargs)
        
        resultado = self._fazer_requisicao(self.ENDPOINTS['editais'], params)
        
        if resultado is None:
            return []
        
        return resultado.get('content', [])
    
    def buscar_contratos(
        self,
        pagina: int = 1,
        quantidade: int = 10,
        data_inicio: Optional[str] = None,
        data_fim: Optional[str] = None,
        orgao: Optional[str] = None,
        **kwargs
    ) -> List[Dict]:
        """
        Busca contratos no PNCP
        
        Args:
            pagina: Número da página
            quantidade: Quantidade de registros por página
            data_inicio: Data inicial (formato: YYYY-MM-DD)
            data_fim: Data final (formato: YYYY-MM-DD)
            orgao: CNPJ ou nome do órgão
            **kwargs: Parâmetros adicionais
            
        Returns:
            Lista de contratos encontrados
        """
        
        quantidade = min(max(quantidade, 1), 100)
        
        params = {
            'page': pagina - 1,
            'size': quantidade,
        }
        
        if data_inicio:
            params['dataInicio'] = data_inicio
        if data_fim:
            params['dataFim'] = data_fim
        if orgao:
            params['orgao'] = orgao
        
        params.update(kwargs)
        
        resultado = self._fazer_requisicao(self.ENDPOINTS['contratos'], params)
        return resultado.get('content', []) if resultado else []
    
    def buscar_atas(
        self,
        pagina: int = 1,
        quantidade: int = 10,
        data_inicio: Optional[str] = None,
        data_fim: Optional[str] = None,
        **kwargs
    ) -> List[Dict]:
        """
        Busca Atas de Registro de Preço
        
        Args:
            pagina: Número da página
            quantidade: Quantidade de registros por página
            data_inicio: Data inicial (formato: YYYY-MM-DD)
            data_fim: Data final (formato: YYYY-MM-DD)
            **kwargs: Parâmetros adicionais
            
        Returns:
            Lista de atas encontradas
        """
        
        quantidade = min(max(quantidade, 1), 100)
        
        params = {
            'page': pagina - 1,
            'size': quantidade,
        }
        
        if data_inicio:
            params['dataInicio'] = data_inicio
        if data_fim:
            params['dataFim'] = data_fim
        
        params.update(kwargs)
        
        resultado = self._fazer_requisicao(self.ENDPOINTS['atas'], params)
        return resultado.get('content', []) if resultado else []
    
    def buscar_planos_contratacao(
        self,
        pagina: int = 1,
        quantidade: int = 10,
        ano: Optional[int] = None,
        orgao: Optional[str] = None,
        **kwargs
    ) -> List[Dict]:
        """
        Busca Planos de Contratação Anual
        
        Args:
            pagina: Número da página
            quantidade: Quantidade de registros por página
            ano: Ano do plano
            orgao: CNPJ ou nome do órgão
            **kwargs: Parâmetros adicionais
            
        Returns:
            Lista de planos encontrados
        """
        
        quantidade = min(max(quantidade, 1), 100)
        
        params = {
            'page': pagina - 1,
            'size': quantidade,
        }
        
        if ano:
            params['ano'] = ano
        if orgao:
            params['orgao'] = orgao
        
        params.update(kwargs)
        
        resultado = self._fazer_requisicao(self.ENDPOINTS['planos'], params)
        return resultado.get('content', []) if resultado else []
    
    def fechar(self):
        """Fecha a sessão HTTP"""
        self.session.close()


def exemplo_uso():
    """Exemplos de uso do cliente PNCP"""
    
    client = PNCPClient()
    
    print("=" * 80)
    print("EXEMPLO 1: Buscar editais dos últimos 30 dias")
    print("=" * 80)
    
    data_fim = datetime.now().strftime("%Y-%m-%d")
    data_inicio = datetime.now().strftime("%Y-%m-01")  # Início do mês
    
    editais = client.buscar_editais(
        quantidade=5,
        data_inicio=data_inicio,
        data_fim=data_fim
    )
    
    if editais:
        for i, edital in enumerate(editais, 1):
            print(f"\n{i}. {edital.get('numero', 'N/A')}")
            print(f"   Órgão: {edital.get('orgao', {}).get('nome', 'N/A')}")
            print(f"   Objeto: {edital.get('objeto', 'N/A')[:100]}...")
            print(f"   Data Publicação: {edital.get('dataPublicacao', 'N/A')}")
            print(f"   ID PNCP: {edital.get('id', 'N/A')}")
    else:
        print("Nenhum edital encontrado")
    
    print("\n" + "=" * 80)
    print("EXEMPLO 2: Buscar contratos")
    print("=" * 80)
    
    contratos = client.buscar_contratos(quantidade=3)
    
    if contratos:
        for i, contrato in enumerate(contratos, 1):
            print(f"\n{i}. {contrato.get('numero', 'N/A')}")
            print(f"   Valor: R$ {contrato.get('valor', 0):,.2f}")
            print(f"   Data: {contrato.get('dataPublicacao', 'N/A')}")
    else:
        print("Nenhum contrato encontrado")
    
    print("\n" + "=" * 80)
    print("EXEMPLO 3: Buscar atas de registro de preço")
    print("=" * 80)
    
    atas = client.buscar_atas(quantidade=3)
    
    if atas:
        for i, ata in enumerate(atas, 1):
            print(f"\n{i}. {ata.get('numero', 'N/A')}")
            print(f"   Vigência: {ata.get('dataInicio', 'N/A')} a {ata.get('dataFim', 'N/A')}")
    else:
        print("Nenhuma ata encontrada")
    
    client.fechar()


if __name__ == "__main__":
    exemplo_uso()
