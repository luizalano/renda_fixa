# coding: utf-8
import psycopg2
import json
import sys
from psycopg2._psycopg import cursor
import wx


class ConectaBD():

    usuario = ''
    senha = ''
    banco = ''
    base = ''
    local = ''
    porta = 5432

    def __init__(self):
        
        self.fileSettings = open(".\\settings.cfg", )
        self.dataSettings = json.load(self.fileSettings)

        self.recuperaDadosParaCoexao(self.dataSettings)

    def recuperaDadosParaCoexao(self, configFile):
        data = configFile
        self.usuario = data['settings']['database']['user']
        self.senha = data['settings']['database']['password']
        self.banco = data['settings']['database']['banco']
        self.base = data['settings']['database']['base']
        self.local = data['settings']['database']['url']
        self.porta = data['settings']['database']['porta']

    def trocaPontoPorVirgula(argStr):
        return argStr.replace('.', ',')


    def trocaVirgulaPorPonto(argStr):
        return argStr.replace(',', '.')

    def conectaPostGres(self):
        try:
            conpg__ = psycopg2.connect(user=self.usuario,
                                       password=self.senha,
                                       host=self.local,
                                       port=self.porta,
                                       database=self.base)

            return conpg__

        except (Exception, psycopg2.Error) as error:
            dlg = wx.MessageDialog(None, 'Conexão falhou. Verifique o código',
                                   'Erro na conexão ao Postgres', wx.OK | wx.ICON_ERROR)
            result = dlg.ShowModal()
            return None, None



    def executaSQL(self, sql):
        """Executa INSERT, UPDATE ou DELETE"""
        try:
            self.cursor.execute(sql)
            self.con.commit()  # Confirma a transação
        except Exception as e:
            print(f"Erro ao executar SQL: {e}")
            self.con.rollback()  # Desfaz a operação em caso de erro

    def executaSelect(self, sql):
        """Executa um SELECT e retorna os resultados"""
        try:
            self.cursor.execute(sql)
            return self.cursor.fetchall()  # Retorna os resultados
        except Exception as e:
            print(f"Erro ao executar SELECT: {e}")
            return None

    def conectaBanco(self):
        con = None
        con = self.conectaPostGres()
        return con
    
    @staticmethod
    def retornaConexao():
        fileSettings = open(".\\settings.cfg", )
        fonte = json.load(fileSettings)

        usuario = fonte['settings']['database']['user']
        senha = fonte['settings']['database']['password']
        banco = fonte['settings']['database']['banco']
        base = fonte['settings']['database']['base']
        local = fonte['settings']['database']['url']
        porta = fonte['settings']['database']['porta']

        con = None
        try:
            con = psycopg2.connect(user=usuario, password=senha, host=local, port=porta, database=base)
            return con

        except (Exception, psycopg2.Error) as error:
            dlg = wx.MessageDialog(None, 'Conexão falhou. Verifique o código',
                                   'Erro na conexão ao Postgres', wx.OK | wx.ICON_ERROR)
            result = dlg.ShowModal()
            return None


