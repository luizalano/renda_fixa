# frm_despesa.py

from wx import *
import wx.adv
from floatValidator import FloatValidator
import wx.grid as gridlib
import wx.grid
from datetime import datetime
from dateutil.relativedelta import relativedelta

from baseCrudFrame import *
from despesa import Despesa
from conta import Conta
from cotacao import Cotacao
from frm_notaNegociacao import FrmNotaNegociacao
from frm_resumoDespesas import FrmResumoDespesas
from frm_resumoDespesasMes import FrmResumoDespesasMes

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

        self.frmNotaNegociacao = None
        self.frmResumoDespesas = None
        self.frmResumoDespesasMes = None


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

        self.cancela_operacao(None)
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
        #self.cbConta = wx.ComboBox(self.form_panel, style=wx.CB_READONLY, size=(200, -1))
        #self.cbConta.Bind(wx.EVT_COMBOBOX, self.contaSelecionada)
        #self.add_field("Conta", self.cbConta)

        self.header_box.Label = "Despesas da conta corrente"
        self.cbConta = wx.ComboBox(self.header_box, style=wx.CB_READONLY)

        container = wx.BoxSizer(wx.VERTICAL)
        #label = wx.StaticText(self.header_box, label="Conta")
        #container.Add(label, 0, wx.BOTTOM, 3)
        container.Add(self.cbConta, 0, wx.EXPAND)

        self.header_right_sizer.Add(container, 0, wx.EXPAND | wx.BOTTOM, 10)

        self.txtNomeMoeda = wx.TextCtrl(self.form_panel, style=wx.TE_READONLY | wx.TE_RIGHT, size=(120, -1))
        self.txtValorMoeda = wx.TextCtrl(self.form_panel, style=wx.TE_READONLY | wx.TE_RIGHT, size=(120, -1))
        nm = self.create_labeled_control("Moeda", self.txtNomeMoeda)
        vm = self.create_labeled_control("Valor moeda", self.txtValorMoeda)
        self.add_row([nm, vm])

        # Datas lado a lado
        self.dpLancamento = wx.adv.DatePickerCtrl(self.form_panel, size=(120, -1), style=wx.adv.DP_DROPDOWN | wx.adv.DP_SHOWCENTURY)
        self.dpEfetivacao = wx.adv.DatePickerCtrl(self.form_panel, size=(120, -1), style=wx.adv.DP_DROPDOWN | wx.adv.DP_SHOWCENTURY)
        #self.dpEfetivacao = wx.adv.DatePickerCtrl(self.form_panel)

        dp1 = self.create_labeled_control("Data lançamento", self.dpLancamento)
        dp2 = self.create_labeled_control("Data efetivação", self.dpEfetivacao)

        self.add_row([dp1, dp2])
        #self.add_row([self.dpLancamento, self.dpEfetivacao])

        self.txtNumeroNota = wx.TextCtrl(self.form_panel, size=(120, -1))
        self.add_field("Número da nota", self.txtNumeroNota)
        #nota_field = self.create_labeled_control("Número da nota", self.txtNumeroNota)

        #self.iconeNota = wx.Bitmap(self.caminho + 'invoice32.png')
        #lb, ab = self.iconeNota.GetSize()
        #self.botaoNota = wx.BitmapButton(self.form_panel, bitmap=self.iconeNota, size=(lb + 10, ab + 10))
        #self.Bind(wx.EVT_BUTTON, self.chamaNota, self.botaoNota)
        #self.botaoNota.SetToolTip("Confere as notas de negociação")
        #self.add_row([nota_field, self.botaoNota])

        # Tipo despesa
        self.cbTipoDespesa = wx.ComboBox(self.form_panel, style=wx.CB_READONLY, size=(200, -1))
        self.cbTipoDespesa.Bind(wx.EVT_COMBOBOX, self.tipoDespesaSelecionada)
        self.add_field("Tipo de despesa", self.cbTipoDespesa)

        # Descrição
        self.txtDescricao = wx.TextCtrl(self.form_panel, size=(300, -1))
        self.add_field("Descrição", self.txtDescricao)

        # Valor
        self.txtValor = wx.TextCtrl(self.form_panel, style=wx.TE_RIGHT, size=(120, -1), validator=FloatValidator())
        self.add_field("Valor", self.txtValor)

        # Texto para números inteiros
        #self.numeroNota = intctrl.IntCtrl(self.form_panel, size=(120, -1), allow_none=True)

        # Saldo bancário (readonly)
        self.txtSaldo = wx.TextCtrl(
            self.form_panel,
            style=wx.TE_READONLY | wx.TE_RIGHT, size=(120, -1)
        )
        self.add_field("Saldo bancário", self.txtSaldo)

        
        self.btnMostraResumoPorTipo = Button(self.form_panel, id=ID_ANY, label="Consolidado por Tipo de Despesa", style=0)
        self.Bind(wx.EVT_BUTTON, self.chamaResumo, self.btnMostraResumoPorTipo)
        self.btnMostraResumoPorTipo.Enabled = False

        self.btnMostraResumoPorMesTipo = Button(self.form_panel, id=ID_ANY, label="Consolidado por Tipo de Despesa e Mês", style=0)
        self.Bind(wx.EVT_BUTTON, self.chamaResumoMes, self.btnMostraResumoPorMesTipo)
        self.btnMostraResumoPorMesTipo.Enabled = False
        
        self.form_sizer.Add(self.btnMostraResumoPorTipo, 1, wx.EXPAND | wx.CENTER, 0)
        self.form_sizer.Add(self.btnMostraResumoPorMesTipo, 1, wx.EXPAND | wx.CENTER, 0)

        #
        #  Acrescentando iten no tollbar
        #

        iconeNota = wx.Bitmap(self.caminho + 'invoice32.png')
        self.ID_NOTAS = wx.NewIdRef()
        self.add_toolbar_item(self.ID_NOTAS, iconeNota, "Notas de negociação", self.chamaNota, "Confere as notas de negociação", separator = True)


        self._load_combos()

    # =============================
    # Eventos
    # =============================

    def _bind_events(self):

        super()._bind_events()

        #self.Bind(wx.EVT_TOOL, self.habilita_novo, id=wx.ID_NEW)
        #self.Bind(wx.EVT_TOOL, self.salva_elemento, id=wx.ID_SAVE)
        #self.Bind(wx.EVT_TOOL, self.deleta_elemento, id=wx.ID_DELETE)
        #self.Bind(wx.EVT_TOOL, self.cancela_operacao, id=wx.ID_CANCEL)

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
        self.left_sizer.Add(self.btnTogglePeriodo, 0, wx.EXPAND | wx.TOP | wx.BOTTOM, 5)


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

    def on_close(self, event, frame_attr):
        """Garante que o objeto seja destruído ao fechar a janela."""
        frame = getattr(self, frame_attr, None)  # Obtém a referência ao frame
        if frame:
            frame.Destroy()  # Destrói a janela
            setattr(self, frame_attr, None)  # Define como None

    def chamaNota(self, event):
        if self.frmNotaNegociacao is None:  # Se não existir, cria uma nova janela
            self.frmNotaNegociacao = FrmNotaNegociacao()
            self.frmNotaNegociacao.Bind(wx.EVT_CLOSE, lambda evt: self.on_close(evt, "frmNotaNegociacao"))
            self.frmNotaNegociacao.Show()
        else:
            self.frmNotaNegociacao.Raise()  # Se já existir, apenas traz para frente

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
                    if col_idx == 3:  # Coluna de valor
                        self.grid.SetCellAlignment(row_idx, col_idx, wx.ALIGN_RIGHT, wx.ALIGN_RIGHT)
                    if col_idx in (0, 1):  # Coluna de id e data
                        self.grid.SetCellAlignment(row_idx, col_idx, wx.ALIGN_CENTRE, wx.ALIGN_CENTRE)

        self.grid.AutoSizeRows()

    def contaSelecionada(self, event):
        nomeConta = self.cbConta.GetStringSelection()
        listaConta = None
        listaConta = Conta.mc_select_one_by_nome(nomeConta)
        self.btnMostraResumoPorTipo.Enabled = False
        self.btnMostraResumoPorMesTipo.Enabled = False
        self.idConta = -1
        if listaConta:
            self.idConta = listaConta[0]
            self.nomeConta = listaConta[4]
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
            self.btnMostraResumoPorTipo.Enabled = True
            self.btnMostraResumoPorMesTipo.Enabled = True
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
            self.txtNumeroNota.SetValue(self.despesas.numero_nota)

            #self.insert = False
            self._set_state(CrudState.VIEWING)

            self.dpEfetivacao.Enable()
            self.dpLancamento.Enable()
            self.txtNumeroNota.Enable()
            self.cbTipoDespesa.Enable()
            self.txtDescricao.Enable()
            self.txtValor.Enable()

            self.toolbar.EnableTool(wx.ID_DELETE, True)
            self.toolbar.EnableTool(wx.ID_SAVE, True) 

    def habilita_novo(self, event):
        super().habilita_novo(event)

        #self.insert = True
        self.txtDescricao.Clear()
        self.txtValor.Clear()

        #self.dpEfetivacao.Enable()
        #self.dpLancamento.Enable()
        #self.txtNumeroNota.Enable()
        #self.cbTipoDespesa.Enable()
        #self.txtDescricao.Enable()
        #self.txtValor.Enable()

        self.toolbar.EnableTool(wx.ID_SAVE, True)  

    def salva_elemento(self, event):

        self.despesas.set_descricao(self.txtDescricao.GetValue())
        self.despesas.set_valor(devolve_float(self.txtValor.GetValue()))
        self.despesas.set_nome_conta(self.cbConta.GetStringSelection())
        self.despesas.set_nome_tipo_despesa(self.cbTipoDespesa.GetStringSelection())
        self.despesas.set_data_lancamento(self.dpLancamento.GetValue().Format('%d/%m/%Y'))
        self.despesas.set_data_efetivacao(self.dpEfetivacao.GetValue().Format('%d/%m/%Y'))
        self.despesas.set_numero_nota(self.txtNumeroNota.GetValue())

        if self.insert:
            self.despesas.insere()
        else:
            self.despesas.update()

        self.cancela_operacao(None)
        self.montaGrid(self.dataInicial)

    def deleta_elemento(self, event):
        super().deleta_elemento(event)

        if self.prossegueEliminacao:
            self.despesas.delete()
            self.cancela_operacao(None)
            self.montaGrid(self.dataInicial)

    def cancela_operacao(self, event):
        super().cancela_operacao(event)

        self.txtDescricao.Clear()
        self.txtValor.Clear()

        #self.dpEfetivacao.Disable()
        #self.dpLancamento.Disable()
        #self.txtNumeroNota.Disable()
        #self.cbTipoDespesa.Disable()
        #self.txtDescricao.Disable()
        #self.txtValor.Disable()




def main():
    app = wx.App()
    FrmDespesa(1)
    app.MainLoop()


if __name__ == "__main__":
    main()
