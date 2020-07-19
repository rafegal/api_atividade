from flask import Flask, request
from flask_restful import Resource, Api
from models import Pessoas, Atividades, Usuarios
from flask_httpauth import HTTPBasicAuth

auth = HTTPBasicAuth()
app = Flask(__name__)
api = Api(app)

# USUARIOS = {
#     'rafael':'321',
#     'galleani':'321'
# }

# @auth.verify_password
# def verificacao(login, senha):
#     if not (login, senha):
#         return False
#     return USUARIOS.get(login) == senha

@auth.verify_password
def verificacao(login, senha):
    if not (login, senha):
        return False
    return Usuarios.query.filter_by(login=login, senha=senha, ativo=1).first()

class Pessoa(Resource):
    def get(self, nome):
        pessoa = Pessoas.query.filter_by(nome=nome).first()
        try:
            response = {
                'nome':pessoa.nome,
                'idade':pessoa.idade,
                'id':pessoa.id
            }
        except AttributeError:
            response = {
                'status':'error',
                'mensagem':f'Pessoa de nome {nome} não foi encontrada'
            }
        return response

    @auth.login_required
    def put(self, nome):
        pessoa = Pessoas.query.filter_by(nome=nome).first()
        dados = request.json
        try:
            if 'nome' in dados:
                pessoa.nome = dados['nome']
            if 'idade' in dados:
                pessoa.idade = dados['idade']
            pessoa.save()
            response = {
                'id':pessoa.id,
                'nome':pessoa.nome,
                'idade':pessoa.idade
            }
        except AttributeError:
            response = {
                'status':'error',
                'mensagem':f'Pessoa de nome {nome} não foi encontrada'
            }
        return response

    @auth.login_required
    def delete(self, nome):
        pessoa = Pessoas.query.filter_by(nome=nome).first()
        try:
            pessoa.delete()
            response = {
                'status':'sucesso', 
                'mensagem':f'Pessoa de nome {nome} foi excluida com sucesso'
            }
        except AttributeError:
            response = {
                'status':'error', 
                'mensagem':f'Pessoa de nome {nome} não foi encontrada'
            }
        return response

class ListaPessoas(Resource):
    def get(self):
        pessoas = Pessoas.query.all()
        if len(pessoas) > 0:
            response = [{'id':i.id, 'nome':i.nome, 'idade':i.idade} for i in pessoas]
        else:
            response = {
                'status':'error',
                'mensagem':'Nâo foi encontrada nenhuma pessoa'
            }
        return response

    @auth.login_required
    def post(self):
        dados = request.json
        pessoa = Pessoas(nome=dados['nome'], idade=dados['idade'])
        pessoa.save()    
        response = {
            'id':pessoa.id,
            'nome':pessoa.nome,
            'idade':pessoa.idade
        }
        return response
        
class Atividade(Resource):
    def get(self, nome):
        pessoa = Pessoas.query.filter_by(nome=nome).first()
        try:
            atividades = Atividades.query.filter_by(pessoa_id=pessoa.id).all()
            response = [{'id':a.id, 'nome':a.nome, 'pessoa':a.pessoa.nome} for a in atividades]
        except AttributeError:
            response = {
                'status':'error',
                'mensagem':f'Pessoa de nome {nome} não foi encontrada'
            }
        return response    

class StatusAtividade(Resource):
    def get(self, id):
        atividade = Atividades.query.filter_by(id=id).first()
        try:
            if atividade.status == 0:
                status = 'pendente'
            else:
                status = 'concluído'
            response = {'id':atividade.id, 'status':status}
        except AttributeError:
            response = {
                'status':'error',
                'mensagem':f'Atividade de id {id} não foi encontrada'
            }
        return response

    @auth.login_required
    def put(self, id):
        atividade = Atividades.query.filter_by(id=id).first()
        try:
            dados = request.json
            if dados['status'] == 'pendente':
                atividade.status = 0
            elif dados['status'] == 'concluído':
                atividade.status = 1
            atividade.save()
            if atividade.status == 0:
                status = 'pendente'
            else:
                status = 'concluído'
            response = {'id':atividade.id, 'status':status}
        except AttributeError:
            response = {
                'status':'error',
                'mensagem':f'Atividade de id {id} não foi encontrada'
            }
        return response

class ListaAtividades(Resource):
    def get(self):
        atividades = Atividades.query.all()
        if len(atividades) > 0:
            response = [{'id':i.id, 'nome':i.nome, 'pessoa':i.pessoa.nome}  for i in atividades]
        else:
            response = {
                'status':'error',
                'mensagem':'Nâo foi encontrada nenhuma atividade'
            }
        return response

    @auth.login_required
    def post(self):
        dados = request.json
        pessoa = Pessoas.query.filter_by(nome=dados['pessoa']).first()
        atividade = Atividades(nome=dados['nome'], pessoa=pessoa)
        try:
            atividade.save()
            response = {
                'pessoa':atividade.pessoa.nome,
                'nome':atividade.nome,
                'id':atividade.id
            }
        except AttributeError:
            response = {
                'status':'error',
                'mensagem':'Pessoa de nome {nome} não foi encontrada'.format(nome=dados['pessoa'])
            }
        return response

api.add_resource(Pessoa, '/pessoa/<string:nome>/')
api.add_resource(ListaPessoas, '/pessoa/')
api.add_resource(Atividade, '/atividades/<string:nome>/')
api.add_resource(ListaAtividades, '/atividades/')
api.add_resource(StatusAtividade, '/status_atividade/<int:id>/')

if __name__ == '__main__':
    app.run(debug=True)