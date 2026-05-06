"""
Integração Flask para API PNCP
Endpoints HTTP para buscar editais, contratos e atas

Uso:
    flask run
    
Endpoints:
    GET /api/pncp/editais - Buscar editais
    GET /api/pncp/contratos - Buscar contratos
    GET /api/pncp/atas - Buscar atas
"""

from flask import Flask, request, jsonify
from datetime import datetime, timedelta
import logging
from pncp_api_client import PNCPClient

app = Flask(__name__)

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Instância global do cliente PNCP
pncp_client = PNCPClient()


@app.route('/api/pncp/editais', methods=['GET'])
def get_editais():
    """
    GET /api/pncp/editais
    
    Parâmetros de query:
        - pagina: Número da página (padrão: 1)
        - quantidade: Registros por página (padrão: 10, máx: 100)
        - data_inicio: Data inicial (YYYY-MM-DD)
        - data_fim: Data final (YYYY-MM-DD)
        - dias: Últimos N dias (alternativa a data_inicio/data_fim)
        - situacao: Situação do edital
        - orgao: Nome ou CNPJ do órgão
    
    Exemplos:
        /api/pncp/editais?quantidade=20
        /api/pncp/editais?dias=7&quantidade=50
        /api/pncp/editais?data_inicio=2024-01-01&data_fim=2024-12-31
        /api/pncp/editais?orgao=Ministério%20da%20Educação
    """
    
    try:
        # Obter parâmetros
        pagina = request.args.get('pagina', default=1, type=int)
        quantidade = request.args.get('quantidade', default=10, type=int)
        data_inicio = request.args.get('data_inicio', default=None, type=str)
        data_fim = request.args.get('data_fim', default=None, type=str)
        dias = request.args.get('dias', default=None, type=int)
        situacao = request.args.get('situacao', default=None, type=str)
        orgao = request.args.get('orgao', default=None, type=str)
        
        # Calcular datas se usar parâmetro 'dias'
        if dias and not data_inicio:
            hoje = datetime.now()
            data_fim = hoje.strftime("%Y-%m-%d")
            data_inicio = (hoje - timedelta(days=dias)).strftime("%Y-%m-%d")
        
        # Buscar editais
        logger.info(f"Buscando editais: pagina={pagina}, quantidade={quantidade}")
        editais = pncp_client.buscar_editais(
            pagina=pagina,
            quantidade=quantidade,
            data_inicio=data_inicio,
            data_fim=data_fim,
            situacao=situacao,
            orgao=orgao
        )
        
        return jsonify({
            'sucesso': True,
            'quantidade': len(editais),
            'pagina': pagina,
            'data_consulta': datetime.now().isoformat(),
            'filtros': {
                'data_inicio': data_inicio,
                'data_fim': data_fim,
                'situacao': situacao,
                'orgao': orgao
            },
            'dados': editais
        }), 200
        
    except Exception as e:
        logger.error(f"Erro ao buscar editais: {e}")
        return jsonify({
            'sucesso': False,
            'erro': str(e),
            'data_consulta': datetime.now().isoformat()
        }), 500


@app.route('/api/pncp/contratos', methods=['GET'])
def get_contratos():
    """
    GET /api/pncp/contratos
    
    Parâmetros de query:
        - pagina: Número da página (padrão: 1)
        - quantidade: Registros por página (padrão: 10, máx: 100)
        - data_inicio: Data inicial (YYYY-MM-DD)
        - data_fim: Data final (YYYY-MM-DD)
        - dias: Últimos N dias
        - orgao: Nome ou CNPJ do órgão
    """
    
    try:
        pagina = request.args.get('pagina', default=1, type=int)
        quantidade = request.args.get('quantidade', default=10, type=int)
        data_inicio = request.args.get('data_inicio', default=None, type=str)
        data_fim = request.args.get('data_fim', default=None, type=str)
        dias = request.args.get('dias', default=None, type=int)
        orgao = request.args.get('orgao', default=None, type=str)
        
        if dias and not data_inicio:
            hoje = datetime.now()
            data_fim = hoje.strftime("%Y-%m-%d")
            data_inicio = (hoje - timedelta(days=dias)).strftime("%Y-%m-%d")
        
        logger.info(f"Buscando contratos: pagina={pagina}, quantidade={quantidade}")
        contratos = pncp_client.buscar_contratos(
            pagina=pagina,
            quantidade=quantidade,
            data_inicio=data_inicio,
            data_fim=data_fim,
            orgao=orgao
        )
        
        return jsonify({
            'sucesso': True,
            'quantidade': len(contratos),
            'pagina': pagina,
            'data_consulta': datetime.now().isoformat(),
            'filtros': {
                'data_inicio': data_inicio,
                'data_fim': data_fim,
                'orgao': orgao
            },
            'dados': contratos
        }), 200
        
    except Exception as e:
        logger.error(f"Erro ao buscar contratos: {e}")
        return jsonify({
            'sucesso': False,
            'erro': str(e),
            'data_consulta': datetime.now().isoformat()
        }), 500


