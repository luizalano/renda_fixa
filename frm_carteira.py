# coding: utf-8

from diversos import *
from ativo import *
from cotacao import Cotacao
from conta import Conta
from wxFrameMG import FrameMG

from wx import *

class FrmCarteira(FrameMG):
    insert = False
    caminho = '.\\icones\\'
    id_conta = -1
    sigla_bolsa = None


    def __init__(self, idContaInicial, siglaBolsa):
        self.lista_negociacoes = []
        self.lista_ativos = []
        self.lista_patrimonio = []

        self.total_comprado = 0.0
        self.sigla_bolsa = siglaBolsa

        super(FrmCarteira, self).__init__(pai=None, titulo='Ativos em carteira',
                                       lar = 1100, alt = 730,
                                       xibot = 150, split=False)

        self.criaComponentes()
        self.set_conta(idContaInicial)

    def criaComponentes(self):
        X = self.posx(3)
        Y = self.posy(2)
        tamX = self.larguraEmPx(220)
        tamY = self.alturaEmPx(15)

        self.setAvancoVertical(8)

        label0811, self.cbConta = self.criaCombobox(self.painel, pos=(3, 0), tamanho=22, label='Conta')
        self.cbConta.Bind(wx.EVT_COMBOBOX, self.conta_selecionada)

        label0991, self.cbBolsa = self.criaCombobox(self.painel, pos=(30, 0), tamanho=22, label='Bolsa')
        self.cbBolsa.Bind(wx.EVT_COMBOBOX, self.bolsaSelecionada)

        self.btnBuscaaAtivos = Button(self.painel, id=ID_ANY, label="Busca Ativos"
                                      , pos=(self.posx(60), self.posy(0)+15),
                                      size=(self.posx(15), self.posy(1)-30), style=0)  
        self.Bind(wx.EVT_BUTTON, self.busca_tudo, self.btnBuscaaAtivos)


        label10555, self.txtNomeMoeda = self.criaCaixaDeTexto(self.painel, pos=(X + 65, 0),
                                                    label='Moeda da conta', tamanho = (15, 1),
                                                    max=0, multi=False)
        self.txtNomeMoeda.SetForegroundColour(wx.BLACK)
        self.txtNomeMoeda.SetBackgroundColour(wx.Colour(237, 237, 237))
        self.txtNomeMoeda.SetEditable(False)
        self.negrita(self.txtNomeMoeda)

        label1055, self.txtValorMoeda = self.criaCaixaDeTexto(self.painel, pos=(X + 85, 0),
                                                    label='Última cotação', tamanho = (15, 1),
                                                    max=0, multi=False, align='direita')
        self.txtValorMoeda.SetForegroundColour(wx.BLACK)
        self.txtValorMoeda.SetBackgroundColour(wx.Colour(237, 237, 237))
        self.txtValorMoeda.SetEditable(False)
        self.negrita(self.txtValorMoeda)

        self.grid = wx.grid.Grid(self.painel, pos=(30, 70), size=(980, 530))
        self.grid.CreateGrid(0, 8)

        # Definindo os tamanhos das colunas
        col_sizes = [80, 120, 100, 120, 100, 120, 100, 140]
        col_labels = ["Ativo", "Valor Comprado", "Quantidade", "Preço médio", "Última cotação", "Patrimônio", "Variação %", "Valor de Mercado"]

        for i, (size, label) in enumerate(zip(col_sizes, col_labels)):
            self.grid.SetColSize(i, size)
            self.grid.SetColLabelValue(i, label)


        y = 12

        label08, self.txtComprado = self.criaCaixaDeTexto(self.painel, pos=(35, y), label='Comprado',
                                                        tamanho = (12, 1),  align='direita' )
        label09, self.txtPatrimonio = self.criaCaixaDeTexto(self.painel, pos=(55, y), label='Valor atual',
                                                        tamanho = (12, 1),  align='direita' )
        label10, self.txtVariacao = self.criaCaixaDeTexto(self.painel, pos=(75, y), label='Variação',
                                                        tamanho = (12, 1),  align='direita' )

        # Saldo Bancário
        label885, self.txtSaldoBancario = self.criaCaixaDeTexto(self.painel, pos=(95, y),
                                                    label='Saldo bancário', tamanho = (15, 1),
                                                    max=0, multi=False, align='direita')
        self.txtSaldoBancario.SetForegroundColour(wx.BLACK)
        self.txtSaldoBancario.SetBackgroundColour(wx.Colour(237, 237, 237))
        self.txtSaldoBancario.SetEditable(False)
        
        self.negrita(self.txtValorMoeda)

        self.getConexao()
        self.botaoSalva.Hide()
        self.botaoDelete.Hide()
        self.botaoNovo.Hide()
        self.botaoCancela.Hide()

        self.enche_combo_contas()
        self.enche_combo_bolsas()

        self.Show()

    def enche_combo_contas(self):
        lista = Conta.mc_select_all()
        self.cbConta.Clear()
        for row in lista:
            self.cbConta.Append(row[4])

    def enche_combo_bolsas(self):
        self.conexao = FrmCarteira.getConexao()
        cursor = self.conexao.cursor()

        lista = None
        try:
            cursor.execute('select sigla from bolsa order by sigla;')
            lista = cursor.fetchall()
        except  Exception as e:
            dlg = wx.MessageDialog(None, str(e), 'Erro ao ler ativos negociados', wx.OK | wx.ICON_ERROR)
            result = dlg.ShowModal()
        self.conexao.close()
         
        self.cbBolsa.Clear()
        for row in lista:
            self.cbBolsa.Append(row[0])

        if self.sigla_bolsa:
            self.cbBolsa.SetSelection(self.indiceCb(self.cbBolsa, self.sigla_bolsa))

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
            self.conta_selecionada(None)

    def conta_selecionada(self, event):
        nomeConta = self.cbConta.GetStringSelection()
        listaConta = None
        listaConta = Conta.mc_select_one_by_nome(nomeConta)
        self.id_conta = -1
        if listaConta:
            self.id_conta = listaConta[0]
            if listaConta[8] == 'REAL':
                self.txtNomeMoeda.SetValue(listaConta[8])
                self.txtValorMoeda.SetValue('')
            else:
                lista = Cotacao.mc_get_ultima_cotacao(listaConta[7])
                if lista:
                    self.txtNomeMoeda.SetValue(lista[1])
                    self.txtValorMoeda.SetValue(formata_numero(lista[0]))
                else:
                    self.txtNomeMoeda.SetValue('')
                    self.txtValorMoeda.SetValue('')
        else:
            self.txtNomeMoeda.SetValue('')
            self.txtValorMoeda.SetValue('')

    def busca_tudo(self, event):
        if self.sigla_bolsa and self.id_conta > -1:        
            self.conexao = FrmCarteira.getConexao()
            self.busca_lista_ativos()
            self.busca_renda_por_ativo()
            self.monta_grid()
            self.conexao.close()   
                  
    def bolsaSelecionada(self, event):
        self.sigla_bolsa = self.cbBolsa.GetStringSelection()
        #self.buscaTudo()

    @staticmethod
    def getConexao():
        try:
            con = ConectaBD.retornaConexao()
            return con
        except Exception as e:
            print(f"Erro ao conectar com o banco: {e}")
            return False
        
    def busca_lista_ativos(self):
        clausulaSql = 'select distinct idativo from ativonegociado where idconta = %s;'

        cursor = self.conexao.cursor()
        try:
            cursor.execute(clausulaSql, (self.id_conta,))
        except  Exception as e:
            dlg = wx.MessageDialog(None, clausulaSql + '\n' + str(e), 'Erro ao buscar ativos negociados', wx.OK | wx.ICON_ERROR)
            result = dlg.ShowModal()

        self.lista_ativos = cursor.fetchall()

    def busca_renda_por_ativo(self):
        self.lista_patrimonio.clear()

        self.total_comprado = 0.0
        self.total_compras = 0.0
        self.total_vendas = 0.0
        for row in self.lista_ativos:
            self.busca_negociacoes(row[0])

            comprado, quantidade, precoMedio = self.estabelece_rendimento_por_acoes()
            if comprado > 0:
                self.total_comprado += comprado
                self.lista_patrimonio.append([row[0], comprado, quantidade, precoMedio])

        a = 0

    def busca_negociacoes(self, arg):
        self.lista_negociacoes.clear()
        cursor = self.conexao.cursor()

        clausulaSql = 'select a.id, a.dataoperacao, a.operacao, a.qtdeoperacao, a.valoroperacao  ' \
                  'from ativonegociado as a ' \
                  'where a.idativo = ' + str(arg) +  ' and a.idconta = ' + str(self.id_conta) + ' '\
                  'order by a.dataoperacao, a.ordemdia, a.id;'

        try:
            cursor.execute(clausulaSql)
        except  Exception as e:
            dlg = wx.MessageDialog(None, clausulaSql + '\n' + str(e), 'Erro ao ler ativos negociados', wx.OK | wx.ICON_ERROR)
            result = dlg.ShowModal()

        self.lista_negociacoes = cursor.fetchall()

    def estabelece_rendimento_por_acoes(self):
        saldoQtde = 0
        precomedio = 0.0
        listaProvisoria = []
        for row in self.lista_negociacoes:
            dataOperacao = row[1]
            numoperacao = devolveInteger(row[2])
            valorOperacao = devolve_float_de_formatacao_completa(row[4])
            qtdeOperacao = devolveInteger(row[3])
            if numoperacao == 1:
                totalOperacao = qtdeOperacao * valorOperacao
                if precomedio == 0:
                    precomedio = valorOperacao
                else:
                    precomedio = ((precomedio * saldoQtde) + totalOperacao) / (saldoQtde + qtdeOperacao)
                saldoQtde += qtdeOperacao

            else:
                saldoQtde -= qtdeOperacao
                if saldoQtde == 0:
                    precomedio = 0.0

        comprado = saldoQtde * precomedio
        return comprado, saldoQtde, precomedio

    def monta_grid(self):
        cursor = self.conexao.cursor()
        total_valor_atual = 0.0
        self.grid.ClearGrid()
        if self.grid.GetNumberRows() > 0:
            self.grid.DeleteRows(0, self.grid.GetNumberRows())
        linha = (-1)
        for row in self.lista_patrimonio:

            linha += 1
            self.grid.AppendRows()

            clausulaSql = 'select sigla from ativo where id = ' + str(row[0]) + ';'

            cursor.execute(clausulaSql)
            result = cursor.fetchone()

            cotacao = Ativo.get_ultima_cotacao(result[0])
            valor_atual = cotacao * float(row[2])
            total_valor_atual += valor_atual
            valor_mercado = Ativo.get_valor_mercado_yfinance(result[0], self.sigla_bolsa)
            variacao = (valor_atual / float(row[1]) - 1) * 100.0
            self.grid.SetCellValue(linha, 0, str(result[0]))
            self.grid.SetCellValue(linha, 1, formata_numero(float(row[1])))
            self.grid.SetCellValue(linha, 2, str(row[2]))
            self.grid.SetCellValue(linha, 3, formata_numero(float(row[3])))
            self.grid.SetCellValue(linha, 4, formata_numero(Ativo.get_ultima_cotacao(result[0])))
            self.grid.SetCellValue(linha, 5, formata_numero(valor_atual))
            self.grid.SetCellValue(linha, 6, formata_numero(variacao))
            self.grid.SetCellValue(linha, 7, formatar_valor(valor_mercado))

            self.grid.SetCellAlignment(linha,  0, wx.ALIGN_CENTRE, wx.ALIGN_CENTRE)
            self.grid.SetCellAlignment(linha,  1, wx.ALIGN_RIGHT, wx.ALIGN_RIGHT)
            self.grid.SetCellAlignment(linha,  2, wx.ALIGN_RIGHT, wx.ALIGN_RIGHT)
            self.grid.SetCellAlignment(linha,  3, wx.ALIGN_RIGHT, wx.ALIGN_RIGHT)
            self.grid.SetCellAlignment(linha,  4, wx.ALIGN_RIGHT, wx.ALIGN_RIGHT)
            self.grid.SetCellAlignment(linha,  5, wx.ALIGN_RIGHT, wx.ALIGN_RIGHT)
            self.grid.SetCellAlignment(linha,  6, wx.ALIGN_CENTRE, wx.ALIGN_CENTRE)
            self.grid.SetCellAlignment(linha,  7, wx.ALIGN_RIGHT, wx.ALIGN_RIGHT)

            if variacao < 0: self.grid.SetCellTextColour(linha, 6, wx.RED)

            if linha % 2 != 0:
                for i in range(0, 13):
                    self.grid.SetCellBackgroundColour(linha, i, wx.Colour(230, 255, 255))
        if linha >=0:
            variacao = (total_valor_atual / self.total_comprado - 1) * 100.0
            self.txtComprado.SetValue(formata_numero(self.total_comprado))
            self.txtPatrimonio.SetValue(formata_numero(total_valor_atual))
            self.txtVariacao.SetValue(formata_numero(variacao) + ' %')
            if variacao < 0:
                self.txtVariacao.SetForegroundColour(wx.RED)
                self.txtVariacao.SetBackgroundColour(wx.Colour(255, 230, 255))
            else:
                self.txtVariacao.SetBackgroundColour(wx.Colour(221, 255, 204))

        # Saldo bancario
        saldo_bancario = Conta.mc_get_saldo_bancario(self.id_conta)
        self.txtSaldoBancario.SetValue(formata_numero(saldo_bancario))


def main():
    app = wx.App()
    frmRendaTotal = FrmCarteira(None, 'B3')
    app.MainLoop()


if __name__ == '__main__':
    main()



