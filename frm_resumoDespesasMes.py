# coding: utf-8

from wx import *
import wx.grid as gridlib
from datetime import datetime
from collections import defaultdict
from despesa import Despesas
from diversos import *

class FrmResumoDespesasMes(wx.Frame):
    def __init__(self, id_conta):
        super().__init__(None, title="Resumo de Despesas por Tipo no Mês", size=(1200, 700))
        self.id_conta = id_conta

        panel = wx.Panel(self)
        vbox = wx.BoxSizer(wx.VERTICAL)

        top_panel = wx.Panel(panel)
        top_sizer = wx.BoxSizer(wx.HORIZONTAL)

        self.labelMes = wx.StaticText(top_panel, id=ID_ANY, label='Mês:', pos=posicao(5,1), size=DefaultSize, style=0)
        self.txtMes = wx.TextCtrl(top_panel, pos=posicao(10,1), size=(letrasEmPixels(2), 20))
        self.txtMes.SetMaxLength(2)
        self.labelAno = wx.StaticText(top_panel, id=ID_ANY, label='Ano:', pos=posicao(15, 1), size=DefaultSize, style=0)
        self.txtAno = wx.TextCtrl(top_panel, pos=posicao(20,1), size=(letrasEmPixels(4), 20))
        self.txtAno.SetMaxLength(4)

        self.btnBusca = Button(top_panel, id=ID_ANY, label="Busca dados",
                                        pos=(XemPixel(30), YemPixel(1) - 5),
                                        size=(letrasEmPixels(40), 30), style=0)
        self.Bind(wx.EVT_BUTTON, self.buscaDados, self.btnBusca)

        #top_sizer.Add(self.labelMes, proportion=1, flag=wx.EXPAND | wx.ALL, border=5)
        #top_sizer.Add(self.txtMes, proportion=1, flag=wx.EXPAND | wx.ALL, border=5)
        #top_sizer.Add(self.labelAno, proportion=1, flag=wx.EXPAND | wx.ALL, border=5)
        #top_sizer.Add(self.txtAno, proportion=1, flag=wx.EXPAND | wx.ALL, border=5)
        #top_panel.SetSizer(top_sizer)
        vbox.Add(top_panel, flag=wx.EXPAND | wx.ALL, border=5)

        main_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.grid = gridlib.Grid(panel)
        self.grid.CreateGrid(0, 0)

        main_sizer.Add(self.grid, 3, wx.EXPAND | wx.ALL, 10)
        vbox.Add(main_sizer, proportion=1, flag=wx.EXPAND)

        panel.SetSizer(vbox)

        self.Centre()
        self.Show()

        #self.carregar_dados()
    def buscaDados(self, event):
        try:
            mes = int(self.txtMes.GetValue())
            ano = int(self.txtAno.GetValue())

            continua = False
            if mes > 0 and mes < 13: 
                if ano > 2022 and ano < 3000:
                    continua = True
            
            self.carregar_dados(mes, ano)    

        except Exception as e:
            wx.MessageBox(f"Entre com o mês e ano corretamente!", "Erro", wx.OK | wx.ICON_ERROR)

    def carregar_dados(self, mes, ano):
        resultados = Despesas.mc_busca_despesas_por_mes_ano(mes, ano)   
        if resultados:
            dados = defaultdict(dict)
            todas_despesas = set()

            for datalancamento, nomedespesa, total in resultados:
                dados[datalancamento][nomedespesa] = total
                todas_despesas.add(nomedespesa)

            todas_despesas = sorted(todas_despesas)
            dias = sorted(dados.keys())

            self.grid.ClearGrid()
            if self.grid.GetNumberRows() > 0:
                self.grid.DeleteRows(0, self.grid.GetNumberRows())
            if self.grid.GetNumberCols() > 0:
                self.grid.DeleteCols(0, self.grid.GetNumberCols())

            tamanhoColuna = 120
            tamanhoFonte = 10
            self.grid.AppendCols(1 + len(todas_despesas)+1)
            self.grid.SetColLabelValue(0, "Data")
            
            for idx, nome in enumerate(todas_despesas):
                self.grid.SetColLabelValue(idx + 1, nome)
                self.grid.SetColSize(idx + 1, tamanhoColuna)
            self.grid.SetColLabelValue(self.grid.GetNumberCols() - 1, "Total")
            self.grid.SetColSize(self.grid.GetNumberCols() - 1, tamanhoColuna)

            for row_idx, dialancamento in enumerate(dias):
                self.grid.AppendRows(1)
                self.grid.SetCellValue(row_idx, 0, dialancamento.strftime("%d/%m/%Y"))
                formatar_celula_grid(self.grid, row_idx, 0, align='centro', font_size=tamanhoFonte)
                for col_idx, nome in enumerate(todas_despesas):
                    valor = dados[dialancamento].get(nome, 0.0)
                    self.grid.SetCellValue(row_idx, col_idx + 1, f"{valor:.2f}".replace('.', ','))
                    formatar_celula_grid(self.grid, row_idx, col_idx + 1, align='direita', font_size=tamanhoFonte)
                    
            ultimaColuna = self.grid.GetNumberCols() - 1        
            for linha in range(self.grid.GetNumberRows()):
                total = 0
                for coluna in range(self.grid.GetNumberCols()-2):
                    conteudo = self.grid.GetCellValue(linha, coluna +1)
                    valor = devolveFloat(conteudo)
                    total = total + valor
                self.grid.SetCellValue(linha, ultimaColuna, f"{total:.2f}".replace('.', ','))
                formatar_celula_grid(self.grid, linha, ultimaColuna, align='direita', font_size=tamanhoFonte)

            ultimaLinha = self.grid.GetNumberRows()
            self.grid.AppendRows(1)
            self.grid.SetCellValue(ultimaLinha, 0, 'Total')
            formatar_celula_grid(self.grid, ultimaLinha, 0, align='centro', font_size=tamanhoFonte, bold = True)
            for col in range(1, self.grid.GetNumberCols()):
                total = 0
                for linha in range(ultimaLinha):
                    conteudo = self.grid.GetCellValue(linha, col)
                    valor = devolveFloat(conteudo)
                    total = total + valor
                self.grid.SetCellValue(ultimaLinha, col, f"{total:.2f}".replace('.', ','))
                formatar_celula_grid(self.grid, ultimaLinha, col, align='direita', font_size=tamanhoFonte, bold = True)

if __name__ == '__main__':
    app = wx.App()
    FrmResumoDespesasMes(id_conta=1)  # Substitua pelo id real quando for chamar do programa principal
    app.MainLoop()
