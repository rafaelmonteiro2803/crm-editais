"""
PNCP API Client - Busca de Editais
Portal Nacional de Contratações Públicas

Uso:
    client = PNCPClient()
    editais = client.buscar_editais(
        pagina=1,
        quantidade=10,
        data_inicio="2024-01-01",
        data_fim="2024-12-31",
        modalidade=6
    )

Códigos de modalidade (codigoModalidadeContratacao):
    1  = Leilão Eletrônico
    2  = Diálogo Competitivo
    3  = Concurso
    4  = Concorrência Eletrônica
    5  = Concorrência Presencial
    6  = Pregão Eletrônico
    7  = Pregão Presencial
    8  = Dispensa de Licitação
    9  = Inexigibilidade de Licitação
    10 = Manifestação de Interesse
    11 = Pré-qualificação
    12 = Credenciamento
    13 = Leilão Presencial
"""

import requests
import json
from datetime import datetime
from typing import List, Dict, Optional
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def _formatar_data(data: str) -> str:
    """Converte YYYY-MM-DD para YYYYMMDD exigido pela API PNCP."""
    return data.replace('-', '')


class PNCPClient:
    """Cliente para consumir API do Portal Nacional de Contratações Públicas"""

    BASE_URL = "https://pncp.gov.br/api/consulta/v1"

    ENDPOINTS = {
        'editais': '/contratacoes/publicacao',
        'contratos': '/contratos',
        'atas': '/atas',
        'planos': '/pca/atualizacao',
    }

    def __init__(self, timeout: int = 30):
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers.update({
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        })

    def _fazer_requisicao(self, endpoint: str, params: Dict) -> Optional[Dict]:
        url = f"{self.BASE_URL}{endpoint}"

        try:
            logger.info(f"Buscando: {url} com params: {params}")
            response = self.session.get(url, params=params, timeout=self.timeout)
            response.raise_for_status()

            data = response.json()
            total = data.get('totalRegistros', len(data.get('data', [])))
            logger.info(f"Status: {response.status_code} - {total} registros no total")
            return data

        except requests.exceptions.Timeout:
            logger.error(f"Timeout na requisição a {url}")
            return None
        except requests.exceptions.ConnectionError:
            logger.error(f"Erro de conexão com {url}")
            return None
        except requests.exceptions.HTTPError as e:
            logger.error(f"Erro HTTP {e.response.status_code}: {e.response.text}")
            return None
        except json.JSONDecodeError:
            logger.error("Resposta não é JSON válido")
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
        modalidade: Optional[int] = None,
        uf: Optional[str] = None,
        cnpj: Optional[str] = None,
        **kwargs
    ) -> Dict:
        """
        Busca contratações (editais) no PNCP.

        Args:
            pagina: Número da página (padrão: 1)
            quantidade: Registros por página (padrão: 10, máx: 50)
            data_inicio: Data inicial publicação (YYYY-MM-DD)
            data_fim: Data final publicação (YYYY-MM-DD)
            modalidade: Código da modalidade de contratação (obrigatório na API PNCP)
            uf: Sigla do estado (ex: SP, RJ)
            cnpj: CNPJ do órgão

        Returns:
            Dict com 'data' (lista), 'totalRegistros', 'totalPaginas', 'numeroPagina'
        """
        quantidade = min(max(quantidade, 10), 50)

        params = {
            'pagina': pagina,
            'tamanhoPagina': quantidade,
        }

        if data_inicio:
            params['dataInicial'] = _formatar_data(data_inicio)
        if data_fim:
            params['dataFinal'] = _formatar_data(data_fim)
        if modalidade is not None:
            params['codigoModalidadeContratacao'] = modalidade
        if uf:
            params['uf'] = uf.upper()
        if cnpj:
            params['cnpj'] = cnpj

        params.update(kwargs)

        resultado = self._fazer_requisicao(self.ENDPOINTS['editais'], params)
        return resultado if resultado is not None else {'data': [], 'totalRegistros': 0}

    def buscar_contratos(
        self,
        pagina: int = 1,
        quantidade: int = 10,
        data_inicio: Optional[str] = None,
        data_fim: Optional[str] = None,
        cnpj_orgao: Optional[str] = None,
        **kwargs
    ) -> Dict:
        """
        Busca contratos no PNCP.

        Args:
            pagina: Número da página (padrão: 1)
            quantidade: Registros por página (padrão: 10, máx: 500)
            data_inicio: Data inicial publicação (YYYY-MM-DD)
            data_fim: Data final publicação (YYYY-MM-DD)
            cnpj_orgao: CNPJ do órgão contratante
        """
        quantidade = min(max(quantidade, 10), 500)

        params = {
            'pagina': pagina,
            'tamanhoPagina': quantidade,
        }

        if data_inicio:
            params['dataInicial'] = _formatar_data(data_inicio)
        if data_fim:
            params['dataFinal'] = _formatar_data(data_fim)
        if cnpj_orgao:
            params['cnpjOrgao'] = cnpj_orgao

        params.update(kwargs)

        resultado = self._fazer_requisicao(self.ENDPOINTS['contratos'], params)
        return resultado if resultado is not None else {'data': [], 'totalRegistros': 0}

    def buscar_atas(
        self,
        pagina: int = 1,
        quantidade: int = 10,
        data_inicio: Optional[str] = None,
        data_fim: Optional[str] = None,
        cnpj: Optional[str] = None,
        **kwargs
    ) -> Dict:
        """
        Busca Atas de Registro de Preço no PNCP.

        Args:
            pagina: Número da página (padrão: 1)
            quantidade: Registros por página (padrão: 10, máx: 500)
            data_inicio: Data inicial vigência (YYYY-MM-DD)
            data_fim: Data final vigência (YYYY-MM-DD)
            cnpj: CNPJ do órgão
        """
        quantidade = min(max(quantidade, 10), 500)

        params = {
            'pagina': pagina,
            'tamanhoPagina': quantidade,
        }

        if data_inicio:
            params['dataInicial'] = _formatar_data(data_inicio)
        if data_fim:
            params['dataFinal'] = _formatar_data(data_fim)
        if cnpj:
            params['cnpj'] = cnpj

        params.update(kwargs)

        resultado = self._fazer_requisicao(self.ENDPOINTS['atas'], params)
        return resultado if resultado is not None else {'data': [], 'totalRegistros': 0}

    def buscar_planos_contratacao(
        self,
        pagina: int = 1,
        quantidade: int = 10,
        data_inicio: Optional[str] = None,
        data_fim: Optional[str] = None,
        cnpj: Optional[str] = None,
        **kwargs
    ) -> Dict:
        """
        Busca Planos de Contratação Anual (PCA) por data de atualização.

        Args:
            pagina: Número da página (padrão: 1)
            quantidade: Registros por página (padrão: 10, máx: 500)
            data_inicio: Data início atualização (YYYY-MM-DD)
            data_fim: Data fim atualização (YYYY-MM-DD)
            cnpj: CNPJ do órgão
        """
        quantidade = min(max(quantidade, 10), 500)

        params = {
            'pagina': pagina,
            'tamanhoPagina': quantidade,
        }

        if data_inicio:
            params['dataInicio'] = _formatar_data(data_inicio)
        if data_fim:
            params['dataFim'] = _formatar_data(data_fim)
        if cnpj:
            params['cnpj'] = cnpj

        params.update(kwargs)

        resultado = self._fazer_requisicao(self.ENDPOINTS['planos'], params)
        return resultado if resultado is not None else {'data': [], 'totalRegistros': 0}

    def fechar(self):
        """Fecha a sessão HTTP"""
        self.session.close()
