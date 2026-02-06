# coding: utf-8


import datetime

from diversos import *
from databasefunctions import *
from ativo import Ativo
from conta import Conta
import psycopg2
from datetime import datetime

class Transferencia:
    def __init__(self):
        self.id = -1
        self.id_conta_origem = -1
        self.nome_conta_origem = ''
        self.id_conta_destino = -1
        self.nome_conta_destino = ''
        self.data_lancamento = None
        self.valor = zero

        self.conexao = None

    @staticmethod
    def getConexao():
        try:
            con = ConectaBD.retornaConexao()
            return con
        except Exception as e:
            print(f"Erro ao conectar com o banco: {e}")
            return False

    def set_id_conta_origem(self, arg):
        lista = Conta.mc_select_one_by_id(arg)
        if lista:
            self.id_conta_origem = arg
            self.nome_conta_origem = lista[4]
        else:
            self.id_conta_origem = -1
            self.nome_conta_origem = ''

    def set_nome_conta_origem(self, arg):
        lista = Conta.mc_select_one_by_nome(arg)
        if lista:
            self.id_conta_origem = lista[0]
            self.nome_conta_origem = lista[4]
        else:
            self.id_conta_origem = -1
            self.nome_conta_origem = ''

    def set_id_conta_destino(self, arg):
        lista = Conta.mc_select_one_by_id(arg)
        if lista:
            self.id_conta_destino = arg
            self.nome_conta_destino = lista[4]
        else:
            self.id_conta_destino = -1
            self.nome_conta_destino = ''

    def set_nome_conta_destino(self, arg):
        lista = Conta.mc_select_one_by_nome(arg)
        if lista:
            self.id_conta_destino = lista[0]
            self.nome_conta_destino = lista[4]
        else:
            self.id_conta_destino = -1
            self.nome_conta_destino = ''

    def set_data_lancamento(self, arg):
        self.data_lancamento = devolveDate(arg)

    def set_valor(self, arg):
        tipo = type(arg)
        valor = zero
        if str(tipo) == "<class 'int'>":
            valor = devolveDecimalDeFloat(float(arg))
        if str(tipo) == "<class 'float'>":
            valor = devolveDecimalDeFloat(arg)
        elif str(tipo) == "<class 'decimal.Decimal'>":
            valor = arg
        self.valor = valor

    def clear(self):
        self.id = -1
        self.data_lancamento = None
        self.valor = 0.0
        self.id_conta_origem = -1
        self.id_conta_destino = -1
        self.nome_conta_origem = ''
        self.nome_conta_destino = ''

    def insert(self):
        self.conexao = Transferencia.getConexao()
        try:
            with self.conexao.cursor() as cursor:
                cursor.execute(
                    "INSERT INTO transferencia (contaorigem, contadestino, datalancamento, valor) VALUES (%s, %s, %s, %s) RETURNING id",
                    (self.id_conta_origem, self.id_conta_destino, self.data_lancamento, self.valor),
                )
                self.id = cursor.fetchone()[0]
                self.conexao.commit()
                self.conexao.close()
        except Exception as e:
            raise

    def update(self):
        self.conexao = Transferencia.getConexao()
        try:
            with self.conexao.cursor() as cursor:
                cursor.execute(
                    "UPDATE transferencia set contaorigem = %s, contadestino = %s, datalancamento = %s, valor = %s where id = %s;",
                    (self.id_conta_origem, self.id_conta_destino, self.data_lancamento, self.valor, self.id),
                )
                self.conexao.commit()
                self.conexao.close()
        except Exception as e:
            raise

    def delete(self):
        self.conexao = Transferencia.getConexao()
        with self.conexao.cursor() as cursor:
            cursor.execute("delete from transferencia where id = %s;", (self.id,),)
            self.conexao.commit()
            self.conexao.close()

    def select_by_id(self, id):
        self.clear()
        self.conexao = Transferencia.getConexao()
        with self.conexao.cursor() as cursor:
            cursor.execute("SELECT id, contaorigem, contadestino, datalancamento, valor FROM transferencia WHERE id = %s", (id,))
            row = cursor.fetchone()
            if row:
                self.id = row[0]
                self.set_id_conta_origem(row[1])
                self.set_id_conta_destino(row[2])
                self.set_data_lancamento(row[3])
                self.set_valor(row[4])
            self.conexao.close()

    def get_all(self):
        self.clear()
        self.conexao = Transferencia.getConexao()
        with self.conexao.cursor() as cursor:
            cursor.execute("SELECT p.id, p.contaorigem, co.nomeconta, p.contadestino, cd.nomecontap.datalancamento, p.valor FROM transferencia as p " \
                            "join conta as co on p.contaorigem = co.id " \
                            "join conta as cd on p.contadestino = cd.id " \
                            "order by datalancamento, id")
            lista = cursor.fetchall()
            self.conexao.close()
            if lista: return lista
            else: return None

    @staticmethod
    def mc_busca_por_periodo(dias):
        conexao = Transferencia.getConexao()
        clausulaSql = ''
        numdias = 9999
        try:
            numdias = int(dias)
        except Exception as e:
            numdias = 9999
        
        intervalo = str(numdias) + ' days'
        clausulaSql = "SELECT p.id, p.contaorigem, co.nomeconta, p.contadestino, cd.nomeconta, p.datalancamento, p.valor FROM transferencia as p " \
                        "join conta as co on p.contaorigem = co.id " \
                        "join conta as cd on p.contadestino = cd.id " \
                        "where p.datalancamento >= current_date - interval '" + intervalo + "' " \
                        "order by datalancamento"
        
        with conexao.cursor() as cursor:
            cursor.execute(clausulaSql)
            lista = cursor.fetchall()
            conexao.close()
            if lista: return lista
            else: return None

def main():
    objeto = Transferencia()

    objeto.select_by_id(1)
    print(objeto.id_conta_origem)
    print(objeto.id_conta_destino)
    print(objeto.data_lancamento)
    print(objeto.valor)
    print(objeto.pago)
    

    print('acabou')


if __name__ == '__main__':
    main()
