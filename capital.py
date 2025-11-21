# coding: utf-8
import datetime

from diversos import *
from conta import *
from databasefunctions import *

class Capital():
    id = 0
    data_lancamento = 11
    descricao = ''
    id_conta = -1
    nome_conta = ''
    valor = 0.0
    tam_descricao = 0

    def __init__(self):
        self.nome_base = ConectaBD.mc_retorna_nome_base()
        self.define_tamanhos()

    @staticmethod
    def getConexao():
        try:
            con = ConectaBD.retornaConexao()
            return con
        except Exception as e:
            print(f"Erro ao conectar com o banco: {e}")
            return False

    def define_tamanhos(self):
        self.tam_descricao = self.sql_busca_tamanho('descricao')

    def get_all(self):
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

    def clear_capital(self):
        self.set_id(-1)
        self.set_descricao('')
        self.set_data_lancamento('')
        self.set_valor(0.0)
        self.set_id_conta(-1)

    def popula_capital_by_id(self, arg):
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
        self.clear_capital()
        if row != None:
            self.set_id(row[0])
            self.set_data_lancamento(row[1])
            self.set_descricao(row[2])
            self.set_valor(row[3])
            self.set_id_conta(row[4])

        self.conexao.close()

    def set_id(self, arg):
        self.id = arg
    def set_descricao(self, arg):
        if arg is None:
            arg = ''
        #arg = arg.title()
        self.descricao = arg[0:self.tam_descricao]
    def set_data_lancamento(self, arg):
        self.data_lancamento = devolveDate(arg)
    def set_valor(self, arg):
        self.valor = devolve_float_de_formatacao_completa(arg)
    def set_id_conta(self, arg):
        self.id_conta = -1
        self.nome_conta = ''
        lista = Conta.mc_select_one_by_id(arg)
        if lista:
            self.id_conta = lista[0]
            self.nome_conta = lista[4]

    def sql_busca_tamanho(self, coluna):
        self.conexao = self.getConexao()
        cursor = self.conexao.cursor()

        clausulaSql = "select character_maximum_length from INFORMATION_SCHEMA.COLUMNS "
        clausulaSql += "where table_catalog = '" + self.nome_base + "' and table_name = 'capital'"
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
            cursor.execute(clausulaSql,(self.data_lancamento, self.descricao, self.valor, self.id_conta))
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
            cursor.execute(clausulaSql, (self.descricao, self.data_lancamento, self.valor, self.id_conta, self.id))
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
    def mc_busca_por_periodo(arg, idConta):
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

    @staticmethod
    def mc_busca_capital_por_conta(idconta):
        conexao = Capital.getConexao()
        cursor = conexao.cursor()

        clausulaSql = 'select datalancamento, valor from capital ' \
                      'where idconta = %s order by datalancamento;'

        try:
            cursor.execute(clausulaSql, (idconta,))
        except  Exception as e:
            dlg = wx.MessageDialog(None, clausulaSql + '\n' + str(e), 'Erro ao ler alterações de Capital!', wx.OK | wx.ICON_ERROR)
            result = dlg.ShowModal()

        lista = cursor.fetchall()
        conexao.close()

        return lista

