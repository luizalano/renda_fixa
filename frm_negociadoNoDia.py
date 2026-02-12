# coding: utf-8
from wx import Button, ID_ANY
import pandas as pd
from ativo import Ativo
from conta import Conta
from frm_selecionaConta import SelecionaContaDialog
from wxFrameMG import FrameMG
from diversos import *
from datetime import date
from datetime import datetime
from wx import *

class FrmNegociadoNoDia(FrameMG):
    insert = False
    caminho = '.\\icones\\'
    contador = 0
    id_conta = -1
    id = -1
    nome_conta = ''
    lista = []

    def __init__(self, **kwargs):
        self.ativo = Ativo()

        super(FrmNegociadoNoDia, self).__init__(pai=None, titulo='Ativos Negociados na data - CONTA NÃO DEFINIDA', lar=1300,
                                                alt=720, xibot=1000, split=False)

        self.criaComponentes()
        self.conta_bancaria = None
        self.id_operacao = None
        self.data_operacao_inicial = None
        if len(kwargs) > 0:
            if 'contaBancaria' in kwargs:
                self.conta_bancaria = kwargs['contaBancaria']
            if 'idOperacao' in kwargs:
                self.id_operacao = kwargs['idOperacao']
            if 'dataOperacao' in kwargs:
                #self.dataOperacaoInicial = 
                data_str = kwargs['dataOperacao']
                data_formatada = datetime.strptime(data_str, '%d/%m/%Y').date()
                self.txtDataOperacao.SetValue(data_formatada)

        if self.conta_bancaria and self.id_operacao:
            self.inicia_valores()

    def criaComponentes(self):
        X = self.posx(1)
        Y = self.posy(1) + 15
        tamX = self.larguraEmPx(160)
        tamY = self.alturaEmPx(13)

        self.setAvancoVertical(8)

        self.grid = wx.grid.Grid(self.painel, pos=(X, Y), size=(tamX, tamY))
        self.grid.Bind(wx.grid.EVT_GRID_CELL_RIGHT_CLICK, self.linha_selecionada)

        x0 = 1

        self.iconeConta = wx.Bitmap(self.caminho + 'checkbox_select_32.png')
        lb, ab = self.iconeConta.GetSize()
        self.botaoConta = wx.BitmapButton(self.painel, id=8572, bitmap=self.iconeConta,
                                          pos=(6, 12))
        self.Bind(wx.EVT_BUTTON, self.chama_dialog_conta, self.botaoConta)
        self.botaoConta.SetToolTip("Seleciona a conta corrente")

        label0000, self.txtNomeConta = self.criaCaixaDeTexto(self.painel, pos=(x0 + 5, 0), label='Conta corrente',
                                                         tamanho=(20, 1), max=6, multi=False)

        label0222, self.txtDataOperacao = self.criaCaixaDeTexto(self.painel, pos=(x0 + 29, 0), label='Data operação',
                                                                tamanho=(10, 1), max=6, multi=False, tipodate=True)
        #self.txtDataOperacao.Bind(wx.adv.EVT_DATE_CHANGED, self.dataSelecionada)
        self.txtDataOperacao.Bind(wx.EVT_KILL_FOCUS, self.data_selecionada)

        label00, self.txtAtivo = self.criaCaixaDeTexto(self.painel, pos=(x0 + 43, 0), label='Ativo', tamanho=(6, 1),
                                                       max=6, multi=False)
        self.txtAtivo.Bind(wx.EVT_KILL_FOCUS, self.busca_ativo)
        label0909, self.txtNomeAtivo = self.criaCaixaDeTexto(self.painel, pos=(x0 + 52, 0), label='Nome Ativo',
                                                            tamanho=(20, 1), max=6, multi=False)

        label000, self.cbOperacao = self.criaCombobox(self.painel, pos=(x0 + 75, 0), tamanho=10, label='Operação')
        self.cbOperacao.Append('1 - Compra')
        self.cbOperacao.Append('2 - Venda')

        label001, self.txtQuantidade = self.criaCaixaDeTexto(self.painel, pos=(x0 + 90, 0), label='Quantidade',
                                                             tamanho=(7, 1), max=8, multi=False)
        
        label002, self.txtValor = self.criaCaixaDeTexto(self.painel, pos=(x0 + 101, 0), label='Valor',
                                                        tamanho=(12, 1), max=14, multi=False)
        
        label0021, self.txtNota = self.criaCaixaDeTexto(self.painel, pos=(x0 + 118, 0), label='Nota',
                                                        tamanho=(12, 1), max=14, multi=False)
        
        labelee0, self.cbSimulado = self.criaCombobox(self.painel, pos=(x0 + 135, 0), tamanho=10, label='Simulado')
        self.cbSimulado.Append('1 - Simulado')
        self.cbSimulado.Append('2 - Efetivo')

        self.listaComponentes = [self.cbOperacao, self.txtQuantidade, self.txtValor, self.txtNota, self.cbSimulado]

        self.botaoNovo.SetPosition((1090, 20))
        self.botaoSalva.SetPosition((1130, 20))
        self.botaoDelete.SetPosition((1170, 20))
        self.botaoCancela.SetPosition((1210, 20))

        self.txtNomeAtivo.Disable()
        self.limpa_elementos()

        self.grid.CreateGrid(0, 11)

        self.Show()

    def inicia_valores(self):
        self.id_conta = self.conta_bancaria
        lista = Conta.mc_select_one_by_id(self.id_conta)
        if lista:
            self.nome_conta = lista[4]
            self.SetTitle('Ativos Negociados na data - Conta ' + self.nome_conta)
            self.txtNomeConta.SetValue(self.nome_conta)

            self.data_selecionada(None)

    def chama_dialog_conta(self, event):
        dlg = SelecionaContaDialog(None)
        if dlg.ShowModal() == wx.ID_OK and dlg.selected_id:  # Retorna wx.ID_OK ao confirmar
            self.id_conta = dlg.selected_id
            self.nome_conta = dlg.selected_nome
            self.SetTitle('Ativos Negociados na data - Conta ' + self.nome_conta)

            self.txtNomeConta.SetValue(self.nome_conta)
        dlg.Destroy()

    def limpa_elementos(self):
        self.id = -1
        self.ativo.clearAtivo()

        self.txtAtivo.Clear()
        self.txtValor.Clear()
        self.txtNota.Clear()
        self.txtQuantidade.Clear()

        self.txtAtivo.Disable()
        self.txtValor.Disable()
        self.txtValor.Disable()
        self.txtNota.Disable()
        self.txtQuantidade.Disable()

        self.botaoSalva.Disable()
        self.botaoDelete.Disable()
        self.botaoCancela.Disable()

    def busca_ativo(self, event):
        novo_foco = wx.Window.FindFocus()  # Obtém o próximo elemento que recebeu foco

        # Verifica se o novo foco está na lista de componentes que precisam de validação
        if novo_foco in self.listaComponentes:
            sigla = self.txtAtivo.Value
            self.ativo.populaAtivoBySigla(sigla)
            if self.ativo.id_ativo < 0:
                wx.MessageBox("Ativo não está cadastrado!", "Aviso")
                self.txtAtivo.SetFocus()
            else:
                self.txtNomeAtivo.SetValue(self.ativo.razao_social)

        event.Skip()

    def data_selecionada(self, event):
        if self.id_conta >= 0:
            data_selecionada = self.txtDataOperacao.GetValue()
            data_formatada = data_selecionada.Format('%Y-%m-%d')

            try:
                wx.BeginBusyCursor()
                self.lista = Ativo.devolveLancamentosNaData(data_formatada, self.id_conta)
                self.monta_grid(self.lista)
            finally:
            # Garante que volta ao normal mesmo se der erro
                if wx.IsBusy():
                    wx.EndBusyCursor()

    def linha_selecionada(self, event):
        row = event.GetRow()  # Obtém a linha clicada
        col = event.GetCol()  # Obtém a coluna clicada

        self.id = self.grid.GetCellValue(row, 0)

        if self.id.isdigit():
            self.txtAtivo.SetValue(self.lista[row][2])
            self.txtNomeAtivo.SetValue(self.lista[row][3])
            self.cbOperacao.SetSelection(self.lista[row][10] - 1)
            self.txtQuantidade.SetValue(str(self.lista[row][5]))
            self.txtValor.SetValue(str(self.lista[row][4]))
            self.txtNota.SetValue(str(self.lista[row][12]))
            sim = self.lista[row][12]
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

    def monta_grid(self, lista):
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
        self.grid.SetColSize(10, 100)

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
        self.grid.SetColLabelValue(10, 'Nota')

        self.lista = lista

        linha = 0
        self.contador = 0

        for row in self.lista:
            data_operacao = devolveDateStr(row[6])
            num_operacao = devolveInteger(row[10])
            operacao = ''
            valor_operacao = devolve_float_de_formatacao_completa(row[4])
            qtd_operacao = devolveInteger(row[5])
            valor_compra_str = ''
            valor_venda_str = ''

            if num_operacao == 1:
                operacao = 'Compra'
                valor_compra_str = formata_numero(valor_operacao)
                total_operacao = qtd_operacao * valor_operacao
            else:
                operacao = 'Venda'
                valor_venda_str = formata_numero(valor_operacao)
                total_operacao = valor_operacao * qtd_operacao

            cotacao = Ativo.get_ultima_cotacao(row[2])
            if row[11] == True: simulado = 'SIMULADO'
            else: simulado = 'EFETIVO'

            linha = self.contador
            self.grid.AppendRows()
            self.grid.SetCellValue(linha, 0, str(row[0]))
            self.grid.SetCellValue(linha, 1, str(row[2]))
            self.grid.SetCellValue(linha, 2, data_operacao)
            self.grid.SetCellValue(linha, 3, operacao)
            self.grid.SetCellValue(linha, 4, str(qtd_operacao))
            self.grid.SetCellValue(linha, 5, valor_compra_str)
            self.grid.SetCellValue(linha, 6, valor_venda_str)
            self.grid.SetCellValue(linha, 7, formata_numero(total_operacao))
            self.grid.SetCellValue(linha, 8, formata_numero(cotacao))
            self.grid.SetCellValue(linha, 9, simulado)
            self.grid.SetCellValue(linha, 10, row[12])
            self.contador += 1

            self.grid.SetCellAlignment(linha,  1, wx.ALIGN_CENTRE, wx.ALIGN_CENTRE)
            self.grid.SetCellAlignment(linha,  2, wx.ALIGN_CENTRE, wx.ALIGN_CENTRE)
            self.grid.SetCellAlignment(linha,  3, wx.ALIGN_RIGHT, wx.ALIGN_CENTRE)
            self.grid.SetCellAlignment(linha,  4, wx.ALIGN_RIGHT, wx.ALIGN_RIGHT)
            self.grid.SetCellAlignment(linha,  5, wx.ALIGN_RIGHT, wx.ALIGN_RIGHT)
            self.grid.SetCellAlignment(linha,  6, wx.ALIGN_RIGHT, wx.ALIGN_RIGHT)
            self.grid.SetCellAlignment(linha,  7, wx.ALIGN_RIGHT, wx.ALIGN_RIGHT)
            self.grid.SetCellAlignment(linha,  8, wx.ALIGN_RIGHT, wx.ALIGN_RIGHT)
            self.grid.SetCellAlignment(linha, 10, wx.ALIGN_CENTRE, wx.ALIGN_CENTRE)

    def str_or_none(self, arg):
        if arg is None:
            return ''
        else:
            return arg

    def insere_operacao(self, item):
        avanca = True
        operacao = 0
        quantidade = 0
        valor = 0.0
        dataOperacao = devolveDate(self.txtDataOperacao.Value)
        siglaAtivo = self.txtAtivo.Value

        simulado = False
        avanca = self.ativo.existeAtivo(siglaAtivo)
        nota = None
        if avanca:
            operacao = self.cbOperacao.GetSelection() + 1
            if operacao < 1 or operacao > 2:
                avanca = False
            quantidade = int(self.txtQuantidade.Value)
            if quantidade <= 0:
                avanca = False
            valor_str = str(self.txtValor.Value)
            valor = devolve_float_de_formatacao_completa(valor_str.replace('.', ','))
            if valor <= 0:
                avanca = False
            if self.cbSimulado.GetSelection() == 0:
                simulado = True
            else:
                simulado = False 
            nota = self.txtNota.Value

        if avanca:
            if self.ativo.insereOperacao(siglaAtivo, dataOperacao, operacao, valor, quantidade, self.id_conta, simulado=simulado) == True:
                self.txtQuantidade.SetValue('')
                self.txtValor.SetValue('')
                self.busca_ativo(item)

    def habilita_novo(self, event):
        self.limpa_elementos()
        self.txtAtivo.Enable()
        self.txtValor.Enable()
        self.txtNota.Enable
        self.txtQuantidade.Enable()
        self.cbOperacao.Enable()

        self.botaoSalva.Enable()
        self.botaoDelete.Enable()

        self.txtAtivo.SetFocus()

        self.insert = True


    def cancela_operacao(self, event):
        self.ativo.clearAtivo()
        self.limpa_elementos()

    def salva_elemento(self, event):
        avanca = True
        operacao = 0
        quantidade = 0
        valor = 0.0

        data_selecionada = self.txtDataOperacao.GetValue()
        dataOperacao = self.txtDataOperacao.GetValue().Format('%Y-%m-%d')

        siglaAtivo = self.txtAtivo.Value

        simulado = False
        nota = self.txtNota
        avanca = self.ativo.existeAtivo(siglaAtivo)
        if avanca:
            operacao = self.cbOperacao.GetSelection() + 1
            if operacao < 1 or operacao > 2:
                avanca = False
            quantidade = int(self.txtQuantidade.Value)
            if quantidade <= 0:
                avanca = False
            valor_str = str(self.txtValor.Value)
            valor = devolve_float_de_formatacao_completa(valor_str.replace('.', ','))
            if valor <= 0:
                avanca = False
            if self.cbSimulado.GetSelection() == 0:
                simulado = True
            else:
                simulado = False 

        if avanca:

            if self.insert is True:
                self.ativo.insereOperacao(siglaAtivo, dataOperacao, operacao, valor, quantidade, self.id_conta, simulado=simulado, nota=nota)
                self.insert = False
            else:
                self.ativo.updateOperacao(siglaAtivo, dataOperacao, operacao, valor, quantidade, self.id_conta, self.id, simulado=simulado, nota=nota)
            self.cancela_operacao(event)
            self.data_selecionada(event)

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
            self.data_selecionada(event)


def main():
    app = wx.App()
    desempenhoAtivo = FrmNegociadoNoDia()
    app.MainLoop()


if __name__ == '__main__':
    main()
