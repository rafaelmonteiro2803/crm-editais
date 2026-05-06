"""
Integração PNCP com Microsoft Dynamics 365
Sincroniza editais e oportunidades entre PNCP e Dynamics

Uso:
    sync = PNCPDynamicsSync(
        client_id='seu_client_id',
        tenant_id='seu_tenant_id',
        client_secret='seu_client_secret',
        instance_url='https://seu-org.crm.dynamics.com'
    )
    
    sync.sincronizar_editais()
"""

import requests
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from pncp_api_client import PNCPClient

logger = logging.getLogger(__name__)


class PNCPDynamicsSync:
    """Sincroniza dados do PNCP com Microsoft Dynamics 365"""
    
    def __init__(
        self,
        client_id: str,
        tenant_id: str,
        client_secret: str,
        instance_url: str,
        timeout: int = 30
    ):
        """
        Inicializa a sincronização PNCP-Dynamics
        
        Args:
            client_id: Azure AD Client ID
            tenant_id: Azure AD Tenant ID
            client_secret: Azure AD Client Secret
            instance_url: URL da instância Dynamics (ex: https://org.crm.dynamics.com)
            timeout: Timeout para requisições
        """
        self.client_id = client_id
        self.tenant_id = tenant_id
        self.client_secret = client_secret
        self.instance_url = instance_url.rstrip('/')
        self.timeout = timeout
        
        self.pncp_client = PNCPClient(timeout=timeout)
        self.access_token = None
        self.token_expires_at = None
        
        # Obter token inicial
        self._obter_access_token()
    
    def _obter_access_token(self) -> bool:
        """Obtém um novo access token do Azure AD"""
        
        url = f"https://login.microsoftonline.com/{self.tenant_id}/oauth2/v2.0/token"
        
        data = {
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'scope': f'{self.instance_url}/.default',
            'grant_type': 'client_credentials'
        }
        
        try:
            response = requests.post(url, data=data, timeout=self.timeout)
            response.raise_for_status()
            
            result = response.json()
            self.access_token = result.get('access_token')
            expires_in = result.get('expires_in', 3600)
            self.token_expires_at = datetime.now() + timedelta(seconds=expires_in - 60)
            
            logger.info(f"Token obtido com sucesso. Expira em: {self.token_expires_at}")
            return True
            
        except Exception as e:
            logger.error(f"Erro ao obter token: {e}")
            return False
    
    def _verificar_token(self):
        """Verifica e renova token se necessário"""
        
        if self.token_expires_at and datetime.now() > self.token_expires_at:
            logger.info("Token expirado, renovando...")
            self._obter_access_token()
    
    def _fazer_requisicao_dynamics(
        self,
        metodo: str,
        endpoint: str,
        dados: Optional[Dict] = None
    ) -> Optional[Dict]:
        """
        Faz uma requisição à API Dynamics 365
        
        Args:
            metodo: GET, POST, PATCH, DELETE
            endpoint: Endpoint (ex: /api/data/v9.0/opportunities)
            dados: Dados para POST/PATCH
            
        Returns:
            Resposta JSON ou None
        """
        
        self._verificar_token()
        
        if not self.access_token:
            logger.error("Token não disponível")
            return None
        
        url = f"{self.instance_url}{endpoint}"
        
        headers = {
            'Authorization': f'Bearer {self.access_token}',
            'OData-MaxPageSize': '5000',
            'Content-Type': 'application/json'
        }
        
        try:
            if metodo == 'GET':
                response = requests.get(url, headers=headers, timeout=self.timeout)
            elif metodo == 'POST':
                response = requests.post(url, json=dados, headers=headers, timeout=self.timeout)
            elif metodo == 'PATCH':
                response = requests.patch(url, json=dados, headers=headers, timeout=self.timeout)
            elif metodo == 'DELETE':
                response = requests.delete(url, headers=headers, timeout=self.timeout)
            else:
                logger.error(f"Método HTTP não suportado: {metodo}")
                return None
            
            response.raise_for_status()
            
            if response.status_code == 204:
                return {'sucesso': True}
            
            return response.json() if response.text else {'sucesso': True}
            
        except requests.exceptions.HTTPError as e:
            logger.error(f"Erro HTTP {e.response.status_code}: {e}")
            return None
        except Exception as e:
            logger.error(f"Erro na requisição: {e}")
            return None
    
    def _converter_edital_para_opportunity(self, edital: Dict) -> Dict:
        """
        Converte um edital do PNCP em um Opportunity do Dynamics
        
        Args:
            edital: Dados do edital do PNCP
            
        Returns:
            Dados formatados para criar opportunity
        """
        
        # Extrair informações do edital
        numero = edital.get('numero', 'N/A')
        objeto = edital.get('objeto', '')[:1000]  # Limitar a 1000 caracteres
        orgao = edital.get('orgao', {})
        nome_orgao = orgao.get('nome', 'N/A') if isinstance(orgao, dict) else str(orgao)
        
        valor_estimado = edital.get('valor', 0)
        data_publicacao = edital.get('dataPublicacao', datetime.now().isoformat())
        
        # Determinar estágio da oportunidade
        situacao = edital.get('situacao', '').upper()
        stage_map = {
            'DIVULGADA': 305840000,      # Prospect
            'EM_ANDAMENTO': 305840001,   # Qualify
            'ENCERRADA': 305840005       # Lost
        }
        stage_code = stage_map.get(situacao, 305840000)
        
        # Criar opportunity
        opportunity = {
            'name': f"Edital {numero} - {nome_orgao}",
            'description': objeto,
            'estimatedvalue': valor_estimado,
            'new_pncp_numero_edital': numero,
            'new_pncp_id': edital.get('id', ''),
            'new_pncp_orgao': nome_orgao,
            'new_pncp_data_publicacao': data_publicacao,
            'stagecode': stage_code,
            'statecode': 0,  # Active
            'customertypeconceptcode': 1  # Account
        }
        
        return opportunity
    
    def _buscar_account_por_cnpj(self, cnpj: str) -> Optional[str]:
        """
        Busca um Account no Dynamics pelo CNPJ
        
        Args:
            cnpj: CNPJ do órgão
            
        Returns:
            ID do account ou None
        """
        
        if not cnpj:
            return None
        
        # Remover caracteres especiais do CNPJ
        cnpj_limpo = ''.join(filter(str.isdigit, cnpj))
        
        endpoint = (
            "/api/data/v9.0/accounts?"
            f"$filter=new_cnpj eq '{cnpj_limpo}'"
            "&$select=accountid"
        )
        
        resultado = self._fazer_requisicao_dynamics('GET', endpoint)
        
        if resultado and resultado.get('value'):
            return resultado['value'][0].get('accountid')
        
        return None
    
    def _criar_ou_atualizar_account(self, orgao_info: Dict) -> Optional[str]:
        """
        Cria ou atualiza um Account para o órgão
        
        Args:
            orgao_info: Informações do órgão
            
        Returns:
            ID do account criado/atualizado
        """
        
        cnpj = orgao_info.get('cnpj', '')
        nome = orgao_info.get('nome', 'N/A')[:100]
        
        # Verificar se account já existe
        account_id = self._buscar_account_por_cnpj(cnpj)
        
        if account_id:
            logger.info(f"Account já existe para {nome}: {account_id}")
            return account_id
        
        # Criar novo account
        account_data = {
            'name': nome,
            'new_cnpj': ''.join(filter(str.isdigit, cnpj)) if cnpj else '',
            'customertypecode': 1
        }
        
        endpoint = "/api/data/v9.0/accounts"
        resultado = self._fazer_requisicao_dynamics('POST', endpoint, account_data)
        
        if resultado and 'odata.id' in resultado:
            # Extrair ID da resposta
            account_id = resultado['odata.id'].split('(')[-1].rstrip(')')
            logger.info(f"Account criado para {nome}: {account_id}")
            return account_id
        
        logger.error(f"Erro ao criar account para {nome}")
        return None
    
    def sincronizar_editais(
        self,
        dias: int = 7,
        quantidade_pagina: int = 50,
        limite_registros: Optional[int] = None
    ) -> Dict:
        """
        Sincroniza editais do PNCP para Dynamics 365
        
        Args:
            dias: Buscar editais dos últimos N dias
            quantidade_pagina: Registros por página (máx 100)
            limite_registros: Limite de registros a sincronizar
            
        Returns:
            Relatório da sincronização
        """
        
        relatorio = {
            'inicio': datetime.now().isoformat(),
            'total_buscado': 0,
            'total_criado': 0,
            'total_erro': 0,
            'detalhes': []
        }
        
        try:
            # Calcular datas
            hoje = datetime.now()
            data_fim = hoje.strftime("%Y-%m-%d")
            data_inicio = (hoje - timedelta(days=dias)).strftime("%Y-%m-%d")
            
            logger.info(f"Sincronizando editais de {data_inicio} a {data_fim}")
            
            pagina = 1
            registros_processados = 0
            
            while True:
                # Buscar editais do PNCP
                editais = self.pncp_client.buscar_editais(
                    pagina=pagina,
                    quantidade=quantidade_pagina,
                    data_inicio=data_inicio,
                    data_fim=data_fim
                )
                
                if not editais:
                    break
                
                relatorio['total_buscado'] += len(editais)
                
                for edital in editais:
                    try:
                        # Criar account se necessário
                        orgao = edital.get('orgao', {})
                        if isinstance(orgao, dict):
                            account_id = self._criar_ou_atualizar_account(orgao)
                        else:
                            account_id = None
                        
                        # Converter edital para opportunity
                        opp_data = self._converter_edital_para_opportunity(edital)
                        
                        if account_id:
                            opp_data['parentaccountid@odata.bind'] = f"/accounts({account_id})"
                        
                        # Criar opportunity no Dynamics
                        endpoint = "/api/data/v9.0/opportunities"
                        resultado = self._fazer_requisicao_dynamics('POST', endpoint, opp_data)
                        
                        if resultado:
                            numero_edital = edital.get('numero', 'N/A')
                            relatorio['total_criado'] += 1
                            relatorio['detalhes'].append({
                                'status': 'sucesso',
                                'numero_edital': numero_edital,
                                'mensagem': 'Opportunity criada'
                            })
                            logger.info(f"Opportunity criada para edital {numero_edital}")
                        else:
                            relatorio['total_erro'] += 1
                            relatorio['detalhes'].append({
                                'status': 'erro',
                                'numero_edital': edital.get('numero', 'N/A'),
                                'mensagem': 'Erro ao criar opportunity'
                            })
                    
                    except Exception as e:
                        relatorio['total_erro'] += 1
                        relatorio['detalhes'].append({
                            'status': 'erro',
                            'numero_edital': edital.get('numero', 'N/A'),
                            'mensagem': str(e)
                        })
                        logger.error(f"Erro ao processar edital: {e}")
                    
                    registros_processados += 1
                    
                    if limite_registros and registros_processados >= limite_registros:
                        break
                
                if limite_registros and registros_processados >= limite_registros:
                    break
                
                if len(editais) < quantidade_pagina:
                    break
                
                pagina += 1
        
        except Exception as e:
            logger.error(f"Erro na sincronização: {e}")
            relatorio['erro'] = str(e)
        
        finally:
            relatorio['fim'] = datetime.now().isoformat()
            logger.info(f"Sincronização concluída: {relatorio['total_criado']} criados, {relatorio['total_erro']} erros")
        
        return relatorio


# Exemplo de uso
if __name__ == "__main__":
    
    # Configurar credenciais (substituir com suas credenciais reais)
    sync = PNCPDynamicsSync(
        client_id='SEU_CLIENT_ID',
        tenant_id='SEU_TENANT_ID',
        client_secret='SEU_CLIENT_SECRET',
        instance_url='https://seu-org.crm.dynamics.com'
    )
    
    # Sincronizar editais dos últimos 7 dias
    resultado = sync.sincronizar_editais(dias=7, limite_registros=10)
    
    print("\n=== RELATÓRIO DE SINCRONIZAÇÃO ===")
    print(f"Data: {resultado['inicio']}")
    print(f"Total buscado: {resultado['total_buscado']}")
    print(f"Total criado: {resultado['total_criado']}")
    print(f"Total erro: {resultado['total_erro']}")
    print("\nDetalhes:")
    for detalhe in resultado['detalhes'][:10]:
        print(f"  - {detalhe['numero_edital']}: {detalhe['mensagem']}")
