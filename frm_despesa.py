# coding: utf-8
from wx import Button, ID_ANY

from diversos import *
from despesa import Despesas
from cotacao import Cotacao
from conta import Conta
from wxFrameMG import FrameMG
from frm_resumoDespesas import FrmResumoDespesas
from frm_resumoDespesasMes import FrmResumoDespesasMes

import wx
import wx.grid
from datetime import datetime
from dateutil.relativedelta import relativedelta

class FrmDespesa(FrameMG):
    insert = False
    id_conta = -1
    id_tipo_despesa = -1
    caminho = '.\\icones\\'
    listaFase = []
    frmResumoDespesas = None
    frmResumoDespesasMes = None

    def __init__(self, idContaInicial):
        self.despesas = Despesas()
        self.today = datetime.now().date()

        super(FrmDespesa, self).__init__(pai=None, titulo='Despesas - Corretagem e outras despesas de operações',
                                         lar = 1000, alt = 730,
                                         xibot = 600, split=False)

        self.criaComponentes()
        self.setConta(idContaInicial)

    def criaComponentes(self):
        X = self.posx(1)
        Y = self.posy(1)
        tamX = self.larguraEmPx(70)
        tamY = self.alturaEmPx(14)

        self.setAvancoVertical(8)

        #self.grid = wx.ListCtrl(self.painel, pos=(X, Y), size=(tamX, tamY),
        #                        style=wx.LC_REPORT | wx.LC_VRULES | wx.LC_HRULES | wx.BORDER_SUNKEN)

        label0811, self.cbConta = self.criaCombobox(self.painel, pos=(X, 0), tamanho=22, label='Conta')
        self.cbConta.Bind(wx.EVT_COMBOBOX, self.contaSelecionada)

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

        x0 = 85

        label01, self.txtId = self.criaCaixaDeTexto(self.painel, pos=(x0, 0), label='ID', tamanho = (6, 1),
                                                    max=6, multi=False )
        label02, self.txtDataLancamento = self.criaCaixaDeTexto(self.painel, pos=(x0, 1),
                                                    label='Data', tamanho = (15, 1),
                                                    max=0, multi=False, tipodate=True )

        label0201, self.txtDataEfetivacao = self.criaCaixaDeTexto(self.painel, pos=(x0 + 23, 1),
                                                    label='Data', tamanho = (15, 1),
                                                    max=0, multi=False, tipodate=True )

        label02nota, self.txtNotaNegociacao = self.criaCaixaDeTexto(self.painel, pos=(x0, 2),
                                                    label='Nota de Negociação', tamanho = (17, 1),
                                                    max=0, multi=False)

        label0844, self.cbTipoDespesa = self.criaCombobox(self.painel, pos=(x0, 3), tamanho=40, label='Tipo de despesa')
        self.cbTipoDespesa.Bind(wx.EVT_COMBOBOX, self.tipoDespesaSelecionada)
        
        label03, self.txtDescricao = self.criaCaixaDeTexto(self.painel, pos=(x0, 4),
                                                    label='Descrição', tamanho = (40, 1),
                                                    max=self.despesas.sql_busca_tamanho('descricao'), multi=False )

        label105, self.txtNomeMoeda = self.criaCaixaDeTexto(self.painel, pos=(x0, 5),
                                                    label='Moeda da conta', tamanho = (15, 1),
                                                    max=0, multi=False)
        self.txtNomeMoeda.SetForegroundColour(wx.BLACK)
        self.txtNomeMoeda.SetBackgroundColour(wx.Colour(237, 237, 237))
        self.txtNomeMoeda.SetEditable(False)
        self.negrita(self.txtNomeMoeda)

        label1055, self.txtValorMoeda = self.criaCaixaDeTexto(self.painel, pos=(x0 + 23, 5),
                                                    label='Última cotação', tamanho = (15, 1),
                                                    max=0, multi=False, align='direita')
        self.txtValorMoeda.SetForegroundColour(wx.BLACK)
        self.txtValorMoeda.SetBackgroundColour(wx.Colour(237, 237, 237))
        self.txtValorMoeda.SetEditable(False)
        self.negrita(self.txtValorMoeda)

        label04, self.txtValor = self.criaCaixaDeTexto(self.painel, pos=(x0, 6),
                                                    label='Valor', tamanho = (15, 1),
                                                    max=0, multi=False, tipofloat=True )

        # Saldo Bancário
        label885, self.txtSaldoBancario = self.criaCaixaDeTexto(self.painel, pos=(x0, 7),
                                                    label='Saldo bancário', tamanho = (15, 1),
                                                    max=0, multi=False, align='direita')
        self.txtSaldoBancario.SetForegroundColour(wx.BLACK)
        self.txtSaldoBancario.SetBackgroundColour(wx.Colour(237, 237, 237))
        self.txtSaldoBancario.SetEditable(False)

        self.btnMostraNaoMostra = Button(self.painel, id=ID_ANY, label="Mostra todos"
                                        , pos=(self.posx(17), self.posy(12)+30),
                                        size=(self.posx(50), self.posy(1) - 30), style=0)
        self.Bind(wx.EVT_BUTTON, self.mostraNaoMostra, self.btnMostraNaoMostra)

        self.limpaElementos()

        self.grid.Bind(wx.grid.EVT_GRID_CELL_LEFT_CLICK, self.on_left_click)
        self.grid.Bind(wx.grid.EVT_GRID_CELL_RIGHT_CLICK, self.on_right_click)

        aviso = wx.StaticText(self.painel,
                              label="Atenção!!\nEsta é uma tabela de despesa.\nOs valores relativos às despesas "
                                    "serão informados com sinal positivo.\n"
                                    "Caso tenham valores de receita a serem informados, estes terão que ser negativos.",
                              pos=(self.larguraEmPx(x0), self.alturaEmPx(10)),
                              style=wx.ALIGN_CENTRE_HORIZONTAL)

        # Definindo a fonte do aviso (negrito e maior)
        fonte = wx.Font(12, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD)
        aviso.SetFont(fonte)

        # Definindo cor do texto e do fundo
        aviso.SetForegroundColour(wx.Colour(0, 0, 0))  # Cor do texto (branco)
        aviso.SetBackgroundColour(wx.Colour(255,102,102))

        # Criando uma moldura ao redor da caixa de texto
        aviso.Wrap(300)  # Quebra de linha automática para 400px de largura

        
        self.btnMostraResumoPorTipo = Button(self.painel, id=ID_ANY, label="Consolidado por Tipo de Despesa"
                                        , pos=(self.posx(x0), self.posy(11)),
                                        size=(self.posx(40), self.posy(1) - 30), style=0)
        self.Bind(wx.EVT_BUTTON, self.chamaResumo, self.btnMostraResumoPorTipo)
        self.btnMostraResumoPorTipo.Enabled = False

        self.btnMostraResumoPorMesTipo = Button(self.painel, id=ID_ANY, label="Consolidado por Tipo de Despesa e Mês"
                                        , pos=(self.posx(x0), self.posy(12)),
                                        size=(self.posx(40), self.posy(1) - 30), style=0)
        self.Bind(wx.EVT_BUTTON, self.chamaResumoMes, self.btnMostraResumoPorMesTipo)
        self.btnMostraResumoPorTipo.Enabled = False

        self.dataInicial = self.today - relativedelta(months=3)

        self.encheComboContas()
        self.encheComboTipoDespesa()

        self.Show()

    def chamaResumo(self, evento):

        if self.frmResumoDespesas is None:  # Se não existir, cria uma nova janela
            self.frmResumoDespesas = FrmResumoDespesas(id_conta=self.idConta)
            self.frmResumoDespesas.Bind(wx.EVT_CLOSE, lambda evt: self.on_close(evt, "frmResumoDespesas"))
            self.frmResumoDespesas.Show()
        else:
            self.frmResumoDespesas.Raise()  # Se já existir, apenas traz para frente

    def chamaResumoMes(self, evento):

        if self.frmResumoDespesasMes is None:  # Se não existir, cria uma nova janela
            self.frmResumoDespesasMes = FrmResumoDespesasMes(id_conta=self.idConta)
            self.frmResumoDespesasMes.Bind(wx.EVT_CLOSE, lambda evt: self.on_close(evt, "frmResumoDespesasMes"))
            self.frmResumoDespesasMes.Show()
        else:
            self.frmResumoDespesasMes.Raise()  # Se já existir, apenas traz para frente

    def on_close(self, event, frame_attr):
        """Garante que o objeto seja destruído ao fechar a janela."""
        frame = getattr(self, frame_attr, None)  # Obtém a referência ao frame
        if frame:
            frame.Destroy()  # Destrói a janela
            setattr(self, frame_attr, None)  # Define como None
    
    def encheComboContas(self):
        lista = Conta.mc_select_all()
        self.cbConta.Clear()
        for row in lista:
            self.cbConta.Append(row[4])

    def encheComboTipoDespesa(self):
        lista = Despesas.mc_busca_tipos()
        self.cbTipoDespesa.Clear()
        for row in lista:
            self.cbTipoDespesa.Append(row[1])

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
        lista = Conta.mc_select_one_by_id(idConta)
        self.btnMostraResumoPorTipo.Enabled = False
        if lista:
            self.cbConta.SetSelection(self.indiceCb(self.cbConta, lista[4]))
            self.contaSelecionada(None)

    def contaSelecionada(self, event):
        nomeConta = self.cbConta.GetStringSelection()
        listaConta = None
        listaConta = Conta.mc_select_one_by_nome(nomeConta)
        self.btnMostraResumoPorTipo.Enabled = False
        self.idConta = -1
        if listaConta:
            self.idConta = listaConta[0]
            self.btnMostraResumoPorTipo.Enabled = True
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
            self.montaGrid(self.dataInicial)
        else:
            self.txtNomeMoeda.SetValue('')
            self.txtValorMoeda.SetValue('')

    def setTipoDespesa(self, idTipoDespesa):
        lista = Despesas.mc_busca_tipo_por_id(idTipoDespesa)
        if lista:
            self.cbTipoDespesa.SetSelection(self.indiceCb(self.cbTipoDespesa, lista[1]))
            self.tipoDespesaSelecionada(None)

    def tipoDespesaSelecionada(self, event):
        nomeTipoDespesa = self.cbTipoDespesa.GetStringSelection()
        lista = None
        lista = Despesas.mc_busca_tipo_por_nome(nomeTipoDespesa)
        self.id_tipo_despesa = -1
        if lista:
            self.id_tipo_despesa = lista[0]
            if self.txtDescricao.GetValue().strip() == '':
                self.txtDescricao.SetValue(nomeTipoDespesa.title())

    def limpaElementos(self):
        self.despesas.clear_despesas()

        self.txtId.Clear()
        self.txtDescricao.Clear()
        self.txtValor.Clear()

        self.disabilitaComponentes()

    def disabilitaComponentes(self):
        self.txtId.Disable()
        self.txtDescricao.Disable()
        self.txtDataLancamento.Disable()
        self.txtDataEfetivacao.Disable()
        self.txtNotaNegociacao.Disable()
        self.txtValor.Disable()

        self.botaoSalva.Disable()
        self.botaoDelete.Disable()

    def mostraNaoMostra(self, event):
        caption = self.btnMostraNaoMostra.GetLabel()
        if caption == 'Mostra todos':
            self.btnMostraNaoMostra.SetLabel('Mostra últimos 3 meses')
            self.montaGrid(None)
        else:
            self.btnMostraNaoMostra.SetLabel('Mostra todos')
            self.montaGrid(self.dataInicial)

    def montaGrid(self, arg):
        self.lista = Despesas.mc_busca_por_periodo(arg, self.idConta)

        self.grid.ClearGrid()
        if self.grid.GetNumberRows() > 0:
            self.grid.DeleteRows(0, self.grid.GetNumberRows())
        linha = -1
        colunas = self.grid.GetNumberCols()
        if self.lista:
            for row in self.lista:
                linha += 1
                self.grid.AppendRows()
                for col_idx, value in enumerate(row):
                    if col_idx < colunas:
                        self.grid.SetCellValue(linha, col_idx, str(value))

                self.grid.SetCellAlignment(linha, 1, wx.ALIGN_CENTRE, wx.ALIGN_CENTRE)
                self.grid.SetCellAlignment(linha, 3, wx.ALIGN_RIGHT, wx.ALIGN_RIGHT)
        
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
        self.despesaSelecionada(row)

    def despesaSelecionada(self, item):
        idSelecionado = self.grid.GetCellValue(item, 0)

        if idSelecionado.isdigit():
            self.despesas.popula_despesas_by_id(idSelecionado)

            self.txtId.SetValue(str(self.despesas.id))
            self.txtDescricao.SetValue(self.despesas.descricao)
            self.txtNotaNegociacao.SetValue(self.despesas.numero_nota)

            data_str = self.despesas.data_lancamento.strftime('%d/%m/%Y')
            data_formatada = datetime.strptime(data_str, '%d/%m/%Y').date()
            self.txtDataLancamento.SetValue(data_formatada)

            data_str = self.despesas.data_efetivacao.strftime('%d/%m/%Y')
            data_formatada = datetime.strptime(data_str, '%d/%m/%Y').date()
            self.txtDataEfetivacao.SetValue(data_formatada)

            self.txtValor.SetValue(str(self.despesas.valor))

            self.setTipoDespesa(self.despesas.id_tipo_despesa)

            self.txtDescricao.Enable()
            self.txtNotaNegociacao.Enable()
            self.txtDataLancamento.Enable()
            self.txtDataEfetivacao.Enable()
            self.txtValor.Enable()

            self.botaoSalva.Enable()
            self.botaoDelete.Enable()

            self.txtDataLancamento.SetFocus()

            self.insert = False

    def habilita_novo(self, event):
        if self.idConta >= 0:
            self.limpaElementos()

            self.txtDescricao.Enable()
            self.txtNotaNegociacao.Enable()
            self.txtDataLancamento.Enable()
            self.txtDataEfetivacao.Enable()
            self.txtValor.Enable()

            self.insert = True

            self.botaoSalva.Enable()

            self.txtDataLancamento.SetFocus()

    def cancela_operacao(self, event):
        self.despesas.clear_despesas()
        self.limpaElementos()

    def salva_elemento(self, event):
        self.despesas.set_data_lancamento(self.txtDataLancamento.GetValue().Format('%d/%m/%Y'))
        self.despesas.set_data_efetivacao(self.txtDataEfetivacao.GetValue().Format('%d/%m/%Y'))
        self.despesas.set_descricao(self.txtDescricao.Value)
        self.despesas.set_numero_nota(self.txtNotaNegociacao.Value)
        self.despesas.set_valor(devolve_float(str(self.txtValor.Value)))
        self.despesas.set_id_conta(self.idConta)
        self.despesas.set_id_tipo_despesa(self.id_tipo_despesa)
        if self.insert is True:
            self.despesas.insere()
            self.insert = False
        else:
            self.despesas.update()

        self.limpaElementos()
        self.montaGrid(self.dataInicial)

    def deleta_elemento(self, event):
        prossegueEliminacao = False
        dlg = wx.MessageDialog(None, 'Confirma a eliminação dos dados?',
                               'Prestes a eliminar definitivamente!',
                               wx.YES_NO | wx.NO_DEFAULT | wx.ICON_QUESTION)
        if dlg.ShowModal() == wx.ID_YES:
            prossegueEliminacao = True

        if prossegueEliminacao:
            self.despesas.delete()
            self.limpaElementos()
            self.montaGrid(self.dataInicial)

def main():
    app = wx.App()
    frmCliente = FrmDespesa(1)
    app.MainLoop()


if __name__ == '__main__':
    main()
