# coding: utf-8
from databasefunctions import *
from datetime import *
from diversos import *
from ativo import Ativo
from bolsa import Bolsa 

class Radar:
    def __init__(self):
        self.id = -1
        self.id_ativo = -1
        self.data_provavel = None
        self.data_com = None
        self.tipo_provento = None
        self.valor_provento = -1.0
        self.ultima_cotacao = -1.0
        self.dy = -1.0
        self.id_bolsa = -1

    def set_valor_provento(self, arg):
        self.valor_provento = -1.0
        if isinstance(arg, (float)): self.preco = arg
    
    def set_data_com(self, arg):
        self.data_com = devolveDate(arg)

    def set_data_provavel(self, arg):
        self.data_provavel = devolveDate(arg)

    def set_id_ativo(self, arg):
        self.id_ativo = -1
        if isinstance(arg, (int)):
            lista = Ativo.mc_verifica_ativo_por_id(arg)
            if lista:
                self.id_ativo = arg

    def set_tipo_provento(self, arg):
        self.tipo_provento = None
        if isinstance(arg, (str)):
            self.tipo_provento = arg

    def set_valor_provento(self, arg):
        self.valor_provento = -1.0
        if isinstance(arg, (float)):
            self.valor_provento = arg
        
    def set_ultima_cotacao(self, arg):
        self.ultima_cotacao = -1.0
        if isinstance(arg, (float)):
            self.ultima_cotacao = arg
    
    def set_dy(self, arg):
        self.dy = -1.0
        if isinstance(arg, (float)):
            self.dy = arg

    def set_id_bolsa(self, arg):
        self.id_bolsa = -1
        if isinstance(arg, (int)):
            lista = Bolsa.selectOneById(arg)
            if lista:
                self.id_bolsa = arg


    def insert(self):
        con = self.getConexao()
        with con.cursor() as cursor:
            cursor.execute("INSERT INTO radar (idativo, dataprovavel, datacom, tipoprovento, valorprovento, ultimacotacao, dy, idbolsa) " \
                            "VALUES (%s, %s, %s, %s, %s, %s, %s, %s) RETURNING id",
                (self.id_ativo, self.data_provavel, self.data_com, self.tipo_provento, self.valor_provento, self.ultima_cotacao, self.dy, self.id_bolsa ))
            self.id = cursor.fetchone()[0]
            con.commit()
            con.close()

    def update(self):
        con = self.getConexao()
        with con.cursor() as cursor:
            cursor.execute("UPDATE radar SET idativo = %s, "
                           "dataprovavel = %s, "
                           "datacom = %s, "
                           "tipo_provento = %s, "
                           "valor_provento = %s, "
                           "ultima_cotacao = %s, "
                           "dy = %s, "
                           "id_bolsa = %s "
                           "WHERE id = %s", (self.id_ativo, self.data_provavel, self.data_com, self.tipo_provento, self.valor_provento, self.ultima_cotacao, self.dy, self.id_bolsa, self.id))
            con.commit()
            con.close()

    def delete(self):
        con = self.getConexao()
        with con.cursor() as cursor:
            cursor.execute("DELETE FROM radar WHERE id = %s", (self.id,))
            con.commit()
            self.clear()
            con.close()

    def clear(self):
        self.id = -1
        self.set_id_ativo(-1)
        self.set_data_com(None)
        self.set_data_provavel(None) 
        self.set_tipo_provento(None)
        self.set_valor_provento(-1.0)
        self.set_ultima_cotacao(-1.0)
        self.set_dy(-1)
        self.set_id_bolsa(-1)

    @staticmethod
    def getConexao():
        try:
            con = ConectaBD.retornaConexao()
            return con
        except Exception as e:
            print(f"Erro ao conectar com o banco: {e}")
            return False


def main():
    obj = Radar()
    obj.select_by_id(1)
    print('')
    print(obj.data_cotacao)
    print(obj.preco)
    print(' ')
    obj.set_data_com('15/12/2024')
    print(obj.data_cotacao)
    
    print('Inserindo uma CotacaoAtivo nova')

    obj.clear()
    obj.set_id_moeda(2)
    obj.set_data_com(datetime.today())
    obj.set_valor_provento(15.3)
    obj.insert()
    print (obj.id)

    id = obj.id
    obj.select_by_id(id)
    print('Cotação inserida:')
    print(obj.data_cotacao)
    print(obj.preco)

    obj.set_data_com('15/12/2021')
    obj.set_valor_provento(99.9)
    obj.update()

    obj.select_by_id(id)
    print('Cotação Recuperada:')
    print(obj.data_cotacao)
    print(obj.preco)


    obj.delete()

    lista = Radar.classe_selectAll()
    print(lista)
    print('acabou')


if __name__ == '__main__':
    main()
