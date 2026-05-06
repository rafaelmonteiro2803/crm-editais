"""
Integração Flask para API PNCP
Endpoints HTTP para buscar editais, contratos, atas e planos de contratação

Uso:
    flask run

Endpoints:
    GET /                   - Informações e lista de endpoints da API
    GET /api/pncp/editais   - Buscar contratações (editais)
    GET /api/pncp/contratos - Buscar contratos
    GET /api/pncp/atas      - Buscar atas de registro de preço
    GET /api/pncp/planos    - Buscar planos de contratação anual (PCA)
    GET /api/pncp/status    - Status da API
"""

from flask import Flask, request, jsonify
from datetime import datetime, timedelta
import logging
from pncp_api_client import PNCPClient

app = Flask(__name__)
app.json.ensure_ascii = False

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

pncp_client = PNCPClient()

MODALIDADES = {
    1: 'Leilão Eletrônico',
    2: 'Diálogo Competitivo',
    3: 'Concurso',
    4: 'Concorrência Eletrônica',
    5: 'Concorrência Presencial',
    6: 'Pregão Eletrônico',
    7: 'Pregão Presencial',
    8: 'Dispensa de Licitação',
    9: 'Inexigibilidade de Licitação',
    10: 'Manifestação de Interesse',
    11: 'Pré-qualificação',
    12: 'Credenciamento',
    13: 'Leilão Presencial',
}


@app.route('/', methods=['GET'])
def index():
    """GET / - Informações da API"""
    return jsonify({
        'nome': 'CRM Editais - API PNCP',
        'versao': '1.0.0',
        'descricao': 'API para consulta de dados do Portal Nacional de Contratações Públicas',
        'data_consulta': datetime.now().isoformat(),
        'endpoints': {
            'editais': '/api/pncp/editais',
            'contratos': '/api/pncp/contratos',
            'atas': '/api/pncp/atas',
            'planos': '/api/pncp/planos',
            'status': '/api/pncp/status',
        }
    }), 200


@app.route('/api/pncp/editais', methods=['GET'])
def get_editais():
    """
    GET /api/pncp/editais

    Parâmetros de query:
        - pagina: Número da página (padrão: 1)
        - quantidade: Registros por página (padrão: 10, máx: 50)
        - data_inicio: Data inicial publicação (YYYY-MM-DD)
        - data_fim: Data final publicação (YYYY-MM-DD)
        - dias: Últimos N dias (alternativa a data_inicio/data_fim)
        - modalidade: Código da modalidade (ex: 6 = Pregão Eletrônico) — obrigatório
        - uf: Sigla do estado (ex: SP, RJ)
        - cnpj: CNPJ do órgão

    Exemplos:
        /api/pncp/editais?modalidade=6&dias=7
        /api/pncp/editais?modalidade=8&data_inicio=2026-01-01&data_fim=2026-05-06&uf=SP
    """
    try:
        pagina = request.args.get('pagina', default=1, type=int)
        quantidade = request.args.get('quantidade', default=10, type=int)
        data_inicio = request.args.get('data_inicio', default=None, type=str)
        data_fim = request.args.get('data_fim', default=None, type=str)
        dias = request.args.get('dias', default=None, type=int)
        modalidade = request.args.get('modalidade', default=None, type=int)
        uf = request.args.get('uf', default=None, type=str)
        cnpj = request.args.get('cnpj', default=None, type=str)

        if dias and not data_inicio:
            hoje = datetime.now()
            data_fim = hoje.strftime('%Y-%m-%d')
            data_inicio = (hoje - timedelta(days=dias)).strftime('%Y-%m-%d')

        if modalidade is None:
            return jsonify({
                'sucesso': False,
                'erro': 'Parâmetro obrigatório ausente: modalidade',
                'ajuda': 'Informe o código da modalidade. Ex: ?modalidade=6 (Pregão Eletrônico)',
                'modalidades': MODALIDADES,
                'data_consulta': datetime.now().isoformat(),
            }), 400

        logger.info(f"Buscando editais: pagina={pagina}, quantidade={quantidade}, modalidade={modalidade}")
        resultado = pncp_client.buscar_editais(
            pagina=pagina,
            quantidade=quantidade,
            data_inicio=data_inicio,
            data_fim=data_fim,
            modalidade=modalidade,
            uf=uf,
            cnpj=cnpj,
        )

        return jsonify({
            'sucesso': True,
            'quantidade': len(resultado.get('data', [])),
            'total_registros': resultado.get('totalRegistros', 0),
            'total_paginas': resultado.get('totalPaginas', 0),
            'pagina': resultado.get('numeroPagina', pagina),
            'data_consulta': datetime.now().isoformat(),
            'filtros': {
                'data_inicio': data_inicio,
                'data_fim': data_fim,
                'modalidade': modalidade,
                'modalidade_nome': MODALIDADES.get(modalidade),
                'uf': uf,
                'cnpj': cnpj,
            },
            'dados': resultado.get('data', []),
        }), 200

    except Exception as e:
        logger.error(f"Erro ao buscar editais: {e}")
        return jsonify({
            'sucesso': False,
            'erro': str(e),
            'data_consulta': datetime.now().isoformat(),
        }), 500


