# coding: utf-8

from diversos import *
from ativo import *
from cotacao import Cotacao
from conta import Conta
from wxFrameMG import FrameMG
import psycopg2
#from ClienteDeQuem import ClienteDeQuem

from wx import *

#import wx
#import wx.grid
#import wx.Button

class FrmCarteira(FrameMG):
    insert = False
    caminho = '.\\icones\\'
    idConta = -1
    siglaBolsa = None


    def __init__(self, idContaInicial, siglaBolsa):
        self.listaNegociacoes = []
        self.listaAtivos = []
        self.listaPatrimonio = []

        self.totalComprado = 0.0
        self.siglaBolsa = siglaBolsa

        super(FrmCarteira, self).__init__(pai=None, titulo='Ativos em carteira',
                                       lar = 1100, alt = 730,
                                       xibot = 150, split=False)

        self.criaComponentes()
        self.setConta(idContaInicial)

    def criaComponentes(self):
        X = self.posx(3)
        Y = self.posy(2)
        tamX = self.larguraEmPx(220)
        tamY = self.alturaEmPx(15)

        self.setAvancoVertical(8)

        label0811, self.cbConta = self.criaCombobox(self.painel, pos=(3, 0), tamanho=22, label='Conta')
        self.cbConta.Bind(wx.EVT_COMBOBOX, self.contaSelecionada)

        label0991, self.cbBolsa = self.criaCombobox(self.painel, pos=(30, 0), tamanho=22, label='Bolsa')
        self.cbBolsa.Bind(wx.EVT_COMBOBOX, self.bolsaSelecionada)

        self.btnBuscaaAtivos = Button(self.painel, id=ID_ANY, label="Busca Ativos"
                                      , pos=(self.posx(60), self.posy(0)+15),
                                      size=(self.posx(15), self.posy(1)-30), style=0)  
        self.Bind(wx.EVT_BUTTON, self.buscaTudo, self.btnBuscaaAtivos)


        label10555, self.txtNomeMoeda = self.criaCaixaDeTexto(self.painel, pos=(X + 65, 0),
                                                    label='Moeda da conta', tamanho = (15, 1),
                                                    max=0, multi=False)
        self.txtNomeMoeda.SetForegroundColour(wx.BLACK)
        self.txtNomeMoeda.SetBackgroundColour(wx.Colour(237, 237, 237))
        self.txtNomeMoeda.SetEditable(False)
        self.negrita(self.txtNomeMoeda)

        label1055, self.txtValorMoeda = self.criaCaixaDeTexto(self.painel, pos=(X + 85, 0),
                                                    label='Última cotação', tamanho = (15, 1),
                                                    max=0, multi=False, align='direita')
        self.txtValorMoeda.SetForegroundColour(wx.BLACK)
        self.txtValorMoeda.SetBackgroundColour(wx.Colour(237, 237, 237))
        self.txtValorMoeda.SetEditable(False)
        self.negrita(self.txtValorMoeda)

        self.grid = wx.grid.Grid(self.painel, pos=(30, 70), size=(980, 530))
        self.grid.CreateGrid(0, 8)

        # Definindo os tamanhos das colunas
        col_sizes = [80, 120, 100, 120, 100, 120, 100, 140]
        col_labels = ["Ativo", "Valor Comprado", "Quantidade", "Preço médio", "Última cotação", "Patrimônio", "Variação %", "Valor de Mercado"]

        for i, (size, label) in enumerate(zip(col_sizes, col_labels)):
            self.grid.SetColSize(i, size)
            self.grid.SetColLabelValue(i, label)


        y = 12

        label08, self.txtComprado = self.criaCaixaDeTexto(self.painel, pos=(35, y), label='Comprado',
                                                        tamanho = (12, 1),  align='direita' )
        label09, self.txtPatrimonio = self.criaCaixaDeTexto(self.painel, pos=(55, y), label='Valor atual',
                                                        tamanho = (12, 1),  align='direita' )
        label10, self.txtVariacao = self.criaCaixaDeTexto(self.painel, pos=(75, y), label='Variação',
                                                        tamanho = (12, 1),  align='direita' )

        # Saldo Bancário
        label885, self.txtSaldoBancario = self.criaCaixaDeTexto(self.painel, pos=(95, y),
                                                    label='Saldo bancário', tamanho = (15, 1),
                                                    max=0, multi=False, align='direita')
        self.txtSaldoBancario.SetForegroundColour(wx.BLACK)
        self.txtSaldoBancario.SetBackgroundColour(wx.Colour(237, 237, 237))
        self.txtSaldoBancario.SetEditable(False)
        
        self.negrita(self.txtValorMoeda)

        self.getConexao()
        self.botaoSalva.Hide()
        self.botaoDelete.Hide()
        self.botaoNovo.Hide()
        self.botaoCancela.Hide()

        self.encheComboContas()
        self.encheComboBolsas()

        self.Show()

    def encheComboContas(self):
        lista = Conta.mc_select_all()
        self.cbConta.Clear()
        for row in lista:
            self.cbConta.Append(row[4])

    def encheComboBolsas(self):
        cursor = self.conexao.cursor()

        lista = None
        try:
            cursor.execute('select sigla from bolsa order by sigla;')
            lista = cursor.fetchall()
        except  Exception as e:
            dlg = wx.MessageDialog(None, str(e), 'Erro ao ler ativos negociados', wx.OK | wx.ICON_ERROR)
            result = dlg.ShowModal()

        self.cbBolsa.Clear()
        for row in lista:
            self.cbBolsa.Append(row[0])

        if self.siglaBolsa:
            self.cbBolsa.SetSelection(self.indiceCb(self.cbBolsa, self.siglaBolsa))

    def indiceCb(self, cb, chave):
        indice = 0
        i = 0
        max = cb.Count
        while i < max:
            lido = cb.GetString(i)
            if lido == chave:
                indice = i
                i = max
            i += 1

        return indice

    def setConta(self, idConta):
        lista = Conta.selectOneById(idConta)
        if lista:
            self.cbConta.SetSelection(self.indiceCb(self.cbConta, lista[4]))
            self.contaSelecionada(None)

    def contaSelecionada(self, event):
        nomeConta = self.cbConta.GetStringSelection()
        listaConta = None
        listaConta = Conta.selectOneByNome(nomeConta)
        self.idConta = -1
        if listaConta:
            self.idConta = listaConta[0]
            if listaConta[8] == 'REAL':
                self.txtNomeMoeda.SetValue(listaConta[8])
                self.txtValorMoeda.SetValue('')
            else:
                lista = Cotacao.mc_get_ultima_cotacao(listaConta[7])
                if lista:
                    self.txtNomeMoeda.SetValue(lista[1])
                    self.txtValorMoeda.SetValue(formata_numero(lista[0]))
                else:
                    self.txtNomeMoeda.SetValue('')
                    self.txtValorMoeda.SetValue('')
            #self.buscaTudo()
        else:
            self.txtNomeMoeda.SetValue('')
            self.txtValorMoeda.SetValue('')

    def buscaTudo(self, event):
        if self.siglaBolsa and self.idConta > -1:        
            self.getConexao()
            self.buscaListaAtivos()
            self.buscaRendaPorAtivo()
            self.montaGrid()
                  
    def bolsaSelecionada(self, event):
        self.siglaBolsa = self.cbBolsa.GetStringSelection()
        #self.buscaTudo()

    def getConexao(self):
        self.conexao = psycopg2.connect(dbname="b3", user="postgres", password="seriate", host="localhost",
                                            port="5432")
    def buscaListaAtivos(self):
        clausulaSql = 'select distinct idativo from ativonegociado where idconta = %s;'

        cursor = self.conexao.cursor()
        try:
            cursor.execute(clausulaSql, (self.idConta,))
        except  Exception as e:
            dlg = wx.MessageDialog(None, clausulaSql + '\n' + str(e), 'Erro ao buscar ativos negociados', wx.OK | wx.ICON_ERROR)
            result = dlg.ShowModal()

        self.listaAtivos = cursor.fetchall()

    def buscaRendaPorAtivo(self):
        self.listaPatrimonio.clear()

        self.totalComprado = 0.0
        self.totalCompras = 0.0
        self.totalVendas = 0.0
        for row in self.listaAtivos:
            self.buscaNegociacoes(row[0])

            comprado, quantidade, precoMedio = self.estabeleceRendimentoPorAcoes()
            if comprado > 0:
                self.totalComprado += comprado
                self.listaPatrimonio.append([row[0], comprado, quantidade, precoMedio])

        a = 0
        #lista1.extend(lista2)

    def buscaNegociacoes(self, arg):
        self.listaNegociacoes.clear()
        cursor = self.conexao.cursor()

        clausulaSql = 'select a.id, a.dataoperacao, a.operacao, a.qtdeoperacao, a.valoroperacao  ' \
                  'from ativonegociado as a ' \
                  'where a.idativo = ' + str(arg) +  ' and a.idconta = ' + str(self.idConta) + ' '\
                  'order by a.dataoperacao, a.ordemdia, a.id;'

        try:
            cursor.execute(clausulaSql)
        except  Exception as e:
            dlg = wx.MessageDialog(None, clausulaSql + '\n' + str(e), 'Erro ao ler ativos negociados', wx.OK | wx.ICON_ERROR)
            result = dlg.ShowModal()

        self.listaNegociacoes = cursor.fetchall()

    def estabeleceRendimentoPorAcoes(self):
        saldoQtde = 0
        precomedio = 0.0
        listaProvisoria = []
        for row in self.listaNegociacoes:
            dataOperacao = row[1]
            numoperacao = devolveInteger(row[2])
            valorOperacao = devolveFloat(row[4])
            qtdeOperacao = devolveInteger(row[3])
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
        return comprado, saldoQtde, precomedio

    def montaGrid(self):
        #listaOrdenada = sorted(self.listaGeral, key=lambda x: x[0])
        cursor = self.conexao.cursor()
        totalValorAtual = 0.0
        self.grid.ClearGrid()
        if self.grid.GetNumberRows() > 0:
            self.grid.DeleteRows(0, self.grid.GetNumberRows())
        linha = (-1)
        for row in self.listaPatrimonio:

            linha += 1
            self.grid.AppendRows()

            clausulaSql = 'select sigla from ativo where id = ' + str(row[0]) + ';'

            cursor.execute(clausulaSql)
            result = cursor.fetchone()

            cotacao = Ativo.get_ultima_cotacao(result[0])
            valorAtual = cotacao * float(row[2])
            totalValorAtual += valorAtual
            valorMercado = Ativo.get_valor_mercado_yfinance(result[0], self.siglaBolsa)
            variacao = (valorAtual / float(row[1]) - 1) * 100.0
            self.grid.SetCellValue(linha, 0, str(result[0]))
            self.grid.SetCellValue(linha, 1, formata_numero(float(row[1])))
            self.grid.SetCellValue(linha, 2, str(row[2]))
            self.grid.SetCellValue(linha, 3, formata_numero(float(row[3])))
            self.grid.SetCellValue(linha, 4, formata_numero(Ativo.get_ultima_cotacao(result[0])))
            self.grid.SetCellValue(linha, 5, formata_numero(valorAtual))
            self.grid.SetCellValue(linha, 6, formata_numero(variacao))
            self.grid.SetCellValue(linha, 7, formatar_valor(valorMercado))

            self.grid.SetCellAlignment(linha,  0, wx.ALIGN_CENTRE, wx.ALIGN_CENTRE)
            self.grid.SetCellAlignment(linha,  1, wx.ALIGN_RIGHT, wx.ALIGN_RIGHT)
            self.grid.SetCellAlignment(linha,  2, wx.ALIGN_RIGHT, wx.ALIGN_RIGHT)
            self.grid.SetCellAlignment(linha,  3, wx.ALIGN_RIGHT, wx.ALIGN_RIGHT)
            self.grid.SetCellAlignment(linha,  4, wx.ALIGN_RIGHT, wx.ALIGN_RIGHT)
            self.grid.SetCellAlignment(linha,  5, wx.ALIGN_RIGHT, wx.ALIGN_RIGHT)
            self.grid.SetCellAlignment(linha,  6, wx.ALIGN_CENTRE, wx.ALIGN_CENTRE)
            self.grid.SetCellAlignment(linha,  7, wx.ALIGN_RIGHT, wx.ALIGN_RIGHT)

            if variacao < 0: self.grid.SetCellTextColour(linha, 6, wx.RED)
            #self.text_ctrl.SetBackgroundColour(wx.Colour(255, 255, 0))

            if linha % 2 != 0:
                for i in range(0, 13):
                    self.grid.SetCellBackgroundColour(linha, i, wx.Colour(230, 255, 255))
        if linha >=0:
            variacao = (totalValorAtual / self.totalComprado - 1) * 100.0
            self.txtComprado.SetValue(formata_numero(self.totalComprado))
            self.txtPatrimonio.SetValue(formata_numero(totalValorAtual))
            self.txtVariacao.SetValue(formata_numero(variacao) + ' %')
            if variacao < 0:
                self.txtVariacao.SetForegroundColour(wx.RED)
                self.txtVariacao.SetBackgroundColour(wx.Colour(255, 230, 255))
            else:
                self.txtVariacao.SetBackgroundColour(wx.Colour(221, 255, 204))

        # Saldo bancario
        saldoBancario = Conta.getSaldoBancario(self.idConta)
        self.txtSaldoBancario.SetValue(formata_numero(saldoBancario))


def main():
    app = wx.App()
    frmRendaTotal = FrmCarteira(None, 'B3')
    app.MainLoop()


if __name__ == '__main__':
    main()



