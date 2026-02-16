# coding: utf-8
# BaseCrudFrame.py


# Chatgpt -> “Vamos implementar aquela máquina de estados do CRUD”

import wx
import wx.grid as gridlib
from diversos import *

from enum import Enum, auto

class CrudState(Enum):
    IDLE = auto()
    VIEWING = auto()
    NEW = auto()
    EDITING = auto()

class BaseCrudFrame(wx.Frame):

    def __init__(self,
                 parent=None,
                 title="",
                 size=(1100, 750),
                 split_ratio=0.45,
                 min_left=250,
                 min_right=350,
                 config_name="basecrud",
                 style=wx.DEFAULT_FRAME_STYLE):

        super().__init__(parent, title=title, size=size, style=style)

        self._split_ratio = split_ratio
        self._min_left = min_left
        self._min_right = min_right
        self._config_name = config_name

        self.caminho = '.\\icones\\'
        self.insert = None

        self._config = wx.Config("SistemaFinanceiro")

        self._build_ui()

        # Máquina de estados
        self._state = CrudState.IDLE
        self._apply_state()

        #self._bind_events()
        self._restore_layout()

        self.Centre()
        self.CreateStatusBar()

    # ==========================================================
    # UI
    # ==========================================================

    def _build_ui(self):

        # -------- Toolbar --------
        self.toolbar = self.CreateToolBar()

        self.iconeNovo = wx.Bitmap(self.caminho + 'new32.ico')
        self.toolbar.AddTool(wx.ID_NEW, "Novo",self.iconeNovo)

        self.iconeSalva = wx.Bitmap(self.caminho + 'save32.ico')
        self.toolbar.AddTool(wx.ID_SAVE, "Salvar", self.iconeSalva)
        
        self.iconeDelete = wx.Bitmap(self.caminho + 'delete32.ico')
        self.toolbar.AddTool(wx.ID_DELETE, "Excluir", self.iconeDelete)

        self.iconeCancela = wx.Bitmap(self.caminho + 'cancel32.ico')
        self.toolbar.AddTool(wx.ID_CANCEL, "Cancelar", self.iconeCancela)

        #self._extend_toolbar()
        self.toolbar.Realize()

        # -------- Splitter --------
        self.splitter = wx.SplitterWindow(self, style=wx.SP_LIVE_UPDATE)

        self.panel_left = wx.Panel(self.splitter)
        self.panel_right = wx.Panel(self.splitter)

        #self.grid = gridlib.Grid(self.panel_left)

        self.splitter.SplitVertically(
            self.panel_left,
            self.panel_right
        )

        self.splitter.SetMinimumPaneSize(self._min_left)

        # -------- Layout principal --------
        main_sizer = wx.BoxSizer(wx.VERTICAL)
        main_sizer.Add(self.splitter, 1, wx.EXPAND)
        self.SetSizer(main_sizer)

        self._build_right()

    # ==========================================================
    # Grid (Master)
    # ==========================================================
    def __build_left(self):
        self.left_sizer = wx.BoxSizer(wx.VERTICAL)

        self.grid.EnableEditing(False)
        self.grid.SetRowLabelSize(0)

        self.left_sizer.Add(self.grid, 1, wx.EXPAND | wx.ALL, 5)

    # ==========================================================
    # Form (Detail)
    # ==========================================================

    def __build_right(self):

        main_sizer = wx.BoxSizer(wx.VERTICAL)

        self.form_sizer = wx.BoxSizer(wx.VERTICAL)

        main_sizer.Add(self.form_sizer, 0, wx.EXPAND | wx.ALL, 15)
        main_sizer.AddStretchSpacer()

        self.panel_right.SetSizer(main_sizer)

    def _build_right(self):

        main_sizer = wx.BoxSizer(wx.VERTICAL)

        # ===== Header (sempre ativo) =====
        #self.header_right_panel = wx.Panel(self.panel_right)
        #self.header_right_sizer = wx.BoxSizer(wx.VERTICAL)
        #self.header_right_panel.SetSizer(self.header_right_sizer)

        self.header_box = wx.StaticBox(self.panel_right, label="Contexto")
        self.header_right_sizer = wx.StaticBoxSizer(self.header_box, wx.VERTICAL)

        # ===== Form (controlado pelo estado) =====
        self.form_panel = wx.Panel(self.panel_right)
        self.form_sizer = wx.BoxSizer(wx.VERTICAL)
        self.form_panel.SetSizer(self.form_sizer)

        # Layout vertical:
        #main_sizer.Add(self.header_right_panel, 0, wx.EXPAND | wx.ALL, 10)
        main_sizer.Add(self.header_right_sizer, 0, wx.EXPAND | wx.ALL, 10)
        main_sizer.Add(self.form_panel, 0, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM, 15)
        main_sizer.AddStretchSpacer()

        self.panel_right.SetSizer(main_sizer)


    # ==========================================================
    # Helpers
    # ==========================================================

    def _set_state(self, new_state):
        self._state = new_state
        self._apply_state()

    def _apply_state(self):

        # Toolbar
        if self._state == CrudState.IDLE:
            self.toolbar.EnableTool(wx.ID_NEW, True)
            self.toolbar.EnableTool(wx.ID_SAVE, False)
            self.toolbar.EnableTool(wx.ID_DELETE, False)
            self.toolbar.EnableTool(wx.ID_CANCEL, False)
            self._enable_form(False)

        elif self._state == CrudState.VIEWING or self._state == CrudState.EDITING:
            self.toolbar.EnableTool(wx.ID_NEW, False)
            self.toolbar.EnableTool(wx.ID_SAVE, True)
            self.toolbar.EnableTool(wx.ID_DELETE, False)
            self.toolbar.EnableTool(wx.ID_CANCEL, True)
            self.insert = False
            self._enable_form(True)

        elif self._state == CrudState.NEW:
            self.toolbar.EnableTool(wx.ID_NEW, False)
            self.toolbar.EnableTool(wx.ID_SAVE, True)
            self.toolbar.EnableTool(wx.ID_DELETE, False)
            self.toolbar.EnableTool(wx.ID_CANCEL, True)
            self.insert = True
            self._enable_form(True)

    def _enable_form(self, enable=True):
        for child in self.form_panel.GetChildren():
            child.Enable(enable)

    def add_field(self, label_text, control):

        container = wx.BoxSizer(wx.VERTICAL)

        label = wx.StaticText(self.form_panel, label=label_text)
        container.Add(label, 0, wx.BOTTOM, 3)
        container.Add(control, 0, wx.EXPAND)

        self.form_sizer.Add(container, 0, wx.BOTTOM, 12)

    def add_row(self, controls):

        row = wx.BoxSizer(wx.HORIZONTAL)

        for i, ctrl in enumerate(controls):
            if i > 0:
                row.AddSpacer(10)
            row.Add(ctrl, 0, wx.ALIGN_LEFT)

        #self.form_sizer.Add(row, 0, wx.EXPAND | wx.BOTTOM, 12)
        self.form_sizer.Add(row, 0, wx.BOTTOM, 12)

    def create_labeled_control(self, label_text, control):
        container = wx.BoxSizer(wx.VERTICAL)

        label = wx.StaticText(self.form_panel, label=label_text)
        container.Add(label, 0, wx.BOTTOM, 3)
        container.Add(control, 0)

        return container

    def add_toolbar_visual_separator(self):

        self.toolbar.AddSeparator()

        line = wx.StaticLine(
            self.toolbar,
            style=wx.LI_VERTICAL,
            size=(2, 28)
        )

        self.toolbar.AddControl(line)

        self.toolbar.Realize()

    def add_toolbar_item(self, id_ref, icone, label, handler, tip=None, separator=True):

        if separator:
            self.toolbar.AddSeparator()
            self.add_toolbar_visual_separator()

        tool = self.toolbar.AddTool(id_ref, label, icone)

        if tip:
            tool.SetShortHelp(tip)

        self.Bind(wx.EVT_TOOL, handler, id=id_ref)

        self.toolbar.Realize()

    # ==========================================================
    # Layout inteligente (proporcional + persistência)
    # ==========================================================

    def _bind_events(self):

        self.Bind(wx.EVT_SIZE, self._on_resize)
        self.Bind(wx.EVT_CLOSE, self._on_close)

        # Eventos padrão da toolbar
        self.Bind(wx.EVT_TOOL, self.habilita_novo, id=wx.ID_NEW)
        self.Bind(wx.EVT_TOOL, self.salva_elemento, id=wx.ID_SAVE)
        self.Bind(wx.EVT_TOOL, self.deleta_elemento, id=wx.ID_DELETE)
        self.Bind(wx.EVT_TOOL, self.cancela_operacao, id=wx.ID_CANCEL)

    def habilita_novo(self, event):
        #self.toolbar.EnableTool(wx.ID_SAVE, True)
        #self.toolbar.EnableTool(wx.ID_DELETE, False)
        #self._clear_form()
        self._set_state(CrudState.NEW)


    def salva_elemento(self, event):
        #if self._state == CrudState.NEW:
        #    self.insert = True
        #
        #elif self._state == CrudState.EDITING:
        #    self.insert = False

        self._set_state(CrudState.VIEWING)

    def deleta_elemento(self, event):
        self.prossegueEliminacao = False
        dlg = wx.MessageDialog(None, 'Confirma a eliminação dos dados?',
                               'Prestes a eliminar definitivamente!',
                               wx.YES_NO | wx.NO_DEFAULT | wx.ICON_QUESTION)
        if dlg.ShowModal() == wx.ID_YES:
            self.prossegueEliminacao = True
        dlg.Destroy()
        self._set_state(CrudState.IDLE)

    def cancela_operacao(self, event):
        #self.toolbar.EnableTool(wx.ID_SAVE, False)
        #self.toolbar.EnableTool(wx.ID_DELETE, False)
        #self._clear_form()
        self._set_state(CrudState.IDLE)        

    def _on_resize(self, event):

        if not self.splitter.IsSplit():
            return

        total_width = self.GetClientSize().width
        new_pos = int(total_width * self._split_ratio)

        self.splitter.SetSashPosition(new_pos)
        event.Skip()

    def _on_close(self, event):

        self._save_layout()
        event.Skip()

    def _restore_layout(self):

        x = self._config.ReadInt(f"{self._config_name}/x", -1)
        y = self._config.ReadInt(f"{self._config_name}/y", -1)
        w = self._config.ReadInt(f"{self._config_name}/w", -1)
        h = self._config.ReadInt(f"{self._config_name}/h", -1)
        sash = self._config.ReadInt(f"{self._config_name}/sash", -1)

        if w > 0 and h > 0:
            self.SetSize((w, h))

        if x >= 0 and y >= 0:
            self.SetPosition((x, y))

        if sash > 0:
            wx.CallAfter(self.splitter.SetSashPosition, sash)

    def _save_layout(self):

        x, y = self.GetPosition()
        w, h = self.GetSize()
        sash = self.splitter.GetSashPosition()

        self._config.WriteInt(f"{self._config_name}/x", x)
        self._config.WriteInt(f"{self._config_name}/y", y)
        self._config.WriteInt(f"{self._config_name}/w", w)
        self._config.WriteInt(f"{self._config_name}/h", h)
        self._config.WriteInt(f"{self._config_name}/sash", sash)

        self._config.Flush()

    def formatar_celula_grid(grid, linha, coluna, **kwargs):
        """
        Formata uma célula da grid com estilos opcionais.
        
        Parâmetros:
        - bold (bool): aplica negrito (padrão True)
        - italic (bool): aplica itálico (padrão True)
        - font_size (int): tamanho da fonte (padrão 10)
        - text_color (wx.Colour ou (r,g,b)): cor do texto
        - background_color (wx.Colour ou (r,g,b)): cor do fundo
        """
        attr = wx.gridlib.GridCellAttr()

        bold = kwargs.get("bold", False)
        italic = kwargs.get("italic", False)
        font_size = kwargs.get("font_size", 10)

        font = wx.Font(
            font_size,
            wx.FONTFAMILY_DEFAULT,
            wx.FONTSTYLE_ITALIC if italic else wx.FONTSTYLE_NORMAL,
            wx.FONTWEIGHT_BOLD if bold else wx.FONTWEIGHT_NORMAL
        )
        attr.SetFont(font)

        # Cores (opcional)
        if "text_color" in kwargs:
            cor = kwargs["text_color"]
            attr.SetTextColour(wx.Colour(*cor) if isinstance(cor, tuple) else cor)

        if "background_color" in kwargs:
            cor = kwargs["background_color"]
            attr.SetBackgroundColour(wx.Colour(*cor) if isinstance(cor, tuple) else cor)

        # Aplica o atributo à célula
        grid.SetAttr(linha, coluna, attr)

    def setaElementocb(self, cb, valor):
        for i in range(cb.Count):
            if cb.GetString(i) == valor:
                cb.SetSelection(i)
                break

    def setaDataPicker(self, date_picker, data_str):
        try:
            #data = wx.DateTime()
            data = devolveDate(data_str)
            #data.ParseFormat(data_str, "%Y-%m-%d")
            if data:
                date_picker.SetValue(data)
        except Exception as e:
            print(f"Erro ao configurar DatePicker: {e}")