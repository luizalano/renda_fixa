# coding: utf-8
import datetime

from diversos import *
from datetime import date
from databasefunctions import *
from provento import Provento
from tipoprovento import TipoProvento
from ativo import *

class AtivoNegociado():
    id_ativo = -1
    id_conta = -1
    razao_social = ''
    sigla = ''

    tamrazao_social = 0
    tamsigla = 0


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
        self.tamrazao_social = self.sqlBuscaTamanho('razaosocial')
        self.tamsigla = self.sqlBuscaTamanho('sigla')

    def getAll(self):
        self.conexao = AtivoNegociado.getConexao()
        cursor = self.conexao.cursor()

        clausulaSql = 'select a.id, a.razaosocial, a.sigla ' \
                      'from ativo as a ' \
                      'order by a.sigla;'

        try:
            cursor.execute(clausulaSql)
        except  Exception as e:
            dlg = wx.MessageDialog(None, clausulaSql + '\n' + str(e), 'Erro ao ler ativos', wx.OK | wx.ICON_ERROR)
            result = dlg.ShowModal()

        lista = cursor.fetchall()

        self.conexao.close()

        return lista

    def buscaAtivosNegociados(self, idconta):
        self.conexao = AtivoNegociado.getConexao()
        cursor = self.conexao.cursor()


        if idconta > -1:
            clausulaSql = 'select distinct idativo from ativonegociado where idconta =' \
                      ' ' + str(idconta) + ';'
        else :
            clausulaSql = 'select distinct idativo from ativonegociado;'

        try:
            cursor.execute(clausulaSql)
        except  Exception as e:
            dlg = wx.MessageDialog(None, clausulaSql + '\n' + str(e), 'Erro ao buscar ativos negociados', wx.OK | wx.ICON_ERROR)
            result = dlg.ShowModal()

        self.listaAtivos = cursor.fetchall()

        self.conexao.close()

    def clearAtivo(self):
        self.setid_ativo(-1)
        self.setrazao_social('')
        self.setsigla('')

    def insereOperacao(self, argsiglaativo, dataoperacao: date, operacao: int, valoroperacao: float, qtdeoperacao: int, idconta: int):
        self.conexao = AtivoNegociado.getConexao()
        cursor = self.conexao.cursor()
        retorno = True
        try:
            # Inserir os dados na tabela 'operacao'
            insert_query = """
                INSERT INTO ativonegociado (idativo, operacao, valoroperacao, qtdeoperacao, dataoperacao, idconta)
                VALUES ((select id from ativo where upper(sigla) = upper(%s)), %s, %s, %s, %s, %s)
            """
            cursor.execute(insert_query, (argsiglaativo, operacao, valoroperacao, qtdeoperacao, dataoperacao, idconta))

        except Exception as e:
            retorno = False

        finally:
            self.conexao.con.commit()
            self.conexao.close()
            return retorno

    def buscaProventos(self, idconta, pago):
        self.proventos.clear()
        self.proventos = Provento.sm_busca_proventos_por_conta_ativo(self.id_ativo, idconta, pago)

    def buscaTiposDeProventos(self):
        lista = TipoProvento.sm_select_all()
        return lista

    def buscaIdTipoDeProvento(self, arg):
        lista = TipoProvento.sm_recupera_por_nome(arg)
        return lista[0]

    def populaAtivoBySigla(self, arg):
        clausulaSql = 'select a.id, a.razaosocial, a.sigla ' \
                      'from ativo as a ' \
                      'where upper(a.sigla) = upper(\'' + str(arg) + '\');'

        self.conexao = AtivoNegociado.getConexao()
        cursor = self.conexao.cursor()

        try:
            cursor.execute(clausulaSql)
        except  Exception as e:
            dlg = wx.MessageDialog(None, clausulaSql + '\n' + str(e), 'Erro ao ler ativo <' + str(arg) + '>', wx.OK | wx.ICON_ERROR)
            result = dlg.ShowModal()

        row = cursor.fetchone()
        self.clearAtivo()
        if row != None:
            self.setid_ativo(row[0])
            self.setrazao_social(row[1])

        self.conexao.close()

    def populaAtivoById(self, arg):
        clausulaSql = 'select a.id, a.razaosocial, a.sigla ' \
                      'from ativo as a ' \
                      'where a.id = ' + str(arg) + ';'

        self.conexao = AtivoNegociado.getConexao()
        cursor = self.conexao.cursor()

        try:
            cursor.execute(clausulaSql)
        except  Exception as e:
            dlg = wx.MessageDialog(None, clausulaSql + '\n' + str(e), 'Erro ao ler ativo <' + str(arg) + '>', wx.OK | wx.ICON_ERROR)
            result = dlg.ShowModal()

        row = cursor.fetchone()
        self.clearAtivo()
        if row != None:
            self.setid_ativo(row[0])
            self.setrazao_social(row[1])
            self.setsigla(row[2])

        self.conexao.close()

    def existeAtivo(self, arg):
        lista = Ativo.mc_verifica_ativo_por_sigla(arg)
        self.clearAtivo()
        retorno = False
        if lista:
            retorno = True

        return retorno

    def getrazao_social(self):
        return self.razao_social
    def getid_ativo(self):
        return self.id_ativo
    def getsigla(self):
        return self.sigla

    def setlan(self, idconta):
        self.conexao = AtivoNegociado.getConexao()
        cursor = self.conexao.cursor()
        self.lan.clear()

        if idconta == (-1):
            clausulaSql = 'select a.id, a.dataoperacao, a.operacao, a.qtdeoperacao, a.valoroperacao  ' \
                      'from ativonegociado as a ' \
                      'where a.idativo = ' + str(self.id_ativo) +  ' '\
                      'order by a.dataoperacao, a.ordemdia, a.id;'
        else:
            clausulaSql = 'select a.id, a.dataoperacao, a.operacao, a.qtdeoperacao, a.valoroperacao  ' \
                          'from ativonegociado as a ' \
                          'where a.idativo = ' + str(self.id_ativo) + ' ' \
                          'and a.idconta = ' + str(idconta) + ' ' \
                          'order by a.dataoperacao, a.ordemdia, a.id;'
        try:
            cursor.execute(clausulaSql)
        except  Exception as e:
            dlg = wx.MessageDialog(None, clausulaSql + '\n' + str(e), 'Erro ao ler ativos negociados', wx.OK | wx.ICON_ERROR)
            result = dlg.ShowModal()

        self.lan = []

        row = cursor.fetchone()
        while row != None:
            self.lan.append([row[0], row[1], row[2], row[3], row[4]])

            row = cursor.fetchone()

    def limpaListasRenda(self):
        self.listaRendaAcoes.clear()
        self.listaRendaProventos.clear()
        self.listaRendaDespesas.clear()

    def encheListasRenda(self):
        comprado = self.encheListaRendaAcoes()
        self.encheListaRendaProventos()
        return comprado

    def linhaExistente(self, data):
        linha = (-1)
        for row in self.listaRendaAcoes:
            linha +=1
            if row[0] == data:
                return linha

        return (-1)

    def estabeleceRendimentoPorAcoes(self):
        saldoQtde = 0
        aux = self.sigla
        saldoValor = 0.0
        resultado = 0.0
        precomedio = 0.0
        compras = 0.0
        vendas = 0.0
        negocios = 0
        linha = 0
        listaProvisoria = []
        for  row in self.lan:
            dataOperacao = row[1]
            numoperacao = devolveInteger(row[2])
            valorOperacao = devolveFloat(row[4])
            qtdeOperacao = devolveInteger(row[3])
            valorCompraStr = ''
            valorVendaStr = ''
            ganho = 0.0
            strGanho = ""
            strResultado = ''
            resultado = 0.0
            if numoperacao == 1:
                totalOperacao = qtdeOperacao * valorOperacao
                compras += totalOperacao
                if precomedio == 0:
                    precomedio = valorOperacao
                else:
                    precomedio = ((precomedio * saldoQtde) + totalOperacao) / (saldoQtde + qtdeOperacao)
                saldoQtde += qtdeOperacao

            else:
                totalOperacao = valorOperacao * qtdeOperacao
                vendas += totalOperacao
                resultado = totalOperacao - (qtdeOperacao * precomedio)
                #resultado = float(int(resultado*100.0)) / 100.0

                saldoQtde -= qtdeOperacao
                if saldoQtde == 0:
                    precomedio = 0.0

                if resultado != 0.0:
                    listaProvisoria.append([dataOperacao, resultado])
        comprado = saldoQtde * precomedio
        return comprado, compras, vendas, listaProvisoria

    def encheListaRendaAcoes(self):
        #a.dataoperacao, a.operacao, a.qtdeoperacao, a.valoroperacao
        comprado, compras, vendas, listaProvisoria = self.estabeleceRendimentoPorAcoes()
        for row in listaProvisoria:
            dataOperacao = row[0].strftime("%Y/%m")
            #valorRendimento = float(int(row[1] * 100.0) / 100.0)
            valorRendimento = float(row[1])
            if len(self.listaRendaAcoes) == 0:
                self.listaRendaAcoes.append([dataOperacao, valorRendimento])
            else:
                indice = next((i for i, linha in enumerate(self.listaRendaAcoes) if linha[0] == dataOperacao), -1)
                if indice < 0:
                    self.listaRendaAcoes.append([dataOperacao, valorRendimento])
                else:
                    self.listaRendaAcoes[indice][1] += valorRendimento
        return comprado, compras, vendas

    def encheListaRendaProventos(self):
        for row in self.proventos:
            dataOperacao = row[1].strftime("%Y/%m")
            valorRendimento = float(int(row[2] * 100.0) / 100.0)
            if len(self.listaRendaProventos) == 0:
                self.listaRendaProventos.append([dataOperacao, valorRendimento])
            else:
                for item in self.listaRendaProventos:
                    if item[0] == dataOperacao:
                        item[1] += valorRendimento
                        break
                else:
                    self.listaRendaProventos.append([dataOperacao, valorRendimento])

    def buscarRadar(self, siglaAtivo):
        self.conexao = AtivoNegociado.getConexao()
        cursor = self.conexao.cursor()
        lista = []
        try:
            clausulasql = "select r.id, r.datacom, r.dataprovavel, r.tipoprovento, r.dy, r.valorprovento from radar as r " \
                          "join ativo as a on a.id = r.idativo " \
                          "where upper(a.sigla) =  upper('" + siglaAtivo + "');"
            cursor.execute(clausulasql)

            row = cursor.fetchone()
            while row != None:
                lista.append([row[0], row[1], row[2], row[3], row[4], row[5]])

                row = cursor.fetchone()

        except  Exception as e:
            lista = []
        finally:
            # Commit e fechamento
            self.conexao.close()
            return lista

    def setid_ativo(self, arg):
        self.id_ativo = arg
    def setrazao_social(self, arg):
        if arg is None:
            arg = ''
        arg = arg.title()
        self.razao_social = arg[0:self.tamrazao_social]
    def setsigla(self, arg):
        if arg is None:
            arg = ''
        arg = arg.title()
        self.sigla = arg[0:self.tamsigla]

    def sqlBuscaTamanho(self, coluna):
        self.conexao = AtivoNegociado.getConexao()
        cursor = self.conexao.cursor()

        clausulaSql = "select character_maximum_length from INFORMATION_SCHEMA.COLUMNS "
        clausulaSql += "where table_catalog = 'b3' and table_name = 'ativo'"
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
    
    @staticmethod
    def deleteOpoeracaoGenerico(id):
        retorno = True
        try:
            conexao = AtivoNegociado.getConexao()
            cursor = conexao.cursor()
            insert_query = """
                delete from ativonegociado where id = %s 
            """
            cursor.execute(insert_query, (id,))

        except Exception as e:
            retorno = False

        finally:
            conexao.con.commit()
            conexao.close()
            return retorno

    
    @staticmethod
    def devolveSiglaAtivo(id):
        conexao = AtivoNegociado.getConexao()
        with conexao.cursor() as cursor:
            cursor.execute("SELECT sigla FROM ativo WHERE id = %s", (id,))
            row = cursor.fetchone()
            conexao.close()
            if row: return row[0]
            else: return None

    @staticmethod
    def devolveNomeAtivobySigla(arg):
        conexao = AtivoNegociado.getConexao()
        with conexao.cursor() as cursor:
            cursor.execute("SELECT razaosocial FROM ativo WHERE upper(sigla) = upper(%s)", (arg,))
            row = cursor.fetchone()
            conexao.close()
            if row: return row[0]
            else: return None

def main():
    ativo = Ativo()
    ativo.populaAtivoBySigla('VALE3')
    print(ativo.getsigla())

    print('acabou')


if __name__ == '__main__':
    main()