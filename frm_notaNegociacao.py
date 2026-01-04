# coding: utf-8

from ativoNegociado import AtivoNegociado
from despesa import Despesa
from diversos import *
from ativo import *
from conta import Conta
from notanegociacao import NotaNegociacao
from wxFrameMG import FrameMG

from wx import *

class FrmNotaNegociacao(FrameMG):
    insert = False
    caminho = '.\\icones\\'
    id_conta = -1
    sigla_bolsa = None
    dias = 30


    def __init__(self, idContaInicial = -1, notaInicial = ''):
        self.lista_negociacoes = []
        self.lista_ativos = []
        self.lista_patrimonio = []


        super(FrmNotaNegociacao, self).__init__(pai=None, titulo='Notas de Negociação',
                                       lar = 1200, alt = 730,
                                       xibot = 150, split=False)

        self.criaComponentes()

    def criaComponentes(self):
        X = self.posx(3)
        Y = self.posy(2)
        tamX = self.larguraEmPx(220)
        tamY = self.alturaEmPx(15)

        self.setAvancoVertical(8)
        
        self.grid = wx.grid.Grid(self.painel, pos=(30, 10), size=(530, 630))
        self.grid.CreateGrid(0, 4)
        self.grid.Bind(wx.grid.EVT_GRID_CELL_RIGHT_CLICK, self.on_right_click)

        # Definindo os tamanhos das colunas
        col_sizes = [130, 100, 100, 100]
        col_labels = ["Conta", "Nota", "Data Operação", "Data Efetivação"]

        for i, (size, label) in enumerate(zip(col_sizes, col_labels)):
            self.grid.SetColSize(i, size)
            self.grid.SetColLabelValue(i, label)

        self.gridAtivos = wx.grid.Grid(self.painel, pos=(600, 10), size=(530, 250))
        self.gridAtivos.CreateGrid(0, 5)

        # Definindo os tamanhos das colunas
        col_sizes = [80, 80, 70, 100, 100]
        col_labels = ["Ativo", "Operação", "Qtde", "Preço", "Total"]

        for i, (size, label) in enumerate(zip(col_sizes, col_labels)):
            self.gridAtivos.SetColSize(i, size)
            self.gridAtivos.SetColLabelValue(i, label)

        self.gridDespesas = wx.grid.Grid(self.painel, pos=(600, 300), size=(530, 250))
        self.gridDespesas.CreateGrid(0, 2)

        # Definindo os tamanhos das colunas
        col_sizes = [230, 100]
        col_labels = ["Descrição", "Valor"]

        for i, (size, label) in enumerate(zip(col_sizes, col_labels)):
            self.gridDespesas.SetColSize(i, size)
            self.gridDespesas.SetColLabelValue(i, label)
        y = 12
        
        label01, self.txtNumeroNota = self.criaCaixaDeTexto(self.painel, pos=(85, 11),
                                                    label='Número da nota', tamanho = (15, 1),
                                                    max=0, multi=False, align='direita')
        self.txtNumeroNota.SetForegroundColour(wx.BLACK)
        self.txtNumeroNota.SetBackgroundColour(wx.Colour(237, 237, 237))
        self.txtNumeroNota.SetEditable(False)

        label02, self.txtDataOperacao = self.criaCaixaDeTexto(self.painel, pos=(115, 11),
                                                    label='Data da operação', tamanho = (15, 1),
                                                    max=0, multi=False, align='direita')
        self.txtDataOperacao.SetForegroundColour(wx.BLACK)
        self.txtDataOperacao.SetBackgroundColour(wx.Colour(237, 237, 237))
        self.txtDataOperacao.SetEditable(False)

        label03, self.txtValorLiquido = self.criaCaixaDeTexto(self.painel, pos=(145, 11),
                                                    label='Valor líquido da nota', tamanho = (15, 1),
                                                    max=0, multi=False, align='direita')
        self.txtValorLiquido.SetForegroundColour(wx.BLACK)
        self.txtValorLiquido.SetBackgroundColour(wx.Colour(237, 237, 237))
        self.txtValorLiquido.SetEditable(False)


        self.btnMostraNaoMostra = Button(self.painel, id=ID_ANY, label="Mostra todos"
                                        , pos=(150, 645),
                                        size=(self.posx(50), self.posy(1) - 30), style=0)
        self.Bind(wx.EVT_BUTTON, self.mostraNaoMostra, self.btnMostraNaoMostra)

        self.botaoSalva.Hide()
        self.botaoDelete.Hide()
        self.botaoNovo.Hide()
        self.botaoCancela.Hide()

        self.busca_tudo(None)

        self.Show()

    def busca_tudo(self, event):
        lista = NotaNegociacao.mc_busca_todas(self.dias)
        
        self.grid.ClearGrid()
        if self.grid.GetNumberRows() > 0:
            self.grid.DeleteRows(0, self.grid.GetNumberRows())
        for i, linha in enumerate(lista):
            self.grid.AppendRows(1)
            conta = Conta.mc_select_one_by_id(linha[2])
            self.grid.SetCellValue(i, 0, conta[4])  # Nome da conta
            self.grid.SetCellValue(i, 1, linha[0])  # Número da nota
            self.grid.SetCellValue(i, 2, str(linha[1]))  # Data da operação
            self.grid.SetCellValue(i, 3, str(linha[3]))  # Data de efetivação

            self.grid.SetCellAlignment(i,  1, wx.ALIGN_CENTRE, wx.ALIGN_CENTRE)
            self.grid.SetCellAlignment(i,  2, wx.ALIGN_CENTRE, wx.ALIGN_CENTRE)
            self.grid.SetCellAlignment(i,  3, wx.ALIGN_CENTRE, wx.ALIGN_CENTRE)

    def mostraNaoMostra(self, event):
        caption = self.btnMostraNaoMostra.GetLabel()
        if caption == 'Mostra todos':
            self.btnMostraNaoMostra.SetLabel('Mostra últimos 30 dias')
            self.dias = 9999
            self.busca_tudo(None)
        else:
            self.btnMostraNaoMostra.SetLabel('Mostra todos')
            self.dias = 30
            self.busca_tudo(None)   

    def on_right_click(self, event):
        row = event.GetRow()  # Obtém a linha clicada
        col = event.GetCol()  # Obtém a coluna clicada
        self.nota_selecionada(row)

    def nota_selecionada(self, row):
        numero_nota = self.grid.GetCellValue(row, 1)
        nome_conta = self.grid.GetCellValue(row, 0)
        data_operacao = self.grid.GetCellValue(row, 2)
        id_conta = Conta.mc_select_one_by_nome(self.grid.GetCellValue(row, 0))[0]

        saldo_nota = NotaNegociacao.mc_saldo_da_nota(nome_conta, numero_nota)
        if saldo_nota:
            self.txtNumeroNota.SetValue(numero_nota)
            self.txtDataOperacao.SetValue(data_operacao)
            self.txtValorLiquido.SetValue(formatar_valor(saldo_nota))

        lista_ativos = AtivoNegociado.mc_devolve_lancamentos_ativo__por_nota(numero_nota, id_conta)
        self.gridAtivos.ClearGrid()
        if self.gridAtivos.GetNumberRows() > 0:
            self.gridAtivos.DeleteRows(0, self.gridAtivos.GetNumberRows())
        for i, linha in enumerate(lista_ativos):
            self.gridAtivos.AppendRows(1)
            ativo = linha[0]
            operacao = linha[1]
            qtde = linha[2]
            preco = linha[3]
            if operacao == 1:
                operacao_str = 'Compra'
                total = qtde * preco * -1
            else:
                operacao_str = 'Venda'
                total = qtde * preco
            self.gridAtivos.SetCellValue(i, 0, ativo)  # Ativo
            self.gridAtivos.SetCellValue(i, 1, operacao_str)  # Operação
            self.gridAtivos.SetCellValue(i, 2, str(qtde))  # Qtde
            self.gridAtivos.SetCellValue(i, 3, formatar_valor(preco))  # Preço
            self.gridAtivos.SetCellValue(i, 4, formatar_valor(total))  # Total

            self.gridAtivos.SetCellAlignment(i,  0, wx.ALIGN_CENTRE, wx.ALIGN_CENTRE)
            self.gridAtivos.SetCellAlignment(i,  2, wx.ALIGN_RIGHT, wx.ALIGN_RIGHT)
            self.gridAtivos.SetCellAlignment(i,  3, wx.ALIGN_RIGHT, wx.ALIGN_RIGHT)
            self.gridAtivos.SetCellAlignment(i,  4, wx.ALIGN_RIGHT, wx.ALIGN_RIGHT)
        
        lista_despesas = Despesa.mc_busca_despesas_por_nota(numero_nota, id_conta)
        self.gridDespesas.ClearGrid()
        if self.gridDespesas.GetNumberRows() > 0:
            self.gridDespesas.DeleteRows(0, self.gridDespesas.GetNumberRows())
        for i, linha in enumerate(lista_despesas):
            self.gridDespesas.AppendRows(1)
            self.gridDespesas.SetCellValue(i, 0, linha[0])  # Descrição
            self.gridDespesas.SetCellValue(i, 1, formatar_valor(linha[1]))  # Valor
            self.gridDespesas.SetCellAlignment(i,  1, wx.ALIGN_RIGHT, wx.ALIGN_RIGHT)

def main():
    app = wx.App()
    objeto = FrmNotaNegociacao()
    app.MainLoop()


if __name__ == '__main__':
    main()



