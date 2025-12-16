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
        self.id = -1
        self.id_ativo = -1
        self.sigla_ativo = ''
        self.data_recebimento = ''
        self.valor_bruto = 0.0
        self.valor_ir = 0.0
        self.pago = True
        self.id_tipo_provento = -1
        self.nome_provento = ''
        self.id_conta = -1

        self.conexao = None

    @staticmethod
    def getConexao():
        try:
            con = ConectaBD.retornaConexao()
            return con
        except Exception as e:
            print(f"Erro ao conectar com o banco: {e}")
            return False

    def set_id_ativo(self, arg):
        lista = Ativo.mc_verifica_ativo_por_id(arg)
        if lista:
            self.id_ativo = lista[0]
            self.sigla_ativo = lista[2]
        else:
            self.id_ativo = -1
            self.sigla_ativo = ''

    def set_sigla_ativo(self, arg):
        lista = Ativo.mc_verifica_ativo_por_sigla(arg)
        if lista:
            self.id_ativo = lista[0]
            self.sigla_ativo = lista[2]
        else:
            self.id_ativo = -1
            self.sigla_ativo = ''

    def set_id_conta(self, arg):
        lista = Conta.mc_select_one_by_id(arg)
        if lista:
            self.id_conta = arg
            self.nome_conta = lista[4]
        else:
            self.id_conta = -1
            self.nome_conta

    def set_nome_conta(self, arg):
        lista = Conta.mc_select_one_by_nome(arg)
        if lista:
            self.id_conta = lista[0]
            self.nome_conta = lista[4]
        else:
            self.id_conta = -1
            self.nome_conta = ''

    def set_data_recebimento(self, arg):
        self.data_recebimento = devolveDate(arg)

    def set_valor_bruto(self, arg):
        tipo = type(arg)
        valor = zero
        if str(tipo) == "<class 'int'>":
            valor = devolveDecimalDeFloat(float(arg))
        if str(tipo) == "<class 'float'>":
            valor = devolveDecimalDeFloat(arg)
        elif str(tipo) == "<class 'decimal.Decimal'>":
            valor = arg
        self.valor_bruto = valor

    def set_valor_ir(self, arg):
        tipo = type(arg)
        valor = zero
        if str(tipo) == "<class 'int'>":
            valor = devolveDecimalDeFloat(float(arg))
        if str(tipo) == "<class 'float'>":
            valor = devolveDecimalDeFloat(arg)
        elif str(tipo) == "<class 'decimal.Decimal'>":
            valor = arg
        self.valor_ir = valor

    def set_pago(self, arg):
        if isinstance(arg, (bool)):
            self.pago = arg

    def set_id_tipo_provento(self, arg):
        lista = TipoProvento.sm_recupera_por_id(arg)
        if lista:
            self.id_tipo_provento = arg
            self.nome_provento = lista[1]
        else:
            self.id_tipo_provento = -1
            self.nome_provento = ''

    def set_nome_tipo_provento(self, arg):
        lista = TipoProvento.sm_recupera_por_nome(arg)
        if lista:
            self.id_tipo_provento = lista[0]
            self.nome_provento = lista[1]
        else:
            self.id_tipo_provento = -1
            self.nome_provento = ''

    def clear(self):
        self.id = -1
        self.id_ativo = -1
        self.sigla_ativo = ''
        self.data_recebimento = ''
        self.valor_bruto = 0.0
        self.valor_ir = 0.0
        self.pago = True
        self.id_tipo_provento = -1
        self.nome_provento = ''
        self.id_conta = -1

    def insert(self):
        self.conexao = Provento.getConexao()
        try:
            with self.conexao.cursor() as cursor:
                cursor.execute(
                    "INSERT INTO proventos (idativo, datarecebimento, valorbruto, valorir, pago, idtipoprovento, idconta) VALUES (%s, %s, %s, %s, %s, %s, %s) RETURNING id",
                    (self.id_ativo, self.data_recebimento, self.valor_bruto, self.valor_ir, self.pago, self.id_tipo_provento, self.id_conta),
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
                    (self.id_ativo, self.data_recebimento, self.valor_bruto, self.valor_ir, self.pago, self.id_tipo_provento, self.id_conta, self.id),
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

    def select_by_id(self, id):
        self.clear()
        self.conexao = Provento.getConexao()
        with self.conexao.cursor() as cursor:
            cursor.execute("SELECT id, idativo, datarecebimento, valorbruto, valorir, pago, idtipoprovento, idconta FROM proventos WHERE id = %s", (id,))
            row = cursor.fetchone()
            if row:
                self.id = row[0]
                self.set_id_ativo(row[1])
                self.set_data_recebimento(row[2])
                self.set_valor_bruto(row[3])
                self.set_valor_ir(row[4])
                self.set_pago(row[5])
                self.set_id_tipo_provento(row[6])
                self.set_id_conta(row[7])
            self.conexao.close()

    def get_all(self):
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
    def sm_busca_por_periodo_conta(data_inicial, id_conta):
        conexao = Provento.getConexao()
        clausulaSql = ''
        if data_inicial is None:
            clausulaSql = "SELECT p.id, p.idativo, p.datarecebimento, p.valorbruto, p.valorir, p.pago, p.idtipoprovento, " \
                           "p.idconta, a.sigla, tp.nometipoprovento, c.nomeconta FROM proventos as p " \
                           "join ativo as a on p.idativo = a.id " \
                           "join tipoprovento as tp on p.idtipoprovento =  tp.id " \
                           "join conta as c on p.idconta = c.id " \
                           "where p.idconta = " + str(id_conta) + " " \
                           "order by datarecebimento, id"
        else:
            clausulaSql = "SELECT p.id, p.idativo, p.datarecebimento, p.valorbruto, p.valorir, p.pago, p.idtipoprovento, " \
                           "p.idconta, a.sigla, tp.nometipoprovento, c.nomeconta FROM proventos as p " \
                           "join ativo as a on p.idativo = a.id " \
                           "join tipoprovento as tp on p.idtipoprovento =  tp.id " \
                           "join conta as c on p.idconta = c.id " \
                           "where p.datarecebimento >= '" + str(data_inicial) + "' and p.idconta = " + str(id_conta) + " " \
                           "order by datarecebimento, id ;"
        with conexao.cursor() as cursor:
            cursor.execute(clausulaSql)
            lista = cursor.fetchall()
            conexao.close()
            if lista: return lista
            else: return None

    @staticmethod
    def sm_busca_por_periodo_todas_as_contas(data_inicial):
        conexao = Provento.getConexao()
        clausulaSql = ''
        if data_inicial is None:
            clausulaSql = "SELECT p.id, p.idativo, p.datarecebimento, p.valorbruto, p.valorir, p.pago, p.idtipoprovento, " \
                           "p.idconta, a.sigla, tp.nometipoprovento, c.nomeconta FROM proventos as p " \
                           "join ativo as a on p.idativo = a.id " \
                           "join tipoprovento as tp on p.idtipoprovento =  tp.id " \
                           "join conta as c on p.idconta = c.id " \
                           "order by datarecebimento, id"
        else:
            clausulaSql = "SELECT p.id, p.idativo, p.datarecebimento, p.valorbruto, p.valorir, p.pago, p.idtipoprovento, " \
                           "p.idconta, a.sigla, tp.nometipoprovento, c.nomeconta FROM proventos as p " \
                           "join ativo as a on p.idativo = a.id " \
                           "join tipoprovento as tp on p.idtipoprovento =  tp.id " \
                           "join conta as c on p.idconta = c.id " \
                           "where p.datarecebimento >= '" + str(data_inicial) + "' "\
                           "order by datarecebimento, id ;"
        with conexao.cursor() as cursor:
            cursor.execute(clausulaSql)
            lista = cursor.fetchall()
            conexao.close()
            if lista: return lista
            else: return None

    @staticmethod
    def mc_busca_proventos_por_conta_ativo(idativo, idconta, pago):

        conexao = Provento.getConexao()
        cursor = conexao.cursor()
        if idconta >= 0:
            if pago:
                clausulaSql = 'select p.id, p.datarecebimento as "datar", ' \
                              '(p.valorbruto - p.valorir) as "valor", ' \
                              'tp.nometipoprovento as "provento", p.pago  ' \
                              'from proventos as p join  tipoprovento as tp on tp.id = p.idtipoprovento ' \
                              'where p.idativo = ' + str(idativo) + ' and ' \
                              'p.pago = true and ' \
                              'p.idconta = ' + str(idconta) + ';'
            else:
                clausulaSql = 'select p.id, p.datarecebimento as "datar", ' \
                      '(p.valorbruto - p.valorir) as "valor", ' \
                      'tp.nometipoprovento as "provento", p.pago  ' \
                      'from proventos as p join  tipoprovento as tp on tp.id = p.idtipoprovento ' \
                      'where p.idativo = ' + str(idativo) + ' and ' \
                      'p.idconta = ' + str(idconta) + ';'
        else:
            if pago:
                clausulaSql = 'select p.id, p.datarecebimento as "datar", ' \
                      '(p.valorbruto - p.valorir) as "valor", ' \
                      'tp.nometipoprovento as "provento", p.pago  ' \
                      'from proventos as p join  tipoprovento as tp on tp.id = p.idtipoprovento ' \
                      'where p.idativo = ' + str(idativo) + ' and ' \
                      'p.pago = true ;'
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

    provento.select_by_id(1)
    print(provento.nome_provento)
    print(provento.valor_bruto)
    print(provento.data_recebimento)
    print(provento.pago)
    
    print(' ')
    provento.set_id_tipo_provento('-1')
    print(provento.nome_provento)
    print(' ')
    provento.set_id_tipo_provento('3')
    print(provento.nome_provento)
    print(' ')

    print('acabou')


if __name__ == '__main__':
    main()
