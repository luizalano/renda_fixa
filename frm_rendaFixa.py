# coding: utf-8
from diversos import *
from wx import *
from rendafixa import RendaFixa
from conta import Conta
from titulorendafixa import TituloRendaFixa
from frm_tituloRendaFixa import FrmTituloRendaFixa
import wx.grid
from wxFrameMG import FrameMG


class frmRendaFixa(FrameMG):
    insert = False
    caminho = '.\\icones\\'
    id_conta = -1
    nome_conta = ''
    id_titulo_renda_fixa = -1
    nome_titulo_renda_fixa = ''

    def __init__(self):
        self.id_conta = None
        self.id_titulo_renda_fixa = None
        self.nome_conta = ''
        self.nome_titulo_renda_fixa = ''

        self.lista_saldo_bancario = None
        self.saldo_bancario = zero
        self.saldo_bancario_teorico = zero

        self.rendaFixa = RendaFixa()
        self.frmTituloRendaFixa = None

        super(frmRendaFixa, self).__init__(pai=None, titulo='Renda Fixa - Desempenho de ativo - CONTA NÃO DEFINIDA AINDA', lar = 1370, alt = 720,
                                         xibot = 650, split=False)

        self.criaComponentes()

    def criaComponentes(self):
        X = self.posx(1)
        Y = self.posy(1) + 15
        tamX = self.larguraEmPx(185)
        tamY = self.alturaEmPx(13)

        self.setAvancoVertical(8)

        """
        self.grid = wx.ListCtrl(self.painel, pos=(X, Y), size=(tamX, tamY),
                                style=wx.LC_REPORT | wx.LC_VRULES | wx.LC_HRULES | wx.BORDER_SUNKEN)
        """
        self.grid = wx.grid.Grid(self.painel, pos=(X, Y), size=(tamX, tamY))
        self.grid.Bind(wx.grid.EVT_GRID_CELL_RIGHT_CLICK, self.on_right_click)

        label01, self.cbConta = self.criaCombobox(self.painel, pos=(1, 0), tamanho=22, label='Conta corrente')
        self.cbConta.Bind(wx.EVT_COMBOBOX, self.conta_selecionada)
        self.cbConta.SetToolTip("Seleciona a conta corrente")

        label02, self.cbTitulo = self.criaCombobox(self.painel, pos=(27, 0), tamanho=30, label='Nome do título')
        self.cbTitulo.Bind(wx.EVT_COMBOBOX, self.titulo_selecionado)
        self.cbTitulo.SetToolTip("Seleciona o título de renda fixa")

        self.btnEditaTitulos = Button(self.painel, id=ID_ANY, label="..."
                                      , pos=(self.posx(59), self.posy(0)+15),
                                      size=(self.posx(2), self.posy(1)-30), style=0)
        self.Bind(wx.EVT_BUTTON, self.chama_frm_tituloRendaFixa, self.btnEditaTitulos)

        label03, self.txtDataOperacao = self.criaCaixaDeTexto(self.painel, pos=(64, 0), label='Data operação',
                                                               tamanho = (10, 1), max=12, multi=False, tipodate = True )
        
        label04, self.cbOperacao = self.criaCombobox(self.painel, pos=(78, 0), tamanho=10, label='Operação')
        self.cbOperacao.Append('1 - Entrada')
        self.cbOperacao.Append('2 - Saída')

        label05, self.txtValor = self.criaCaixaDeTexto(self.painel, pos=(92, 0), label='Valor',
                                                        tamanho = (12, 1), max=14, multi=False, tipofloat=True )

        label06, self.cbAlteraSaldo = self.criaCombobox(self.painel, pos=(107, 0), tamanho=10, label='Saldo')
        self.cbAlteraSaldo.Append('0 - Não altera')
        self.cbAlteraSaldo.Append('1 - Altera')

        label07, self.txtDescricao = self.criaCaixaDeTexto(self.painel, pos=(121, 0), label='Descrição',
                                                               tamanho = (50, 1), max=100, multi=False)
        

        self.btnInsereOperacao = Button(self.painel, id=ID_ANY, label="Salva Operação"
                                      , pos=(self.posx(175), self.posy(0)+15),
                                      size=(self.posx(13), self.posy(1)-30), style=0)  
        #self.Bind(wx.EVT_BUTTON, self.insere_operacao, self.btnInsereOperacao)

        
        self.botaoSalva.Hide()
        self.botaoDelete.Hide()
        self.botaoNovo.Hide()
        self.botaoCancela.Hide()

        self.limpaElementos()
        self.enche_combo_contas()
        self.enche_combo_titulos()

        self.grid.CreateGrid(0, 14)

        self.Show()

    def enche_combo_contas(self):
        lista = Conta.mc_select_all()
        self.cbConta.Clear()
        for row in lista:
            self.cbConta.Append(row[4])

    def enche_combo_titulos(self):
        lista = TituloRendaFixa.mc_select_all()
        self.cbTitulo.Clear()
        for row in lista:
            self.cbTitulo.Append(row[1])

    def conta_selecionada(self, event):
        nomeConta = self.cbConta.GetStringSelection()
        listaConta = None
        listaConta = Conta.mc_select_one_by_nome(nomeConta)
        self.id_conta = -1
        self.nome_conta = ''
        if listaConta:
            self.id_conta = listaConta[0]
            self.nome_conta = listaConta[4]
            self.id_titulo_renda_fixa

    def titulo_selecionado(self, event):
        nomeTitulo = self.cbTitulo.GetStringSelection()
        listaTitulo = None
        listaTitulo = TituloRendaFixa.mc_select_one_by_nome(nomeTitulo)
        self.id_titulo_renda_fixa = -1
        self.nome_titulo = ''
        if listaTitulo:
            self.id_titulo_renda_fixa = listaTitulo[0]
            self.nome_titulo = listaTitulo[1]

    def on_right_click(self, event):
        row = event.GetRow()  # Obtém a linha clicada

        menu = wx.Menu()
        self.grid.SelectRow(row)
        # Criando as opções do menu
        deleta = menu.Append(wx.ID_ANY, "&Deleta")
        altera = menu.Append(wx.ID_ANY, "&Altera")

        self.Bind(wx.EVT_MENU, lambda evt: self.deleta_lancamento(row), deleta)
        self.Bind(wx.EVT_MENU, lambda evt: self.altera_lancamento(row), altera)

        # Exibe o menu na posição do mouse
        self.PopupMenu(menu)
        self.grid.ClearSelection()
        menu.Destroy()  # Destrói o menu após uso

    def deleta_lancamento(self, row):
        id = self.grid.GetCellValue(row, 0)
        if self.rendaFixa.select_by_id(id):
            self.prossegueEliminacao = False
            dlg = wx.MessageDialog(None, 'Confirma a eliminação dos dados?',
                               'Prestes a eliminar definitivamente!',
                               wx.YES_NO | wx.NO_DEFAULT | wx.ICON_QUESTION)
            if dlg.ShowModal() == wx.ID_YES:
                id = self.grid.GetCellValue(row, 0)
                self.rendaFixa.delete()
                self.busca_ativo(1)

    def altera_lancamento(self, row):
        #contaBancaria = self.id_conta
        #idOperacao = self.grid.GetCellValue(row, 0)
        #dataOperacao = self.grid.GetCellValue(row, 1)#

        #frmNegociadoNoDia = FrmNegociadoNoDia(contaBancaria = contaBancaria, idOperacao = idOperacao, dataOperacao = dataOperacao)
        #frmNegociadoNoDia.Show()

        #self.busca_ativo(1)
        a = 0

    def chama_frm_tituloRendaFixa(self, evento):
        if self.frmTituloRendaFixa is None:  # Se não existir, cria uma nova janela
            self.frmTituloRendaFixa = FrmTituloRendaFixa()
            self.frmTituloRendaFixa.Bind(wx.EVT_CLOSE, lambda evt: self.on_close(evt, "frmTituloRendaFixa"))
            self.frmTituloRendaFixa.Show()
        else:
            self.frmTituloRendaFixa.temAtivoInicial()
            self.frmTituloRendaFixa.Raise()  # Se já existir, apenas traz para frente

    def on_close(self, event, frame_attr):
        """Garante que o objeto seja destruído ao fechar a janela."""
        self.enche_combo_titulos()
        frame = getattr(self, frame_attr, None)  # Obtém a referência ao frame
        if frame:
            frame.Destroy()  # Destrói a janela
            setattr(self, frame_attr, None)  # Define como None

    def limpaElementos(self):
        a = 0
        # daqui para baixo


def main():
    app = wx.App()
    objeto = frmRendaFixa()
    app.MainLoop()


if __name__ == '__main__':
    main()
