# coding: utf-8

import wx
import wx.grid as gridlib
from datetime import datetime
from collections import defaultdict
from databasefunctions import ConectaBD
from diversos import *
from despesa import Despesas

class FrmResumoDespesas(wx.Frame):
    def __init__(self, id_conta):
        super().__init__(None, title="Resumo de Despesas por Tipo (Pivot)", size=(1200, 700))
        self.id_conta = id_conta

        panel = wx.Panel(self)
        vbox = wx.BoxSizer(wx.VERTICAL)

        self.grid = gridlib.Grid(panel)
        self.grid.CreateGrid(0, 0)

        vbox.Add(self.grid, 1, wx.EXPAND | wx.ALL, 10)
        panel.SetSizer(vbox)

        self.Centre()
        self.Show()

        self.carregar_dados()

    @staticmethod
    def getConexao():
        try:
            con = ConectaBD.retornaConexao()
            return con
        except Exception as e:
            print(f"Erro ao conectar com o banco: {e}")
            return False

    def carregar_dados(self):
        resultados = Despesas.mc_busca_todas_despesas_por_mes()
        if resultados:
            dados = defaultdict(dict)
            todas_despesas = set()

            for mes_ano, nomedespesa, total in resultados:
                dados[mes_ano][nomedespesa] = total
                todas_despesas.add(nomedespesa)

            todas_despesas = sorted(todas_despesas)
            meses = sorted(dados.keys())

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

            for row_idx, mes in enumerate(meses):
                self.grid.AppendRows(1)
                self.grid.SetCellValue(row_idx, 0, mes)
                formatar_celula_grid(self.grid, row_idx, 0, align='centro', font_size=tamanhoFonte)
                for col_idx, nome in enumerate(todas_despesas):
                    valor = dados[mes].get(nome, 0.0)
                    self.grid.SetCellValue(row_idx, col_idx + 1, f"{valor:.2f}".replace('.', ','))
                    formatar_celula_grid(self.grid, row_idx, col_idx + 1, align='direita', font_size=tamanhoFonte)
                    
            ultimaColuna = self.grid.GetNumberCols() - 1        
            for linha in range(self.grid.GetNumberRows()):
                total = 0
                for coluna in range(self.grid.GetNumberCols()-2):
                    conteudo = self.grid.GetCellValue(linha, coluna +1)
                    valor = devolve_float_de_formatacao_completa(conteudo)
                    total = total + valor
                self.grid.SetCellValue(linha, ultimaColuna, f"{total:.2f}".replace('.', ','))
                formatar_celula_grid(self.grid, linha, ultimaColuna, align='direita', font_size=tamanhoFonte)

if __name__ == '__main__':
    app = wx.App()
    FrmResumoDespesas(id_conta=1)  # Substitua pelo id real quando for chamar do programa principal
    app.MainLoop()
