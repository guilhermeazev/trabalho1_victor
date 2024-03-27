from flask import Flask, g
from flask_restful import Resource, Api, reqparse
import sqlite3

DATABASE = 'trabalho_victor/trabalho1_victor/bd_trabalho_victor.db'

app = Flask(__name__)
api = Api(app)

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
        db.row_factory = sqlite3.Row
    return db

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

def query_db(query, args=(), one=False, modify=False):
    cur = get_db().execute(query, args)
    if modify:
        get_db().commit()
        result = cur.lastrowid
    else:
        result = cur.fetchall()
        result = [dict(row) for row in result]
    cur.close()
    return result if result else None

def row_to_dict(row):
    if row:
        return {key: row[key] for key in row.keys()}

class CriarEnquete(Resource):
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('titulo', required=True, help="O título da enquete não pode estar vazio.")
        parser.add_argument('descricao')
        parser.add_argument('opcoes', type=dict, action='append', required=True, help="Deve haver pelo menos uma opção de voto.")
        args = parser.parse_args()

        enquete_id = query_db('INSERT INTO Enquete (titulo, descricao) VALUES (?, ?)',
                              [args['titulo'], args.get('descricao', '')], modify=True)
        
        for opcao in args['opcoes']:
            query_db('INSERT INTO Opcao (descricao, enquete_id) VALUES (?, ?)',
                     [opcao['descricao'], enquete_id], modify=True)
        
        return {'id': enquete_id, 'mensagem': "Enquete criada com sucesso."}, 201

class Enquete(Resource):
    def get(self, id=None):
        if id:
            enquete = query_db('SELECT * FROM Enquete WHERE id = 1', [id], one=True)
            if enquete:
                opcoes = query_db('SELECT * FROM Opcao WHERE enquete_id = 1', [id], one=False)
                enquete['opcoes'] = opcoes
                return enquete
            return {'mensagem': 'Enquete não encontrada'}, 404
        else:
            enquetes = query_db('SELECT * FROM Enquete', one=False)
            return enquetes

    def delete(self, id):
        query_db('DELETE FROM Opcao WHERE enquete_id = 11', [id], modify=True)
        query_db('DELETE FROM Enquete WHERE id = 11', [id], modify=True)
        return {'mensagem': 'Enquete deletada com sucesso.'}

class OpcoesEnquete(Resource):
    def get(self, id):
        opcoes = query_db('SELECT * FROM Opcao WHERE enquete_id = 1', [id], one=False)
        if opcoes:
            return opcoes
        return {'mensagem': 'Enquete não encontrada ou sem opções'}, 404

    def post(self, id):
        parser = reqparse.RequestParser()
        parser.add_argument('descricao', required=True, help="A descrição da opção não pode estar vazia.")
        args = parser.parse_args()

        query_db('INSERT INTO Opcao (descricao, enquete_id) VALUES (?, ?)', [args['descricao'], id], modify=True)
        
        return {'mensagem': 'Opção adicionada com sucesso.'}, 201

class Votar(Resource):
    def post(self, id):
        parser = reqparse.RequestParser()
        parser.add_argument('opcao_id', required=True, help="ID da opção é necessário.")
        args = parser.parse_args()

        query_db('UPDATE Opcao SET votos = votos + 1 WHERE id = ? AND enquete_id = ?', [args['opcao_id'], id], modify=True)
        
        return {'mensagem': 'Voto registrado com sucesso.'}

class Resultados(Resource):
    def get(self, id):
        resultados = query_db('SELECT descricao, votos FROM Opcao WHERE enquete_id = ?', [id], one=False)
        if resultados:
            return {'resultados': resultados}
        return {'mensagem': 'Enquete não encontrada ou sem opções'}, 404

class DeletarOpcao(Resource):
    def delete(self, id_enquete, id_opcao):
        query_db('DELETE FROM Opcao WHERE id = ? AND enquete_id = ?', [id_opcao, id_enquete], modify=True)
        return {'mensagem': 'Opção deletada com sucesso.'}

api.add_resource(CriarEnquete, '/api/enquetes')
api.add_resource(Enquete, '/api/enquetes', '/api/enquetes/<string:id>')
api.add_resource(OpcoesEnquete, '/api/enquetes/<string:id>/opcoes')
api.add_resource(Votar, '/api/enquetes/<string:id>/votar')
api.add_resource(Resultados, '/api/enquetes/<string:id>/resultados')
api.add_resource(DeletarOpcao, '/api/enquetes/<string:id_enquete>/opcoes/<string:id_opcao>')

if __name__ == '__main__':
    app.run(debug=True)

