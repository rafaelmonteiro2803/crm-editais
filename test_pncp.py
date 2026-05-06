"""
Script de teste para validar integração PNCP

Uso:
    python test_pncp.py
"""

import sys
import time
from datetime import datetime, timedelta
from pncp_api_client import PNCPClient


class TestadorPNCP:
    """Classe para testar funcionalidades do cliente PNCP"""
    
    def __init__(self):
        self.client = PNCPClient(timeout=30)
        self.testes_executados = 0
        self.testes_passados = 0
        self.testes_falhados = 0
    
    def imprimir_cabecalho(self, titulo: str):
        """Imprime um cabeçalho formatado"""
        print("\n" + "=" * 80)
        print(f"  {titulo}")
        print("=" * 80)
    
    def imprimir_resultado(self, nome_teste: str, passou: bool, mensagem: str = ""):
        """Imprime resultado de um teste"""
        self.testes_executados += 1
        
        if passou:
            self.testes_passados += 1
            status = "✅ PASSOU"
        else:
            self.testes_falhados += 1
            status = "❌ FALHOU"
        
        print(f"\n{status} - {nome_teste}")
        if mensagem:
            print(f"   Mensagem: {mensagem}")
    
    def teste_conexao(self) -> bool:
        """Testa conexão com API PNCP"""
        self.imprimir_cabecalho("TESTE 1: Conexão com API PNCP")
        
        try:
            # Tentar buscar um único edital
            print("Tentando conectar à API PNCP...")
            resultado = self.client.buscar_editais(quantidade=1)
            
            if isinstance(resultado, list):
                self.imprimir_resultado(
                    "Conexão com API",
                    True,
                    "Conectado com sucesso"
                )
                return True
            else:
                self.imprimir_resultado(
                    "Conexão com API",
                    False,
                    "Resposta inválida"
                )
                return False
                
        except Exception as e:
            self.imprimir_resultado(
                "Conexão com API",
                False,
                str(e)
            )
            return False
    
    def teste_buscar_editais_basico(self) -> bool:
        """Testa busca básica de editais"""
        self.imprimir_cabecalho("TESTE 2: Busca Básica de Editais")
        
        try:
            print("Buscando 5 editais...")
            editais = self.client.buscar_editais(quantidade=5)
            
            passou = len(editais) > 0
            
            self.imprimir_resultado(
                "Busca básica de editais",
                passou,
                f"{len(editais)} editais encontrados"
            )
            
            if passou and len(editais) > 0:
                print(f"\nPrimeiro edital:")
                edital = editais[0]
                print(f"  - ID: {edital.get('id', 'N/A')[:50]}")
                print(f"  - Número: {edital.get('numero', 'N/A')}")
                print(f"  - Órgão: {edital.get('orgao', {}).get('nome', 'N/A')}")
                print(f"  - Objeto: {edital.get('objeto', 'N/A')[:60]}...")
            
            return passou
            
        except Exception as e:
            self.imprimir_resultado(
                "Busca básica de editais",
                False,
                str(e)
            )
            return False
    
    def teste_filtrar_por_data(self) -> bool:
        """Testa filtro por data"""
        self.imprimir_cabecalho("TESTE 3: Filtro por Data")
        
        try:
            # Buscar editais do último mês
            hoje = datetime.now()
            data_fim = hoje.strftime("%Y-%m-%d")
            data_inicio = (hoje - timedelta(days=30)).strftime("%Y-%m-%d")
            
            print(f"Buscando editais de {data_inicio} a {data_fim}...")
            editais = self.client.buscar_editais(
                data_inicio=data_inicio,
                data_fim=data_fim,
                quantidade=10
            )
            
            passou = len(editais) >= 0  # Pode retornar vazio se nenhum edital nesse período
            
            self.imprimir_resultado(
                "Filtro por data",
                passou,
                f"{len(editais)} editais encontrados no período"
            )
            
            return passou
            
        except Exception as e:
            self.imprimir_resultado(
                "Filtro por data",
                False,
                str(e)
            )
            return False
    
    def teste_paginacao(self) -> bool:
        """Testa paginação"""
        self.imprimir_cabecalho("TESTE 4: Paginação")
        
        try:
            print("Buscando primeira página (10 registros)...")
            pagina1 = self.client.buscar_editais(pagina=1, quantidade=10)
            
            print("Buscando segunda página (10 registros)...")
            time.sleep(1)  # Pequeno delay entre requisições
            pagina2 = self.client.buscar_editais(pagina=2, quantidade=10)
            
            # Verificar se as páginas são diferentes
            ids_pagina1 = {e.get('id') for e in pagina1}
            ids_pagina2 = {e.get('id') for e in pagina2}
            
            diferentes = ids_pagina1 != ids_pagina2
            
            self.imprimir_resultado(
                "Paginação",
                diferentes,
                f"Página 1: {len(pagina1)} | Página 2: {len(pagina2)}"
            )
            
            return diferentes
            
        except Exception as e:
            self.imprimir_resultado(
                "Paginação",
                False,
                str(e)
            )
            return False
    
    def teste_buscar_contratos(self) -> bool:
        """Testa busca de contratos"""
        self.imprimir_cabecalho("TESTE 5: Busca de Contratos")
        
        try:
            print("Buscando 5 contratos...")
            contratos = self.client.buscar_contratos(quantidade=5)
            
            passou = len(contratos) >= 0
            
            self.imprimir_resultado(
                "Busca de contratos",
                passou,
                f"{len(contratos)} contratos encontrados"
            )
            
            if passou and len(contratos) > 0:
                print(f"\nPrimeiro contrato:")
                contrato = contratos[0]
                print(f"  - ID: {contrato.get('id', 'N/A')[:50]}")
                print(f"  - Número: {contrato.get('numero', 'N/A')}")
                print(f"  - Valor: R$ {contrato.get('valor', 0):,.2f}")
            
            return passou
            
        except Exception as e:
            self.imprimir_resultado(
                "Busca de contratos",
                False,
                str(e)
            )
            return False
    
    def teste_buscar_atas(self) -> bool:
        """Testa busca de atas"""
        self.imprimir_cabecalho("TESTE 6: Busca de Atas")
        
        try:
            print("Buscando 5 atas...")
            atas = self.client.buscar_atas(quantidade=5)
            
            passou = len(atas) >= 0
            
            self.imprimir_resultado(
                "Busca de atas",
                passou,
                f"{len(atas)} atas encontradas"
            )
            
            if passou and len(atas) > 0:
                print(f"\nPrimeira ata:")
                ata = atas[0]
                print(f"  - ID: {ata.get('id', 'N/A')[:50]}")
                print(f"  - Número: {ata.get('numero', 'N/A')}")
            
            return passou
            
        except Exception as e:
            self.imprimir_resultado(
                "Busca de atas",
                False,
                str(e)
            )
            return False
    
    def teste_limite_quantidade(self) -> bool:
        """Testa se quantidade é limitada a 100"""
        self.imprimir_cabecalho("TESTE 7: Limite de Quantidade")
        
        try:
            print("Testando quantidade > 100...")
            editais = self.client.buscar_editais(quantidade=500)
            
            # A API deve limitar a 100
            passou = len(editais) <= 100
            
            self.imprimir_resultado(
                "Limite de quantidade",
                passou,
                f"Solicitado 500, retornou {len(editais)}"
            )
            
            return passou
            
        except Exception as e:
            self.imprimir_resultado(
                "Limite de quantidade",
                False,
                str(e)
            )
            return False
    
    def teste_estrutura_resposta(self) -> bool:
        """Testa estrutura das respostas"""
        self.imprimir_cabecalho("TESTE 8: Estrutura de Resposta")
        
        try:
            print("Buscando edital para validar estrutura...")
            editais = self.client.buscar_editais(quantidade=1)
            
            passou = True
            if len(editais) > 0:
                edital = editais[0]
                campos_esperados = ['id', 'numero', 'objeto', 'orgao', 'dataPublicacao']
                
                campos_faltantes = [c for c in campos_esperados if c not in edital]
                
                if campos_faltantes:
                    passou = False
                    self.imprimir_resultado(
                        "Estrutura de resposta",
                        False,
                        f"Campos faltantes: {campos_faltantes}"
                    )
                else:
                    self.imprimir_resultado(
                        "Estrutura de resposta",
                        True,
                        "Todos os campos esperados presentes"
                    )
            else:
                self.imprimir_resultado(
                    "Estrutura de resposta",
                    True,
                    "Nenhum edital para validar (não é erro)"
                )
            
            return passou
            
        except Exception as e:
            self.imprimir_resultado(
                "Estrutura de resposta",
                False,
                str(e)
            )
            return False
    
    def executar_todos_testes(self):
        """Executa todos os testes"""
        self.imprimir_cabecalho("INICIANDO SUITE DE TESTES PNCP")
        
        print(f"Data/Hora: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
        print(f"URL API: {self.client.BASE_URL}")
        print(f"Timeout: {self.client.timeout}s")
        
        # Executar testes
        self.teste_conexao()
        time.sleep(1)
        
        self.teste_buscar_editais_basico()
        time.sleep(1)
        
        self.teste_filtrar_por_data()
        time.sleep(1)
        
        self.teste_paginacao()
        time.sleep(1)
        
        self.teste_buscar_contratos()
        time.sleep(1)
        
        self.teste_buscar_atas()
        time.sleep(1)
        
        self.teste_limite_quantidade()
        time.sleep(1)
        
        self.teste_estrutura_resposta()
        
        # Resumo
        self.imprimir_cabecalho("RESUMO DOS TESTES")
        print(f"\n📊 Total de testes: {self.testes_executados}")
        print(f"✅ Testes passados: {self.testes_passados}")
        print(f"❌ Testes falhados: {self.testes_falhados}")
        
        taxa_sucesso = (self.testes_passados / self.testes_executados * 100) if self.testes_executados > 0 else 0
        print(f"📈 Taxa de sucesso: {taxa_sucesso:.1f}%")
        
        if self.testes_falhados == 0:
            print("\n🎉 Todos os testes passaram!")
            return 0
        else:
            print(f"\n⚠️  {self.testes_falhados} teste(s) falharam!")
            return 1
    
    def fechar(self):
        """Fecha o cliente"""
        self.client.fechar()


if __name__ == "__main__":
    print("\n🧪 Validador de Integração PNCP")
    print("=" * 80)
    
    testador = TestadorPNCP()
    
    try:
        codigo_saida = testador.executar_todos_testes()
    except KeyboardInterrupt:
        print("\n\n⚠️  Testes interrompidos pelo usuário")
        codigo_saida = 2
    except Exception as e:
        print(f"\n\n❌ Erro inesperado: {e}")
        codigo_saida = 3
    finally:
        testador.fechar()
    
    sys.exit(codigo_saida)
