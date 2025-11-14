# coding: utf-8
from databasefunctions import *
from datetime import *
from diversos import *
from ativo import Ativo

class CotacaoAtivo:
    def __init__(self):
        self.id = -1
        self.id_ativo = -1
        self.data_cotacao = None
        self.preco = -1
        self.maximo = -1
        self.minimo = -1
        self.qtd_negocios = -1
        self.valor_negociado = -1
        self.qtd_acoes_negociadas = -1

    def set_preco(self, arg):
        self.preco = -1.0
        if isinstance(arg, (float)): self.preco = arg
    
    def set_data_cotacao(self, arg):
        self.data_cotacao = devolveDate(arg)

    def set_id_ativo(self, arg):
        self.id_ativo = -1
        if isinstance(arg, (int)):
            lista = Ativo.verificaAtivoPorId(arg)
            if lista:
                self.id_ativo = arg

    def set_maximo(self, arg):
        self.maximo = -1.0
        if isinstance(arg, (float)):
            self.maximo = arg
        
    def set_minimo(self, arg):
        self.minimo = -1.0
        if isinstance(arg, (float)):
            self.minimo = arg
    
    def set_qtd_negocios(self, arg):
        self.qtd_negocios = -1
        if isinstance(arg, (int)):
            self.qtd_negocios = arg

    def set_valor_negociado(self, arg):
        self.valor_negociado = -1.0
        if isinstance(arg, (float)):
            self.valor_negociado = arg

    def set_qtd_acoes_negociadas(self, arg):
        self.qtd_acoes_negociadas = -1
        if isinstance(arg, (float)):
            self.qtd_acoes_negociadas = arg

    def insert(self):
        con = self.getConexao()
        with con.cursor() as cursor:
            cursor.execute("INSERT INTO cotacaoativo (idativo, datacotacao, preco, maximo, minimo, qtdnegocios, qtdacoesnegociadas, valornegociado) VALUES (%s, %s, %s, %s, %s, %s, %s, %s) RETURNING id",
                (self.id_moeda, self.data_cotacao, self.preco, self.maximo, self.minimo, self.qtd_negocios, self.qtd_acoes_negociadas, self.valor_negociado ))
            self.id = cursor.fetchone()[0]
            con.commit()
            con.close()

    def update(self):
        con = self.getConexao()
        with con.cursor() as cursor:
            cursor.execute("UPDATE cotacaoativo SET idmoeda = %s, "
                           "datacotacao = %s, "
                           "preco = %s, "
                           "maximo = %s, "
                           "minimo = %s, "
                           "qtdnegocios = %s, "
                           "qtdacoesnegociadas = %s, "
                           "valornegociado = %s, "
                           "WHERE id = %s", (self.id_moeda, self.data_cotacao, self.preco, self.maximo, self.minimo, self.qtd_negocios, self.qtd_acoes_negociadas, self.valor_negociado, self.id))
            con.commit()
            con.close()

    def delete(self):
        con = self.getConexao()
        with con.cursor() as cursor:
            cursor.execute("DELETE FROM cotacaoativo WHERE id = %s", (self.id,))
            con.commit()
            self.clear()
            con.close()

    def clear(self):
        self.id = -1
        self.set_id_ativo(-1)
        self.set_data_cotacao(None)
        self.set_preco(-1.0)
        self.set_maximo(-1.0)
        self.set_minimo(-1.0)
        self.set_qtd_negocios(-1)
        self.set_valor_negociado(-1-0)
        self.set_qtd_acoes_negociadas(-1)

    def select_by_id(self, arg):
        con = self.getConexao()
        cursor = con.cursor()
        self.clear()
        cursor.execute("SELECT id, idativo, datacotacao, preco, maximo, minimo, qtdnegocios, qtdacoesnegociadas, valornegociado" \
                       " FROM cotacao WHERE id = %s", (arg,))
        row = cursor.fetchone()
        if row:
            self.id = row[0]
            self.set_id_moeda(row[1])
            self.set_data_cotacao(row[2])
            self.set_preco(row[3])
        con.close()

    @staticmethod
    def getConexao():
        try:
            con = ConectaBD.retornaConexao()
            return con
        except Exception as e:
            print(f"Erro ao conectar com o banco: {e}")
            return False


    @staticmethod
    def mc_select_all():
        con = CotacaoAtivo.getConexao()
        cursor = con.cursor()
        #with self.conexao.cursor as cursor:
        cursor.execute("SELECT id, idativo, datacotacao, preco, maximo, minimo, qtdnegocios, qtdacoesnegociadas, valornegociado FROM cotacao order by idativo, datacotacao")
        lista = cursor.fetchall()
        if lista:
            con.close()
            return lista
            
        con.close()


def main():
    obj = CotacaoAtivo()
    obj.select_by_id(1)
    print('')
    print(obj.data_cotacao)
    print(obj.preco)
    print(' ')
    obj.set_data_cotacao('15/12/2024')
    print(obj.data_cotacao)
    
    print('Inserindo uma CotacaoAtivo nova')

    obj.clear()
    obj.set_id_moeda(2)
    obj.set_data_cotacao(datetime.today())
    obj.set_preco(15.3)
    obj.insert()
    print (obj.id)

    id = obj.id
    obj.select_by_id(id)
    print('Cotação inserida:')
    print(obj.data_cotacao)
    print(obj.preco)

    obj.set_data_cotacao('15/12/2021')
    obj.set_preco(99.9)
    obj.update()

    obj.select_by_id(id)
    print('Cotação Recuperada:')
    print(obj.data_cotacao)
    print(obj.preco)


    obj.delete()

    lista = CotacaoAtivo.classe_selectAll()
    print(lista)
    print('acabou')


if __name__ == '__main__':
    main()
