# coding: utf-8
from frm_notaNegociacao import FrmNotaNegociacao
from frm_radar import *
from frm_rendaTotal import *
from frm_variacao import *
from frm_capital import *
from frm_carteira import *
from frm_rendaFixa import *
from cotacao import *
from ativo import Ativo
from diversos import *
from frm_despesa import FrmDespesa
from AwesomeCotacao import AwesomeCotacao
from selecionaBolsa import SelecionaBolsaDialog
from frm_provento import FrmProvento
from frm_leRadarB3 import *
from frm_negociadoNoDia import *
import psycopg2
import wx


class frmDesempenhoAtivo(FrameMG):
    insert = False
    caminho = '.\\icones\\'
    ordem = 'nome'
    escopo = 'tudo'
    totalComprado = Decimal('0.0')
    totalRendimento = Decimal('0.0')
    totalProventos = Decimal('0.0')
    totalGeral = Decimal('0.0')
    tipoProvento = 0
    proventoBruto =Decimal('0.0')
    proventoIR = Decimal('0.0')
    contador = 0
    idConta = -1
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
        self.frmRendaFixa = None
        self.frmNotaNegociacao = None

        self.idBolsa = None
        self.idConta = None

        self.awsomeCotacao = AwesomeCotacao()
        self.awsomeCotacao.busca_dollar()
        self.awsomeCotacao.busca_euro()

        self.listaSaldoBancario = None
        self.saldoBancario = 0.0
        self.SaldoBancarioTeorico = 0.0

        super(frmDesempenhoAtivo, self).__init__(pai=None, titulo='Renda Fixa - Desempenho de ativo - CONTA NÃO DEFINIDA AINDA', lar = 1370, alt = 720,
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
        self.botaoConta = wx.BitmapButton(self.painel, id=3556, bitmap=self.iconeConta,
                                         pos=(6, 12))
        self.Bind(wx.EVT_BUTTON, self.chama_Dialog_conta, self.botaoConta)
        self.botaoConta.SetToolTip("Seleciona a conta corrente")


        label00, self.txtAtivo = self.criaCaixaDeTexto(self.painel, pos=(x0 + 5, 0), label='Ativo', tamanho = (6, 1),
                                                    max=6, multi=False )
        self.btnOk = Button(self.painel, id=ID_ANY, label="OK"
                                      , pos=(self.posx(15), self.posy(0)+15),
                                      size=(self.posx(5), self.posy(1)-30), style=0)
        self.Bind(wx.EVT_BUTTON, self.busca_ativo, self.btnOk)

        self.iconeBolsas = wx.Bitmap(self.caminho + 'bolsas-32.png')
        lb, ab = self.iconeBolsas.GetSize()
        self.botaoBolsas = wx.BitmapButton(self.painel, id=ID_ANY, bitmap=self.iconeBolsas,
                                         pos=(self.posx(x0 + 25), 12))
        self.Bind(wx.EVT_BUTTON, self.chama_Dialog_bolsas, self.botaoBolsas)
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
        self.Bind(wx.EVT_BUTTON, self.insere_operacao, self.btnInsereOperacao)

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
        self.Bind(wx.EVT_BUTTON, self.chama_frmnegociadoNoDiaNoDia, self.botaoHoje)
        self.botaoHoje.SetToolTip("Ativos negociados na data")

        self.iconeCarteira = wx.Bitmap(self.caminho + 'wallet_32.png')
        lb, ab = self.iconeCarteira.GetSize()
        self.botaoCarteira = wx.BitmapButton(self.painel, id=8472, bitmap=self.iconeCarteira,
                                         pos=(1107, 12))
        self.Bind(wx.EVT_BUTTON, self.chama_frmcarteira, self.botaoCarteira)
        self.botaoCarteira.SetToolTip("Ações em carteira")

        self.iconeProvento = wx.Bitmap(self.caminho + 'money_dollar_cash_coins_32.png')
        lb, ab = self.iconeProvento.GetSize()
        self.botaoProvento = wx.BitmapButton(self.painel, id=8442, bitmap=self.iconeProvento,
                                         pos=(1147, 12))
        self.Bind(wx.EVT_BUTTON, self.chama_frmproventos, self.botaoProvento)
        self.botaoProvento.SetToolTip("Proventos recebidos")

        self.iconeCapital = wx.Bitmap(self.caminho + 'dinheiro_entra_32.png')
        lb, ab = self.iconeCapital.GetSize()
        self.botaoCapital = wx.BitmapButton(self.painel, id=5572, bitmap=self.iconeCapital,
                                         pos=(1187, 12))
        self.Bind(wx.EVT_BUTTON, self.chama_frmcapital, self.botaoCapital)
        self.botaoCapital.SetToolTip("Aumento de Capital ou retiradas")

        self.iconeDespesas = wx.Bitmap(self.caminho + 'dinheiro_sai_32.png')
        lb, ab = self.iconeDespesas.GetSize()
        self.botaoDespesas = wx.BitmapButton(self.painel, id=5552, bitmap=self.iconeDespesas,
                                         pos=(1227, 12))
        self.Bind(wx.EVT_BUTTON, self.chama_frmdespesas, self.botaoDespesas)
        self.botaoDespesas.SetToolTip("Registrar Despesas")

        self.iconeImporta = wx.Bitmap(self.caminho + 'importa-32.png')
        lb, ab = self.iconeImporta.GetSize()
        self.botaoImporta = wx.BitmapButton(self.painel, id=2202, bitmap=self.iconeImporta,
                                         pos=(1267, 12))
        self.Bind(wx.EVT_BUTTON, self.chama_frmleRadarB3, self.botaoImporta)
        self.botaoImporta.SetToolTip("Importa planiha de Radar de Proventos")

        self.iconeRadar = wx.Bitmap(self.caminho + 'radar-32.png')
        lb, ab = self.iconeRadar.GetSize()
        self.botaoRadar = wx.BitmapButton(self.painel, id=1202, bitmap=self.iconeRadar,
                                         pos=(1307, 12))
        self.Bind(wx.EVT_BUTTON, self.chama_frmradar, self.botaoRadar)
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

        self.iconeRendaFixa = wx.Bitmap(self.caminho + 'Cofre-32x32.png')
        lb, ab = self.iconeRendaFixa.GetSize()
        self.botaoRendaFixa = wx.BitmapButton(self.painel, id=132, bitmap=self.iconeRendaFixa, pos=(1100, 595))
        self.Bind(wx.EVT_BUTTON, self.chama_frmRendaFixa, self.botaoRendaFixa)
        self.botaoRendaFixa.SetToolTip("Renda Fixa")

        self.iconeNota = wx.Bitmap(self.caminho + 'invoice32.png')
        lb, ab = self.iconeNota.GetSize()
        self.botaoNota = wx.BitmapButton(self.painel, id=8572, bitmap=self.iconeNota, pos=(1150, 597))
        self.Bind(wx.EVT_BUTTON, self.chamaNota, self.botaoNota)
        self.botaoNota.SetToolTip("Confere as notas de negociação")

        self.iconeVariacao = wx.Bitmap(self.caminho + 'stock-exchange-32.png')
        lb, ab = self.iconeVariacao.GetSize()
        self.botaoVariacao = wx.BitmapButton(self.painel, id=9902, bitmap=self.iconeVariacao, pos=(1150, 640))
        self.Bind(wx.EVT_BUTTON, self.chama_frmvariacao, self.botaoVariacao)
        self.botaoVariacao.SetToolTip("Grafico da variação diária de ativos")

        self.iconeRenda = wx.Bitmap(self.caminho + 'Rendimento-64.png')
        lb, ab = self.iconeRenda.GetSize()
        self.botaoRenda = wx.BitmapButton(self.painel, id=5202, bitmap=self.iconeRenda, pos=(1200, 597))
        self.Bind(wx.EVT_BUTTON, self.chama_frmrRendaTotal, self.botaoRenda)
        self.botaoRenda.SetToolTip("Mapa de Rendimentos")

        self.botaoSalva.Hide()
        self.botaoDelete.Hide()
        self.botaoNovo.Hide()
        self.botaoCancela.Hide()

        self.limpaElementos()

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
                self.busca_ativo(1)

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
                self.ativo.efetiva_lancamento_simulado(id)
                self.busca_ativo(1)

    def altera_lancamento(self, row):
        contaBancaria = self.idConta
        idOperacao = self.grid.GetCellValue(row, 0)
        dataOperacao = self.grid.GetCellValue(row, 1)

        frmNegociadoNoDia = FrmNegociadoNoDia(contaBancaria = contaBancaria, idOperacao = idOperacao, dataOperacao = dataOperacao)
        frmNegociadoNoDia.Show()

        self.busca_ativo(1)

    def chama_Dialog_bolsas(self, event):
        dlg = SelecionaBolsaDialog(None)
        if dlg.ShowModal() == wx.ID_OK and dlg.selected_id:  # Retorna wx.ID_OK ao confirmar
            self.idBolsa = dlg.selected_id
            self.nomeBolsa = dlg.selected_nome

            self.SetTitle('Renda Fixa - Desempenho de ativo -  Conta ' + self.nomeConta + ' para ' + self.nomeBolsa)

        dlg.Destroy()

    def chama_Dialog_conta(self, event):
        dlg = SelecionaContaDialog(None)
        if dlg.ShowModal() == wx.ID_OK and dlg.selected_id:  # Retorna wx.ID_OK ao confirmar
            idConta = dlg.selected_id
            self.nomeConta = dlg.selected_nome

            listaConta = Conta.mc_select_one_by_id(idConta)
            if listaConta:
                if self.nomeBolsa:
                    self.SetTitle('Renda Fixa - Desempenho de ativo -  Conta ' + self.nomeConta + ' para ' + self.nomeBolsa)
                else:
                    self.SetTitle('Renda Fixa - Desempenho de ativo -  Conta ' + self.nomeConta)

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

        dlg.Destroy()

    def chamaNota(self, evento):
        if self.frmNotaNegociacao is None:  # Se não existir, cria uma nova janela
            self.frmNotaNegociacao = FrmNotaNegociacao()
            self.frmNotaNegociacao.Bind(wx.EVT_CLOSE, lambda evt: self.on_close(evt, "frmNotaNegociacao"))
            self.frmNotaNegociacao.Show()
        else:
            self.frmNotaNegociacao.Raise()  # Se já existir, apenas traz para frente

    
    def chama_frmvariacao(self, evento):
        ativo = self.txtAtivo.GetValue()
        if self.frmVariacao is None:  # Se não existir, cria uma nova janela
            self.frmVariacao = VariacaoFrm(None, ativo)
            self.frmVariacao.Bind(wx.EVT_CLOSE, lambda evt: self.on_close(evt, "frmVariacao"))
            self.frmVariacao.Show()
        else:
            if len(ativo) > 1:
                self.frmVariacao.temAtivoInicial(ativo)
            self.frmVariacao.Raise()  # Se já existir, apenas traz para frente

    def chama_frmRendaFixa(self, evento):
        ativo = self.txtAtivo.GetValue()
        if self.frmRendaFixa is None:  # Se não existir, cria uma nova janela
            self.frmRendaFixa = FrmRendaFixa()
            self.frmRendaFixa.Bind(wx.EVT_CLOSE, lambda evt: self.on_close(evt, "frmRendaFixa"))
            self.frmRendaFixa.Show()
        else:
            self.frmRendaFixa.Raise()  # Se já existir, apenas traz para frente
            
    def chama_frmnegociadoNoDiaNoDia(self, evento):
        if self.frmNegociadoNoDia is None:  # Se não existir, cria uma nova janela
            self.frmNegociadoNoDia = FrmNegociadoNoDia()
            self.frmNegociadoNoDia.Bind(wx.EVT_CLOSE, lambda evt: self.on_close(evt, "frmNegociadoNoDia"))
            self.frmNegociadoNoDia.Show()
        else:
            self.frmNegociadoNoDia.Raise()  # Se já existir, apenas traz para frente

    def chama_frmrRendaTotal(self, evento):

        if self.frmRendaTotal is None:  # Se não existir, cria uma nova janela
            self.frmRendaTotal = FrmRendaTotal()
            self.frmRendaTotal.Bind(wx.EVT_CLOSE, lambda evt: self.on_close(evt, "frmRendaTotal"))
            self.frmRendaTotal.Show()
        else:
            self.frmRendaTotal.Raise()  # Se já existir, apenas traz para frente

    def chama_frmcarteira(self, evento):

        if self.frmCarteira is None:  # Se não existir, cria uma nova janela
            self.frmCarteira = FrmCarteira(self.idConta, self.nomeBolsa)
            self.frmCarteira.Bind(wx.EVT_CLOSE, lambda evt: self.on_close(evt, "frmCarteira"))
            self.frmCarteira.Show()
        else:
            self.frmCarteira.Raise()  # Se já existir, apenas traz para frente

    def chama_frmproventos(self, evento):

        if self.frmProvento is None:  # Se não existir, cria uma nova janela
            self.frmProvento = FrmProvento(self.idConta)
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

    def chama_frmdespesas(self, evento):

        if self.frmDespesa is None:  # Se não existir, cria uma nova janela
            self.frmDespesa = FrmDespesa(self.idConta)
            self.frmDespesa.Bind(wx.EVT_CLOSE, lambda evt: self.on_close(evt, "frmDespesa"))
            self.frmDespesa.Show()
        else:
            self.frmDespesa.Raise()  # Se já existir, apenas traz para frente

    def chama_frmcapital(self, evento):
        self.awsomeCotacao.busca_dollar()
        self.awsomeCotacao.busca_euro()

        if self.frmCapital is None:
            self.frmCapital = FrmCapital(self.idConta)
            self.frmCapital.Bind(wx.EVT_CLOSE, lambda evt: self.on_close(evt, "frmCapital"))
            self.frmCapital.Show()
        else:
            self.frmCapital.Raise()  # Se já existir, apenas traz para frente

    def chama_frmradar(self, evento):
        self.awsomeCotacao.busca_dollar()
        self.awsomeCotacao.busca_euro()

        if self.frmRadar is None:
            self.frmRadar = RadarFrm(None, title="Radar de Proventos")
            self.frmRadar.Bind(wx.EVT_CLOSE, lambda evt: self.on_close(evt, "frmRadar"))
            self.frmRadar.Show()
        else:
            self.frmRadar.Raise()  # Se já existir, apenas traz para frente

    def chama_frmleRadarB3(self, evento):
        if self.leRadarB3 is None:  # Se não existir, cria uma nova janela
            self.leRadarB3 = LeRadarB3()
            self.leRadarB3.Bind(wx.EVT_CLOSE, lambda evt: self.on_close(evt, "leRadarB3"))
            self.leRadarB3.Show()
        else:
            self.leRadarB3.Raise()  # Se já existir, apenas traz para frente

    def limpaElementos(self):

        self.ativo.clearAtivo()
        self.txtAtivo.Clear()

    def montaGrid(self, lista):
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
        saldoValor = Decimal('0.0')
        totalCompradoQtde = 0
        self.totalComprado = Decimal('0.0')
        self.totalResultado = Decimal('0.0')
        self.totalRendimento = Decimal('0.0')
        self.totalProventos = Decimal('0.0')
        resultado = Decimal('0.0')
        precomedio = Decimal('0.0')
        negocios = 0
        linha = 0
        self.contador = 0
        
        for  row in self.lista:
            negocios +=1
            dataOperacao = devolveDateStr(row[1])
            numoperacao = devolveInteger(row[2])
            operacao =''
            #valorOperacao = devolve_float_de_formatacao_completa(row[4])
            valorOperacao = row[4]
            qtdeOperacao = devolveInteger(row[3])
            valorCompraStr = ''
            valorVendaStr = ''
            ganho = Decimal('0.0')
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
                if precomedio > 0.0:
                    precomedio = ((precomedio * saldoQtde) + totalOperacao) / (saldoQtde + qtdeOperacao)
                else:
                    precomedio = valorOperacao
                    
                saldoQtde += qtdeOperacao

            else:
                operacao = 'Venda'
                if simulado: operacao = 'Venda Simulada'
                valorVendaStr = formata_numero(valorOperacao)
                totalOperacao = valorOperacao * qtdeOperacao
                resultado = totalOperacao - (qtdeOperacao * precomedio)
                ganho = resultado / (qtdeOperacao * precomedio)
                ganho = ganho * cem
                strGanho = formata_numero(ganho) +  ' %'
                self.totalResultado += resultado
                saldoQtde -= qtdeOperacao
                strResultado = formata_numero(resultado)
                if saldoQtde == 0:
                    precomedio = Decimal('0.0')

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

        self.totalProventos = zero
        resultado = zero

        for row in lista:
            dataOperacao = devolveDateStr(row[1])
            #valorOperacao = devolve_float_de_formatacao_completa(row[2])
            valorOperacao = row[2]
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
        if self.totalComprado > 0:
            self.totalRendimento = (self.totalGeral / self.totalComprado) * cem
        else:
            self.totalRendimento = zero
        self.txtProventos.SetValue(formata_numero(self.totalProventos))
        self.txtTotalGeral.SetValue(formata_numero(self.totalGeral))
        self.txtResultadoGeral.SetValue(formata_numero(self.totalRendimento) + ' %')

    def gridRadar(self, lista):

        for row in lista:
            dataOperacao = devolveDateStr(row[1])
            dataProvavel = devolveDateStr(row[2])
            valorprovento = devolve_float_de_formatacao_completa(row[5])
            dy = devolve_float_de_formatacao_completa(row[4])
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

            valor = devolve_float_de_formatacao_completa(self.grid.GetCellValue(linha, 9))
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

    def busca_ativo(self, item):
        siglaAtivo = self.txtAtivo.Value
        avanca = True        
        if self.idBolsa == None or self.idConta == None:
            dlg = wx.MessageDialog(None, 'Conta corrente ou Bolsa não definidos', 'Erro de inserção', wx.OK | wx.ICON_ERROR)
            result = dlg.ShowModal()
            avanca = False
        
        if avanca:
            if len(siglaAtivo) > 0:
                self.ativo.populaAtivoBySigla(siglaAtivo) #, self.idconta)

                if self.ativo.id_ativo > 0:
                    self.ativo.setlan(self.idConta)
                    self.ativo.busca_proventos_do_ativo(self.idConta, False)
                    self.saldoBancario = Conta.mc_get_saldo_bancario(self.idConta)
                    self.saldoBancarioTeorico = Conta.mc_get_saldo_bancario_teorico(self.idConta)
                    self.montaGrid(self.ativo.lan)
                    self.gridProventos(self.ativo.proventos)
                    self.gridRadar(self.ativo.busca_radar(siglaAtivo))
                    self.ordenarGrid()
                else:
                    dlg = wx.MessageDialog(None, 'Não foi encontrado o ativo indicado!', 'Erro no Ativo!', wx.OK | wx.ICON_ERROR)
                    result = dlg.ShowModal()

    def insere_operacao(self, item):
        avanca = True
        operacao = 0
        quantidade = 0
        valor = 0.0
        dataOperacao = self.txtDataOperacao.GetValue().Format('%d/%m/%Y')
        siglaAtivo = self.txtAtivo.GetValue()
        simulacao = False

        avanca = self.ativo.existeAtivo(siglaAtivo)
        if avanca:
            if self.idBolsa == None or self.idConta == None:
                dlg = wx.MessageDialog(None, 'Conta corrente ou Bolsa não definidos', 'Erro de inserção', wx.OK | wx.ICON_ERROR)
                result = dlg.ShowModal()

                avanca = False
        if avanca:
            operacao = self.cbOperacao.GetSelection() + 1
            if operacao < 1 or operacao > 2:
                avanca = False
            quantidade = int(self.txtQuatidade.GetValue())
            if quantidade <= 0:
                avanca = False
            valor_str = str(self.txtValor.GetValue())
            valor = devolve_float(valor_str)
            if valor <= 0:
                avanca = False
           
            sim = self.cbSimulado.GetSelection()
            if sim == 0:
                simulacao = True

        if avanca:
            if self.ativo.insereOperacao(siglaAtivo, dataOperacao, operacao, valor, quantidade, self.idConta, simulado=simulacao) == True:
                self.txtQuatidade.SetValue('')
                self.txtValor.SetValue('')
                self.busca_ativo(item)


def main():
    app = wx.App()
    desempenhoAtivo = frmDesempenhoAtivo()
    app.MainLoop()


if __name__ == '__main__':
    main()
