# coding: utf-8
#from wx import Button, ID_ANY

from diversos import *
from conta import *
from cotacao import *
from capital import Capital
from wxFrameMG import FrameMG
#from ClienteDeQuem import ClienteDeQuem

from wx import *
import wx.grid
from datetime import datetime
from dateutil.relativedelta import relativedelta

class FrmCapital(FrameMG):
    insert = False
    caminho = '.\\icones\\'
    listaFase = []
    idConta = -1
    totalAporte = 0.0
    totalRetirada = 0.0


    def __init__(self, idContaInicial):
        self.capital = Capital()
        self.today = datetime.now().date()

        super(FrmCapital, self).__init__(pai=None, titulo='Lançamentos de Alteração de Capital',
                                         lar = 1000, alt = 730,
                                         xibot = 700, split=False)

        self.cria_componentes()
        self.set_conta(idContaInicial)

    def cria_componentes(self):
        X = self.posx(1)
        Y = self.posy(1)
        tamX = self.larguraEmPx(70)
        tamY = self.alturaEmPx(12)

        self.setAvancoVertical(8)

        label0811, self.cbConta = self.criaCombobox(self.painel, pos=(X, 0), tamanho=22, label='Conta')
        self.cbConta.Bind(wx.EVT_COMBOBOX, self.conta_selecionada)

        self.grid = wx.grid.Grid(self.painel, pos=(X, Y), size=(tamX, tamY))
        self.grid.CreateGrid(0, 4)
        self.grid.SetColSize(0,  30)
        self.grid.SetColSize(1,  80)
        self.grid.SetColSize(2, 200)
        self.grid.SetColSize(3, 80)
        self.grid.SetColLabelValue(0, "ID")
        self.grid.SetColLabelValue(1, "Data")
        self.grid.SetColLabelValue(2, "Descrição")
        self.grid.SetColLabelValue(3, "Valor")
        #self.grid.GetGridColLabelWindow().GetChildren()[1].SetWindowStyleFlag(wx.ALIGN_CENTRE)
        #self.grid.GetGridColLabelWindow().GetChildren()[2].SetWindowStyleFlag(wx.ALIGN_RIGHT)
        #self.grid.GetGridColLabelWindow().GetChildren()[3].SetWindowStyleFlag(wx.ALIGN_RIGHT)

        #self.grid.Bind(wx.grid.EVT_GRID_LABEL_RIGHT_CLICK, self.on_sort_column)

        x0 = 75

        label01, self.txtId = self.criaCaixaDeTexto(self.painel, pos=(x0 + 10, 1), label='ID', tamanho = (6, 1),
                                                    max=6, multi=False )
        label02, self.txtDataLancamento = self.criaCaixaDeTexto(self.painel, pos=(x0 + 10, 2),
                                                    label='Data', tamanho = (15, 1),
                                                    max=0, multi=False, tipodate=True)


        label03, self.txtDescricao = self.criaCaixaDeTexto(self.painel, pos=(x0 + 10, 3),
                                                           label='Descrição', tamanho = (40, 1),
                                                           max=self.capital.sql_busca_tamanho('descricao'), multi=False)

        label03, self.txtValor = self.criaCaixaDeTexto(self.painel, pos=(x0 + 10, 4),
                                                    label='Valor', tamanho = (15, 1),
                                                    max=0, multi=False, tipofloat=True )

        label105, self.txtNomeMoeda = self.criaCaixaDeTexto(self.painel, pos=(x0 + 10, 5),
                                                    label='Moeda da conta', tamanho = (15, 1),
                                                    max=0, multi=False)
        self.txtNomeMoeda.SetForegroundColour(wx.BLACK)
        self.txtNomeMoeda.SetBackgroundColour(wx.Colour(237, 237, 237))
        self.txtNomeMoeda.SetEditable(False)
        self.negrita(self.txtNomeMoeda)

        label1055, self.txtValorMoeda = self.criaCaixaDeTexto(self.painel, pos=(x0 + 10, 6),
                                                    label='Última cotação', tamanho = (15, 1),
                                                    max=0, multi=False, align='direita')
        self.txtValorMoeda.SetForegroundColour(wx.BLACK)
        self.txtValorMoeda.SetBackgroundColour(wx.Colour(237, 237, 237))
        self.txtValorMoeda.SetEditable(False)
        self.negrita(self.txtValorMoeda)

        # Saldo Bancário
        label885, self.txtSaldoBancario = self.criaCaixaDeTexto(self.painel, pos=(x0 + 10, 7),
                                                    label='Saldo bancário', tamanho = (15, 1),
                                                    max=0, multi=False, align='direita')
        self.txtSaldoBancario.SetForegroundColour(wx.BLACK)
        self.txtSaldoBancario.SetBackgroundColour(wx.Colour(237, 237, 237))
        self.txtSaldoBancario.SetEditable(False)
        self.negrita(self.txtValorMoeda)


        label93, self.txtTotalAporte = self.criaCaixaDeTexto(self.painel, pos=(20, 12),
                                                    label='Aportes', tamanho = (15, 1),
                                                    max=0, multi=False )
        self.txtTotalAporte.SetWindowStyleFlag(wx.TE_RIGHT)

        label943, self.txtTotalRetirada = self.criaCaixaDeTexto(self.painel, pos=(45, 12),
                                                    label='Retiradas', tamanho = (15, 1),
                                                    max=0, multi=False )
        self.txtTotalRetirada.SetWindowStyleFlag(wx.TE_RIGHT)
        self.txtTotalAporte.Disable()
        self.txtTotalRetirada.Disable()

        self.btnMostraNaoMostra = Button(self.painel, id=ID_ANY, label="Mostra todos"
                                        , pos=(self.posx(17), self.posy(11)),
                                        size=(self.posx(50), self.posy(1) - 30), style=0)
        self.Bind(wx.EVT_BUTTON, self.mostra_nao_mostra, self.btnMostraNaoMostra)


        self.limpa_elementos()

        self.grid.Bind(wx.grid.EVT_GRID_CELL_LEFT_CLICK, self.on_left_click)
        self.grid.Bind(wx.grid.EVT_GRID_CELL_RIGHT_CLICK, self.on_right_click)
        #self.grid.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.selecionaLinha)
        #self.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.selecionaLinha, self.grid)
        #self.Bind(wx.EVT_CHAR_HOOK, self.teclaPressionada)

        self.dataInicial = self.today - relativedelta(months=3)
        self.enche_combo_contas()
        self.Show()

    def indice_cb(self, cb, chave):
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

    def enche_combo_contas(self):
        lista = Conta.mc_select_all()
        self.cbConta.Clear()
        for row in lista:
            self.cbConta.Append(row[4])

    def set_conta(self, idConta):
        lista = Conta.mc_select_one_by_id(idConta)
        if lista:
            self.cbConta.SetSelection(self.indice_cb(self.cbConta, lista[4]))
            self.conta_selecionada(None)

    def conta_selecionada(self, event):
        nomeConta = self.cbConta.GetStringSelection()
        listaConta = None
        listaConta = Conta.mc_select_one_by_nome(nomeConta)
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
            self.monta_grid(self.dataInicial)

        else:
            self.txtNomeMoeda.SetValue('')
            self.txtValorMoeda.SetValue('')

    def limpa_elementos(self):
        self.capital.clear_capital()

        self.txtId.Clear()
        self.txtDescricao.Clear()
        self.txtValor.Clear()

        self.disabilita_componentes()

    def disabilita_componentes(self):
        self.txtId.Disable()
        self.txtDescricao.Disable()
        self.txtDataLancamento.Disable()
        self.txtValor.Disable()

        self.botaoSalva.Disable()
        self.botaoDelete.Disable()

    def mostra_nao_mostra(self, event):
        caption = self.btnMostraNaoMostra.GetLabel()
        if caption == 'Mostra todos':
            self.btnMostraNaoMostra.SetLabel('Mostra últimos 3 meses')
            self.monta_grid(None)
        else:
            self.btnMostraNaoMostra.SetLabel('Mostra todos')
            self.monta_grid(self.dataInicial)

    def monta_grid(self, arg):
        self.lista = Capital.mc_busca_por_periodo(arg, self.idConta)
        self.grid.ClearGrid()
        self.totalAporte = 0.0
        self.totalRetirada = 0.0

        if self.grid.GetNumberRows() > 0:
            self.grid.DeleteRows(0, self.grid.GetNumberRows())
        linha = -1
        for row in self.lista:
            linha += 1
            self.grid.AppendRows()
            self.grid.SetCellValue(linha, 0, str(row[0]))
            self.grid.SetCellValue(linha, 1, devolveDateStr(row[1]))
            self.grid.SetCellValue(linha, 2, str(row[2]))
            self.grid.SetCellValue(linha, 3, formata_numero(row[3]))

            self.grid.SetCellAlignment(linha, 1, wx.ALIGN_CENTRE, wx.ALIGN_CENTRE)
            self.grid.SetCellAlignment(linha, 3, wx.ALIGN_RIGHT, wx.ALIGN_RIGHT)

            valor = devolveFloat(row[3])
            if valor < 0:
                self.totalRetirada += valor
            else:
                self.totalAporte += valor

        self.totalRetirada = self.totalRetirada * (-1)

        self.txtTotalAporte.SetValue(formata_numero(self.totalAporte))
        self.txtTotalRetirada.SetValue(formata_numero(self.totalRetirada))

        # Saldo bancario
        saldoBancario = Conta.mc_get_saldo_bancario(self.idConta)
        self.txtSaldoBancario.SetValue(formata_numero(saldoBancario))

    def on_left_click(self, event):
        row = event.GetRow()  # Obtém a linha clicada
        col = event.GetCol()  # Obtém a coluna clicada
        #self.empresaSelecionada(row)

    def on_right_click(self, event):
        row = event.GetRow()  # Obtém a linha clicada
        col = event.GetCol()  # Obtém a coluna clicada
        self.linha_da_grid_selecionada(row)

    def linha_da_grid_selecionada(self, item):
        idSelecionado = self.grid.GetCellValue(item, 0)

        if idSelecionado.isdigit():
            self.capital.popula_capital_by_id(idSelecionado)

            self.txtId.SetValue(str(self.capital.id))
            self.txtDescricao.SetValue(self.capital.descricao)
            data_str = self.capital.data_lancamento.strftime('%d/%m/%Y')
            data_formatada = datetime.strptime(data_str, '%d/%m/%Y').date()
            self.txtDataLancamento.SetValue(data_formatada)

            self.txtValor.SetValue(str(self.capital.valor))

            self.txtDescricao.Enable()
            self.txtDataLancamento.Enable()
            self.txtValor.Enable()

            self.botaoSalva.Enable()
            self.botaoDelete.Enable()

            self.txtDataLancamento.SetFocus()

            self.insert = False

    def habilita_novo(self, event):
        self.limpa_elementos()

        self.txtDescricao.Enable()
        self.txtDataLancamento.Enable()
        self.txtValor.Enable()

        self.insert = True

        self.botaoSalva.Enable()

        self.txtDataLancamento.SetFocus()

    def cancela_operacao(self, event):
        self.capital.clear_capital()
        self.limpa_elementos()

    def salva_elemento(self, event):
        #data_selecionada = self.txtDataLancamento.GetValue()
        #data_formatada = self.txtDataLancamento.GetValue().Format('%Y-%m-%d')
        self.capital.set_data_lancamento(self.txtDataLancamento.GetValue().Format('%d/%m/%Y'))
        self.capital.set_descricao(self.txtDescricao.Value)
        self.capital.set_valor(devolveFloat(str(self.txtValor.Value).replace('.', ',')))
        self.capital.set_id_conta(self.idConta)

        if self.insert is True:
            self.capital.insere()
            self.insert = False
        else:
            self.capital.update()

        self.limpa_elementos()
        self.monta_grid(self.dataInicial)

    def deleta_elemento(self, event):
        prossegueEliminacao = False
        dlg = wx.MessageDialog(None, 'Confirma a eliminação dos dados?',
                               'Prestes a eliminar definitivamente!',
                               wx.YES_NO | wx.NO_DEFAULT | wx.ICON_QUESTION)
        if dlg.ShowModal() == wx.ID_YES:
            prossegueEliminacao = True

        if prossegueEliminacao:
            self.capital.delete()
            self.limpa_elementos()
            self.monta_grid(self.dataInicial)

def main():
    app = wx.App()
    frmCliente = FrmCapital(1)
    app.MainLoop()


if __name__ == '__main__':
    main()
