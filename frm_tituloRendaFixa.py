# coding: utf-8
from wx import Button, ID_ANY

from diversos import *
from titulorendafixa import TituloRendaFixa
from wxFrameMG import FrameMG

import wx
import wx.grid

class FrmTituloRendaFixa(FrameMG):
    insert = False
    caminho = '.\\icones\\'

    def __init__(self):
        self.tituloRendaFixa = TituloRendaFixa()

        super(FrmTituloRendaFixa, self).__init__(pai=None, titulo='Títulos negociados na Renda Fixa',
                                         lar = 1000, alt = 730,
                                         xibot = 600, split=False)

        self.criaComponentes()

    def criaComponentes(self):
        X = self.posx(1)
        Y = self.posy(1)
        tamX = self.larguraEmPx(70)
        tamY = self.alturaEmPx(14)

        self.setAvancoVertical(8)

        self.grid = wx.grid.Grid(self.painel, pos=(X, Y), size=(tamX, tamY))
        self.grid.CreateGrid(0, 2)
        self.grid.SetColSize(0,  30)
        self.grid.SetColSize(1,  360)
        self.grid.SetColLabelValue(0, "ID")
        self.grid.SetColLabelValue(1, "Nome Título")

        x0 = 85

        label01, self.txtId = self.criaCaixaDeTexto(self.painel, pos=(x0, 2), label='ID', tamanho = (6, 1),
                                                    max=6, multi=False )
        
        label03, self.txtNomeTitulo = self.criaCaixaDeTexto(self.painel, pos=(x0, 3),
                                                    label='Nome Título', tamanho = (40, 1),
                                                    max=self.tituloRendaFixa.sql_busca_tamanho('nometitulo'), multi=False )


        self.limpaElementos()

        self.grid.Bind(wx.grid.EVT_GRID_CELL_RIGHT_CLICK, self.on_right_click)

        self.montaGrid()
        self.Show()


    def limpaElementos(self):
        self.tituloRendaFixa.clear_titulorendafixa()

        self.txtId.Clear()
        self.txtNomeTitulo.Clear()

        self.disabilitaComponentes()

    def disabilitaComponentes(self):
        self.txtId.Disable()
        self.txtNomeTitulo.Disable()

        self.botaoSalva.Disable()
        self.botaoDelete.Disable()


    def montaGrid(self):
        self.lista = self.tituloRendaFixa.get_all()

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


    def on_right_click(self, event):
        row = event.GetRow()  # Obtém a linha clicada
        col = event.GetCol()  # Obtém a coluna clicada
        self.tituloRendaFixaSelecionado(row)

    def tituloRendaFixaSelecionado(self, item):
        idSelecionado = self.grid.GetCellValue(item, 0)

        if idSelecionado.isdigit():
            self.tituloRendaFixa.popula_titulorendafixa_by_id(idSelecionado)

            self.txtId.SetValue(str(self.tituloRendaFixa.id))
            self.txtNomeTitulo.SetValue(self.tituloRendaFixa.nome_titulo)
            self.txtNomeTitulo.Enable()

            self.botaoSalva.Enable()
            self.botaoDelete.Enable()

            self.txtNomeTitulo.SetFocus()

            self.insert = False

    def habilita_novo(self, event):
        self.limpaElementos()
        self.txtNomeTitulo.Enable()
        self.insert = True
        self.botaoSalva.Enable()
        self.txtNomeTitulo.SetFocus()

    def cancela_operacao(self, event):
        self.tituloRendaFixa.clear_titulorendafixa()
        self.limpaElementos()

    def salva_elemento(self, event):
        self.tituloRendaFixa.set_nomeTitulo(self.txtNomeTitulo.GetValue())
        if self.insert is True:
            self.tituloRendaFixa.insere()
            self.insert = False
        else:
            self.tituloRendaFixa.update()
        self.limpaElementos()
        self.montaGrid()

    def deleta_elemento(self, event):
        prossegueEliminacao = False
        dlg = wx.MessageDialog(None, 'Confirma a eliminação dos dados?',
                               'Prestes a eliminar definitivamente!',
                               wx.YES_NO | wx.NO_DEFAULT | wx.ICON_QUESTION)
        if dlg.ShowModal() == wx.ID_YES:
            prossegueEliminacao = True

        if prossegueEliminacao:
            self.tituloRendaFixa.delete()
            self.limpaElementos()
            self.montaGrid()

def main():
    app = wx.App()
    objeto = FrmTituloRendaFixa()
    app.MainLoop()


if __name__ == '__main__':
    main()
