# coding: utf-8
import datetime

from diversos import *
from conta import *
from databasefunctions import *

class Capital():
    id = 0
    data_lancamento = 11
    descricao = ''
    idConta = -1
    nomeConta = ''
    valor = 0.0
    tamdescricao = 0

    def __init__(self):
        self.defineTamanhos()

    @staticmethod
    def getConexao():
        try:
            con = ConectaBD.retornaConexao()
            return con
        except Exception as e:
            print(f"Erro ao conectar com o banco: {e}")
            return False

    def defineTamanhos(self):
        self.tamdescricao = self.sqlBuscaTamanho('descricao')

    def getAll(self):
        self.conexao = self.getConexao()
        cursor = self.conexao.cursor()
        clausulaSql = 'select cp.id, cp.datalancamento, cp,descricao, cp.valor, cp.idConta, cn.nomeconta ' \
                      'from capital as cp join conta as cn on cp.idconta = cn.id ' \
                      'order by datalancamento;'

        try:
            cursor.execute(clausulaSql)
        except  Exception as e:
            dlg = wx.MessageDialog(None, clausulaSql + '\n' + str(e), 'Erro ao ler lançamentos de Capital', wx.OK | wx.ICON_ERROR)
            result = dlg.ShowModal()

        lista = []

        lista = self.conexao.cursor.fetchall()

        self.conexao.close()

        return lista

    def clearCapital(self):
        self.setid(-1)
        self.setdescricao('')
        self.setdata_lancamento('')
        self.setvalor(0.0)
        self.setidConta(-1)

    def populaCapitalById(self, arg):
        clausulaSql = 'select cp.id, cp.datalancamento, cp.descricao, cp.valor, cp.idConta, cn.nomeconta ' \
                      'from capital as cp join conta as cn on cp.idconta = cn.id ' \
                      'where cp.id = ' + str(arg) + ' order by datalancamento;'

        self.conexao = self.getConexao()
        cursor = self.conexao.cursor()

        try:
            cursor.execute(clausulaSql)
        except  Exception as e:
            dlg = wx.MessageDialog(None, clausulaSql + '\n' + str(e), 'Erro ao ler lançamento de Capital <' + str(arg) + '>', wx.OK | wx.ICON_ERROR)
            result = dlg.ShowModal()

        row = cursor.fetchone()
        self.clearCapital()
        if row != None:
            self.setid(row[0])
            self.setdata_lancamento(row[1])
            self.setdescricao(row[2])
            self.setvalor(row[3])
            self.setidConta(row[4])

        self.conexao.close()

    def setid(self, arg):
        self.id = arg
    def setdescricao(self, arg):
        if arg is None:
            arg = ''
        #arg = arg.title()
        self.descricao = arg[0:self.tamdescricao]
    def setdata_lancamento(self, arg):
        self.data_lancamento = devolveDate(arg)
    def setvalor(self, arg):
        self.valor = devolveFloat(arg)
    def setidConta(self, arg):
        self.idConta = -1
        self.nomeConta = ''
        lista = Conta.selectOneById(arg)
        if lista:
            self.idConta = lista[0]
            self.nomeConta = lista[4]

    def sqlBuscaTamanho(self, coluna):
        self.conexao = self.getConexao()
        cursor = self.conexao.cursor()

        clausulaSql = "select character_maximum_length from INFORMATION_SCHEMA.COLUMNS "
        clausulaSql += "where table_catalog = 'b3' and table_name = 'capital'"
        clausulaSql += "and column_name = '" + coluna + "';"

        try:
            cursor.execute(clausulaSql)
            row = cursor.fetchone()
            tam = 0
            if row != None:
                tam = row[0]
            self.conexao.close()
            return tam
        except:
            self.conexao.close()
            return 0

    def insere(self):
        clausulaSql = 'insert into capital (datalancamento, descricao, valor, idconta) values (%s, %s, %s, %s);'

        self.conexao =self.getConexao()
        cursor = self.conexao.cursor()

        try:
            cursor.execute(clausulaSql,(self.data_lancamento, self.descricao, self.valor, self.idConta))
            self.conexao.commit()
        except  Exception as e:
            dlg = wx.MessageDialog(None, clausulaSql + '\n' + str(e), 'Erro ao inserir lançamento de Capital!', wx.OK | wx.ICON_ERROR)
            result = dlg.ShowModal()

        self.conexao.close()

    def update(self):
        clausulaSql = 'update capital set descricao = %s, datalancamento = %s, valor = %s, idconta = %s where id = %s;'

        self.conexao = self.getConexao()
        cursor = self.conexao.cursor()

        try:
            cursor.execute(clausulaSql, (self.descricao, self.data_lancamento, self.valor, self.idConta, self.id))
            self.conexao.commit()
        except  Exception as e:
            dlg = wx.MessageDialog(None, clausulaSql + '\n' + str(e), 'Erro ao atualizar lançamento de Capital <' + self.id + '>', wx.OK | wx.ICON_ERROR)
            result = dlg.ShowModal()

        self.conexao.close()

    def delete(self):
        clausulaSql = 'delete from capital '
        clausulaSql += "where id = " + str(self.id) + ";"

        self.conexao = self.getConexao()
        cursor = self.conexao.cursor()

        try:
            cursor.execute(clausulaSql)
            self.conexao.commit()
        except  Exception as e:
            dlg = wx.MessageDialog(None, clausulaSql + '\n' + str(e), 'Erro ao eliminar lançamento de Capital <' + self.id + '>', wx.OK | wx.ICON_ERROR)
            result = dlg.ShowModal()

        self.conexao.close()

    @staticmethod
    def buscaPorPeriodo(arg, idConta):
        conexao = Capital.getConexao()
        cursor = conexao.cursor()

        clausulaSql = ''
        lista = []
        if arg is None:
            clausulaSql = 'select id, datalancamento, descricao, valor ' \
                      'from capital ' \
                      'where idconta = ' + str(idConta) + ' ' \
                      'order by datalancamento;'
        else:
            clausulaSql = 'select id, datalancamento, descricao, valor ' \
                      'from capital ' \
                      'where idconta = ' + str(idConta) + ' and ' \
                      'datalancamento >= \'' + str(arg) + '\'' \
                      'order by datalancamento;'

        try:
            with conexao.cursor() as cursor:
                cursor.execute(clausulaSql)
                lista = cursor.fetchall()

        except  Exception as e:
            dlg = wx.MessageDialog(None, clausulaSql + '\n' + str(e), 'Erro ao ler lançamentos de Capital', wx.OK | wx.ICON_ERROR)
            result = dlg.ShowModal()
        conexao.close()
        return lista

