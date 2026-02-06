# coding: utf-8
#from wx import Button, ID_ANY

from diversos import *
from ativo import *
from conta import *
from transferencia import Transferencia
from wxFrameMG import FrameMG

from wx import *
import wx.grid
from datetime import datetime
from dateutil.relativedelta import relativedelta

class FrmTransferencia(FrameMG):
    insert = False
    caminho = '.\\icones\\'
    id_conta_origem = -1
    id_conta_destino = -1
    num_dias = 90

    def __init__(self):
        self.transferencia = Transferencia()
        self.today = datetime.now().date()

        super(FrmTransferencia, self).__init__(pai=None, titulo='Lançamentos de Transferências bancárias',
                                         lar = 1000, alt = 730,
                                         xibot = 700, split=False)

        self.criaComponentes()

    def criaComponentes(self):
        X = self.posx(1)
        Y = self.posy(1)
        tamX = self.larguraEmPx(130)
        tamY = self.alturaEmPx(14)

        self.setAvancoVertical(8)

        self.grid = wx.grid.Grid(self.painel, pos=(X, Y), size=(650, tamY))
        self.grid.CreateGrid(0, 5)
        self.grid.SetColSize(0,  50)
        self.grid.SetColSize(1,  80)
        self.grid.SetColSize(2, 150)
        self.grid.SetColSize(3, 150)
        self.grid.SetColSize(4, 100)
        self.grid.SetColLabelValue(0, "ID")
        self.grid.SetColLabelValue(1, "Data")
        self.grid.SetColLabelValue(2, "Origem")
        self.grid.SetColLabelValue(3, "Destino")
        self.grid.SetColLabelValue(4, "Valor")

        x0 = 90

        label01, self.txtId = self.criaCaixaDeTexto(self.painel, pos=(x0 + 10, 1), label='ID', tamanho = (6, 1),
                                                    max=6, multi=False )

        label02, self.cbConta_origem = self.criaCombobox(self.painel, pos=(x0 + 10, 2), tamanho=22, label='Conta origem')
        self.cbConta_origem.Bind(wx.EVT_COMBOBOX, self.conta_origem_selecionada)

        label03, self.txtSaldo_conta_origem = self.criaCaixaDeTexto(self.painel, pos=(x0 + 10, 3),
                                                    label='Saldo conta origem', tamanho = (15, 1),
                                                    max=0, multi=False )
        self.txtSaldo_conta_origem.SetWindowStyleFlag(wx.TE_RIGHT)
        self.txtSaldo_conta_origem.SetForegroundColour(wx.BLACK)
        self.txtSaldo_conta_origem.SetBackgroundColour(wx.Colour(237, 237, 237))
        self.txtSaldo_conta_origem.Disable()

        label04, self.cbConta_destino = self.criaCombobox(self.painel, pos=(x0 + 10, 4), tamanho=22, label='Conta destino')
        self.cbConta_destino.Bind(wx.EVT_COMBOBOX, self.conta_destino_selecionada)

        label05, self.txtSaldo_conta_destino = self.criaCaixaDeTexto(self.painel, pos=(x0 + 10, 5),
                                                    label='Saldo conta destino', tamanho = (15, 1),
                                                    max=0, multi=False )
        self.txtSaldo_conta_destino.SetWindowStyleFlag(wx.TE_RIGHT)
        self.txtSaldo_conta_destino.SetForegroundColour(wx.BLACK)
        self.txtSaldo_conta_destino.SetBackgroundColour(wx.Colour(237, 237, 237))
        self.txtSaldo_conta_destino.Disable()
        
        label06, self.txtData_lancamento = self.criaCaixaDeTexto(self.painel, pos=(x0 + 10, 6),
                                                           label='Datda transferência', tamanho = (12, 1),
                                                           multi=False, tipodate=True)

        label07, self.txtValor = self.criaCaixaDeTexto(self.painel, pos=(x0 + 10, 7),
                                                    label='Valor', tamanho = (15, 1),
                                                    max=0, multi=False, tipofloat=True)

        self.btnMostraNaoMostra = Button(self.painel, id=ID_ANY, label="Mostra todos"
                                        , pos=(self.posx(30), self.posy(12)+15),
                                        size=(self.posx(50), self.posy(1) - 30), style=0)
        self.Bind(wx.EVT_BUTTON, self.mostra_nao_mostra, self.btnMostraNaoMostra)

        self.valores_default()

        self.grid.Bind(wx.grid.EVT_GRID_CELL_RIGHT_CLICK, self.on_right_click)

        self.enche_combo_contas()
        self.monta_grid()
        self.Show()

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

    def set_conta(self, idConta):
        lista = Conta.mc_select_one_by_id(idConta)
        if lista:
            self.cbConta.SetSelection(self.indiceCb(self.cbConta, lista[4]))
            self.conta_origem_selecionada(None)

    def conta_origem_selecionada(self, event):
        nomeConta = self.cbConta_origem.GetStringSelection()
        listaConta = None
        listaConta = Conta.mc_select_one_by_nome(nomeConta)
        self.id_conta = -1
        if listaConta:
            self.id_conta_origem = listaConta[0]
            saldo = Conta.mc_get_saldo_bancario(self.id_conta_origem)
            self.txtSaldo_conta_origem.SetValue(formata_numero(saldo))

    def conta_destino_selecionada(self, event):
        nomeConta = self.cbConta_destino.GetStringSelection()
        listaConta = None
        listaConta = Conta.mc_select_one_by_nome(nomeConta)
        self.id_conta = -1
        if listaConta:
            self.id_conta_destino = listaConta[0]
            saldo = Conta.mc_get_saldo_bancario(self.id_conta_destino)
            self.txtSaldo_conta_destino.SetValue(formata_numero(saldo))

    def valores_default(self):
        self.transferencia.clear()

        self.txtId.Clear()
        self.txtValor.Clear()
        self.txtSaldo_conta_origem.Clear()
        self.txtSaldo_conta_destino.Clear()
        self.txtData_lancamento.SetValue(datetime.now().date())
        self.cbConta_origem.SetSelection(-1)
        self.cbConta_destino.SetSelection(-1)

        self.disabilita_componentes()

    def limpa_elementos(self):
        self.valores_default()

    def disabilita_componentes(self):
        self.txtId.Disable()
        self.txtValor.Disable()
        self.txtData_lancamento.Disable()
        self.txtValor.Disable()
        self.cbConta_origem.Disable()
        self.cbConta_destino.Disable()

        self.botaoSalva.Disable()
        self.botaoDelete.Disable()

    def enche_combo_contas(self):
        lista = Conta.mc_select_all()
        self.cbConta_origem.Clear()
        self.cbConta_destino.Clear()
        for row in lista:
            self.cbConta_origem.Append(row[4])
            self.cbConta_destino.Append(row[4])

    def mostra_nao_mostra(self, event):
        caption = self.btnMostraNaoMostra.GetLabel()
        if caption == 'Mostra todos':
            self.btnMostraNaoMostra.SetLabel('Mostra últimos 90 dias')
            self.num_dias = 9000
            self.monta_grid()
        else:
            self.btnMostraNaoMostra.SetLabel('Mostra todos')
            self.num_dias = 90
            self.monta_grid()

    def monta_grid(self):
        self.lista = Transferencia.mc_busca_por_periodo(self.num_dias)
        self.grid.ClearGrid()

        if self.grid.GetNumberRows() > 0:
            self.grid.DeleteRows(0, self.grid.GetNumberRows())
        linha = -1
        if self.lista:
            for row in self.lista:
                linha += 1

                self.grid.AppendRows()
                self.grid.SetCellValue(linha, 0, str(row[0]))
                self.grid.SetCellValue(linha, 1, row[5].strftime("%d/%m/%Y"))
                self.grid.SetCellValue(linha, 2, row[2])
                self.grid.SetCellValue(linha, 3, row[4])
                self.grid.SetCellValue(linha, 4, formata_numero(row[6]))
                self.grid.SetCellAlignment(linha, 1, wx.ALIGN_CENTRE, wx.ALIGN_CENTRE)
                self.grid.SetCellAlignment(linha, 2, wx.ALIGN_CENTRE, wx.ALIGN_CENTRE)
                self.grid.SetCellAlignment(linha, 4, wx.ALIGN_RIGHT, wx.ALIGN_RIGHT)

    def on_right_click(self, event):
        row = event.GetRow()  # Obtém a linha clicada
        self.linha_da_grid_selecionada(row)

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

    def linha_da_grid_selecionada(self, item):
        id_selecionado = self.grid.GetCellValue(item, 0)

        if id_selecionado.isdigit():
            self.transferencia.select_by_id(id_selecionado)

            self.txtId.SetValue(str(self.transferencia.id))

            data_str = self.transferencia.data_lancamento.strftime('%d/%m/%Y')
            data_formatada = datetime.strptime(data_str, '%d/%m/%Y').date()
            self.txtData_lancamento.SetValue(data_formatada)

            self.txtValor.SetValue(str(self.transferencia.valor))

            self.cbConta_origem.SetSelection(self.indiceCb(self.cbConta_origem, self.transferencia.nome_conta_origem))
            self.cbConta_destino.SetSelection(self.indiceCb(self.cbConta_destino, self.transferencia.nome_conta_destino))
           
            self.txtData_lancamento.Enable()
            self.txtValor.Enable()
            self.cbConta_origem.Enable()
            self.cbConta_destino.Enable()

            saldo = Conta.mc_get_saldo_bancario(self.transferencia.id_conta_origem)
            self.txtSaldo_conta_origem.SetValue(formata_numero(saldo))

            saldo = Conta.mc_get_saldo_bancario(self.transferencia.id_conta_destino)
            self.txtSaldo_conta_destino.SetValue(formata_numero(saldo))

            self.botaoSalva.Enable()
            self.botaoDelete.Enable()

            self.txtData_lancamento.SetFocus()

            self.insert = False

    def habilita_novo(self, event):
        self.limpa_elementos()
        self.txtData_lancamento.Enable()
        self.txtValor.Enable()
        self.cbConta_origem.Enable()
        self.cbConta_destino.Enable()

        self.botaoSalva.Enable()
        self.botaoDelete.Enable()

        self.txtData_lancamento.SetFocus()

        self.insert = True

    def cancela_operacao(self, event):
        self.transferencia.clear()
        self.limpa_elementos()
        self.disabilita_componentes()

    def salva_elemento(self, event):
        aux = self.txtData_lancamento.GetValue().Format('%d/%m/%Y')
        self.transferencia.set_data_lancamento(aux)

        self.transferencia.set_valor(devolve_float(self.txtValor.GetValue()))
        self.transferencia.set_nome_conta_origem(self.cbConta_origem.GetStringSelection())
        self.transferencia.set_nome_conta_destino(self.cbConta_destino.GetStringSelection())

        validado = True
        if self.transferencia.valor <= 0: validado = False
        if self.transferencia.id_conta_origem < 0: validado = False
        if self.transferencia.id_conta_destino < 0: validado = False
        if validado:
            try:
                if self.insert is True:
                    self.transferencia.insert()
                    self.insert = False
                else:
                    self.transferencia.update()
                self.cancela_operacao(event)
                self.monta_grid()
            except  Exception as e:
                dlg = wx.MessageDialog(None, str(e), 'Erro ao salvar transferência!', wx.OK | wx.ICON_ERROR)
                result = dlg.ShowModal()
        else:
            dlg = wx.MessageDialog(None, 'Verifique os valores informados!' , 'Erro ao salvar transferência!', wx.OK | wx.ICON_ERROR)
            result = dlg.ShowModal()

    def deleta_elemento(self, event):
        prossegueEliminacao = False
        dlg = wx.MessageDialog(None, 'Confirma a eliminação dos dados?',
                               'Prestes a eliminar definitivamente!',
                               wx.YES_NO | wx.NO_DEFAULT | wx.ICON_QUESTION)
        if dlg.ShowModal() == wx.ID_YES:
            prossegueEliminacao = True

        if prossegueEliminacao:
            self.transferencia.delete()
            self.cancela_operacao(event)
            self.monta_grid()

def main():
    app = wx.App()
    frmProvento = FrmTransferencia()
    app.MainLoop()


if __name__ == '__main__':
    main()
