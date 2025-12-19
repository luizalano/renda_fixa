# coding: utf-8
from diversos import *
from wx import *
from rendafixa import RendaFixa
from conta import Conta
from titulorendafixa import TituloRendaFixa
from frm_tituloRendaFixa import FrmTituloRendaFixa
import wx.grid
from wxFrameMG import FrameMG


class FrmRendaFixa(FrameMG):
    insert = True
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

        super(FrmRendaFixa, self).__init__(pai=None, titulo='Renda Fixa - Lançamentos por título', lar = 1370, alt = 720,
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
        
        label05, self.txtValor = self.criaCaixaDeTexto(self.painel, pos=(78, 0), label='Valor',
                                                        tamanho = (12, 1), max=14, multi=False, tipofloat=True )

        label06, self.cbAlteraSaldo = self.criaCombobox(self.painel, pos=(93, 0), tamanho=10, label='Saldo')
        self.cbAlteraSaldo.Append('0 - Não altera')
        self.cbAlteraSaldo.Append('1 - Altera')

        label0601, self.cbTipoLancamento = self.criaCombobox(self.painel, pos=(107, 0), tamanho=12, label='Tipo lcto')
        lista = RendaFixa.sm_tipos_lancamento()
        self.cbTipoLancamento.Append('0 - ' + str(lista[0]))
        self.cbTipoLancamento.Append('1 - ' + str(lista[1]))
        self.cbTipoLancamento.Append('2 - ' + str(lista[2]))
        self.cbTipoLancamento.Append('3 - ' + str(lista[3]))

        label07, self.txtDescricao = self.criaCaixaDeTexto(self.painel, pos=(122, 0), label='Descrição',
                                                               tamanho = (40, 1), max=100, multi=False)
        

        self.btnInsereOperacao = Button(self.painel, id=ID_ANY, label="Salva Operação"
                                      , pos=(self.posx(165), self.posy(0)+15),
                                      size=(self.posx(13), self.posy(1)-30), style=0)  
        self.Bind(wx.EVT_BUTTON, self.insere_operacao, self.btnInsereOperacao)

        self.btnCancelaOperacao = Button(self.painel, id=ID_ANY, label="Cancela"
                                      , pos=(self.posx(180), self.posy(0)+15),
                                      size=(self.posx(8), self.posy(1)-30), style=0)  
        self.Bind(wx.EVT_BUTTON, self.cancela_operacao, self.btnCancelaOperacao)

        
        self.botaoSalva.Hide()
        self.botaoDelete.Hide()
        self.botaoNovo.Hide()
        self.botaoCancela.Hide()

        self.limpa_elementos()
        self.enche_combo_contas()
        self.enche_combo_titulos()

        self.grid.CreateGrid(0, 9)

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
            self.monta_grid()

    def titulo_selecionado(self, event):
        nomeTitulo = self.cbTitulo.GetStringSelection()
        listaTitulo = None
        listaTitulo = TituloRendaFixa.mc_select_one_by_nome(nomeTitulo)
        self.id_titulo_renda_fixa = -1
        self.nome_titulo_renda_fixa = ''
        if listaTitulo:
            self.id_titulo_renda_fixa = listaTitulo[0]
            self.nome_titulo_renda_fixa = listaTitulo[1]
            self.monta_grid()

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

    def insere_operacao(self, event):
        continua = True
        if self.id_conta == -1:
            dlg = wx.MessageDialog(None, 'Conta corrente não definida.', 'Erro ao inserir operação de renda fixa', wx.OK | wx.ICON_ERROR)
            result = dlg.ShowModal()
            continua = False
        if self.id_titulo_renda_fixa == -1:
            dlg = wx.MessageDialog(None, 'Título de renda fixa não definido.', 'Erro ao inserir operação de renda fixa', wx.OK | wx.ICON_ERROR)
            result = dlg.ShowModal()
            continua = False
        if self.cbTipoLancamento.GetSelection() == -1:
            dlg = wx.MessageDialog(None, 'Tipo do lançamento não definido.', 'Erro ao inserir operação de renda fixa', wx.OK | wx.ICON_ERROR)
            result = dlg.ShowModal()
            continua = False
        aux = self.cbAlteraSaldo.GetSelection()
        alterasaldobancario = False
        if aux == 0:
            alterasaldobancario = False
        elif aux == 1:
            alterasaldobancario = True
        else:
            dlg = wx.MessageDialog(None, 'Opção de alteração de saldo bancário não definida.', 'Erro ao inserir operação de renda fixa', wx.OK | wx.ICON_ERROR)
            result = dlg.ShowModal()
            continua = False
        valor = devolveDecimalDeFloat(self.txtValor.GetValue())
        if valor == 0:
            dlg = wx.MessageDialog(None, 'Valor da operação não pode ser zero.', 'Erro ao inserir operação de renda fixa', wx.OK | wx.ICON_ERROR)
            result = dlg.ShowModal()
            continua = False
        if continua:
            self.rendaFixa.set_id_conta(self.id_conta)
            self.rendaFixa.set_id_titulo_renda_fixa(self.id_titulo_renda_fixa)
            self.rendaFixa.set_data_lancamento(self.txtDataOperacao.GetValue().Format('%d/%m/%Y'))
            self.rendaFixa.set_valor(valor)
            self.rendaFixa.set_altera_saldo_bancario(alterasaldobancario)
            self.rendaFixa.set_descricao(self.txtDescricao.GetValue())
            self.rendaFixa.set_tipo_lancamento(self.cbTipoLancamento.GetSelection())
            if self.insert == True:
                self.rendaFixa.insert()
            else:
                self.rendaFixa.update()
            self.monta_grid()
            
    def cancela_operacao(self, event):
        self.limpa_elementos()

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
                self.limpa_elementos()
                self.monta_grid()

    def altera_lancamento(self, row):
        id = self.grid.GetCellValue(row, 0)
        self.rendaFixa.select_by_id(id)
        self.txtDataOperacao.SetValue(self.rendaFixa.data_lancamento)
        self.txtValor.SetValue(str(self.rendaFixa.valor))
        self.txtDescricao.SetValue(self.rendaFixa.descricao)
        if self.rendaFixa.altera_saldo_bancario:
            self.cbAlteraSaldo.SetSelection(1)
        else:
            self.cbAlteraSaldo.SetSelection(0)
        self.cbTipoLancamento.SetSelection(self.rendaFixa.tipo_lancamento)
        self.insert = False

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

    def limpa_elementos(self):
        self.txtValor.SetValue('')
        self.txtDescricao.SetValue('')
        self.cbTipoLancamento.SetSelection(-1)
        self.insert = True

    def monta_grid(self):
        if self.nome_conta == '' or self.nome_titulo_renda_fixa == '':
            return
        numrows = self.grid.GetNumberRows()
        if numrows >0:
            self.grid.DeleteRows(pos=0, numRows=self.grid.GetNumberRows())
        self.grid.SetColSize( 0,  40)
        self.grid.SetColSize( 1, 300)
        self.grid.SetColSize( 2,  75)
        self.grid.SetColSize( 3, 100)
        self.grid.SetColSize( 4, 100)
        self.grid.SetColSize( 5, 100)
        self.grid.SetColSize( 6,  80)
        self.grid.SetColSize( 7, 300)
        self.grid.SetColSize( 8, 100)
        
        self.grid.SetColLabelValue(0, 'id')
        self.grid.SetColLabelValue(1, 'Titulo')
        self.grid.SetColLabelValue(2, 'Data')
        self.grid.SetColLabelValue(3, 'Entrada')
        self.grid.SetColLabelValue(4, 'Saída')
        self.grid.SetColLabelValue(5, 'Tipo Lançamento')
        self.grid.SetColLabelValue(6, 'Altera Saldo')
        self.grid.SetColLabelValue(7, 'Descrição')
        self.grid.SetColLabelValue(8, 'Saldo')

        lista = RendaFixa.sm_busca_por_nome_conta_nome_titulo(self.nome_conta, self.nome_titulo_renda_fixa)

        linha = 0
        saldo = zero
        
        if lista:
            for row in lista:
                id = str(row[0])
                dataOperacao = devolveDateStr(row[1])
                valor = devolveDecimalDeFloat(row[2])
                descricao = row[3]
                alterasaldobancario = row[6]
                nometitulo = row[7]
                nomeconta = row[8]
                tipoLancamento = row[9]
                saldo += valor

                if valor < 0: 
                    aporte = zero
                    retirada = valor
                else:
                    aporte = valor
                    retirada = zero
                
                self.grid.AppendRows()
                self.grid.SetCellValue(linha,  0, str(row[0]))
                self.grid.SetCellValue(linha,  1, nometitulo)
                self.grid.SetCellValue(linha,  2, dataOperacao)
                self.grid.SetCellValue(linha,  3, formata_numero(aporte))
                self.grid.SetCellValue(linha,  4, formata_numero(retirada))
                self.grid.SetCellValue(linha,  5, RendaFixa.sm_nome_tipo_lancamento(tipoLancamento))
                self.grid.SetCellValue(linha,  6, str(alterasaldobancario))
                self.grid.SetCellValue(linha,  7, descricao)
                self.grid.SetCellValue(linha,  8, formata_numero(saldo))
                self.grid.SetCellAlignment(linha,  3, wx.ALIGN_RIGHT, wx.ALIGN_RIGHT)
                self.grid.SetCellAlignment(linha,  4, wx.ALIGN_RIGHT, wx.ALIGN_RIGHT)
                self.grid.SetCellAlignment(linha,  8, wx.ALIGN_RIGHT, wx.ALIGN_RIGHT)
                linha += 1

        self.limpa_elementos()

def main():
    app = wx.App()
    objeto = FrmRendaFixa()
    app.MainLoop()


if __name__ == '__main__':
    main()
