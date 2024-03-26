from flask import Flask, request, g
from flask_restful import Resource, Api, reqparse
import sqlite3

DATABASE = 'enquetes.db'

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

# Função para executar consultas no banco de dados
def query_db(query, args=(), one=False, modify=False):
    cur = get_db().execute(query, args)
    if modify:
        get_db().commit()
        cur.close()
        return
    rv = cur.fetchall()
    cur.close()
    return (rv[0] if rv else None) if one else rv

# Converter linhas do banco de dados para dicionário
def row_to_dict(row):
    return {key: row[key] for key in row.keys()}

# Aqui você atualizaria as classes de recursos para interagir com o banco de dados...
# Por exemplo, a classe CriarEnquete agora deve inserir uma nova enquete no banco de dados

# Exemplo de método POST modificado para usar SQLite
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

# Não esqueça de adicionar as outras classes de recursos adaptadas para usar o SQLite...

if __name__ == '__main__':
    app.run(debug=True)
