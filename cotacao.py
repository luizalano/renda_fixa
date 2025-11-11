# coding: utf-8
from databasefunctions import *
from datetime import *
from diversos import *

class Cotacao:
    def __init__(self):
        self.id = -1
        self.id_moeda = -1
        self.data_cotacao = None
        self.valor_cotacao = -1

    def set_valor_cotacao(self, arg):
        if isinstance(arg, (float)): self.valor_cotacao = arg
    
    def set_data_cotacao(self, arg):
        self.data_cotacao = devolve_date(arg)

    def set_id_moeda(self, arg):
        self.id_moeda = -1
        if isinstance(arg, (int)):
            con = self.getConexao()
            with con.cursor() as cursor:
                cursor.execute("SELECT id FROM moeda WHERE id = %s", (arg,))
                resultado = cursor.fetchone()
                if resultado:
                    self.id_moeda = arg
            con.close()

    def insert(self):
        con = self.getConexao()
        with con.cursor() as cursor:
            cursor.execute("INSERT INTO cotacao (idmoeda, datacotacao, valorcotacao) VALUES (%s, %s, %s) RETURNING id",
                (self.id_moeda, self.data_cotacao, self.valor_cotacao ))
            self.id = cursor.fetchone()[0]
            con.commit()
            con.close()

    def update(self):
        con = self.getConexao()
        with con.cursor() as cursor:
            cursor.execute("UPDATE cotacao SET idmoeda = %s, "
                           "datacotacao = %s, "
                           "valorcotacao = %s "
                           "WHERE id = %s", (self.id_moeda, self.data_cotacao, self.valor_cotacao, self.id))
            con.commit()
            con.close()

    def delete(self):
        con = self.getConexao()
        with con.cursor() as cursor:
            cursor.execute("DELETE FROM cotacao WHERE id = %s", (self.id,))
            con.commit()
            self.clear()
            con.close()

    def clear(self):
        self.id = -1
        self.set_id_moeda(-1)
        self.set_data_cotacao(None)
        self.set_valor_cotacao(None)

    def selectById(self, arg):
        con = self.getConexao()
        cursor = con.cursor()
        self.clear()
        cursor.execute("SELECT id, idmoeda, datacotacao, valorcotacao FROM cotacao WHERE id = %s", (arg,))
        row = cursor.fetchone()
        if row:
            self.id = row[0]
            self.set_id_moeda(row[1])
            self.set_data_cotacao(row[2])
            self.set_valor_cotacao(row[3])
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
    def classe_selectAll():
        con = Cotacao.getConexao()
        cursor = con.cursor()
        #with self.conexao.cursor as cursor:
        cursor.execute("SELECT id, idmoeda, datacotacao, valorcotacao FROM cotacao order by idmoeda, datacotacao")
        lista = cursor.fetchall()
        if lista:
            con.close()
            return lista
            
        con.close()


def main():
    obj = Cotacao()
    obj.selectById(1)
    print('')
    print(obj.data_cotacao)
    print(obj.valor_cotacao)
    print(' ')
    obj.set_data_cotacao('15/12/2024')
    print(obj.data_cotacao)
    
    print('Inserindo uma Cotacao nova')

    obj.clear()
    obj.set_id_moeda(2)
    obj.set_data_cotacao(datetime.today())
    obj.set_valor_cotacao(15.3)
    obj.insert()
    print (obj.id)

    id = obj.id
    obj.selectById(id)
    print('Cotação inserida:')
    print(obj.data_cotacao)
    print(obj.valor_cotacao)

    obj.set_data_cotacao('15/12/2021')
    obj.set_valor_cotacao(99.9)
    obj.update()

    obj.selectById(id)
    print('Cotação Recuperada:')
    print(obj.data_cotacao)
    print(obj.valor_cotacao)


    obj.delete()

    lista = Cotacao.classe_selectAll()
    print(lista)
    print('acabou')


if __name__ == '__main__':
    main()
