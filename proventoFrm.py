# coding: utf-8
#from wx import Button, ID_ANY

from diversos import *
from Provento import Provento
from Ativo import *
from Cotacao import *
from Conta import *
from wxFrameMG import FrameMG
#from ClienteDeQuem import ClienteDeQuem

from wx import *
import wx.grid
from datetime import datetime
from dateutil.relativedelta import relativedelta

class FrmProvento(FrameMG):
    insert = False
    caminho = '.\\icones\\'
    idConta = -1
    listaFase = []
    totalProventos = 0.0

    def __init__(self, idContaInicial):
        self.provento = Provento()
        self.today = datetime.now().date()

        super(FrmProvento, self).__init__(pai=None, titulo='Lançamentos de Proventos',
                                         lar = 1370, alt = 730,
                                         xibot = 1000, split=False)

        self.criaComponentes()
        self.setConta(idContaInicial)

    def criaComponentes(self):
        X = self.posx(1)
        Y = self.posy(1)
        tamX = self.larguraEmPx(130)
        tamY = self.alturaEmPx(13)

        self.setAvancoVertical(8)

        #self.grid = wx.ListCtrl(self.painel, pos=(X, Y), size=(tamX, tamY),
        #                        style=wx.LC_REPORT | wx.LC_VRULES | wx.LC_HRULES | wx.BORDER_SUNKEN)

        label08, self.cbConta = self.criaCombobox(self.painel, pos=(X, 0), tamanho=22, label='Conta')
        self.cbConta.Bind(wx.EVT_COMBOBOX, self.contaSelecionada)

        self.grid = wx.grid.Grid(self.painel, pos=(X, Y), size=(tamX, tamY))
        self.grid.CreateGrid(0, 9)
        self.grid.SetColSize(0,  50)
        self.grid.SetColSize(1,  80)
        self.grid.SetColSize(2,  80)
        self.grid.SetColSize(3, 100)
        self.grid.SetColSize(4, 100)
        self.grid.SetColSize(5, 100)
        self.grid.SetColSize(6,  60)
        self.grid.SetColSize(7, 100)
        self.grid.SetColSize(8, 150)
        self.grid.SetColLabelValue(0, "ID")
        self.grid.SetColLabelValue(1, "Data")
        self.grid.SetColLabelValue(2, "Ativo")
        self.grid.SetColLabelValue(3, "Valor Bruto")
        self.grid.SetColLabelValue(4, "Valor IR")
        self.grid.SetColLabelValue(5, "Valor Liquido")
        self.grid.SetColLabelValue(6, "Status")
        self.grid.SetColLabelValue(7, "Tipo Provento")
        self.grid.SetColLabelValue(8, "Conta")
        #self.grid.GetGridColLabelWindow().GetChildren()[1].SetWindowStyleFlag(wx.ALIGN_CENTRE)
        #self.grid.GetGridColLabelWindow().GetChildren()[2].SetWindowStyleFlag(wx.ALIGN_RIGHT)
        #self.grid.GetGridColLabelWindow().GetChildren()[3].SetWindowStyleFlag(wx.ALIGN_RIGHT)

        #self.grid.Bind(wx.grid.EVT_GRID_LABEL_RIGHT_CLICK, self.on_sort_column)

        x0 = 130

        label01, self.txtId = self.criaCaixaDeTexto(self.painel, pos=(x0 + 10, 0), label='ID', tamanho = (6, 1),
                                                    max=6, multi=False )

        label02, self.txtSiglaAtivo = self.criaCaixaDeTexto(self.painel, pos=(x0 + 10, 1),
                                                    label='Ativo', tamanho = (5, 1),
                                                    max=0, multi=False )
        self.txtSiglaAtivo.Bind(wx.EVT_KILL_FOCUS, self.validaSigla)
        label0202, self.txtNomeAtivo = self.criaCaixaDeTexto(self.painel, pos=(x0 + 20, 1),
                                                    label='Nome do ativo', tamanho = (35, 1),
                                                    max=0, multi=False )
        self.txtNomeAtivo.Disable()

        label04, self.txtDataRecebimento = self.criaCaixaDeTexto(self.painel, pos=(x0 + 10, 2),
                                                           label='Recebido em', tamanho = (12, 1),
                                                           multi=False, tipodate=True)

        label105, self.txtNomeMoeda = self.criaCaixaDeTexto(self.painel, pos=(x0 + 10, 3),
                                                    label='Moeda da conta', tamanho = (15, 1),
                                                    max=0, multi=False)
        self.txtNomeMoeda.SetForegroundColour(wx.BLACK)
        self.txtNomeMoeda.SetBackgroundColour(wx.Colour(237, 237, 237))
        self.txtNomeMoeda.SetEditable(False)
        self.negrita(self.txtNomeMoeda)

        label1055, self.txtValorMoeda = self.criaCaixaDeTexto(self.painel, pos=(x0 + 10, 4),
                                                    label='Última cotação', tamanho = (15, 1),
                                                    max=0, multi=False, align='direita')
        self.txtValorMoeda.SetForegroundColour(wx.BLACK)
        self.txtValorMoeda.SetBackgroundColour(wx.Colour(237, 237, 237))
        self.txtValorMoeda.SetEditable(False)
        self.negrita(self.txtValorMoeda)

        label05, self.txtValorBruto = self.criaCaixaDeTexto(self.painel, pos=(x0 + 10, 5),
                                                    label='Valor Bruto', tamanho = (15, 1),
                                                    max=0, multi=False, tipofloat=True)

        label06, self.txtValorIr = self.criaCaixaDeTexto(self.painel, pos=(x0 + 10, 6),
                                                    label='Valor IR', tamanho = (15, 1),
                                                    max=0, multi=False, tipofloat=True)

        
        label7, self.txtLiquido = self.criaCaixaDeTexto(self.painel, pos=(x0 + 10, 7),
                                                    label='Líquido', tamanho = (15, 1),
                                                    max=0, multi=False, tipofloat=True, readonly = True)
        
        self.txtValorBruto.Bind(wx.EVT_KILL_FOCUS, self.mostraValorLiquido)
        self.txtValorIr.Bind(wx.EVT_KILL_FOCUS, self.mostraValorLiquido)

        self.txtLiquido.SetForegroundColour(wx.BLACK)
        self.txtLiquido.SetBackgroundColour(wx.Colour(237, 237, 237))
        #self.txtLiquido.SetEditable(False)

        # Opções do RadioBox
        opcoes = ["Pago", "Não Pago"]

        # Criando o RadioBox
        self.rb_Pago = wx.RadioBox(self.painel, label="Status do Pagamento", choices=opcoes, majorDimension=1,
                                     pos=(self.posx(x0+ 10), self.posy(8)), size=(200, 50), style=wx.RA_SPECIFY_ROWS)

        label07, self.cbTipoProvento = self.criaCombobox(self.painel, pos=(x0 + 10, 9), tamanho=22, label='Provento')

        # Saldo Bancário
        label885, self.txtSaldoBancario = self.criaCaixaDeTexto(self.painel, pos=(x0 + 10, 10),
                                                    label='Saldo bancário', tamanho = (15, 1),
                                                    max=0, multi=False, align='direita')
        self.txtSaldoBancario.SetForegroundColour(wx.BLACK)
        self.txtSaldoBancario.SetBackgroundColour(wx.Colour(237, 237, 237))
        self.txtSaldoBancario.SetEditable(False)

        label93, self.txtTotalProventos = self.criaCaixaDeTexto(self.painel, pos=(13, 12),
                                                    label='Total Recebido', tamanho = (15, 1),
                                                    max=0, multi=False )
        self.txtTotalProventos.SetWindowStyleFlag(wx.TE_RIGHT)

        label930, self.txtTotalPendente = self.criaCaixaDeTexto(self.painel, pos=(45, 12),
                                                    label='Total a receber', tamanho = (15, 1),
                                                    max=0, multi=False )
        self.txtTotalPendente.SetWindowStyleFlag(wx.TE_RIGHT)
        self.txtTotalProventos.Disable()
        self.txtTotalPendente.Disable()

        self.btnMostraNaoMostra = Button(self.painel, id=ID_ANY, label="Mostra todos"
                                        , pos=(self.posx(80), self.posy(12)+15),
                                        size=(self.posx(50), self.posy(1) - 30), style=0)
        self.Bind(wx.EVT_BUTTON, self.mostraNaoMostra, self.btnMostraNaoMostra)


        self.listaComponentes = [self.txtValorIr, self.txtValorBruto, self.txtDataRecebimento, self.rb_Pago,
                                 self.cbTipoProvento, self.salva_elemento]
        self.valoresDefault()
        self.dataInicial = self.today - relativedelta(months=3)

        #self.grid.Bind(wx.grid.EVT_GRID_CELL_LEFT_CLICK, self.on_left_click)
        self.grid.Bind(wx.grid.EVT_GRID_CELL_RIGHT_CLICK, self.on_right_click)
        #self.grid.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.selecionaLinha)
        #self.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.selecionaLinha, self.grid)
        #self.Bind(wx.EVT_CHAR_HOOK, self.teclaPressionada)

        self.encheComboContas()
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

    def setConta(self, idConta):
        lista = Conta.selectOneById(idConta)
        if lista:
            self.cbConta.SetSelection(self.indiceCb(self.cbConta, lista[4]))
            self.contaSelecionada(None)

    def contaSelecionada(self, event):
        nomeConta = self.cbConta.GetStringSelection()
        listaConta = None
        listaConta = Conta.selectOneByNome(nomeConta)
        self.idConta = -1
        if listaConta:
            self.idConta = listaConta[0]
            if listaConta[8] == 'REAL':
                self.txtNomeMoeda.SetValue(listaConta[8])
                self.txtValorMoeda.SetValue('')
            else:
                lista = Cotacao.getultimacotacao(listaConta[7])
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

    def validaSigla(self, event):
        novo_foco = wx.Window.FindFocus()  # Obtém o próximo elemento que recebeu foco

        # Verifica se o novo foco está na lista de componentes que precisam de validação
        if novo_foco in self.listaComponentes:
            sigla = self.txtSiglaAtivo.Value
            nomeAtivo = Ativo.devolveNomeAtivobySigla(sigla)
            if nomeAtivo == None:
                wx.MessageBox("Ativo não está cadastrado!", "Aviso")
                self.txtSiglaAtivo.SetFocus()
            else:
                self.txtNomeAtivo.SetValue(nomeAtivo)

        event.Skip()  #
        a = 2

    def valoresDefault(self):
        self.provento.clear()

        self.txtId.Clear()
        self.txtSiglaAtivo.Clear()
        self.txtDataRecebimento.SetValue(datetime.now().date())
        self.txtValorBruto.Clear()
        self.txtValorIr.Clear()
        self.cbTipoProvento.Clear()
        self.encheComboTipoProventos()
        #self.encheComboContas()

        self.disabilitaComponentes()

    def limpaElementos(self):
        self.provento.clear()

        self.txtId.Clear()
        self.txtSiglaAtivo.Clear()
        self.txtNomeAtivo.Clear()
        self.txtDataRecebimento.SetValue(datetime.now().date())
        self.txtValorBruto.Clear()
        self.txtValorIr.Clear()

    def disabilitaComponentes(self):
        self.txtId.Disable()
        self.txtSiglaAtivo.Disable()
        self.txtDataRecebimento.Disable()
        self.txtValorBruto.Disable()
        self.txtValorIr.Disable()
        self.rb_Pago.Disable()
        self.cbTipoProvento.Disable()

        self.botaoSalva.Disable()
        self.botaoDelete.Disable()

    def encheComboTipoProventos(self):
        lista = self.buscaTiposProvento()
        self.cbTipoProvento.Clear()
        for row in lista:
            self.cbTipoProvento.Append(row[1])

    def encheComboContas(self):
        lista = Conta.selectAll()
        self.cbConta.Clear()
        for row in lista:
            self.cbConta.Append(row[4])

    def buscaTiposProvento(self):
        conexao = psycopg2.connect(dbname="b3", user="postgres", password="seriate", host="localhost",
                                   port="5432")
        with conexao.cursor() as cursor:
            cursor.execute("SELECT id, nometipoprovento FROM tipoprovento order by nometipoprovento")
            lista = cursor.fetchall()
            if lista:
                return lista
            else:
                return None

    def buscaTipoProventobyNome(self, arg):
        conexao = psycopg2.connect(dbname="b3", user="postgres", password="seriate", host="localhost",
                                   port="5432")
        with conexao.cursor() as cursor:
            cursor.execute("SELECT id, nometipoprovento FROM tipoprovento WHERE upper(nometipoprovento) = upper(%s)", (arg,))
            lista = cursor.fetchall()
            if lista:
                return lista
            else:
                return None

    def buscaTipoProventobyId(self, arg):
        conexao = psycopg2.connect(dbname="b3", user="postgres", password="seriate", host="localhost", port="5432")
        with conexao.cursor() as cursor:
            cursor.execute("SELECT id, nometipoprovento FROM tipoprovento WHERE id = %s", (arg,))
            lista = cursor.fetchone()
            if lista:
                return lista
            else:
                return None

    def mostraNaoMostra(self, event):
        caption = self.btnMostraNaoMostra.GetLabel()
        if caption == 'Mostra todos':
            self.btnMostraNaoMostra.SetLabel('Mostra últimos 3 meses')
            self.montaGrid(None)
        else:
            self.btnMostraNaoMostra.SetLabel('Mostra todos')
            self.montaGrid(self.dataInicial)

    def montaGrid(self, dataInicial):
        #self.lista = self.provento.getAll()
        self.lista = Provento.buscaPorPeriodo(dataInicial, self.idConta)
        self.grid.ClearGrid()
        self.totalProventos = 0.0
        self.totalPendente = 0.0

        if self.grid.GetNumberRows() > 0:
            self.grid.DeleteRows(0, self.grid.GetNumberRows())
        linha = -1
        if self.lista:
            for row in self.lista:
                linha += 1
                if row[5]:
                    pago = 'Pago'
                    self.totalProventos += (row[3] - row[4])
                else:
                    self.grid.SetCellBackgroundColour(linha, 6, wx.Colour(176, 10, 4))
                    for col in (0, 1, 2 ,3 ,4 ,5 ,7 ,8):
                        self.grid.SetCellBackgroundColour(linha, col, wx.Colour(245, 179, 176))
                    pago = ''
                    self.totalPendente += (row[3] - row[4])

                self.grid.AppendRows()
                #conta = Conta.selectOneById(row[7])
                self.grid.SetCellValue(linha, 0, str(row[0]))
                self.grid.SetCellValue(linha, 1, row[2].strftime("%Y/%m/%d"))
                self.grid.SetCellValue(linha, 2, row[8])    #Ativo.devolveSiglaAtivo(row[1]))
                self.grid.SetCellValue(linha, 3, formata_numero(row[3]))
                self.grid.SetCellValue(linha, 4, formata_numero(row[4]))
                self.grid.SetCellValue(linha, 5, formata_numero(row[3]- row[4]))
                self.grid.SetCellValue(linha, 6, pago)
                self.grid.SetCellValue(linha, 7, row[9])     #self.buscaTipoProventobyId(row[6])[1])
                self.grid.SetCellValue(linha, 8, row[10])
                self.grid.SetCellAlignment(linha, 1, wx.ALIGN_CENTRE, wx.ALIGN_CENTRE)
                self.grid.SetCellAlignment(linha, 3, wx.ALIGN_RIGHT, wx.ALIGN_RIGHT)
                self.grid.SetCellAlignment(linha, 4, wx.ALIGN_RIGHT, wx.ALIGN_RIGHT)
                self.grid.SetCellAlignment(linha, 5, wx.ALIGN_RIGHT, wx.ALIGN_RIGHT)

        self.txtTotalProventos.SetValue(formata_numero(self.totalProventos))
        self.txtTotalPendente.SetValue(formata_numero(self.totalPendente))
        
        # Saldo bancario
        saldoBancario = Conta.getSaldoBancario(self.idConta)
        self.txtSaldoBancario.SetValue(formata_numero(saldoBancario))

    def on_left_click(self, event):
        row = event.GetRow()  # Obtém a linha clicada
        col = event.GetCol()  # Obtém a coluna clicada
        #self.empresaSelecionada(row)

    def on_right_click(self, event):
        row = event.GetRow()  # Obtém a linha clicada
        col = event.GetCol()  # Obtém a coluna clicada
        self.linhaDaGridSelecionada(row)

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

    def linhaDaGridSelecionada(self, item):
        idSelecionado = self.grid.GetCellValue(item, 0)

        if idSelecionado.isdigit():
            self.provento.selectById(idSelecionado)

            self.txtId.SetValue(str(self.provento.id))
            self.txtSiglaAtivo.SetValue(self.provento.ativo.sigla)
            #self.txtDataRecebimento.SetValue(self.provento.datarecebimento.strftime('%d/%m/%Y'))

            data_str = self.provento.datarecebimento.strftime('%d/%m/%Y')
            data_formatada = datetime.strptime(data_str, '%d/%m/%Y').date()
            self.txtDataRecebimento.SetValue(data_formatada)

            self.txtValorBruto.SetValue(str(formata_numero(self.provento.valorbruto)))
            self.txtValorIr.SetValue(str(formata_numero(self.provento.valorir)))

            self.cbTipoProvento.SetSelection(self.indiceCb(self.cbTipoProvento, self.provento.nomeprovento))
            #self.cbConta.SetSelection(self.indiceCb(self.cbConta, self.provento.conta.nomeConta))

            if self.provento.pago:
                self.rb_Pago.SetSelection(0)  # Seleciona "Pago"
            else:
                self.rb_Pago.SetSelection(1)  # Sele

            self.mostraValorLiquido(None)

            self.txtSiglaAtivo.Enable()
            self.txtDataRecebimento.Enable()
            self.txtValorBruto.Enable()
            self.txtValorIr.Enable()
            self.rb_Pago.Enable()
            self.cbTipoProvento.Enable()
            #self.cbConta.Enable()

            self.botaoSalva.Enable()
            self.botaoDelete.Enable()

            self.txtSiglaAtivo.SetFocus()

            self.insert = False

    def habilita_novo(self, event):
        self.limpaElementos()
        self.txtSiglaAtivo.Enable()
        self.txtDataRecebimento.Enable()
        self.txtValorBruto.Enable()
        self.txtValorIr.Enable()
        self.rb_Pago.Enable()
        self.cbTipoProvento.Enable()
        #self.cbConta.Enable()

        self.botaoSalva.Enable()
        self.botaoDelete.Enable()

        self.txtSiglaAtivo.SetFocus()

        self.insert = True

    def mostraValorLiquido(self, event):
        if len(self.txtValorBruto.GetValue()) <= 0: self.txtValorBruto.SetValue('0.0')
        if len(self.txtValorIr.GetValue()) <= 0: self.txtValorIr.SetValue('0.0')

        self.provento.set_valorbruto(float(str(self.txtValorBruto.GetValue()).replace(',','.')))
        self.provento.set_valorir(float(str(self.txtValorIr.GetValue()).replace(',','.')))

        liquido = self.provento.valorbruto - self.provento.valorir
        self.txtLiquido.SetValue(str(formata_numero(liquido)))

    def cancela_operacao(self, event):
        self.provento.clear()
        self.limpaElementos()
        self.disabilitaComponentes()

    def salva_elemento(self, event):
        #self.provento.set_datarecebimento(devolveDate(self.txtDataRecebimento.Value))
        self.provento.set_datarecebimento(self.txtDataRecebimento.GetValue().Format('%d/%m/%Y'))

        if len(self.txtValorBruto.GetValue()) <= 0: self.txtValorBruto.SetValue('0.0')
        if len(self.txtValorIr.GetValue()) <= 0: self.txtValorIr.SetValue('0.0')

        self.provento.set_valorbruto(float(str(self.txtValorBruto.GetValue()).replace(',','.')))
        self.provento.set_valorir(float(str(self.txtValorIr.GetValue()).replace(',','.')))
        self.provento.set_siglaativo(self.txtSiglaAtivo.GetValue())
        self.provento.set_nometipoprovento(self.cbTipoProvento.GetStringSelection())
        self.provento.set_nomeconta(self.cbConta.GetStringSelection())
        aux = self.rb_Pago.GetStringSelection()
        if aux == 'Pago': self.provento.set_pago(True)
        else: self.provento.set_pago(False)

        validado = True
        if self.provento.valorbruto <= 0: validado = False
        if self.provento.idtipoprovento < 0: validado = False
        if self.provento.idconta < 0: validado = False
        if validado:
            try:
                if self.insert is True:
                    self.provento.insert()
                    self.insert = False
                else:
                    self.provento.update()
                self.cancela_operacao(event)
                self.montaGrid(self.dataInicial)
            except  Exception as e:
                dlg = wx.MessageDialog(None, str(e), 'Erro ao salvar provento!', wx.OK | wx.ICON_ERROR)
                result = dlg.ShowModal()
        else:
            dlg = wx.MessageDialog(None, 'Verifique os valores informados!' , 'Erro ao salvar provento!', wx.OK | wx.ICON_ERROR)
            result = dlg.ShowModal()

    def deletaElemento(self, event):
        prossegueEliminacao = False
        dlg = wx.MessageDialog(None, 'Confirma a eliminação dos dados?',
                               'Prestes a eliminar definitivamente!',
                               wx.YES_NO | wx.NO_DEFAULT | wx.ICON_QUESTION)
        if dlg.ShowModal() == wx.ID_YES:
            prossegueEliminacao = True

        if prossegueEliminacao:
            self.provento.delete()
            self.cancela_operacao(event)
            self.montaGrid(self.dataInicial)

def main():
    app = wx.App()
    frmProvento = FrmProvento(1)
    app.MainLoop()


if __name__ == '__main__':
    main()
