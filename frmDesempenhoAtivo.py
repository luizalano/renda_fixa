# coding: utf-8
#from wx import Button, ID_ANY
from frm_radar import *
from frmRendaTotal import *
from frm_variacao import *
from frm_capital import *
from frm_carteira import *
from cotacao import *
#import pandas as pd
from ativo import Ativo
#from wxFrameMG import FrameMG
from diversos import *
#from ferramentas import *
#from datetime import date
#from datetime import datetime
from frm_despesa import FrmDespesa
from AwesomeCotacao import AwesomeCotacao
#from selecionaConta import SelecionaContaDialog
from selecionaBolsa import SelecionaBolsaDialog
from frm_provento import FrmProvento
#from programasSimples.ImportaRadar import *
from frm_leRadarB3 import *
from frm_negociadoNoDia import *
import psycopg2
import wx


class frmDesempenhoAtivo(FrameMG):
    insert = False
    caminho = '.\\icones\\'
    ordem = 'nome'
    escopo = 'tudo'
    totalComprado = 0.0
    totalRendimento = 0.0
    totalProventos = 0.0
    totalGeral = 0.0
    tipoProvento = 0
    proventoBruto = 0.0
    proventoIR = 0.0
    contador = 0
    idconta = -1
    nomeConta = ''
    idBolsa = -1
    nomeBolsa = None
    #dbname = 'b3teste'
    dbname = 'b3'


    def __init__(self):
        self.ativo = Ativo()
        self.frmCapital = None
        self.frmRendaTotal = None
        self.frmDespesa = None
        self.frmRadar = None
        self.frmProvento = None
        self.frmCarteira = None
        self.frmNegociadoNoDia = None
        self.frmVariacao = None
        self.leRadarB3 = None

        self.awsomeCotacao = AwesomeCotacao()
        self.awsomeCotacao.busca_dollar()
        self.awsomeCotacao.busca_euro()

        self.listaSaldoBancario = None
        self.saldoBancario = 0.0
        self.SaldoBancarioTeorico = 0.0

        super(frmDesempenhoAtivo, self).__init__(pai=None, titulo='Desempenho de ativo - CONTA NÃO DEFINIDA AINDA', lar = 1370, alt = 720,
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
        x0 = 1

        self.iconeConta = wx.Bitmap(self.caminho + 'checkbox_select_32.png')
        lb, ab = self.iconeConta.GetSize()
        self.botaoConta = wx.BitmapButton(self.painel, id=8572, bitmap=self.iconeConta,
                                         pos=(6, 12))
        self.Bind(wx.EVT_BUTTON, self.chamaDialogConta, self.botaoConta)
        self.botaoConta.SetToolTip("Seleciona a conta corrente")


        label00, self.txtAtivo = self.criaCaixaDeTexto(self.painel, pos=(x0 + 5, 0), label='Ativo', tamanho = (6, 1),
                                                    max=6, multi=False )
        self.btnOk = Button(self.painel, id=ID_ANY, label="OK"
                                      , pos=(self.posx(15), self.posy(0)+15),
                                      size=(self.posx(5), self.posy(1)-30), style=0)
        self.Bind(wx.EVT_BUTTON, self.buscaAtivo, self.btnOk)

        self.iconeBolsas = wx.Bitmap(self.caminho + 'bolsas-32.png')
        lb, ab = self.iconeBolsas.GetSize()
        self.botaoBolsas = wx.BitmapButton(self.painel, id=ID_ANY, bitmap=self.iconeBolsas,
                                         pos=(self.posx(x0 + 25), 12))
        self.Bind(wx.EVT_BUTTON, self.chamaDialogBolsas, self.botaoBolsas)
        self.botaoBolsas.SetToolTip("Seleciona a bolsa")


        #era 25 tirei 5 de tudo
        label001, self.txtDataOperacao = self.criaCaixaDeTexto(self.painel, pos=(x0 + 33, 0), label='Data operação',
                                                               tamanho = (10, 1), max=12, multi=False, tipodate = True )
        label000, self.cbOperacao = self.criaCombobox(self.painel, pos=(x0 + 47, 0), tamanho=10, label='Operação')
        self.cbOperacao.Append('1 - Compra')
        self.cbOperacao.Append('2 - Venda')

        label001, self.txtQuatidade = self.criaCaixaDeTexto(self.painel, pos=(x0+60, 0), label='Quantidade',
                                                            tamanho = (7, 1), max=8, multi=False, tipoint=True )
        label002, self.txtValor = self.criaCaixaDeTexto(self.painel, pos=(x0+70, 0), label='Valor',
                                                        tamanho = (12, 1), max=14, multi=False, tipofloat=True )

        labelee0, self.cbSimulado = self.criaCombobox(self.painel, pos=(x0 + 85, 0), tamanho=10, label='Simulado')
        self.cbSimulado.Append('1 - Simulado')
        self.cbSimulado.Append('2 - Efetivo')

        self.btnInsereOperacao = Button(self.painel, id=ID_ANY, label="Salva Operação"
                                      , pos=(self.posx(100), self.posy(0)+15),
                                      size=(self.posx(15), self.posy(1)-30), style=0)  
        self.Bind(wx.EVT_BUTTON, self.insereOperacao, self.btnInsereOperacao)

        #label3444, self.txtValorMercado = self.criaCaixaDeTexto(self.painel, pos=(x0+105, 0), label='Valor de Mercado',
        #                                                    tamanho = (15, 1), max=8, multi=False, align='direita' )

        label1095, self.txtNomeMoeda = self.criaCaixaDeTexto(self.painel, pos=(x0 + 124, 0),
                                                    label='Moeda da conta', tamanho = (10, 1),
                                                    max=0, multi=False)
        self.txtNomeMoeda.SetForegroundColour(wx.BLACK)
        self.txtNomeMoeda.SetBackgroundColour(wx.Colour(237, 237, 237))
        self.txtNomeMoeda.SetEditable(False)
        self.negrita(self.txtNomeMoeda)

        label10955, self.txtValorMoeda = self.criaCaixaDeTexto(self.painel, pos=(x0 + 137, 0),
                                                    label='Última cotação', tamanho = (10, 1),
                                                    max=0, multi=False, align='direita')
        self.txtValorMoeda.SetForegroundColour(wx.BLACK)
        self.txtValorMoeda.SetBackgroundColour(wx.Colour(237, 237, 237))
        self.txtValorMoeda.SetEditable(False)
        self.negrita(self.txtValorMoeda)

        #
        #
        #    Inicio dos bõtões de cima
        #
        self.iconeHoje = wx.Bitmap(self.caminho + 'hoje-32.png')
        lb, ab = self.iconeConta.GetSize()
        self.botaoHoje = wx.BitmapButton(self.painel, id=8571, bitmap=self.iconeHoje,
                                         pos=(1067, 12))
        self.Bind(wx.EVT_BUTTON, self.chamaNegociadoNoDia, self.botaoHoje)
        self.botaoHoje.SetToolTip("Ativos negociados na data")

        self.iconeCarteira = wx.Bitmap(self.caminho + 'wallet_32.png')
        lb, ab = self.iconeCarteira.GetSize()
        self.botaoCarteira = wx.BitmapButton(self.painel, id=8472, bitmap=self.iconeCarteira,
                                         pos=(1107, 12))
        self.Bind(wx.EVT_BUTTON, self.chamaCarteira, self.botaoCarteira)
        self.botaoCarteira.SetToolTip("Ações em carteira")

        self.iconeProvento = wx.Bitmap(self.caminho + 'money_dollar_cash_coins_32.png')
        lb, ab = self.iconeProvento.GetSize()
        self.botaoProvento = wx.BitmapButton(self.painel, id=8442, bitmap=self.iconeProvento,
                                         pos=(1147, 12))
        self.Bind(wx.EVT_BUTTON, self.chamaProventos, self.botaoProvento)
        self.botaoProvento.SetToolTip("Proventos recebidos")

        self.iconeCapital = wx.Bitmap(self.caminho + 'dinheiro_entra_32.png')
        lb, ab = self.iconeCapital.GetSize()
        self.botaoCapital = wx.BitmapButton(self.painel, id=5572, bitmap=self.iconeCapital,
                                         pos=(1187, 12))
        self.Bind(wx.EVT_BUTTON, self.chamaCapital, self.botaoCapital)
        self.botaoCapital.SetToolTip("Aumento de Capital ou retiradas")

        self.iconeDespesas = wx.Bitmap(self.caminho + 'dinheiro_sai_32.png')
        lb, ab = self.iconeDespesas.GetSize()
        self.botaoDespesas = wx.BitmapButton(self.painel, id=5552, bitmap=self.iconeDespesas,
                                         pos=(1227, 12))
        self.Bind(wx.EVT_BUTTON, self.chamaDespesas, self.botaoDespesas)
        self.botaoDespesas.SetToolTip("Registrar Despesas")

        self.iconeImporta = wx.Bitmap(self.caminho + 'importa-32.png')
        lb, ab = self.iconeImporta.GetSize()
        self.botaoImporta = wx.BitmapButton(self.painel, id=2202, bitmap=self.iconeImporta,
                                         pos=(1267, 12))
        self.Bind(wx.EVT_BUTTON, self.importaRadar, self.botaoImporta)
        self.botaoImporta.SetToolTip("Importa planiha de Radar de Proventos")

        self.iconeRadar = wx.Bitmap(self.caminho + 'radar-32.png')
        lb, ab = self.iconeRadar.GetSize()
        self.botaoRadar = wx.BitmapButton(self.painel, id=1202, bitmap=self.iconeRadar,
                                         pos=(1307, 12))
        self.Bind(wx.EVT_BUTTON, self.chamaRadar, self.botaoRadar)
        self.botaoRadar.SetToolTip("Exibe Radar de Proventos")

        # wallet_32.png
        #  Fiom dos botões de cima
        #

        label01, self.txtNegocios = self.criaCaixaDeTexto(self.painel, pos=(x0, 12), label='Negócios', tamanho=(6, 1),
                                                       max=6, multi=False)
        label02, self.txtTotalCompradoQtde = self.criaCaixaDeTexto(self.painel, pos=(x0 + 10, 12), label='Total Comprado', tamanho=(6, 1),
                                                       max=6, multi=False)
        label03, self.txtTotalCompradoValor = self.criaCaixaDeTexto(self.painel, pos=(x0 + 20, 12), label='', tamanho=(12, 1),
                                                       max=6, multi=False)
        label04, self.txtSaldoQtde = self.criaCaixaDeTexto(self.painel, pos=(x0 + 35, 12), label='Saldo do ativo', tamanho=(6, 1),
                                                       max=6, multi=False)
        label05, self.txtSaldoValor = self.criaCaixaDeTexto(self.painel, pos=(x0 + 45, 12), label='', tamanho=(12, 1),
                                                       max=6, multi=False)
        label06, self.txtResultado = self.criaCaixaDeTexto(self.painel, pos=(x0 + 60, 12), label='Resultado', tamanho=(12, 1),
                                                       max=6, multi=False)
        label07, self.txtProventos = self.criaCaixaDeTexto(self.painel, pos=(x0 + 75, 12), label='Proventos',
                                                           tamanho=(12, 1),  max=6, multi=False)
        label08, self.txtTotalGeral = self.criaCaixaDeTexto(self.painel, pos=(x0 + 90, 12), label='Total recebido',
                                                           tamanho=(12, 1),  max=6, multi=False)
        label09, self.txtResultadoGeral = self.criaCaixaDeTexto(self.painel, pos=(x0 + 105, 12), label='Renda %',
                                                           tamanho=(12, 1), max=6, multi=False)

        label10, self.txtSaldoBancario = self.criaCaixaDeTexto(self.painel, pos=(x0 + 120, 12), label='Saldo bancario',
                                                           tamanho=(12, 1), max=6, multi=False)

        labelOnze, self.txtSaldoTeorico = self.criaCaixaDeTexto(self.painel, pos=(x0 + 135, 12), label='Saldo teórico',
                                                           tamanho=(12, 1), max=6, multi=False)

        self.iconeVariacao = wx.Bitmap(self.caminho + 'stock-exchange-32.png')
        lb, ab = self.iconeVariacao.GetSize()
        self.botaoVariacao = wx.BitmapButton(self.painel, id=9902, bitmap=self.iconeVariacao,
                                         pos=(1100, 620))
        self.Bind(wx.EVT_BUTTON, self.chamaVariacao, self.botaoVariacao)
        self.botaoVariacao.SetToolTip("Grafico da variação diária de ativos")

        self.iconeRenda = wx.Bitmap(self.caminho + 'Rendimento-64.png')
        lb, ab = self.iconeRenda.GetSize()
        self.botaoRenda = wx.BitmapButton(self.painel, id=5202, bitmap=self.iconeRenda,
                                         pos=(1170, 597))
        self.Bind(wx.EVT_BUTTON, self.chamaRenda, self.botaoRenda)
        self.botaoRenda.SetToolTip("Mapa de Rendimentos")


        self.btnOk.Disable()
        self.botaoCapital.Disable()
        self.botaoDespesas.Disable()
        self.btnInsereOperacao.Disable()
        #self.btnInsereProvento.Disable()

        self.botaoSalva.Hide()
        self.botaoDelete.Hide()
        self.botaoNovo.Hide()
        self.botaoCancela.Hide()

        self.limpaElementos()

        #self.encheComboTipoProventos()
        self.grid.CreateGrid(0, 14)

        self.Show()

    def on_right_click(self, event):
        row = event.GetRow()  # Obtém a linha clicada

        menu = wx.Menu()
        self.grid.SelectRow(row)
        # Criando as opções do menu
        deleta = menu.Append(wx.ID_ANY, "&Deleta")
        efetiva = menu.Append(wx.ID_ANY, "&Efetiva")
        altera = menu.Append(wx.ID_ANY, "&Altera")

        # Vinculando funções aos itens do menu
        #self.Bind(wx.EVT_MENU, lambda evt: self.ativa_interesse(row), interesse)
        #self.Bind(wx.EVT_MENU, lambda evt: self.ativa_desinteresse(row), desinteresse)
        #self.Bind(wx.EVT_MENU, lambda evt: self.ativa_neutro(row), neutro)

        self.Bind(wx.EVT_MENU, lambda evt: self.deleta_lancamento(row), deleta)
        self.Bind(wx.EVT_MENU, lambda evt: self.efetiva_lancamento(row), efetiva)
        self.Bind(wx.EVT_MENU, lambda evt: self.altera_lancamento(row), altera)

        # Exibe o menu na posição do mouse
        self.PopupMenu(menu)
        self.grid.ClearSelection()
        menu.Destroy()  # Destrói o menu após uso

    def deleta_lancamento(self, row):
        operacao = self.grid.GetCellValue(row, 2)
        correto = ("Compra", "Venda","Compra Simulada", "Venda Simulada")
        if operacao in correto:

            self.prossegueEliminacao = False
            dlg = wx.MessageDialog(None, 'Confirma a eliminação dos dados?',
                               'Prestes a eliminar definitivamente!',
                               wx.YES_NO | wx.NO_DEFAULT | wx.ICON_QUESTION)
            if dlg.ShowModal() == wx.ID_YES:
                id = self.grid.GetCellValue(row, 0)
                self.ativo.deleteOperacao(id)
                self.buscaAtivo(1)

    def efetiva_lancamento(self, row):
        operacao = self.grid.GetCellValue(row, 2)
        correto = ("Compra Simulada", "Venda Simulada")
        if operacao in correto:

            self.prossegueEliminacao = False
            dlg = wx.MessageDialog(None, 'Confirma a fetivação do lançamento?',
                               'Efetiva um lançamento simulado!',
                               wx.YES_NO | wx.NO_DEFAULT | wx.ICON_QUESTION)
            if dlg.ShowModal() == wx.ID_YES:
                id = self.grid.GetCellValue(row, 0)
                self.ativo.efetivaLancamentoiSimulado(id)
                self.buscaAtivo(1)

    def altera_lancamento(self, row):
        contaBancaria = self.idConta
        idOperacao = self.grid.GetCellValue(row, 0)
        dataOperacao = self.grid.GetCellValue(row, 1)

        frmNegociadoNoDia = FrmNegociadoNoDia(contaBancaria = contaBancaria, idOperacao = idOperacao, dataOperacao = dataOperacao)
        #frmNegociadoNoDia.Bind(wx.EVT_CLOSE, lambda evt: self.on_close(evt, "frmNegociadoNoDia"))
        frmNegociadoNoDia.Show()

        self.buscaAtivo(1)

    #def mudaInteresse(self, interesse):
    #    conexao = psycopg2.connect(dbname=self.dbname, user="postgres", password="seriate", host="localhost",
    #                               port="5432")
    #    clausulaSql = 'update ativo set interesse = %s where sigla = upper(%s);'
    #    ativo = self.txtAtivo.GetValue()
    #
    #    try:
    #        with conexao.cursor() as cursor:
    #            cursor.execute(clausulaSql, (interesse, ativo))
    #            conexao.commit()
    #
    #    except  Exception as e:
    #        dlg = wx.MessageDialog(None, clausulaSql + '\n' + str(e), 'Erro ao alterar interesse do ativo', wx.OK | wx.ICON_ERROR)
    #        result = dlg.ShowModal()
    #
    #    conexao.close()

    def chamaDialogBolsas(self, event):
        dlg = SelecionaBolsaDialog(None)
        if dlg.ShowModal() == wx.ID_OK and dlg.selected_id:  # Retorna wx.ID_OK ao confirmar
            self.idBolsa = dlg.selected_id
            self.nomeBolsa = dlg.selected_nome

            self.SetTitle('Desempenho de ativo -  Conta ' + self.nomeConta + ' para ' + self.nomeBolsa)

        dlg.Destroy()

    def chamaDialogConta(self, event):
        dlg = SelecionaContaDialog(None)
        if dlg.ShowModal() == wx.ID_OK and dlg.selected_id:  # Retorna wx.ID_OK ao confirmar
            self.idconta = dlg.selected_id
            self.nomeConta = dlg.selected_nome

            listaConta = Conta.selectOneById(self.idconta)
            if listaConta:
                if self.nomeBolsa:
                    self.SetTitle('Desempenho de ativo -  Conta ' + self.nomeConta + ' para ' + self.nomeBolsa)
                else:
                    self.SetTitle('Desempenho de ativo -  Conta ' + self.nomeConta)

                self.idConta = listaConta[0]
                if listaConta[8] == 'REAL':
                    self.txtNomeMoeda.SetValue(listaConta[8])
                    self.txtValorMoeda.SetValue('')
                else:
                    lista = Cotacao.mc_get_ultima_cotacao(listaConta[7], self.nomeBolsa)
                    if lista:
                        self.txtNomeMoeda.SetValue(lista[1])
                        self.txtValorMoeda.SetValue(formata_numero(lista[0]))
                    else:
                        self.txtNomeMoeda.SetValue('')
                        self.txtValorMoeda.SetValue('')

                self.btnOk.Enable()
                self.botaoCapital.Enable()
                self.botaoDespesas.Enable()
                self.btnInsereOperacao.Enable()

        dlg.Destroy()

    def chamaVariacao(self, evento):
        ativo = self.txtAtivo.GetValue()
        if self.frmVariacao is None:  # Se não existir, cria uma nova janela
            self.frmVariacao = VariacaoFrm(None, ativo)
            self.frmVariacao.Bind(wx.EVT_CLOSE, lambda evt: self.on_close(evt, "frmVariacao"))
            self.frmVariacao.Show()
        else:
            if len(ativo) > 1:
                self.frmVariacao.temAtivoInicial(ativo)
            self.frmVariacao.Raise()  # Se já existir, apenas traz para frente

    def chamaNegociadoNoDia(self, evento):
        if self.frmNegociadoNoDia is None:  # Se não existir, cria uma nova janela
            self.frmNegociadoNoDia = FrmNegociadoNoDia()
            self.frmNegociadoNoDia.Bind(wx.EVT_CLOSE, lambda evt: self.on_close(evt, "frmNegociadoNoDia"))
            self.frmNegociadoNoDia.Show()
        else:
            self.frmNegociadoNoDia.Raise()  # Se já existir, apenas traz para frente

    def chamaRenda(self, evento):

        if self.frmRendaTotal is None:  # Se não existir, cria uma nova janela
            self.frmRendaTotal = FrmRendaTotal()
            self.frmRendaTotal.Bind(wx.EVT_CLOSE, lambda evt: self.on_close(evt, "frmRendaTotal"))
            self.frmRendaTotal.Show()
        else:
            self.frmRendaTotal.Raise()  # Se já existir, apenas traz para frente

    def chamaCarteira(self, evento):

        if self.frmCarteira is None:  # Se não existir, cria uma nova janela
            self.frmCarteira = FrmCarteira(self.idconta, self.nomeBolsa)
            self.frmCarteira.Bind(wx.EVT_CLOSE, lambda evt: self.on_close(evt, "frmCarteira"))
            self.frmCarteira.Show()
        else:
            self.frmCarteira.Raise()  # Se já existir, apenas traz para frente

    def chamaProventos(self, evento):

        if self.frmProvento is None:  # Se não existir, cria uma nova janela
            self.frmProvento = FrmProvento(self.idconta)
            self.frmProvento.Bind(wx.EVT_CLOSE, lambda evt: self.on_close(evt, "frmProvento"))
            self.frmProvento.Show()
        else:
            self.frmProvento.Raise()  # Se já existir, apenas traz para frente

    def on_close_Renda(self, event):
        """Garante que o objeto seja destruído ao fechar a janela."""
        self.frmCapital.Destroy()  # Destrói a janela
        self.frmCapital = None  # Libera a referência

    def on_close(self, event, frame_attr):
        """Garante que o objeto seja destruído ao fechar a janela."""
        frame = getattr(self, frame_attr, None)  # Obtém a referência ao frame
        if frame:
            frame.Destroy()  # Destrói a janela
            setattr(self, frame_attr, None)  # Define como None

    def chamaDespesas(self, evento):

        if self.frmDespesa is None:  # Se não existir, cria uma nova janela
            self.frmDespesa = FrmDespesa(self.idconta)
            self.frmDespesa.Bind(wx.EVT_CLOSE, lambda evt: self.on_close(evt, "frmDespesa"))
            self.frmDespesa.Show()
        else:
            self.frmDespesa.Raise()  # Se já existir, apenas traz para frente

    def chamaCapital(self, evento):
        self.awsomeCotacao.busca_dollar()
        self.awsomeCotacao.busca_euro()

        if self.frmCapital is None:
            self.frmCapital = FrmCapital(self.idconta)
            self.frmCapital.Bind(wx.EVT_CLOSE, lambda evt: self.on_close(evt, "frmCapital"))
            self.frmCapital.Show()
        else:
            self.frmCapital.Raise()  # Se já existir, apenas traz para frente

    def chamaRadar(self, evento):
        self.awsomeCotacao.busca_dollar()
        self.awsomeCotacao.busca_euro()

        if self.frmRadar is None:
            self.frmRadar = RadarFrm(None, title="Radar de Proventos")
            self.frmRadar.Bind(wx.EVT_CLOSE, lambda evt: self.on_close(evt, "frmRadar"))
            self.frmRadar.Show()
        else:
            self.frmRadar.Raise()  # Se já existir, apenas traz para frente

    def importaRadar(self, evento):
        if self.leRadarB3 is None:  # Se não existir, cria uma nova janela
            self.leRadarB3 = LeRadarB3()
            self.leRadarB3.Bind(wx.EVT_CLOSE, lambda evt: self.on_close(evt, "leRadarB3"))
            self.leRadarB3.Show()
        else:
            self.leRadarB3.Raise()  # Se já existir, apenas traz para frente

        #importaRadarBolsas(1)
        #dlg = wx.MessageDialog(None, 'Tudo certo', 'Radar B3 importado!', wx.OK | wx.ICON_INFORMATION)
        #result = dlg.ShowModal()

    def limpaElementos(self):

        self.ativo.clearAtivo()

        self.txtAtivo.Clear()

    def montaGrid(self, lista):
        #self.grid.CreateGrid(0, 14)
        #self.grid.ClearGrid()
        numrows = self.grid.GetNumberRows()
        if numrows >0:
            self.grid.DeleteRows(pos=0, numRows=self.grid.GetNumberRows())
        self.grid.SetColSize( 0,  60)
        self.grid.SetColSize( 1,  80)
        self.grid.SetColSize( 2, 120)
        self.grid.SetColSize( 3,  60)
        self.grid.SetColSize( 4, 100)
        self.grid.SetColSize( 5, 100)
        self.grid.SetColSize( 6, 120)
        self.grid.SetColSize( 7,  80)
        self.grid.SetColSize( 8, 100)
        self.grid.SetColSize( 9, 120)
        self.grid.SetColSize(10,  50)
        self.grid.SetColSize(11,  90)
        self.grid.SetColSize(12, 120)
        self.grid.SetColSize(13, 10)
        
        self.grid.SetColLabelValue(0, 'id')
        self.grid.SetColLabelValue(1, 'Data')
        self.grid.SetColLabelValue(2, 'Operação')
        self.grid.SetColLabelValue(3, 'Qtde')
        self.grid.SetColLabelValue(4, 'Compra')
        self.grid.SetColLabelValue(5, 'Venda')
        self.grid.SetColLabelValue(6, 'Total Operação')
        self.grid.SetColLabelValue(7, 'Saldo')
        self.grid.SetColLabelValue(8, 'Preço médio')
        self.grid.SetColLabelValue(9, 'Resultado')
        self.grid.SetColLabelValue(10, 'Ganho')
        self.grid.SetColLabelValue(11, 'Provento')
        self.grid.SetColLabelValue(12, 'R$')
        self.grid.SetColLabelValue(13, 'x')
        self.grid.HideCol(13)

        self.lista = lista

        saldoQtde = 0
        saldoValor = 0.0
        totalCompradoQtde = 0
        self.totalComprado = 0.0
        self.totalResultado = 0.0
        self.totalRendimento = 0,0
        self.totalProventos = 0.0
        resultado = 0.0
        precomedio = 0.0
        negocios = 0
        linha = 0
        self.contador = 0

        for  row in self.lista:
            negocios +=1
            dataOperacao = devolveDateStr(row[1])
            numoperacao = devolveInteger(row[2])
            operacao =''
            valorOperacao = devolveFloat(row[4])
            qtdeOperacao = devolveInteger(row[3])
            valorCompraStr = ''
            valorVendaStr = ''
            ganho = 0.0
            strGanho = ""
            strResultado = ''
            simulado = row[5]
            self.txtProventos.SetValue('')
            self.txtTotalGeral.SetValue('')
            self.txtResultadoGeral.SetValue('')

            if numoperacao == 1:
                operacao = 'Compra'
                if simulado: operacao = 'Compra Simulada'
                valorCompraStr = formata_numero(valorOperacao)
                totalOperacao = qtdeOperacao * valorOperacao
                totalCompradoQtde += qtdeOperacao
                self.totalComprado += totalOperacao
                if precomedio == 0:
                    precomedio = valorOperacao
                else:
                    precomedio = ((precomedio * saldoQtde) + totalOperacao) / (saldoQtde + qtdeOperacao)
                saldoQtde += qtdeOperacao

            else:
                operacao = 'Venda'
                if simulado: operacao = 'Venda Simulada'
                valorVendaStr = formata_numero(valorOperacao)
                totalOperacao = valorOperacao * qtdeOperacao
                resultado = totalOperacao - (qtdeOperacao * precomedio)
                ganho = resultado / (qtdeOperacao * precomedio)
                ganho = ganho * 100.0
                strGanho = formata_numero(ganho) +  ' %'
                self.totalResultado += resultado
                saldoQtde -= qtdeOperacao
                strResultado = formata_numero(resultado)
                if saldoQtde == 0:
                    precomedio = 0.0

            linha = self.contador
            self.grid.AppendRows()
            self.grid.SetCellValue(linha,  0, str(row[0]))
            self.grid.SetCellValue(linha,  1, dataOperacao)
            self.grid.SetCellValue(linha,  2, operacao)
            self.grid.SetCellValue(linha,  3, str(qtdeOperacao))
            self.grid.SetCellValue(linha,  4, valorCompraStr)
            self.grid.SetCellValue(linha,  5, valorVendaStr)
            self.grid.SetCellValue(linha,  6, formata_numero(totalOperacao))
            self.grid.SetCellValue(linha,  7, str(saldoQtde))
            self.grid.SetCellValue(linha,  8, formata_numero(precomedio))
            self.grid.SetCellValue(linha,  9, strResultado)
            self.grid.SetCellValue(linha, 10, strGanho)
            self.grid.SetCellValue(linha, 11, '--------')
            self.grid.SetCellValue(linha, 12, '----------')
            self.grid.SetCellValue(linha, 13, str(self.contador))
            self.contador += 1

        saldoValor = precomedio * saldoQtde
        self.txtNegocios.SetValue(str(negocios))
        self.txtTotalCompradoQtde.SetValue(str(totalCompradoQtde))
        self.txtTotalCompradoValor.SetValue(formata_numero(self.totalComprado))
        self.txtSaldoQtde.SetValue(str(saldoQtde))
        self.txtSaldoValor.SetValue(formata_numero(saldoValor))
        self.txtResultado.SetValue(formata_numero(self.totalResultado))

    def gridProventos(self, lista):

        self.totalProventos = 0.0
        resultado = 0.0

        for row in lista:
            dataOperacao = devolveDateStr(row[1])
            valorOperacao = devolveFloat(row[2])
            foiPago = row[4]
            tipoProvento = row[3]
            linha = self.contador
            self.grid.AppendRows()
            self.grid.SetCellValue(linha,  0, str(row[0]))
            self.grid.SetCellValue(linha,  1, dataOperacao)
            if foiPago:
                self.grid.SetCellValue(linha,  2, 'PROVENTOS')
                self.grid.SetCellValue(linha,  9, '----------')
            else:
                self.grid.SetCellValue(linha,  2, 'PREVISÃO')
                self.grid.SetCellValue(linha,  9, 'PREVISÃO')
            self.grid.SetCellValue(linha,  3, '----------')
            self.grid.SetCellValue(linha,  4, '----------')
            self.grid.SetCellValue(linha,  5, '----------')
            self.grid.SetCellValue(linha,  6, '----------')
            self.grid.SetCellValue(linha,  7, '----------')
            self.grid.SetCellValue(linha,  8, '----------')
            self.grid.SetCellValue(linha, 10, '----------')
            self.grid.SetCellValue(linha, 11, tipoProvento)
            self.grid.SetCellValue(linha, 12, formata_numero(valorOperacao))
            self.grid.SetCellValue(linha, 13, str(self.contador))
            self.contador += 1
            if foiPago: self.totalProventos += valorOperacao

        self.totalGeral = self.totalProventos + self.totalResultado
        if self.totalComprado != 0:
            self.totalRendimento = (self.totalGeral / self.totalComprado) * 100
        else:
            self.totalRendimento = 0.0
        self.txtProventos.SetValue(formata_numero(self.totalProventos))
        self.txtTotalGeral.SetValue(formata_numero(self.totalGeral))
        self.txtResultadoGeral.SetValue(formata_numero(self.totalRendimento) + ' %')

    def gridRadar(self, lista):

        for row in lista:
            dataOperacao = devolveDateStr(row[1])
            dataProvavel = devolveDateStr(row[2])
            valorprovento = devolveFloat(row[5])
            dy = devolveFloat(row[4])
            tipoProvento = row[3]
            linha = self.contador
            self.grid.AppendRows()
            self.grid.SetCellValue(linha, 0, str(row[0]))
            self.grid.SetCellValue(linha, 1, dataOperacao)
            self.grid.SetCellValue(linha, 2, 'PGTO -> ' + dataProvavel)
            self.grid.SetCellValue(linha, 3, 'RADAR')
            self.grid.SetCellValue(linha, 4, 'RADAR')
            self.grid.SetCellValue(linha, 5, 'RADAR')
            self.grid.SetCellValue(linha, 6, 'RADAR')
            self.grid.SetCellValue(linha, 7, '  POR AÇÃO')
            self.grid.SetCellValue(linha, 8, formata_numero_6(valorprovento))
            self.grid.SetCellValue(linha, 9, 'RADAR')
            self.grid.SetCellValue(linha, 10, 'RADAR')
            self.grid.SetCellValue(linha, 11, tipoProvento)
            self.grid.SetCellValue(linha, 12, 'DY = ' + formata_numero(dy))
            self.grid.SetCellValue(linha, 13, str(self.contador))
            self.contador += 1

    def ordenarGrid(self):
        dados = []

        self.grid.ForceRefresh()  # Atualiza a grid para aplicar as mudanças
        # Percorre as linhas para coletar os dados
        for linha in range(self.grid.GetNumberRows()):
            data_str = self.grid.GetCellValue(linha, 1)  # Coluna Data
            col_x = int(self.grid.GetCellValue(linha, 13))  # Coluna x

            try:
                data = datetime.strptime(data_str, "%d/%m/%Y")  # Converte data para datetime
            except ValueError:
                data = datetime.min  # Se der erro, coloca uma data mínima

            linha_dados = [self.grid.GetCellValue(linha, col) for col in range(self.grid.GetNumberCols())]
            dados.append((data, col_x, linha_dados))

        # Ordena pelos critérios: primeiro por Data e depois por X
        dados.sort(key=lambda x: (x[0], x[1]))

        # Limpa a grid atual
        self.grid.ClearGrid()

        # Reescreve os dados na grid na ordem correta
        for i, (_, _, linha_dados) in enumerate(dados):
            for col, valor in enumerate(linha_dados):
                self.grid.SetCellValue(i, col, valor)

        fonte = self.grid.GetDefaultCellFont()
        fonte_negrito = fonte.Bold()

        for linha in range(self.grid.GetNumberRows()):
            #elf.grid.SetCellBackgroundColour(linha, coluna, wx.BLACK)  # Fundo preto

            valor = devolveFloat(self.grid.GetCellValue(linha, 9))
            operacao = self.grid.GetCellValue(linha, 2)
            temradar = self.grid.GetCellValue(linha, 3)
            if operacao == 'PROVENTOS':
                for i in range(13):
                    self.grid.SetCellBackgroundColour(linha, i, cor_azulzinho)#wx.Colour(230,255,255))
            if operacao == 'PREVISÃO':
                for i in range(13):
                    self.grid.SetCellBackgroundColour(linha, i, cor_rosinha)#wx.Colour(255,191,181))
            if temradar == 'RADAR':
                for i in range(13):
                    self.grid.SetCellBackgroundColour(linha, i, cor_verdinho)
                self.grid.SetCellFont(linha,  8, fonte_negrito)
                self.grid.SetCellFont(linha, 12, fonte_negrito)
            if valor < 0 :
                self.grid.SetCellTextColour(linha,  9, wx.RED)
                self.grid.SetCellTextColour(linha, 10, wx.RED)
            self.grid.SetCellAlignment(linha,  1, wx.ALIGN_CENTRE, wx.ALIGN_CENTRE)
            self.grid.SetCellAlignment(linha, 10, wx.ALIGN_CENTRE, wx.ALIGN_CENTRE)
            self.grid.SetCellAlignment(linha,  3, wx.ALIGN_RIGHT, wx.ALIGN_RIGHT)
            self.grid.SetCellAlignment(linha,  4, wx.ALIGN_RIGHT, wx.ALIGN_RIGHT)
            self.grid.SetCellAlignment(linha,  5, wx.ALIGN_RIGHT, wx.ALIGN_RIGHT)
            self.grid.SetCellAlignment(linha,  6, wx.ALIGN_RIGHT, wx.ALIGN_RIGHT)
            self.grid.SetCellAlignment(linha,  7, wx.ALIGN_RIGHT, wx.ALIGN_RIGHT)
            self.grid.SetCellAlignment(linha,  8, wx.ALIGN_RIGHT, wx.ALIGN_RIGHT)
            self.grid.SetCellAlignment(linha,  9, wx.ALIGN_RIGHT, wx.ALIGN_RIGHT)
            self.grid.SetCellAlignment(linha, 12, wx.ALIGN_RIGHT, wx.ALIGN_RIGHT)
        self.grid.ForceRefresh()

        if self.grid.GetNumberRows() == 0:
            self.grid.AppendRows()
            self.grid.SetCellValue(0, 0, "Vazio")

        #if self.listaSaldoBancario:
        #    self.txtSaldoBancario.SetValue(formata_numero(self.listaSaldoBancario[5]))
        self.txtSaldoBancario.SetValue(formata_numero(self.saldoBancario))
        self.txtSaldoTeorico.SetValue(formata_numero(self.saldoBancarioTeorico))

    def strOrNone(self, arg):
        if arg is None:
            return ''
        else:
            return arg

    def buscaAtivo(self, item):
        siglaAtivo = self.txtAtivo.Value
        
        if len(siglaAtivo) > 0:
            self.ativo.populaAtivoBySigla(siglaAtivo) #, self.idconta)

            if self.ativo.getid_ativo() > 0:
                #valorMercado = Ativo.get_valor_mercado_yfinance(siglaAtivo, self.nomeBolsa)
                #self.txtValorMercado.SetValue(formata_numero(valorMercado))
                self.ativo.setlan(self.idconta)
                self.ativo.buscaProventos(self.idconta, False)
                #self.listaSaldoBancario = self.selectSaldoBancario()
                self.saldoBancario = Conta.getSaldoBancario(self.idconta)
                self.saldoBancarioTeorico = Conta.getSaldoBancarioTeorico(self.idconta)
                #self.ativo.buscaProventos()
                self.montaGrid(self.ativo.lan)
                self.gridProventos(self.ativo.proventos)
                self.gridRadar(self.ativo.buscarRadar(siglaAtivo))
                self.ordenarGrid()
            else:
                dlg = wx.MessageDialog(None, 'Não foi encontrado o ativo indicado!', 'Erro no Ativo!', wx.OK | wx.ICON_ERROR)
                result = dlg.ShowModal()


    def selectSaldoBancario(self):
        conexao = psycopg2.connect(dbname=self.dbname, user="postgres", password="seriate", host="localhost",
                                   port="5432")
        with conexao.cursor() as cursor:
            clausulaSql = 'WITH valores AS (    ' \
                          'SELECT ' \
                             '(SELECT COALESCE(SUM(valorbruto) - SUM(valorir), 0) FROM proventos WHERE pago = TRUE) AS proventos, ' \
                             '(SELECT COALESCE(SUM(valor), 0) FROM despesas) AS despesas, '\
                             '(SELECT COALESCE(SUM(valor), 0) FROM capital) AS aportes '\
                           '), ' \
                          'transacoes AS ( ' \
                          'SELECT ' \
                             'COALESCE(SUM(CASE WHEN operacao = 1 THEN valoroperacao * qtdeoperacao ELSE 0 END), 0) AS compras, ' \
                             'COALESCE(SUM(CASE WHEN operacao = 2 THEN valoroperacao * qtdeoperacao ELSE 0 END), 0) AS vendas ' \
                          'FROM ativonegociado ' \
                          ') ' \
                          'SELECT ' \
                             ' v.proventos, v.despesas, v.aportes, t.compras, t.vendas, ' \
                             '(v.proventos - v.despesas + v.aportes - t.compras + t.vendas) AS saldo ' \
                          'FROM valores v, transacoes t;'

            cursor.execute(clausulaSql)
            lista = cursor.fetchone()
            if lista:
                return lista
            else:
                return None

    def insereOperacao(self, item):
        avanca = True
        operacao = 0
        quantidade = 0
        valor = 0.0
        dataOperacao = self.txtDataOperacao.GetValue().Format('%d/%m/%Y')
        #self.despesas.setdata_lancamento(self.txtDataLancamento.GetValue().)Format('%d/%m/%Y')
        siglaAtivo = self.txtAtivo.GetValue()
        simulacao = False

        avanca = self.ativo.existeAtivo(siglaAtivo)
        if avanca:
            operacao = self.cbOperacao.GetSelection() + 1
            if operacao < 1 or operacao > 2:
                avanca = False
            quantidade = int(self.txtQuatidade.GetValue())
            if quantidade <= 0:
                avanca = False
            valor_str = str(self.txtValor.GetValue())
            valor = devolveFloat(valor_str.replace('.',','))
            if valor <= 0:
                avanca = False
           
            sim = self.cbSimulado.GetSelection()
            if sim == 0:
                simulacao = True

        if avanca:
            if self.ativo.insereOperacao(siglaAtivo, dataOperacao, operacao, valor, quantidade, self.idconta, simulado=simulacao) == True:
                self.txtQuatidade.SetValue('')
                self.txtValor.SetValue('')
                self.buscaAtivo(item)


def main():
    app = wx.App()
    desempenhoAtivo = frmDesempenhoAtivo()
    app.MainLoop()


if __name__ == '__main__':
    main()
