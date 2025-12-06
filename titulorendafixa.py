# coding: utf-8
import datetime

from diversos import *
from databasefunctions import *

class TituloRendaFixa():
    id = 0
    nome_titulo = ''
    tam_nome_titulo = 0

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
        self.tam_nome_titulo = self.sql_busca_tamanho('nometitulo')

    def get_all(self):
        self.conexao = self.getConexao()
        cursor = self.conexao.cursor()
        
        try:
            cursor.execute('select id, nometitulo from titulorendafixa order by nometitulo')
        except  Exception as e:
            dlg = wx.MessageDialog(None, str(e), 'Erro ao ler Titulos de Renda Fixa', wx.OK | wx.ICON_ERROR)
            result = dlg.ShowModal()

        lista = cursor.fetchall()

        self.conexao.close()

        return lista

    def clear_titulorendafixa(self):
        self.set_id(-1)
        self.set_nomeTitulo('')

    def popula_titulorendafixa_by_id(self, arg):
        self.conexao = self.getConexao()
        cursor = self.conexao.cursor()

        try:
            cursor.execute('select id, nometitulo from titulorendafixa where id = %s;', (arg,))
        except  Exception as e:
            dlg = wx.MessageDialog(None, str(e), 'Erro ao ler Titulo de Renda Fixa <' + str(arg) + '>', wx.OK | wx.ICON_ERROR)
            result = dlg.ShowModal()

        row = cursor.fetchone()
        self.clear_titulorendafixa()
        if row != None:
            self.set_id(row[0])
            self.set_nomeTitulo(row[1])

        self.conexao.close()

    def set_id(self, arg):
        self.id = arg
    def set_nomeTitulo(self, arg):
        if arg is None:
            arg = ''
        #arg = arg.title()
        self.nome_titulo = arg[0:self.tam_nome_titulo]

    def sql_busca_tamanho(self, coluna):
        self.conexao = self.getConexao()
        cursor = self.conexao.cursor()

        clausulaSql = "select character_maximum_length from INFORMATION_SCHEMA.COLUMNS "
        clausulaSql += "where table_catalog = '" + self.nome_base + "' and table_name = 'titulorendafixa' "
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
        clausulaSql = 'insert into titulorendafixa (nometitulo) values (%s);'

        self.conexao =self.getConexao()
        cursor = self.conexao.cursor()

        try:
            cursor.execute(clausulaSql,(self.nome_titulo, ))
            self.conexao.commit()
        except  Exception as e:
            dlg = wx.MessageDialog(None, clausulaSql + '\n' + str(e), 'Erro ao inserir Titulo de Renda Fixa!', wx.OK | wx.ICON_ERROR)
            result = dlg.ShowModal()

        self.conexao.close()

    def update(self):
        clausulaSql = 'update titulorendafixa set nometitulo = %s where id = %s;'

        self.conexao = self.getConexao()
        cursor = self.conexao.cursor()

        try:
            cursor.execute(clausulaSql, (self.nome_titulo, self.id))
            self.conexao.commit()
        except  Exception as e:
            dlg = wx.MessageDialog(None, clausulaSql + '\n' + str(e), 'Erro ao atualizar Titulo de Renda Fixa <' + str(self.id) + '>', wx.OK | wx.ICON_ERROR)
            result = dlg.ShowModal()

        self.conexao.close()

    def delete(self):
        self.conexao = self.getConexao()
        cursor = self.conexao.cursor()

        try:
            cursor.execute('delete from titulorendafixa where id = %s', (self.id,))
            self.conexao.commit()
        except  Exception as e:
            dlg = wx.MessageDialog(None, str(e), 'Erro ao eliminar Titulo de Renda Fixa <' + str(self.id) + '>', wx.OK | wx.ICON_ERROR)
            result = dlg.ShowModal()

        self.conexao.close()

    @staticmethod
    def mc_select_one_by_id(arg):
        conexao = TituloRendaFixa.getConexao()
        cursor = conexao.cursor()
        row = None

        try:
            cursor.execute('select id, nometitulo from titulorendafixa where id = %s;', (arg,))
            row = cursor.fetchone()
        except  Exception as e:
            dlg = wx.MessageDialog(None, str(e), 'Erro ao ler Titulo de Renda Fixa <' + str(arg) + '>', wx.OK | wx.ICON_ERROR)
            result = dlg.ShowModal()
        finally:
            conexao.close()

        return row

    @staticmethod
    def mc_select_one_by_nome(arg):
        conexao = TituloRendaFixa.getConexao()
        cursor = conexao.cursor()
        row = None

        try:
            cursor.execute('select id, nometitulo from titulorendafixa where upper(nometitulo) = upper(%s) ;', (arg,))
            row = cursor.fetchone()
        except  Exception as e:
            dlg = wx.MessageDialog(None, str(e), 'Erro ao ler Titulo de Renda Fixa <' + str(arg) + '>', wx.OK | wx.ICON_ERROR)
            result = dlg.ShowModal()
        finally:
            conexao.close()

        return row

    @staticmethod
    def mc_select_all():
        conexao = TituloRendaFixa.getConexao()
        cursor = conexao.cursor()
        
        try:
            cursor.execute('select id, nometitulo from titulorendafixa order by nometitulo')
        except  Exception as e:
            dlg = wx.MessageDialog(None, str(e), 'Erro ao ler Titulos de Renda Fixa', wx.OK | wx.ICON_ERROR)
            result = dlg.ShowModal()

        lista = cursor.fetchall()

        conexao.close()

        return lista


