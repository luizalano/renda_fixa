# coding: utf-8

from diversos import *
from ativo import *
from cotacao import Cotacao
from conta import Conta
from wxFrameMG import FrameMG

from wx import *

class FrmCarteira(FrameMG):
    insert = False
    caminho = '.\\icones\\'
    id_conta = -1
    sigla_bolsa = None


    def __init__(self, idContaInicial = -1, siglaBolsa = -1):
        self.lista_negociacoes = []
        self.lista_ativos = []
        self.lista_patrimonio = []

        self.total_comprado = 0.0
        self.sigla_bolsa = siglaBolsa

        super(FrmCarteira, self).__init__(pai=None, titulo='Ativos em carteira',
                                       lar = 870, alt = 730,
                                       xibot = 150, split=False)

        self.criaComponentes()

    def criaComponentes(self):
        X = self.posx(3)
        Y = self.posy(2)
        tamX = self.larguraEmPx(220)
        tamY = self.alturaEmPx(15)

        self.setAvancoVertical(8)

        self.grid = wx.grid.Grid(self.painel, pos=(30, 10), size=(800, 590))
        self.grid.CreateGrid(0, 6)

        # Definindo os tamanhos das colunas
        col_sizes = [80, 200, 80, 120, 100, 120]
        col_labels = ["Bolsa", "Conta", "Ativo", "Valor Comprado", "Quantidade", "Preço médio"]

        for i, (size, label) in enumerate(zip(col_sizes, col_labels)):
            self.grid.SetColSize(i, size)
            self.grid.SetColLabelValue(i, label)

        y = 12
        
        self.getConexao()
        self.botaoSalva.Hide()
        self.botaoDelete.Hide()
        self.botaoNovo.Hide()
        self.botaoCancela.Hide()

        self.busca_tudo(None)

        self.Show()

    def busca_tudo(self, event):
        self.conexao = FrmCarteira.getConexao()
        self.busca_lista_ativos()
        self.busca_renda_por_ativo()
        self.monta_grid()
        self.conexao.close()   
                  
    @staticmethod
    def getConexao():
        try:
            con = ConectaBD.retornaConexao()
            return con
        except Exception as e:
            print(f"Erro ao conectar com o banco: {e}")
            return False
        
    def busca_lista_ativos(self):
        clausulaSql = 'select distinct idativo, idconta from ativonegociado'

        cursor = self.conexao.cursor()
        try:
            cursor.execute(clausulaSql)
        except  Exception as e:
            dlg = wx.MessageDialog(None, clausulaSql + '\n' + str(e), 'Erro ao buscar ativos negociados', wx.OK | wx.ICON_ERROR)
            result = dlg.ShowModal()

        self.lista_ativos = cursor.fetchall()

    def busca_renda_por_ativo(self):
        self.lista_patrimonio.clear()

        self.total_comprado = 0.0
        self.total_compras = 0.0
        self.total_vendas = 0.0
        for row in self.lista_ativos:
            self.busca_negociacoes(row[0], row[1])
            self.estabelece_rendimento_por_acoes()

    def busca_negociacoes(self, idativo, idconta):
        self.lista_negociacoes.clear()
        cursor = self.conexao.cursor()

        clausulaSql = 'select b.sigla, c.nomeconta, an.id, an.dataoperacao, an.operacao, an.qtdeoperacao, an.valoroperacao, an.idativo, a.sigla  ' \
                  'from ativonegociado as an ' \
                  'join conta as c on c.id = an.idconta ' \
                  'join ativo as a on a.id = an.idativo ' \
                  'join bolsa as b on b.id = a.idbolsa ' \
                  'where an.idativo = ' + str(idativo) +  ' and an.idconta = ' + str(idconta) + ' '\
                  'order by an.dataoperacao, an.ordemdia, an.id, c.nomeconta, b.sigla;'

        try:
            cursor.execute(clausulaSql)
        except  Exception as e:
            dlg = wx.MessageDialog(None, clausulaSql + '\n' + str(e), 'Erro ao ler ativos negociados', wx.OK | wx.ICON_ERROR)
            result = dlg.ShowModal()

        self.lista_negociacoes = cursor.fetchall()

    def estabelece_rendimento_por_acoes(self):
        saldoQtde = 0
        precomedio = 0.0
        listaProvisoria = []
        
        nome_conta_ant = ''
        nome_bolsa_ant = ''
        for row in self.lista_negociacoes:
            nome_conta= row[1]
            nome_bolsa= row[0]
            sigla_ativo = row[8]
            id_ativo = row[7]
            if nome_conta != nome_conta_ant:
                if nome_conta_ant != '':
                    comprado = saldoQtde * precomedio
                    if comprado > 0:
                        self.lista_patrimonio.append([nome_bolsa_ant, nome_conta_ant, comprado, saldoQtde, precomedio, id_ativo, sigla_ativo])
                saldoQtde = 0
                precomedio = 0.0
                nome_conta_ant = nome_conta
                nome_bolsa_ant = nome_bolsa
            dataOperacao = row[3]
            numoperacao = devolveInteger(row[4])
            valorOperacao = devolve_float_de_formatacao_completa(row[6])
            qtdeOperacao = devolveInteger(row[5])
            if numoperacao == 1:
                totalOperacao = qtdeOperacao * valorOperacao
                if precomedio == 0:
                    precomedio = valorOperacao
                else:
                    precomedio = ((precomedio * saldoQtde) + totalOperacao) / (saldoQtde + qtdeOperacao)
                saldoQtde += qtdeOperacao

            else:
                saldoQtde -= qtdeOperacao
                if saldoQtde == 0:
                    precomedio = 0.0

        comprado = saldoQtde * precomedio
        if comprado > 0:
            self.lista_patrimonio.append([nome_bolsa_ant, nome_conta_ant, comprado, saldoQtde, precomedio, id_ativo, sigla_ativo])

    def monta_grid(self):
        cursor = self.conexao.cursor()
        total_valor_atual = 0.0
        self.grid.ClearGrid()
        if self.grid.GetNumberRows() > 0:
            self.grid.DeleteRows(0, self.grid.GetNumberRows())
        linha = (-1)
        for row in self.lista_patrimonio:

            linha += 1
            self.grid.AppendRows()

            cotacao = Ativo.get_ultima_cotacao(row[6])
            valor_atual = cotacao * float(row[4])
            total_valor_atual += valor_atual
            valor_mercado = Ativo.get_valor_mercado_yfinance(row[6], self.sigla_bolsa)
            variacao = (valor_atual / float(row[3]) - 1) * 100.0

            qtdeFormatada = f"{float(row[3]):,.0f}".replace(",", "X").replace(".", ",").replace("X", ".")

            self.grid.SetCellValue(linha, 0, row[0])
            self.grid.SetCellValue(linha, 1, row[1])
            self.grid.SetCellValue(linha, 2, row[6])
            self.grid.SetCellValue(linha, 3, formata_numero(float(row[2])))
            self.grid.SetCellValue(linha, 4, qtdeFormatada)
            self.grid.SetCellValue(linha, 5, formata_numero(float(row[4])))

            self.grid.SetCellAlignment(linha,  2, wx.ALIGN_CENTRE, wx.ALIGN_CENTRE)
            self.grid.SetCellAlignment(linha,  3, wx.ALIGN_RIGHT, wx.ALIGN_RIGHT)
            self.grid.SetCellAlignment(linha,  4, wx.ALIGN_RIGHT, wx.ALIGN_RIGHT)
            self.grid.SetCellAlignment(linha,  5, wx.ALIGN_RIGHT, wx.ALIGN_RIGHT)


            if linha % 2 != 0:
                for i in range(0, 6):
                    self.grid.SetCellBackgroundColour(linha, i, wx.Colour(230, 255, 255))


def main():
    app = wx.App()
    frmRendaTotal = FrmCarteira(None, 'B3')
    app.MainLoop()


if __name__ == '__main__':
    main()



