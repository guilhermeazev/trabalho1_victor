from flask import Flask, request
from flask_restful import Resource, Api, reqparse
import uuid

app = Flask(__name__)
api = Api(app)

enquetes = {}

parser = reqparse.RequestParser()

class Enquete(Resource):
    def get(self, id=None):
        if id:
            if id in enquetes:
                return enquetes[id]
            return {'mensagem': 'Enquete não encontrada'}, 404
        return enquetes

    def delete(self, id):
        if id in enquetes:
            del enquetes[id]
            return {'mensagem': 'Enquete deletada com sucesso.'}
        return {'mensagem': 'Enquete não encontrada'}, 404

class CriarEnquete(Resource):
    def post(self):
        parser.add_argument('titulo', required=True, help="O título da enquete não pode estar vazio.")
        parser.add_argument('descricao')
        parser.add_argument('opcoes', type=dict, action='append', required=True, help="Deve haver pelo menos uma opção de voto.")
        args = parser.parse_args()

        enquete_id = str(uuid.uuid4())
        enquetes[enquete_id] = {
            'titulo': args['titulo'],
            'descricao': args.get('descricao', ''),
            'opcoes': {str(uuid.uuid4()): opcao['descricao'] for opcao in args['opcoes']},
            'votos': {opcao_id: 0 for opcao_id in list(enquetes[enquete_id]['opcoes'].keys())}
        }

        return {'id': enquete_id, 'mensagem': "Enquete criada com sucesso."}, 201

class OpcoesEnquete(Resource):
    def get(self, id):
        if id in enquetes:
            return enquetes[id]['opcoes']
        return {'mensagem': 'Enquete não encontrada'}, 404

    def post(self, id):
        if id not in enquetes:
            return {'mensagem': 'Enquete não encontrada'}, 404

        parser.add_argument('descricao', required=True, help="A descrição da opção não pode estar vazia.")
        args = parser.parse_args()

        opcao_id = str(uuid.uuid4())
        enquetes[id]['opcoes'][opcao_id] = args['descricao']
        enquetes[id]['votos'][opcao_id] = 0

        return {'mensagem': 'Opção adicionada com sucesso.'}, 201

class Votar(Resource):
    def post(self, id):
        if id not in enquetes:
            return {'mensagem': 'Enquete não encontrada'}, 404

        parser.add_argument('opcao_id', required=True, help="ID da opção é necessário.")
        args = parser.parse_args()

        opcao_id = args['opcao_id']
        if opcao_id in enquetes[id]['votos']:
            enquetes[id]['votos'][opcao_id] += 1
            return {'mensagem': 'Voto registrado com sucesso.'}
        return {'mensagem': 'Opção não encontrada'}, 404

class Resultados(Resource):
    def get(self, id):
        if id in enquetes:
            return {'resultados': enquetes[id]['votos']}
        return {'mensagem': 'Enquete não encontrada'}, 404

class DeletarOpcao(Resource):
    def delete(self, id_enquete, id_opcao):
        if id_enquete in enquetes and id_opcao in enquetes[id_enquete]['opcoes']:
            del enquetes[id_enquete]['opcoes'][id_opcao]
            del enquetes[id_enquete]['votos'][id_opcao]
            return {'mensagem': 'Opção deletada com sucesso.'}
        return {'mensagem': 'Enquete ou opção não encontrada'}, 404

api.add_resource(CriarEnquete, '/api/enquetes')
api.add_resource(Enquete, '/api/enquetes', '/api/enquetes/<string:id>')
api.add_resource(OpcoesEnquete, '/api/enquetes/<string:id>/opcoes')
api.add_resource(Votar, '/api/enquetes/<string:id>/votar')
api.add_resource(Resultados, '/api/enquetes/<string:id>/resultados')
api.add_resource(DeletarOpcao, '/api/enquetes/<string:id_enquete>/opcoes/<string:id_opcao>')

