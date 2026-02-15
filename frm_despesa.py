# frm_despesa.py

'''
Quase perfeito. Mas abaixo da grid, preciso do botão que eu tinha antes onde escolho se quero ver últimos 3 meses ou todas as despesas. Por padrão são os últimos 3 meses. Então o Caption do botão é "Mostra todos". Clicando no botão, refaz a grid com data inicial de 01/01/2023 (não tem nada antes disso) e muda o caption para "Mostra últimos 3 meses". Na tela à direita, dois problemas. Faltou a linha com o número da nota e o botão que tinha para chamar frm_notaNegociacao.py. Este campo ficava logo abaixo das datas. O segundo problema é que os tamanhos das caixas de texto devem ser compatíveis com a informação que recebe. Não podem ser todas do mesmo tamanho. Questão de estética.
'''


from wx import *
import wx.adv
from floatValidator import FloatValidator
import wx.grid as gridlib
import wx.grid
from datetime import datetime
from dateutil.relativedelta import relativedelta

from baseCrudFrame import BaseCrudFrame
from despesa import Despesa
from conta import Conta
from cotacao import Cotacao
from frm_notaNegociacao import FrmNotaNegociacao
from diversos import *


class FrmDespesa(BaseCrudFrame):

    def __init__(self, idContaInicial):

        super().__init__(
            title="Despesas",
            size=(1050, 680),
            split_ratio=0.55,
            min_left=400,
            min_right=300,
            config_name="FrmDespesa"
        )

        self.despesas = Despesa()
        self.idConta = -1
        self.id_tipo_despesa = -1
        self.insert = False
        self.nomeConta = None
        self._build_form()

        frmNotaNegociacao = None

        self.dataInicial = datetime.now().date() - relativedelta(months=3)

        self._build_left()
        self._configure_grid()
        self._bind_events()
        
        if idContaInicial > 0:
            conta = Conta.mc_select_one_by_id(idContaInicial)
            if conta:
                self.nomeConta = conta[4]
                self.idConta = idContaInicial
                self.setaElementocb(self.cbConta, self.nomeConta)
                self.contaSelecionada(None)


        self.Show()

    # =============================
    # Grid
    # =============================

    def _configure_grid(self):

        columns = [
            ("ID", 60),
            ("Data", 100),
            ("Descrição", 250),
            ("Valor", 120),
        ]

        self.setup_grid_columns(columns)
        #self.montaGrid(self.dataInicial)

    # =============================
    # Form
    # =============================

    def setup_grid_columns(self, columns):

        self.grid.CreateGrid(0, len(columns))

        for idx, (label, width) in enumerate(columns):
            self.grid.SetColLabelValue(idx, label)
            self.grid.SetColSize(idx, width)


    def _build_form(self):

        # Conta
        self.cbConta = wx.ComboBox(self.panel_right, style=wx.CB_READONLY, size=(200, -1))
        self.cbConta.Bind(wx.EVT_COMBOBOX, self.contaSelecionada)
        self.add_field("Conta", self.cbConta)

        self.txtNomeMoeda = wx.TextCtrl(self.panel_right, style=wx.TE_READONLY | wx.TE_RIGHT, size=(120, -1))
        self.txtValorMoeda = wx.TextCtrl(self.panel_right, style=wx.TE_READONLY | wx.TE_RIGHT, size=(120, -1))
        nm = self.create_labeled_control("Moeda", self.txtNomeMoeda)
        vm = self.create_labeled_control("Valor moeda", self.txtValorMoeda)
        self.add_row([nm, vm])

        # Datas lado a lado
        self.dpLancamento = wx.adv.DatePickerCtrl(self.panel_right, size=(120, -1), style=wx.adv.DP_DROPDOWN | wx.adv.DP_SHOWCENTURY)
        self.dpEfetivacao = wx.adv.DatePickerCtrl(self.panel_right, size=(120, -1), style=wx.adv.DP_DROPDOWN | wx.adv.DP_SHOWCENTURY)
        #self.dpEfetivacao = wx.adv.DatePickerCtrl(self.panel_right)

        dp1 = self.create_labeled_control("Data lançamento", self.dpLancamento)
        dp2 = self.create_labeled_control("Data efetivação", self.dpEfetivacao)

        self.add_row([dp1, dp2])
        #self.add_row([self.dpLancamento, self.dpEfetivacao])

        self.numeroNota = wx.TextCtrl(self.panel_right, size=(120, -1))
        nota_field = self.create_labeled_control("Número da nota", self.numeroNota)

        self.iconeNota = wx.Bitmap(self.caminho + 'invoice32.png')
        lb, ab = self.iconeNota.GetSize()
        self.botaoNota = wx.BitmapButton(self.panel_right, bitmap=self.iconeNota, size=(lb + 10, ab + 10))
        self.Bind(wx.EVT_BUTTON, self.chamaNota, self.botaoNota)
        self.botaoNota.SetToolTip("Confere as notas de negociação")
        self.add_row([nota_field, self.botaoNota])

        # Tipo despesa
        self.cbTipoDespesa = wx.ComboBox(self.panel_right, style=wx.CB_READONLY, size=(200, -1))
        self.cbTipoDespesa.Bind(wx.EVT_COMBOBOX, self.tipoDespesaSelecionada)
        self.add_field("Tipo de despesa", self.cbTipoDespesa)

        # Descrição
        self.txtDescricao = wx.TextCtrl(self.panel_right, size=(300, -1))
        self.add_field("Descrição", self.txtDescricao)

        # Valor
        self.txtValor = wx.TextCtrl(self.panel_right, style=wx.TE_RIGHT, size=(120, -1), validator=FloatValidator())
        self.add_field("Valor", self.txtValor)

        # Texto para números inteiros
        #self.numeroNota = intctrl.IntCtrl(self.panel_right, size=(120, -1), allow_none=True)

        # Saldo bancário (readonly)
        self.txtSaldo = wx.TextCtrl(
            self.panel_right,
            style=wx.TE_READONLY | wx.TE_RIGHT, size=(120, -1)
        )
        self.add_field("Saldo bancário", self.txtSaldo)

        self._load_combos()

    # =============================
    # Eventos
    # =============================

    def _bind_events(self):

        super()._bind_events()

        self.Bind(wx.EVT_TOOL, self.on_new, id=wx.ID_NEW)
        self.Bind(wx.EVT_TOOL, self.on_save, id=wx.ID_SAVE)
        self.Bind(wx.EVT_TOOL, self.on_delete, id=wx.ID_DELETE)
        self.Bind(wx.EVT_TOOL, self.on_cancel, id=wx.ID_CANCEL)

        self.grid.Bind(wx.grid.EVT_GRID_CELL_LEFT_CLICK, self.on_grid_click)
        self.cbConta.Bind(wx.EVT_COMBOBOX, self.contaSelecionada)

    # =============================
    # Lógica
    # =============================

    def _build_left(self):
        self.left_sizer = wx.BoxSizer(wx.VERTICAL)

        # Cria a grid
        self.grid = gridlib.Grid(self.panel_left)
        self.grid.EnableEditing(False)
        self.grid.SetRowLabelSize(0)

        self.left_sizer.Add(self.grid, 1, wx.EXPAND | wx.ALL, 5)

        # Botão alterna período
        self.btnTogglePeriodo = wx.Button(self.panel_left, label="Mostra todos")
        self.left_sizer.Add(self.btnTogglePeriodo, 0, wx.ALIGN_CENTER | wx.ALL, 5)

        self.panel_left.SetSizer(self.left_sizer)

        # Evento
        self.btnTogglePeriodo.Bind(wx.EVT_BUTTON, self.on_toggle_periodo)

    def on_toggle_periodo(self, event):
        if self.btnTogglePeriodo.GetLabel() == "Mostra todos":
            self.dataInicial = datetime(2023, 1, 1).date()
            self.btnTogglePeriodo.SetLabel("Mostra últimos 3 meses")
        else:
            self.dataInicial = datetime.now().date() - relativedelta(months=3)
            self.btnTogglePeriodo.SetLabel("Mostra todos")

        self.montaGrid(self.dataInicial)

    def _load_combos(self):

        self.cbConta.Clear()
        for row in Conta.mc_select_all():
            self.cbConta.Append(row[4])

        self.cbTipoDespesa.Clear()
        for row in Despesa.mc_busca_tipos():
            self.cbTipoDespesa.Append(row[1])

    def chamaNota(self, event):
        if self.frmNotaNegociacao is None:  # Se não existir, cria uma nova janela
            self.frmNotaNegociacao = FrmNotaNegociacao()
            self.frmNotaNegociacao.Bind(wx.EVT_CLOSE, lambda evt: self.on_close(evt, "frmNotaNegociacao"))
            self.frmNotaNegociacao.Show()
        else:
            self.frmNotaNegociacao.Raise()  # Se já existir, apenas traz para frente

    def montaGrid(self, dataInicial):

        lista = Despesa.mc_busca_por_periodo(dataInicial, self.idConta)

        data_grid = [
            (row[0], row[1], row[2], row[3])
            for row in lista
        ]

        self.grid.ClearGrid()
        saldo = zero
        if lista:
            self.setaElementocb(self.cbConta, self.nomeConta)
            saldo = Conta.mc_get_saldo_bancario(self.idConta)
            self.txtSaldo.SetValue(formata_numero(saldo))

            if self.grid.GetNumberRows() > 0:
                self.grid.DeleteRows(0, self.grid.GetNumberRows())

            for row in data_grid:
                self.grid.AppendRows()
                row_idx = self.grid.GetNumberRows() - 1

                for col_idx, value in enumerate(row):
                    self.grid.SetCellValue(row_idx, col_idx, str(value))
                    if col_idx in (0, 3):  # Coluna de id e valor
                        self.grid.SetCellAlignment(row_idx, col_idx, wx.ALIGN_RIGHT, wx.ALIGN_RIGHT)
                    if col_idx == 2:  # Coluna de data
                        self.grid.SetCellAlignment(row_idx, col_idx, wx.ALIGN_CENTRE, wx.ALIGN_CENTRE)

        self.grid.AutoSizeRows()

    def contaSelecionada(self, event):
        nomeConta = self.cbConta.GetStringSelection()
        listaConta = None
        listaConta = Conta.mc_select_one_by_nome(nomeConta)
        #self.btnMostraResumoPorTipo.Enabled = False
        self.idConta = -1
        if listaConta:
            self.idConta = listaConta[0]
            #self.btnMostraResumoPorTipo.Enabled = True
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

    def tipoDespesaSelecionada(self, event):
        nomeTipoDespesa = self.cbTipoDespesa.GetStringSelection()
        lista = None
        lista = Despesa.mc_busca_tipo_por_nome(nomeTipoDespesa)
        self.id_tipo_despesa = -1
        if lista:
            self.id_tipo_despesa = lista[0]
            if self.txtDescricao.GetValue().strip() == '':
                self.txtDescricao.SetValue(nomeTipoDespesa.title())

    def on_grid_click(self, event):
        row = event.GetRow()
        idSelecionado = self.grid.GetCellValue(row, 0)

        if idSelecionado.isdigit():
            self.despesas.popula_despesas_by_id(idSelecionado)
            self.cbTipoDespesa.SetSelection(self.cbTipoDespesa.FindString(self.despesas.nome_tipo_despesa))
            self.txtDescricao.SetValue(self.despesas.descricao)
            self.txtValor.SetValue(str(self.despesas.valor))
            self.setaDataPicker(self.dpLancamento, self.despesas.data_lancamento)
            self.setaDataPicker(self.dpEfetivacao, self.despesas.data_efetivacao)
            self.numeroNota.SetValue(self.despesas.numero_nota)

    def habilita_novo(self, event):
        super().habilia_novo(event)

        self.insert = True
        self.txtDescricao.Clear()
        self.txtValor.Clear()

        self.dpEfetivacao.Disable()
        self.dpLancamento.Disable()
        self.txtNumeroNota.Disable()
        self.cbTipoDespesa.Disable()
        self.txtDescricao.Disable()
        self.txtValor.Disable()

    def salva_elemento(self, event):

        self.despesas.set_descricao(self.txtDescricao.GetValue())
        self.despesas.set_valor(devolve_float(self.txtValor.GetValue()))
        self.despesas.set_id_conta(self.idConta)
        self.despesas.set_id_tipo_despesa(self.id_tipo_despesa)
        self.despesas.set_data_lancamento(self.getDataPicker(self.dpLancamento))
        self.despesas.set_data_efetivacao(self.getDataPicker(self.dpEfetivacao))
        self.despesas.set_numero_nota(self.numeroNota.GetValue())

        if self.insert:
            self.despesas.insere()
        else:
            self.despesas.update()

        self.montaGrid(self.dataInicial)

    def deleta_elemento(self, event):
        super().delete_elemento(event)

        if self.prossegueEliminacao:
            self.despesas.delete()
            self.cancela_operacao(None)
            self.montaGrid(self.dataInicial)

    def cancela_operacao(self, event):
        super().cancela_operacao(event)

        self.txtDescricao.Clear()
        self.txtValor.Clear()

        self.dpEfetivacao.Disable()
        self.dpLancamento.Disable()
        self.txtNumeroNota.Disable()
        self.cbTipoDespesa.Disable()
        self.txtDescricao.Disable()
        self.txtValor.Disable()




def main():
    app = wx.App()
    FrmDespesa(1)
    app.MainLoop()


if __name__ == "__main__":
    main()
