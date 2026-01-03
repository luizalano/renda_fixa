# coding: utf-8
import datetime

from diversos import *
from conta import Conta
from databasefunctions import *
from tipodespesa import TipoDespesa
from notanegociacao import NotaNegociacao
import psycopg2

class Despesas():
    id = 0
    data_lancamento = None
    data_efetivacao = None
    descricao = ''
    numero_nota = ''
    valor = 0.0
    id_conta = -1
    id_tipo_despesa = -1
    notaNegociacao = NotaNegociacao() 

    def __init__(self):
        self.tam_descricao = 0
        self.tam_numero_nota = 0
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
        self.tam_numero_nota = self.sql_busca_tamanho('numeronota')

    def get_all(self):
        self.conexao = self.getConexao()
        cursor = self.conexao.cursor()

        clausulaSql = 'select id, datalancamento, descricao, valor, idconta, idtipodespesa, numeronota, dataefetivacao ' \
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

    def clear_despesas(self):
        self.set_id(-1)
        self.set_descricao('')
        self.set_numero_nota('')
        self.set_data_lancamento(None)
        self.set_data_efetivacao(None)
        self.set_valor(0.0)
        self.set_id_conta(-1)
        self.set_id_tipo_despesa(-1)

    def popula_despesas_by_id(self, arg):
        clausulaSql = 'select id, datalancamento, descricao, valor, idconta, idtipodespesa, numeronota, dataefetivacao ' \
                      'from despesas ' \
                      'where id = ' + str(arg) + ' order by datalancamento;'

        self.conexao = self.getConexao()
        cursor = self.conexao.cursor()

        try:
            cursor.execute(clausulaSql)
        except  Exception as e:
            dlg = wx.MessageDialog(None, clausulaSql + '\n' + str(e), 'Erro ao ler despesa <' + str(arg) + '>', wx.OK | wx.ICON_ERROR)
            result = dlg.ShowModal()

        row = cursor.fetchone()
        self.clear_despesas()
        if row != None:
            self.set_id(row[0])
            self.set_data_lancamento(row[1])
            self.set_descricao(row[2])
            self.set_valor(row[3])
            self.set_id_conta(row[4])
            self.set_id_tipo_despesa(row[5])
            self.set_numero_nota(row[6])
            self.set_data_efetivacao(row[7])

        self.conexao.close()

    def set_id(self, arg):
        self.id = arg
    def set_descricao(self, arg):
        if arg is None:
            arg = ''
        self.descricao = arg[0:self.tam_descricao]
    def set_numero_nota(self, arg):
        if arg is None:
            arg = ''
        #arg = arg.title()
        self.numero_nota = arg[0:self.tam_numero_nota]
    def set_data_lancamento(self, arg):
        self.data_lancamento = devolveDate(arg)
    def set_data_efetivacao(self, arg):
        self.data_efetivacao = devolveDate(arg)
    def set_valor(self, arg):
        self.valor = devolve_float_de_formatacao_completa(arg)
    def set_id_conta(self, arg):
        self.id_conta = 1
        lista = Conta.mc_select_one_by_id(arg)
        if lista:
            self.id_conta = lista[0]
    def set_id_tipo_despesa(self, arg):
        self.id_tipo_despesa = -1
        lista = TipoDespesa.mc_select_by_id(arg)
        if lista:
            self.id_tipo_despesa = lista[0]
    def sql_busca_tamanho(self, coluna):
        self.conexao = self.getConexao()
        cursor = self.conexao.cursor()

        clausulaSql = "select character_maximum_length from INFORMATION_SCHEMA.COLUMNS "
        clausulaSql += "where table_catalog = '" + self.nome_base + "' and table_name = 'despesas'"
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
        self.conexao = self.getConexao()
        cursor = self.conexao.cursor()

        self.notaNegociacao.criaNotaNegociao(self.numero_nota, self.data_lancamento, self.id_conta)

        clausulaSql = 'insert into despesas (datalancamento, descricao, valor, idconta, idtipodespesa, numeronota, dataefetivacao) values (%s, %s, %s, %s, %s, %s) returning id'

        try:
            cursor.execute(clausulaSql, 
                           (self.data_lancamento, self.descricao, self.valor, self.id_conta, self.id_tipo_despesa, self.numero_nota, self.data_efetivacao))
            self.conexao.commit()
        except  Exception as e:
            dlg = wx.MessageDialog(None, clausulaSql + '\n' + str(e), 'Erro ao inserir despesa', wx.OK | wx.ICON_ERROR)
            result = dlg.ShowModal()
        finally:
            self.conexao.close()

    def update(self):
        clausulaSql = 'update despesas set ' \
                      'descricao = %s, ' \
                      'numeronota = %s, ' \
                      'datalancamento = %s, ' \
                      'dataefetivacao = %s, ' \
                      'idconta = %s, ' \
                      'idtipodespesa = %s, ' \
                      'valor = %s ' \
                      'where id = %s'

        #clausulaSql += "descricao = '" + tiraAspas(self.descricao) + "', "
        #clausulaSql += "numeronota = '" + tiraAspas(self.numero_nota) + "', "
        #clausulaSql += "id = " + str(self.id) + ", "
        #clausulaSql += "datalancamento = '" + str(self.data_lancamento) + "', "
        #clausulaSql += "dataefetivacao = '" + str(self.data_efetivacao) + "', "
        #clausulaSql += "idconta = " + str(self.id_conta) + ", "
        #clausulaSql += "idtipodespesa = " + str(self.id_tipo_despesa) + ", "
        #clausulaSql += "valor = " + str(self.valor) + " "
        #clausulaSql += "where id = " + str(self.id) + ";"

        self.conexao = self.getConexao()
        cursor = self.conexao.cursor()  

        try:
            cursor.execute(clausulaSql,(self.descricao, self.numero_nota, self.data_lancamento, self.data_efetivacao, self.id_conta, self.id_tipo_despesa, self.valor, self.id))
            self.conexao.commit()
        except  Exception as e:
            dlg = wx.MessageDialog(None, clausulaSql + '\n' + str(e), 'Erro ao atualizar despesa <' + self.id + '>', wx.OK | wx.ICON_ERROR)
            result = dlg.ShowModal()
        finally:
            self.conexao.close()

    def delete(self):
        self.conexao = self.getConexao()
        cursor = self.conexao.cursor()

        try:
            cursor.execute("delete from despesas where id = %s", (self.id,))
            self.conexao.commit()
        except  Exception as e:
            dlg = wx.MessageDialog(None, str(e), 'Erro ao eliminar despesa <' + str(self.id) + '>', wx.OK | wx.ICON_ERROR)
            result = dlg.ShowModal()
        finally:
            self.conexao.close()

    @staticmethod
    def mc_busca_por_periodo(arg, idconta):
        conexao = Despesas.getConexao() 
        cursor = conexao.cursor()   
        clausulaSql = ''
        if arg is None:
            clausulaSql = 'select id, datalancamento, descricao, valor, dataehorainsert, idconta, numeronota, dataefetivacao ' \
                      'from despesas where idconta = ' + str(idconta) + ' ' \
                      'order by datalancamento, dataehorainsert;'
        else:
            clausulaSql = 'select id, datalancamento, descricao, valor, dataehorainsert, idconta, numeronota, dataefetivacao ' \
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
    def mc_busca_tipos():
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
    def mc_busca_tipo_por_nome(arg):
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
    def mc_busca_tipo_por_id(arg):
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

    @staticmethod
    def mc_busca_todas_despesas_por_mes():
        try:
            conn = Despesas.getConexao()
            cursor = conn.cursor()

            consulta = '''
                SELECT 
                    TO_CHAR(d.datalancamento, 'YYYY/MM') AS mes_ano,
                    t.nomedespesa,
                    SUM(d.valor) AS total
                FROM despesas d
                JOIN tipodespesa t ON d.idtipodespesa = t.id
                GROUP BY mes_ano, t.nomedespesa
                ORDER BY mes_ano;
            '''

            cursor.execute(consulta)
            lista = cursor.fetchall()

        except  Exception as e:
            dlg = wx.MessageDialog(None, str(e), 'Erro ao buscar despesas por mês', wx.OK | wx.ICON_ERROR)
            result = dlg.ShowModal()
            lista = None
        finally:
            conn.close()
            return lista
        
    @staticmethod
    def mc_busca_despesas_por_mes_ano(mes, ano):
        try:
            conn = Despesas.getConexao()
            cursor = conn.cursor()
            
            consulta = '''
                SELECT d.datalancamento, t.nomedespesa, SUM(d.valor) AS total 
                FROM despesas d JOIN tipodespesa t ON d.idtipodespesa = t.id 
                WHERE EXTRACT(year FROM d.datalancamento) = %s and EXTRACT(month FROM d.datalancamento) = %s  
                GROUP BY d.datalancamento, t.nomedespesa ORDER BY d.datalancamento;
            '''

            cursor.execute(consulta, (ano, mes))
            lista = cursor.fetchall()

        except  Exception as e:
            dlg = wx.MessageDialog(None, str(e), 'Erro ao buscar despesas por mês', wx.OK | wx.ICON_ERROR)
            result = dlg.ShowModal()
            lista = None
        finally:
            conn.close()
            return lista
        
    @staticmethod
    def mc_busca_despesas_por_conta(idconta):
        conexao = Despesas.getConexao()
        cursor = conexao.cursor()

        try:
            cursor.execute("select datalancamento, valor from despesas where idconta = %s order by datalancamento ;", (idconta,))
        except  Exception as e:
            dlg = wx.MessageDialog(None, str(e), 'Erro ao ler despesas!', wx.OK | wx.ICON_ERROR)
            result = dlg.ShowModal()

        lista =  cursor.fetchall()
        conexao.close()

        return lista

