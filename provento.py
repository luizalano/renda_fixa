# coding: utf-8


import datetime

from diversos import *
from databasefunctions import *
from ativo import Ativo
from conta import Conta
from tipoprovento import TipoProvento
import psycopg2
from datetime import datetime

class Provento:
    def __init__(self):
        self.clear()
        self.conexao = None

    @staticmethod
    def getConexao():
        try:
            con = ConectaBD.retornaConexao()
            return con
        except Exception as e:
            print(f"Erro ao conectar com o banco: {e}")
            return False

    def set_idativo(self, arg):
        lista = Ativo.verificaAtivoPorId(arg)
        if lista:
            self.idativo = arg
        else:
            self.idativo = -1

    def set_siglaativo(self, arg):
        lista = Ativo.verificaAtivoPorSigla(arg)
        if lista:
            self.idativo = lista[0]
        else:
            self.idativo = -1

    def set_idconta(self, arg):
        lista = Conta.selectOneById(arg)
        if lista:
            self.idconta = arg
        else:
            self.idconta = -1

    def set_nomeconta(self, arg):
        lista = Conta.selectOneByNome(arg)
        if lista:
            self.idconta = lista[0]
        else:
            self.idconta = -1

    def set_datarecebimento(self, arg):
        self.datarecebimento = devolveDate(arg)

    def set_valorbruto(self, arg):
        if isinstance(arg, (int, float)) and arg >= 0:
            self.valorbruto = float(arg)
        else:
            self.valorbruto = 0.0

    def set_valorir(self, arg):
        if isinstance(arg, (int, float)) and arg >= 0:
            self.valorir = float(arg)
        else:
            self.valorir = 0.0

    def set_pago(self, arg):
        if isinstance(arg, (bool)):
            self.pago = arg

    def set_idtipoprovento(self, arg):
        lista = TipoProvento.sm_recuperaPorId(arg)
        if lista:
            self.idtipoprovento = arg
            self.nomeprovento = lista[1]
        else:
            self.idtipoprovento = -1
            self.nomeprovento = ''

    def set_nometipoprovento(self, arg):
        lista = TipoProvento.sm_recuperaPorId(arg)
        if lista:
            self.idtipoprovento = lista[0]
            self.nomeprovento = lista[1]
        else:
            self.idtipoprovento = -1
            self.nomeprovento = ''

    def clear(self):
        self.id = -1
        self.idativo = -1
        self.datarecebimento = ''
        self.valorbruto = 0.0
        self.valorir = 0.0
        self.pago = True
        self.idtipoprovento = -1
        self.nomeprovento = ''
        self.idconta = -1

    def insert(self):
        self.conexao = Provento.getConexao()
        try:
            with self.conexao.cursor() as cursor:
                cursor.execute(
                    "INSERT INTO proventos (idativo, datarecebimento, valorbruto, valorir, pago, idtipoprovento, idconta) VALUES (%s, %s, %s, %s, %s, %s, %s) RETURNING id",
                    (self.ativo.id_ativo, self.datarecebimento, self.valorbruto, self.valorir, self.pago, self.idtipoprovento, self.idconta),
                )
                self.id = cursor.fetchone()[0]
                self.conexao.commit()
                self.conexao.close()
        except Exception as e:
            raise

    def update(self):
        self.conexao = Provento.getConexao()
        try:
            with self.conexao.cursor() as cursor:
                cursor.execute(
                    "UPDATE proventos set idativo = %s, datarecebimento = %s, valorbruto = %s, "
                    "valorir = %s, pago = %s, idtipoprovento = %s, idconta = %s where id = %s;",
                    (self.ativo.id_ativo, self.datarecebimento, self.valorbruto, self.valorir, self.pago, self.idtipoprovento, self.idconta, self.id),
                )
                self.conexao.commit()
                self.conexao.close()
        except Exception as e:
            raise

    def delete(self):
        self.conexao = Provento.getConexao()
        with self.conexao.cursor() as cursor:
            cursor.execute("delete from proventos where id = %s;", (self.id,),)
            self.conexao.commit()
            self.conexao.close()

    def selectById(self, id):
        self.clear()
        self.conexao = Provento.getConexao()
        with self.conexao.cursor() as cursor:
            cursor.execute("SELECT id, idativo, datarecebimento, valorbruto, valorir, pago, idtipoprovento, idconta FROM proventos WHERE id = %s", (id,))
            row = cursor.fetchone()
            if row:
                self.id = row[0]
                self.set_idativo(row[1])
                self.set_datarecebimento(row[2])
                self.set_valorbruto(row[3])
                self.set_valorir(row[4])
                self.set_pago(row[5])
                self.set_idtipoprovento(row[6])
                self.set_idconta(row[7])
            self.conexao.close()

    def getAll(self):
        self.clear()
        self.conexao = Provento.getConexao()
        with self.conexao.cursor() as cursor:
            cursor.execute("SELECT p.id, p.idativo, p.datarecebimento, p.valorbruto, p.valorir, p.pago, p.idtipoprovento, "
                           "p.idconta, a.sigla, tp.nometipoprovento, c.nomeconta FROM proventos as p "
                           "join ativo as a on p.idativo = a.id "
                           "join tipoprovento as tp on p.idtipoprovento =  tp.id "
                           "join conta as c on p.idconta = c.id "
                           "order by datarecebimento, id")
            lista = cursor.fetchall()
            self.conexao.close()
            if lista: return lista
            else: return None

    @staticmethod
    def sm_buscaPorPeriodo(arg, idConta):
        conexao = Provento.getConexao()
        clausulaSql = ''
        if arg is None:
            clausulaSql = "SELECT p.id, p.idativo, p.datarecebimento, p.valorbruto, p.valorir, p.pago, p.idtipoprovento, " \
                           "p.idconta, a.sigla, tp.nometipoprovento, c.nomeconta FROM proventos as p " \
                           "join ativo as a on p.idativo = a.id " \
                           "join tipoprovento as tp on p.idtipoprovento =  tp.id " \
                           "join conta as c on p.idconta = c.id " \
                           "where p.idconta = " + str(idConta) + " " \
                           "order by datarecebimento, id"
        else:
            clausulaSql = "SELECT p.id, p.idativo, p.datarecebimento, p.valorbruto, p.valorir, p.pago, p.idtipoprovento, " \
                           "p.idconta, a.sigla, tp.nometipoprovento, c.nomeconta FROM proventos as p " \
                           "join ativo as a on p.idativo = a.id " \
                           "join tipoprovento as tp on p.idtipoprovento =  tp.id " \
                           "join conta as c on p.idconta = c.id " \
                           "where p.datarecebimento >= '" + str(arg) + "' and p.idconta = " + str(idConta) + " " \
                           "order by datarecebimento, id ;"
        with conexao.cursor() as cursor:
            cursor.execute(clausulaSql)
            lista = cursor.fetchall()
            conexao.close()
            if lista: return lista
            else: return None

    @staticmethod
    def sm_buscaProventosPorContaAtivo(idativo, idconta, pago):

        conexao = Provento.getConexao()
        cursor = conexao.cursor()
        if idconta >= 0:
            clausulaSql = 'select p.id, p.datarecebimento as "datar", ' \
                      '(p.valorbruto - p.valorir) as "valor", ' \
                      'tp.nometipoprovento as "provento", p.pago  ' \
                      'from proventos as p join  tipoprovento as tp on tp.id = p.idtipoprovento ' \
                      'where p.idativo = ' + str(idativo) + ' and ' \
                      'p.idconta = ' + str(idconta) + ';'
        else:
            clausulaSql = 'select p.id, p.datarecebimento as "datar", ' \
                      '(p.valorbruto - p.valorir) as "valor", ' \
                      'tp.nometipoprovento as "provento", p.pago  ' \
                      'from proventos as p join  tipoprovento as tp on tp.id = p.idtipoprovento ' \
                      'where p.idativo = ' + str(idativo) + ';'

        try:
            cursor.execute(clausulaSql)
        except  Exception as e:
            dlg = wx.MessageDialog(None, clausulaSql + '\n' + str(e), 'Erro ao ler proventos!', wx.OK | wx.ICON_ERROR)
            result = dlg.ShowModal()

        row = cursor.fetchone()
        lista = []
        while row != None:
            if pago and row[4]:
                lista.append([row[0], row[1], row[2], row[3], row[4]])
            else:
                lista.append([row[0], row[1], row[2], row[3], row[4]])
            row = cursor.fetchone()

        conexao.close()

        return lista


def main():
    provento = Provento()

    provento.selectById(1)
    print(provento.nomeprovento)
    print(provento.valorbruto)
    print(provento.datarecebimento)
    print(provento.pago)
    print(provento.ativo.sigla)
    print(' ')
    provento.set_idtipoprovento('-1')
    print(provento.nomeprovento)
    print(' ')
    provento.set_idtipoprovento('3')
    print(provento.nomeprovento)
    print(' ')

    print('acabou')


if __name__ == '__main__':
    main()