@app.route('/api/pncp/atas', methods=['GET'])
def get_atas():
    """
    GET /api/pncp/atas
    
    Parâmetros de query:
        - pagina: Número da página (padrão: 1)
        - quantidade: Registros por página (padrão: 10, máx: 100)
        - data_inicio: Data inicial (YYYY-MM-DD)
        - data_fim: Data final (YYYY-MM-DD)
        - dias: Últimos N dias
    """
    
    try:
        pagina = request.args.get('pagina', default=1, type=int)
        quantidade = request.args.get('quantidade', default=10, type=int)
        data_inicio = request.args.get('data_inicio', default=None, type=str)
        data_fim = request.args.get('data_fim', default=None, type=str)
        dias = request.args.get('dias', default=None, type=int)
        
        if dias and not data_inicio:
            hoje = datetime.now()
            data_fim = hoje.strftime("%Y-%m-%d")
            data_inicio = (hoje - timedelta(days=dias)).strftime("%Y-%m-%d")
        
        logger.info(f"Buscando atas: pagina={pagina}, quantidade={quantidade}")
        atas = pncp_client.buscar_atas(
            pagina=pagina,
            quantidade=quantidade,
            data_inicio=data_inicio,
            data_fim=data_fim
        )
        
        return jsonify({
            'sucesso': True,
            'quantidade': len(atas),
            'pagina': pagina,
            'data_consulta': datetime.now().isoformat(),
            'filtros': {
                'data_inicio': data_inicio,
                'data_fim': data_fim
            },
            'dados': atas
        }), 200
        
    except Exception as e:
        logger.error(f"Erro ao buscar atas: {e}")
        return jsonify({
            'sucesso': False,
            'erro': str(e),
            'data_consulta': datetime.now().isoformat()
        }), 500


@app.route('/api/pncp/planos', methods=['GET'])
def get_planos():
    """
    GET /api/pncp/planos
    
    Parâmetros de query:
        - pagina: Número da página (padrão: 1)
        - quantidade: Registros por página (padrão: 10, máx: 100)
        - ano: Ano do plano
        - orgao: Nome ou CNPJ do órgão
    """
    
    try:
        pagina = request.args.get('pagina', default=1, type=int)
        quantidade = request.args.get('quantidade', default=10, type=int)
        ano = request.args.get('ano', default=None, type=int)
        orgao = request.args.get('orgao', default=None, type=str)
        
        logger.info(f"Buscando planos: pagina={pagina}, quantidade={quantidade}")
        planos = pncp_client.buscar_planos_contratacao(
            pagina=pagina,
            quantidade=quantidade,
            ano=ano,
            orgao=orgao
        )
        
        return jsonify({
            'sucesso': True,
            'quantidade': len(planos),
            'pagina': pagina,
            'data_consulta': datetime.now().isoformat(),
            'filtros': {
                'ano': ano,
                'orgao': orgao
            },
            'dados': planos
        }), 200
        
    except Exception as e:
        logger.error(f"Erro ao buscar planos: {e}")
        return jsonify({
            'sucesso': False,
            'erro': str(e),
            'data_consulta': datetime.now().isoformat()
        }), 500


@app.route('/api/pncp/status', methods=['GET'])
def status():
    """GET /api/pncp/status - Status da API"""
    return jsonify({
        'status': 'ativo',
        'versao': '1.0.0',
        'data_consulta': datetime.now().isoformat(),
        'endpoints': [
            '/api/pncp/editais',
            '/api/pncp/contratos',
            '/api/pncp/atas',
            '/api/pncp/planos',
            '/api/pncp/status'
        ]
    }), 200


@app.errorhandler(404)
def nao_encontrado(error):
    return jsonify({
        'sucesso': False,
        'erro': 'Endpoint não encontrado',
        'data_consulta': datetime.now().isoformat()
    }), 404


@app.errorhandler(500)
def erro_servidor(error):
    return jsonify({
        'sucesso': False,
        'erro': 'Erro interno do servidor',
        'data_consulta': datetime.now().isoformat()
    }), 500


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
