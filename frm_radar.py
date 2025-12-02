# coding: utf-8

from wx import *
import wx.grid
from ativo import Ativo
from diversos import *
from bolsa import Bolsa
from datetime import date

class RadarFrm(wx.Frame):
    hoje = None
    sigla_bolsa = None

    def __init__(self, parent, title):
        super().__init__(parent, title=title, size=(1200, 700))

        self.SetPosition((10, 10))
        self.interesse = -1
        self.dias_regresso = 7
        self.dy_minimo = 0
        self.hoje = date.today()

        self.init_ui()

    def init_ui(self):
        panel = wx.Panel(self)
        vbox = wx.BoxSizer(wx.VERTICAL)

        # Filtro por datacom e dy
        
        self.cbBolsa = wx.ComboBox(panel)
        self.cbBolsa.Bind(wx.EVT_COMBOBOX, self.bolsa_selecionada)

        filter_box = wx.BoxSizer(wx.HORIZONTAL)
        #self.date_filter = wx.TextCtrl(panel)
        self.dy_filter = wx.TextCtrl(panel)
        filter_btn = wx.Button(panel, label="Filtrar")
        filter_btn.Bind(wx.EVT_BUTTON, self.on_filter)

        self.dias_filter = wx.TextCtrl(panel)
        regresso_btn = wx.Button(panel, label="Regresso")
        regresso_btn.Bind(wx.EVT_BUTTON, self.on_regresso)

        interesse_btn = wx.Button(panel, label="Só de interesse")
        interesse_btn.Bind(wx.EVT_BUTTON, self.mostra_so_interesse)

        neutro_btn = wx.Button(panel, label="Interesse e neutro")
        neutro_btn.Bind(wx.EVT_BUTTON, self.mostra_neutro)

        tudo_btn = wx.Button(panel, label="Todos os ativos")
        tudo_btn.Bind(wx.EVT_BUTTON, self.mostra_tudo)

        #filter_box.Add(wx.StaticText(panel, label="Filtrar por datacom: "), flag=wx.RIGHT, border=5)
        #filter_box.Add(self.date_filter, proportion=1)
        filter_box.Add(wx.StaticText(panel, label="Bolsa: "), flag=wx.LEFT | wx.RIGHT, border=5)
        filter_box.Add(self.cbBolsa, flag=wx.LEFT, border=5, proportion=1)
        filter_box.Add(interesse_btn, flag=wx.LEFT, border=5, proportion=1)
        filter_box.Add(neutro_btn, flag=wx.LEFT, border=5, proportion=1)
        filter_box.Add(tudo_btn, flag=wx.LEFT, border=5, proportion=1)
        filter_box.Add(wx.StaticText(panel, label="Regredir: "), flag=wx.LEFT | wx.RIGHT, border=5)
        filter_box.Add(self.dias_filter, proportion=1)
        filter_box.Add(regresso_btn, flag=wx.LEFT, border=5, proportion=1)
        filter_box.Add(wx.StaticText(panel, label="Filtrar por DY: "), flag=wx.LEFT | wx.RIGHT, border=5)
        filter_box.Add(self.dy_filter, proportion=1)
        filter_box.Add(filter_btn, flag=wx.LEFT, border=5, proportion=1)

        vbox.Add(filter_box, flag=wx.EXPAND | wx.ALL, border=10)

        # Grid para exibir os dados
        self.grid = wx.grid.Grid(panel)
        self.grid.Bind(wx.grid.EVT_GRID_CELL_RIGHT_CLICK, self.on_right_click)
        self.grid.Bind(wx.grid.EVT_GRID_LABEL_LEFT_CLICK, self.on_coluna_clicada)
        self.grid.CreateGrid(0, 9)
        self.grid.SetColSize(0,  40)
        self.grid.SetColSize(1,  70)
        self.grid.SetColSize(2, 300)
        self.grid.SetColSize(3, 200)
        self.grid.SetColSize(4, 100)
        self.grid.SetColSize(5,  80)
        self.grid.SetColSize(6,  80)
        self.grid.SetColSize(0,  80)
        self.grid.SetColSize(8,  60)
        self.grid.SetColLabelValue(0, "ID")
        self.grid.SetColLabelValue(1, "Ticket")
        self.grid.SetColLabelValue(2, "Ativo")
        self.grid.SetColLabelValue(3, "Tipo ")
        self.grid.SetColLabelValue(4, "DataCom")
        self.grid.SetColLabelValue(5, "Data Pgto")
        self.grid.SetColLabelValue(6, "Valor")
        self.grid.SetColLabelValue(7, "Última $")
        self.grid.SetColLabelValue(8, "DY")

        #self.grid.Bind(wx.grid.EVT_GRID_LABEL_RIGHT_CLICK, self.on_sort_column)

        vbox.Add(self.grid, proportion=1, flag=wx.EXPAND | wx.ALL, border=10)

        panel.SetSizer(vbox)
        self.monta_combo_bolsa()

    def monta_combo_bolsa(self):
        lista = Bolsa.mc_select_all_order_sigla()
        self.cbBolsa.Clear()
        for row in lista:
            self.cbBolsa.Append(row[1])

    def bolsa_selecionada(self, event):
        self.sigla_bolsa = self.cbBolsa.GetStringSelection()
        if self.sigla_bolsa:
            self.populate_grid()

    def on_right_click(self, event):
        row = event.GetRow()  # Obtém a linha clicada

        menu = wx.Menu()
        self.grid.SelectRow(row)
        # Criando as opções do menu
        interesse = menu.Append(wx.ID_ANY, "Ativa &Interesse")
        desinteresse = menu.Append(wx.ID_ANY, "Ativa &Desinteresse")
        neutro = menu.Append(wx.ID_ANY, "Ativa &Neutro")

        # Vinculando funções aos itens do menu
        #self.Bind(wx.EVT_MENU, lambda evt: self.ativa_interesse(row), interesse)
        #self.Bind(wx.EVT_MENU, lambda evt: self.ativa_desinteresse(row), desinteresse)
        #self.Bind(wx.EVT_MENU, lambda evt: self.ativa_neutro(row), neutro)

        self.Bind(wx.EVT_MENU, lambda evt, r=row: self.ativa_interesse(r), interesse)
        self.Bind(wx.EVT_MENU, lambda evt, r=row: self.ativa_desinteresse(r), desinteresse)
        self.Bind(wx.EVT_MENU, lambda evt, r=row: self.ativa_neutro(r), neutro)

        # Exibe o menu na posição do mouse
        self.PopupMenu(menu)
        self.grid.ClearSelection()
        menu.Destroy()  # Destrói o menu após uso

    def on_coluna_clicada(self, event):
        col_idx = event.GetCol()
        nome_coluna = self.grid.GetColLabelValue(col_idx).strip()

        # Mapeia nomes visíveis na grid para nomes do banco/dados
        mapeamento_colunas = {
            "ID": "id",
            "Ticket": "sigla",
            "Ativo": "razaosocial",
            "Tipo": "tipoprov",
            "DataCom": "datacom",
            "Data Pgto": "datapgto",
            "Valor": "valor",
            "Última $": "cotacao",
            "DY": "dy"
        }

        chave = mapeamento_colunas.get(nome_coluna)
        if not chave:
            return  # coluna não mapeada

        # Garante que a ordenação seja pela coluna + datacom
        ordem = f"{chave}, datacom"
        self.populate_grid(order_by=chave) #ordem)

    def ativa_interesse(self, row):
        ativo = self.grid.GetCellValue(row, 1)
        Ativo.mc_mudainteresse_do_ativo(ativo, 1)
        self.populate_grid()

    def ativa_desinteresse(self, row):
        ativo = self.grid.GetCellValue(row, 1)
        Ativo.mc_mudainteresse_do_ativo(ativo, -2)  
        self.populate_grid()

    def ativa_neutro(self, row):
        ativo = self.grid.GetCellValue(row, 1)
        Ativo.mc_mudainteresse_do_ativo(ativo, 0)
        self.populate_grid()

    def mostra_so_interesse(self, event):
        self.interesse = 1
        self.populate_grid()

    def mostra_neutro(self, event):
        self.interesse = -1
        self.populate_grid()

    def mostra_tudo(self, event):
        self.interesse = -2
        self.populate_grid()

    def populate_grid(self, order_by="datacom"):
        if self.sigla_bolsa:
            aux = devolve_float_de_formatacao_completa(self.dy_filter.GetValue())
            self.dy_minimo = aux
            aux = devolveInteger(self.dias_filter.GetValue().replace('.',','))
            if aux == 0: aux = 7
            self.dias_regresso = aux

            try:
                data = Ativo.mc_busca_radar(self.dy_minimo, order_by, self.interesse, self.dias_regresso, self.sigla_bolsa)

                self.grid.ClearGrid()
                if self.grid.GetNumberRows() > 0:
                    self.grid.DeleteRows(0, self.grid.GetNumberRows())
                linhapar = -1

                for row_idx, row in enumerate(data):
                    self.grid.AppendRows()
                    interesse = row[9]
                    bold = False
                    if interesse > 0: bold = True
                    if interesse == -1: amarelo = True
                    else: amarelo = False
                    if interesse == -2: ehdesinteresse = True
                    else: ehdesinteresse = False
                    linhapar += 1
                    azul = False
                    bg = cor_branco #wx.Colour(255, 255, 255)
                    if linhapar == 1:
                        azul = True
                        bg = cor_azulzinho #wx.Colour(221, 255, 204)
                        linhapar = -1
                    
                    italico = False
                    if row[4] == self.hoje: 
                        bg = cor_rosinha #wx.Colour(255, 204, 238)
                        italico = True
                        bold = True
                    if amarelo: bg = cor_amarelinho
                    fontetamanho = 8
                    if ehdesinteresse: 
                        italico = True
                        fontetamanho = 7
                    dataComHoje = False
                    for col_idx, value in enumerate(row):
                        if col_idx < 9:
                            alinha = None
                            if col_idx > 3 and col_idx < 6: alinha = 'centro'
                            elif col_idx > 5 and col_idx < 9: alinha = 'direita'
                            cell_attr = wx.grid.GridCellAttr()
                            valor = value
                            if col_idx == 8:
                                valor = devolveDecimalDeFloat(str(value), 2)
                            self.grid.SetCellValue(row_idx, col_idx, str(valor))
                            formatar_celula_grid(self.grid, row_idx, col_idx, bold=bold, italic=italico, 
                                                 background_color=bg, align=alinha, font_size=fontetamanho)
                    
            except Exception as e:
                wx.MessageBox(f"Erro ao buscar dados: {e}", "Erro", wx.OK | wx.ICON_ERROR)

    def on_filter(self, event):
        try:
            self.populate_grid()
        except ValueError:
            wx.MessageBox("Por favor, insira um número válido para os dias de regresso ou DY.", "Erro", wx.OK | wx.ICON_ERROR)
        

    def on_regresso(self, event):
        try:
            self.populate_grid()
        except ValueError:
            wx.MessageBox("Por favor, insira um número válido para os dias de regresso ou DY.", "Erro", wx.OK | wx.ICON_ERROR)

    def on_sort_column(self, event):
        col = event.GetCol()
        order_by = ["r.id", "a.sigla", "a.razaosocial", "r.tipoprovento", "r.datacom", "r.dataprovavel", "r.valorprovento", "r.ultimacotacao", "r.dy"][col]
        self.populate_grid(order_by=order_by)

if __name__ == '__main__':
    app = wx.App()
    frame = RadarFrm(None, title="Radar de Proventos")
    frame.Show()
    app.MainLoop()