# coding: utf-8
import datetime

from diversos import *
from conta import Conta
from databasefunctions import *
from tipodespesa import TipoDespesa
import psycopg2

class Despesas():
    id = 0
    data_lancamento = None
    descricao = ''
    numeronota = ''
    valor = 0.0
    idConta = -1
    idTipoDespesa = -1
    tamdescricao = 0
    tamnumeronota = 0

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
        self.tamnumeronota = self.sqlBuscaTamanho('numeronota')

    def getAll(self):
        self.conexao = self.getConexao()
        cursor = self.conexao.cursor()

        clausulaSql = 'select id, datalancamento, descricao, valor, idconta, idtipodespesa, nuneronota ' \
                      'from despesas ' \
                      'order by datalancamento;'

        try:
            cursor.execute(clausulaSql)
        except  Exception as e:
            dlg = wx.MessageDialog(None, clausulaSql + '\n' + str(e), 'Erro ao ler despesas', wx.OK | wx.ICON_ERROR)
            result = dlg.ShowModal()

        lista = []

        lista = cursor.fetchall()

        self.conexao.close()

        return lista

    def clearDespesas(self):
        self.setid(-1)
        self.setdescricao('')
        self.setnumeronota('')
        self.setdata_lancamento(None)
        self.setvalor(0.0)
        self.setidConta(-1)
        self.setidTipoDespesa(-1)

    def populaDespesasById(self, arg):
        clausulaSql = 'select id, datalancamento, descricao, valor, idconta, idtipodespesa, numeronota ' \
                      'from despesas ' \
                      'where id = ' + str(arg) + ' order by datalancamento;'

        self.cursor = self.getConexao()
        cursor = self.conexao.cursor()

        try:
            cursor.execute(clausulaSql)
        except  Exception as e:
            dlg = wx.MessageDialog(None, clausulaSql + '\n' + str(e), 'Erro ao ler despesa <' + str(arg) + '>', wx.OK | wx.ICON_ERROR)
            result = dlg.ShowModal()

        row = cursor.fetchone()
        self.clearDespesas()
        if row != None:
            self.setid(row[0])
            self.setdata_lancamento(row[1])
            self.setdescricao(row[2])
            self.setvalor(row[3])
            self.setidConta(row[4])
            self.setidTipoDespesa(row[5])
            self.setnumeronota(row[6])

        self.conexao.close()

    def setid(self, arg):
        self.id = arg
    def setdescricao(self, arg):
        if arg is None:
            arg = ''
        self.descricao = arg[0:self.tamdescricao]
    def setnumeronota(self, arg):
        if arg is None:
            arg = ''
        #arg = arg.title()
        self.numeronota = arg[0:self.tamnumeronota]
    def setdata_lancamento(self, arg):
        self.data_lancamento = devolveDate(arg)
    def setvalor(self, arg):
        self.valor = devolveFloat(arg)
    def setidConta(self, arg):
        self.idConta = 1
        lista = Conta.selectOneById(arg)
        if lista:
            self.idConta = lista[0]
    def setidTipoDespesa(self, arg):
        self.idTipoDespesa = -1
        lista = TipoDespesa.mc_select_by_id(arg)
        if lista:
            self.idTipoDespesa = lista[0]

    def sqlBuscaTamanho(self, coluna):
        self.conexao = self.getConexao()
        cursor = self.conexao.cursor()

        clausulaSql = "select character_maximum_length from INFORMATION_SCHEMA.COLUMNS "
        clausulaSql += "where table_catalog = 'b3' and table_name = 'despesas'"
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
        clausulaSql = 'insert into despesas (datalancamento, descricao, valor, idconta, idtipodespesa, numeronota) values (%s, %s, %s, %s, %s, %s)'

        self.conexao = self.getConexao()
        cursor = self.conexao.cursor()

        try:
            cursor.execute(clausulaSql, (self.data_lancamento, self.descricao, self.valor, self.idConta, self.idTipoDespesa, self.numeronota))
            self.conexao.commit()
        except  Exception as e:
            dlg = wx.MessageDialog(None, clausulaSql + '\n' + str(e), 'Erro ao inserir despesa', wx.OK | wx.ICON_ERROR)
            result = dlg.ShowModal()

        self.conexao.close()

    def update(self):
        clausulaSql = 'update despesas set '

        clausulaSql += "descricao = '" + tiraAspas(self.descricao) + "', "
        clausulaSql += "numeronota = '" + tiraAspas(self.numeronota) + "', "
        clausulaSql += "id = " + str(self.id) + ", "
        clausulaSql += "datalancamento = '" + str(self.data_lancamento) + "', "
        clausulaSql += "idconta = " + str(self.idConta) + ", "
        clausulaSql += "idtipodespesa = " + str(self.idTipoDespesa) + ", "
        clausulaSql += "valor = " + str(self.valor) + " "
        clausulaSql += "where id = " + str(self.id) + ";"

        self.conexao = self.getConexao()
        cursor = self.conexao.cursor()  

        try:
            cursor.execute(clausulaSql)
            self.conexao.commit()
        except  Exception as e:
            dlg = wx.MessageDialog(None, clausulaSql + '\n' + str(e), 'Erro ao atualizar despesa <' + self.id + '>', wx.OK | wx.ICON_ERROR)
            result = dlg.ShowModal()

        self.conexaoclose()

    def delete(self):
        clausulaSql = 'delete from despesas '
        clausulaSql += "where id = " + str(self.id) + ";"

        self.conexao = self.getConexao()
        cursor = self.conexao.cursor()

        try:
            cursor.execute(clausulaSql)
            self.conexaocommit()
        except  Exception as e:
            dlg = wx.MessageDialog(None, clausulaSql + '\n' + str(e), 'Erro ao eliminar despesa <' + self.id + '>', wx.OK | wx.ICON_ERROR)
            result = dlg.ShowModal()

        self.conexao.close()

    @staticmethod
    def buscaPorPeriodo(arg, idconta):
        conexao = psycopg2.connect(dbname="b3", user="postgres", password="seriate", host="localhost",
                                        port="5432")
        
        conexao = Despesas.getConexao() 
        cursor = conexao.cursor()   
        clausulaSql = ''
        if arg is None:
            clausulaSql = 'select id, datalancamento, descricao, valor, dataehorainsert, idconta, numeronota ' \
                      'from despesas where idconta = ' + str(idconta) + ' ' \
                      'order by datalancamento, dataehorainsert;'
        else:
            clausulaSql = 'select id, datalancamento, descricao, valor, dataehorainsert, idconta, numeronota ' \
                      'from despesas ' \
                      'where datalancamento >= \'' + str(arg) + '\' and idconta = ' + str(idconta) + ' ' \
                      'order by datalancamento, dataehorainsert;'

        try:
            cursor.execute(clausulaSql)
            lista = cursor.fetchall()
        except  Exception as e:
            dlg = wx.MessageDialog(None, clausulaSql + '\n' + str(e), 'Erro ao ler despesas', wx.OK | wx.ICON_ERROR)
            result = dlg.ShowModal()
        finally:
            return lista

    @staticmethod
    def buscaTipos():
        conexao = Despesas.getConexao() 
        cursor = conexao.cursor()
        
        clausulaSql = 'select id, nomedespesa from tipodespesa order by nomedespesa;'        
        
        try:
            cursor.execute(clausulaSql)
            lista = cursor.fetchall()
        except  Exception as e:
            dlg = wx.MessageDialog(None, clausulaSql + '\n' + str(e), 'Erro ao ler tipos de despesas', wx.OK | wx.ICON_ERROR)
            result = dlg.ShowModal()
        finally:
            return lista

    @staticmethod
    def buscaTipoPorNome(arg):
        conexao = Despesas.getConexao() 
        cursor = conexao.cursor()
        
        clausulaSql = 'select id, nomedespesa from tipodespesa where nomedespesa = %s;'         
        
        lista = None
        try:
            cursor.execute(clausulaSql, (str(arg).upper(),))
            lista = cursor.fetchone()
        except  Exception as e:
            dlg = wx.MessageDialog(None, clausulaSql + '\n' + str(e), 'Erro ao ler tipos de despesas', wx.OK | wx.ICON_ERROR)
            result = dlg.ShowModal()
        finally:
            return lista

    @staticmethod
    def buscaTipoPorId(arg):
        conexao = Despesas.getConexao() 
        cursor = conexao.cursor()
        
        clausulaSql = 'select id, nomedespesa from tipodespesa where id = ' + str(arg) + ';'         
        
        try:
            cursor.execute(clausulaSql)
            lista = cursor.fetchone()
        except  Exception as e:
            dlg = wx.MessageDialog(None, clausulaSql + '\n' + str(e), 'Erro ao ler tipos de despesas', wx.OK | wx.ICON_ERROR)
            result = dlg.ShowModal()
            lista = None
        finally:
            return lista


