# coding: utf-8
from wx import Button, ID_ANY
import pandas as pd
from Ativo import Ativo
from Conta import Conta
from selecionaConta import SelecionaContaDialog
from wxFrameMG import FrameMG
from diversos import *
from ferramentas import *
from datetime import date
from datetime import datetime
from wx import *

class FrmNegociadoNoDia(FrameMG):
    insert = False
    caminho = '.\\icones\\'
    contador = 0
    idconta = -1
    id = -1
    nomeConta = ''
    lista = []

    def __init__(self, **kwargs):
        self.ativo = Ativo()

        super(FrmNegociadoNoDia, self).__init__(pai=None, titulo='Ativos Negociados na data - CONTA NÃO DEFINIDA', lar=1200,
                                                alt=720, xibot=1000, split=False)

        self.criaComponentes()
        self.contaBancaria = None
        self.idOperacao = None
        self.dataOperacaoInicial = None
        if len(kwargs) > 0:
            if 'contaBancaria' in kwargs:
                self.contaBancaria = kwargs['contaBancaria']
            if 'idOperacao' in kwargs:
                self.idOperacao = kwargs['idOperacao']
            if 'dataOperacao' in kwargs:
                #self.dataOperacaoInicial = 
                data_str = kwargs['dataOperacao']
                data_formatada = datetime.strptime(data_str, '%d/%m/%Y').date()
                self.txtDataOperacao.SetValue(data_formatada)


        if self.contaBancaria and self.idOperacao:
            self.iniciaValores()

    def criaComponentes(self):
        X = self.posx(1)
        Y = self.posy(1) + 15
        tamX = self.larguraEmPx(150)
        tamY = self.alturaEmPx(13)

        self.setAvancoVertical(8)

        self.grid = wx.grid.Grid(self.painel, pos=(X, Y), size=(tamX, tamY))
        self.grid.Bind(wx.grid.EVT_GRID_CELL_RIGHT_CLICK, self.linhaSelecionada)

        x0 = 1

        self.iconeConta = wx.Bitmap(self.caminho + 'checkbox_select_32.png')
        lb, ab = self.iconeConta.GetSize()
        self.botaoConta = wx.BitmapButton(self.painel, id=8572, bitmap=self.iconeConta,
                                          pos=(6, 12))
        self.Bind(wx.EVT_BUTTON, self.chamaDialogConta, self.botaoConta)
        self.botaoConta.SetToolTip("Seleciona a conta corrente")

        label0000, self.txtNomeConta = self.criaCaixaDeTexto(self.painel, pos=(x0 + 5, 0), label='Conta corrente',
                                                         tamanho=(20, 1), max=6, multi=False)

        label0222, self.txtDataOperacao = self.criaCaixaDeTexto(self.painel, pos=(x0 + 29, 0), label='Data operação',
                                                                tamanho=(10, 1), max=6, multi=False, tipodate=True)
        #self.txtDataOperacao.Bind(wx.adv.EVT_DATE_CHANGED, self.dataSelecionada)
        self.txtDataOperacao.Bind(wx.EVT_KILL_FOCUS, self.dataSelecionada)

        label00, self.txtAtivo = self.criaCaixaDeTexto(self.painel, pos=(x0 + 43, 0), label='Ativo', tamanho=(6, 1),
                                                       max=6, multi=False)
        self.txtAtivo.Bind(wx.EVT_KILL_FOCUS, self.buscaAtivo)
        label0909, self.txtNomeAtivo = self.criaCaixaDeTexto(self.painel, pos=(x0 + 52, 0), label='Nome Ativo',
                                                            tamanho=(20, 1), max=6, multi=False)

        label000, self.cbOperacao = self.criaCombobox(self.painel, pos=(x0 + 75, 0), tamanho=10, label='Operação')
        self.cbOperacao.Append('1 - Compra')
        self.cbOperacao.Append('2 - Venda')

        label001, self.txtQuantidade = self.criaCaixaDeTexto(self.painel, pos=(x0 + 90, 0), label='Quantidade',
                                                             tamanho=(7, 1), max=8, multi=False)
        label002, self.txtValor = self.criaCaixaDeTexto(self.painel, pos=(x0 + 101, 0), label='Valor',
                                                        tamanho=(12, 1), max=14, multi=False)
        
        labelee0, self.cbSimulado = self.criaCombobox(self.painel, pos=(x0 + 118, 0), tamanho=10, label='Simulado')
        self.cbSimulado.Append('1 - Simulado')
        self.cbSimulado.Append('2 - Efetivo')

        self.listaComponentes = [self.cbOperacao, self.txtQuantidade, self.txtValor, self.salva_elemento]

        self.botaoNovo.SetPosition((950, 20))
        self.botaoSalva.SetPosition((990, 20))
        self.botaoDelete.SetPosition((1030, 20))
        self.botaoCancela.SetPosition((1070, 20))

        self.txtNomeAtivo.Disable()
        self.limpaElementos()

        self.grid.CreateGrid(0, 10)

        self.Show()

    def iniciaValores(self):
        #self.txtDataOperacao.SetValue(self.dataOperacaoInicial)
        self.idconta = self.contaBancaria
        lista = Conta.selectOneById(self.idconta)
        if lista:
            self.nomeConta = lista[4]
            self.SetTitle('Ativos Negociados na data - Conta ' + self.nomeConta)
            self.txtNomeConta.SetValue(self.nomeConta)

            self.dataSelecionada(None)

    def chamaDialogConta(self, event):
        dlg = SelecionaContaDialog(None)
        if dlg.ShowModal() == wx.ID_OK and dlg.selected_id:  # Retorna wx.ID_OK ao confirmar
            self.idconta = dlg.selected_id
            self.nomeConta = dlg.selected_nome
            self.SetTitle('Ativos Negociados na data - Conta ' + self.nomeConta)

            self.txtNomeConta.SetValue(self.nomeConta)
        dlg.Destroy()

    def limpaElementos(self):
        self.id = -1
        self.ativo.clearAtivo()

        self.txtAtivo.Clear()
        self.txtValor.Clear()
        self.txtQuantidade.Clear()

        self.txtAtivo.Disable()
        self.txtValor.Disable()
        self.txtValor.Disable()
        self.txtQuantidade.Disable()

        self.botaoSalva.Disable()
        self.botaoDelete.Disable()
        self.botaoCancela.Disable()

    def buscaAtivo(self, event):
        novo_foco = wx.Window.FindFocus()  # Obtém o próximo elemento que recebeu foco

        # Verifica se o novo foco está na lista de componentes que precisam de validação
        if novo_foco in self.listaComponentes:
            sigla = self.txtAtivo.Value
            self.ativo.populaAtivoBySigla(sigla)
            if self.ativo.id_ativo < 0:
                wx.MessageBox("Ativo não está cadastrado!", "Aviso")
                self.txtAtivo.SetFocus()
            else:
                self.txtNomeAtivo.SetValue(self.ativo.getrazao_social())

        event.Skip()

    def dataSelecionada(self, event):
        if self.idconta >= 0:
            data_selecionada = self.txtDataOperacao.GetValue()
            data_formatada = data_selecionada.Format('%Y-%m-%d')

            try:
                wx.BeginBusyCursor()
                self.lista = Ativo.devolveLancamentosNaData(data_formatada, self.idconta)
                self.montaGrid(self.lista)
            finally:
            # Garante que volta ao normal mesmo se der erro
                if wx.IsBusy():
                    wx.EndBusyCursor()

    def linhaSelecionada(self, event):
        row = event.GetRow()  # Obtém a linha clicada
        col = event.GetCol()  # Obtém a coluna clicada

        self.id = self.grid.GetCellValue(row, 0)

        if self.id.isdigit():
            self.txtAtivo.SetValue(self.lista[row][2])
            self.txtNomeAtivo.SetValue(self.lista[row][3])
            self.cbOperacao.SetSelection(self.lista[row][10] - 1)
            self.txtQuantidade.SetValue(str(self.lista[row][5]))
            self.txtValor.SetValue(str(self.lista[row][4]))
            sim = self.lista[row][11]
            if sim == True: 
                self.cbSimulado.SetSelection(0)
            else: 
                self.cbSimulado.SetSelection(1)

            self.txtAtivo.Enable()
            self.txtQuantidade.Enable()
            self.txtValor.Enable()
            self.cbOperacao.Enable()

            self.botaoSalva.Enable()
            self.botaoDelete.Enable()

            self.txtAtivo.SetFocus()

            self.insert = False

    def montaGrid(self, lista):
        numrows = self.grid.GetNumberRows()
        if numrows > 0:
            self.grid.DeleteRows(pos=0, numRows=self.grid.GetNumberRows())
        self.grid.SetColSize(0, 60)
        self.grid.SetColSize(1, 80)
        self.grid.SetColSize(2, 80)
        self.grid.SetColSize(3, 120)
        self.grid.SetColSize(4, 60)
        self.grid.SetColSize(5, 100)
        self.grid.SetColSize(6, 100)
        self.grid.SetColSize(7, 120)
        self.grid.SetColSize(8, 120)
        self.grid.SetColSize(9, 70)

        self.grid.SetColLabelValue(0, 'id')
        self.grid.SetColLabelValue(1, 'Sigla')
        self.grid.SetColLabelValue(2, 'Data')
        self.grid.SetColLabelValue(3, 'Operação')
        self.grid.SetColLabelValue(4, 'Qtde')
        self.grid.SetColLabelValue(5, 'Compra')
        self.grid.SetColLabelValue(6, 'Venda')
        self.grid.SetColLabelValue(7, 'Total Operação')
        self.grid.SetColLabelValue(8, 'Última cotação')
        self.grid.SetColLabelValue(9, 'Simulado')

        self.lista = lista

        linha = 0
        self.contador = 0

        for row in self.lista:
            dataOperacao = devolveDateStr(row[6])
            numoperacao = devolveInteger(row[10])
            operacao = ''
            valorOperacao = devolveFloat(row[4])
            qtdeOperacao = devolveInteger(row[5])
            valorCompraStr = ''
            valorVendaStr = ''

            if numoperacao == 1:
                operacao = 'Compra'
                valorCompraStr = formata_numero(valorOperacao)
                totalOperacao = qtdeOperacao * valorOperacao
            else:
                operacao = 'Venda'
                valorVendaStr = formata_numero(valorOperacao)
                totalOperacao = valorOperacao * qtdeOperacao

            cotacao = Ativo.get_ultima_cotacao(row[2])
            if row[11] == True: simulado = 'SIMULADO'
            else: simulado = ''

            linha = self.contador
            self.grid.AppendRows()
            self.grid.SetCellValue(linha, 0, str(row[0]))
            self.grid.SetCellValue(linha, 1, str(row[2]))
            self.grid.SetCellValue(linha, 2, dataOperacao)
            self.grid.SetCellValue(linha, 3, operacao)
            self.grid.SetCellValue(linha, 4, str(qtdeOperacao))
            self.grid.SetCellValue(linha, 5, valorCompraStr)
            self.grid.SetCellValue(linha, 6, valorVendaStr)
            self.grid.SetCellValue(linha, 7, formata_numero(totalOperacao))
            self.grid.SetCellValue(linha, 8, formata_numero(cotacao))
            self.grid.SetCellValue(linha, 9, simulado)
            self.contador += 1

            self.grid.SetCellAlignment(linha, 1, wx.ALIGN_CENTRE, wx.ALIGN_CENTRE)
            self.grid.SetCellAlignment(linha, 2, wx.ALIGN_CENTRE, wx.ALIGN_CENTRE)
            self.grid.SetCellAlignment(linha, 3, wx.ALIGN_RIGHT, wx.ALIGN_CENTRE)
            self.grid.SetCellAlignment(linha, 4, wx.ALIGN_RIGHT, wx.ALIGN_RIGHT)
            self.grid.SetCellAlignment(linha, 5, wx.ALIGN_RIGHT, wx.ALIGN_RIGHT)
            self.grid.SetCellAlignment(linha, 6, wx.ALIGN_RIGHT, wx.ALIGN_RIGHT)
            self.grid.SetCellAlignment(linha, 7, wx.ALIGN_RIGHT, wx.ALIGN_RIGHT)
            self.grid.SetCellAlignment(linha, 8, wx.ALIGN_RIGHT, wx.ALIGN_RIGHT)


    def strOrNone(self, arg):
        if arg is None:
            return ''
        else:
            return arg

    def insereOperacao(self, item):
        avanca = True
        operacao = 0
        quantidade = 0
        valor = 0.0
        dataOperacao = devolveDate(self.txtDataOperacao.Value)
        siglaAtivo = self.txtAtivo.Value

        simulado = False
        avanca = self.ativo.existeAtivo(siglaAtivo)
        if avanca:
            operacao = self.cbOperacao.GetSelection() + 1
            if operacao < 1 or operacao > 2:
                avanca = False
            quantidade = int(self.txtQuantidade.Value)
            if quantidade <= 0:
                avanca = False
            valor_str = str(self.txtValor.Value)
            valor = devolveFloat(valor_str.replace('.', ','))
            if valor <= 0:
                avanca = False
            if self.cbSimulado.GetSelection() == 0:
                simulado = True
            else:
                simulado = False 

        if avanca:
            if self.ativo.insereOperacao(siglaAtivo, dataOperacao, operacao, valor, quantidade, self.idconta, simulado=simulado) == True:
                self.txtQuantidade.SetValue('')
                self.txtValor.SetValue('')
                self.buscaAtivo(item)

    def habilita_novo(self, event):
        self.limpaElementos()
        self.txtAtivo.Enable()
        self.txtValor.Enable()
        self.txtQuantidade.Enable()
        self.cbOperacao.Enable()

        self.botaoSalva.Enable()
        self.botaoDelete.Enable()

        self.txtAtivo.SetFocus()

        self.insert = True


    def cancela_operacao(self, event):
        self.ativo.clearAtivo()
        self.limpaElementos()

    def salva_elemento(self, event):
        avanca = True
        operacao = 0
        quantidade = 0
        valor = 0.0

        data_selecionada = self.txtDataOperacao.GetValue()
        dataOperacao = self.txtDataOperacao.GetValue().Format('%Y-%m-%d')

        siglaAtivo = self.txtAtivo.Value

        simulado = False
        avanca = self.ativo.existeAtivo(siglaAtivo)
        if avanca:
            operacao = self.cbOperacao.GetSelection() + 1
            if operacao < 1 or operacao > 2:
                avanca = False
            quantidade = int(self.txtQuantidade.Value)
            if quantidade <= 0:
                avanca = False
            valor_str = str(self.txtValor.Value)
            valor = devolveFloat(valor_str.replace('.', ','))
            if valor <= 0:
                avanca = False
            if self.cbSimulado.GetSelection() == 0:
                simulado = True
            else:
                simulado = False 

        if avanca:

            if self.insert is True:
                self.ativo.insereOperacao(siglaAtivo, dataOperacao, operacao, valor, quantidade, self.idconta, simulado=simulado)
                self.insert = False
            else:
                self.ativo.updateOperacao(siglaAtivo, dataOperacao, operacao, valor, quantidade, self.idconta, self.id, simulado=simulado)
            self.cancela_operacao(event)
            self.dataSelecionada(event)

    def deleta_elemento(self, event):
        prossegueEliminacao = False
        dlg = wx.MessageDialog(None, 'Confirma a eliminação dos dados?',
                               'Prestes a eliminar definitivamente!',
                               wx.YES_NO | wx.NO_DEFAULT | wx.ICON_QUESTION)
        if dlg.ShowModal() == wx.ID_YES:
            prossegueEliminacao = True

        if prossegueEliminacao:
            self.ativo.deleteOperacao(self.id)
            self.cancela_operacao(event)
            self.dataSelecionada(event)


def main():
    app = wx.App()
    desempenhoAtivo = FrmNegociadoNoDia()
    app.MainLoop()


if __name__ == '__main__':
    main()