@app.route('/api/pncp/contratos', methods=['GET'])
def get_contratos():
    """
    GET /api/pncp/contratos

    Parâmetros de query:
        - pagina: Número da página (padrão: 1)
        - quantidade: Registros por página (padrão: 10, máx: 500)
        - data_inicio: Data inicial publicação (YYYY-MM-DD)
        - data_fim: Data final publicação (YYYY-MM-DD)
        - dias: Últimos N dias
        - cnpj_orgao: CNPJ do órgão contratante
    """
    try:
        pagina = request.args.get('pagina', default=1, type=int)
        quantidade = request.args.get('quantidade', default=10, type=int)
        data_inicio = request.args.get('data_inicio', default=None, type=str)
        data_fim = request.args.get('data_fim', default=None, type=str)
        dias = request.args.get('dias', default=None, type=int)
        cnpj_orgao = request.args.get('cnpj_orgao', default=None, type=str)

        if dias and not data_inicio:
            hoje = datetime.now()
            data_fim = hoje.strftime('%Y-%m-%d')
            data_inicio = (hoje - timedelta(days=dias)).strftime('%Y-%m-%d')

        logger.info(f"Buscando contratos: pagina={pagina}, quantidade={quantidade}")
        resultado = pncp_client.buscar_contratos(
            pagina=pagina,
            quantidade=quantidade,
            data_inicio=data_inicio,
            data_fim=data_fim,
            cnpj_orgao=cnpj_orgao,
        )

        return jsonify({
            'sucesso': True,
            'quantidade': len(resultado.get('data', [])),
            'total_registros': resultado.get('totalRegistros', 0),
            'total_paginas': resultado.get('totalPaginas', 0),
            'pagina': resultado.get('numeroPagina', pagina),
            'data_consulta': datetime.now().isoformat(),
            'filtros': {
                'data_inicio': data_inicio,
                'data_fim': data_fim,
                'cnpj_orgao': cnpj_orgao,
            },
            'dados': resultado.get('data', []),
        }), 200

    except Exception as e:
        logger.error(f"Erro ao buscar contratos: {e}")
        return jsonify({
            'sucesso': False,
            'erro': str(e),
            'data_consulta': datetime.now().isoformat(),
        }), 500


@app.route('/api/pncp/atas', methods=['GET'])
def get_atas():
    """
    GET /api/pncp/atas

    Parâmetros de query:
        - pagina: Número da página (padrão: 1)
        - quantidade: Registros por página (padrão: 10, máx: 500)
        - data_inicio: Data inicial vigência (YYYY-MM-DD)
        - data_fim: Data final vigência (YYYY-MM-DD)
        - dias: Últimos N dias
        - cnpj: CNPJ do órgão
    """
    try:
        pagina = request.args.get('pagina', default=1, type=int)
        quantidade = request.args.get('quantidade', default=10, type=int)
        data_inicio = request.args.get('data_inicio', default=None, type=str)
        data_fim = request.args.get('data_fim', default=None, type=str)
        dias = request.args.get('dias', default=None, type=int)
        cnpj = request.args.get('cnpj', default=None, type=str)

        if dias and not data_inicio:
            hoje = datetime.now()
            data_fim = hoje.strftime('%Y-%m-%d')
            data_inicio = (hoje - timedelta(days=dias)).strftime('%Y-%m-%d')

        logger.info(f"Buscando atas: pagina={pagina}, quantidade={quantidade}")
        resultado = pncp_client.buscar_atas(
            pagina=pagina,
            quantidade=quantidade,
            data_inicio=data_inicio,
            data_fim=data_fim,
            cnpj=cnpj,
        )

        return jsonify({
            'sucesso': True,
            'quantidade': len(resultado.get('data', [])),
            'total_registros': resultado.get('totalRegistros', 0),
            'total_paginas': resultado.get('totalPaginas', 0),
            'pagina': resultado.get('numeroPagina', pagina),
            'data_consulta': datetime.now().isoformat(),
            'filtros': {
                'data_inicio': data_inicio,
                'data_fim': data_fim,
                'cnpj': cnpj,
            },
            'dados': resultado.get('data', []),
        }), 200

    except Exception as e:
        logger.error(f"Erro ao buscar atas: {e}")
        return jsonify({
            'sucesso': False,
            'erro': str(e),
            'data_consulta': datetime.now().isoformat(),
        }), 500


@app.route('/api/pncp/planos', methods=['GET'])
def get_planos():
    """
    GET /api/pncp/planos

    Parâmetros de query:
        - pagina: Número da página (padrão: 1)
        - quantidade: Registros por página (padrão: 10, máx: 500)
        - data_inicio: Data início atualização (YYYY-MM-DD)
        - data_fim: Data fim atualização (YYYY-MM-DD)
        - dias: Últimos N dias
        - cnpj: CNPJ do órgão
    """
    try:
        pagina = request.args.get('pagina', default=1, type=int)
        quantidade = request.args.get('quantidade', default=10, type=int)
        data_inicio = request.args.get('data_inicio', default=None, type=str)
        data_fim = request.args.get('data_fim', default=None, type=str)
        dias = request.args.get('dias', default=None, type=int)
        cnpj = request.args.get('cnpj', default=None, type=str)

        if dias and not data_inicio:
            hoje = datetime.now()
            data_fim = hoje.strftime('%Y-%m-%d')
            data_inicio = (hoje - timedelta(days=dias)).strftime('%Y-%m-%d')

        logger.info(f"Buscando planos: pagina={pagina}, quantidade={quantidade}")
        resultado = pncp_client.buscar_planos_contratacao(
            pagina=pagina,
            quantidade=quantidade,
            data_inicio=data_inicio,
            data_fim=data_fim,
            cnpj=cnpj,
        )

        return jsonify({
            'sucesso': True,
            'quantidade': len(resultado.get('data', [])),
            'total_registros': resultado.get('totalRegistros', 0),
            'total_paginas': resultado.get('totalPaginas', 0),
            'pagina': resultado.get('numeroPagina', pagina),
            'data_consulta': datetime.now().isoformat(),
            'filtros': {
                'data_inicio': data_inicio,
                'data_fim': data_fim,
                'cnpj': cnpj,
            },
            'dados': resultado.get('data', []),
        }), 200

    except Exception as e:
        logger.error(f"Erro ao buscar planos: {e}")
        return jsonify({
            'sucesso': False,
            'erro': str(e),
            'data_consulta': datetime.now().isoformat(),
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
            '/api/pncp/status',
        ],
        'modalidades': MODALIDADES,
    }), 200


@app.errorhandler(404)
def nao_encontrado(error):
    return jsonify({
        'sucesso': False,
        'erro': 'Endpoint não encontrado',
        'data_consulta': datetime.now().isoformat(),
    }), 404


@app.errorhandler(500)
def erro_servidor(error):
    return jsonify({
        'sucesso': False,
        'erro': 'Erro interno do servidor',
        'data_consulta': datetime.now().isoformat(),
    }), 500


if __name__ == '__main__':
    import os
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=False, host='0.0.0.0', port=port)
