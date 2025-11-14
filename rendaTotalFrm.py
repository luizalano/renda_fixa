# coding: utf-8

from diversos import *
from wxFrameMG import FrameMG
import psycopg2
#from ClienteDeQuem import ClienteDeQuem

import wx
import wx.grid

class FrmRendaTotal(FrameMG):
    insert = False
    caminho = '.\\icones\\'


    def __init__(self):
        self.listaNegociacoes = []    # era ativo.lan
        self.listaRendaAcoes = []
        self.listaRendaProventos = []
        self.listaRendaDespesas = []
        self.listaDespesas = []
        self.listaCapital = []
        self.listaRetirada = []
        self.listaGeral = []

        self.totalCompras = 0.0
        self.totalVendas = 0.0
        self.totalAporte = 0.0
        self.totalRetirada = 0.0
        self.totalProventos = 0.0
        self.totalRenda = 0.0
        self.totalDespesas = 0.0
        self.totalResultado = 0.0
        self.totalDisponivel = 0.0
        self.totalComprado = 0.0
        self.totalPatrimonio = 0.0
        #self.dbname = 'b3'
        self.dbname= 'b3teste'

        super(FrmRendaTotal, self).__init__(pai=None, titulo='Renda proveniente de renda variável',
                                       lar = 1350, alt = 730,
                                       xibot = 450, split=False)

        self.criaComponentes()

    def criaComponentes(self):
        X = self.posx(2)
        Y = self.posy(0)
        tamX = self.larguraEmPx(200)
        tamY = self.alturaEmPx(15)

        self.setAvancoVertical(8)

        #self.grid = wx.ListCtrl(self.painel, pos=(X, Y), size=(tamX, tamY),
        #                        style=wx.LC_REPORT | wx.LC_VRULES | wx.LC_HRULES | wx.BORDER_SUNKEN)

        self.grid = wx.grid.Grid(self.painel, pos=(X, Y), size=(1300, 590))
        self.grid.CreateGrid(0, 13)
        self.grid.SetColSize( 0,   60)
        self.grid.SetColSize( 1,  100)
        self.grid.SetColSize( 2,  100)
        self.grid.SetColSize( 3,  100)
        self.grid.SetColSize( 4,  100)
        self.grid.SetColSize( 5,  100)
        self.grid.SetColSize( 6,  100)
        self.grid.SetColSize( 7,  100)
        self.grid.SetColSize( 8,  100)
        self.grid.SetColSize( 9,  100)
        self.grid.SetColSize(10,  80)
        self.grid.SetColSize(11,  80)
        self.grid.SetColSize(12,  80)
        self.grid.SetColLabelValue( 0, "Ref")
        self.grid.SetColLabelValue( 1, "Inicial")
        self.grid.SetColLabelValue( 2, "Aporte")
        self.grid.SetColLabelValue( 3, "Retirada")
        self.grid.SetColLabelValue( 4, "Rendimento")
        self.grid.SetColLabelValue( 5, "Provento")
        self.grid.SetColLabelValue( 6, "Despesa")
        self.grid.SetColLabelValue( 7, "Renda Mês")
        self.grid.SetColLabelValue( 8, "Acumulado")
        self.grid.SetColLabelValue( 9, "Saldo")
        self.grid.SetColLabelValue(10, "Renda %")
        self.grid.SetColLabelValue(11, "Acum %")
        self.grid.SetColLabelValue(12, "Media %")

        y = 12

        label01, self.txtAporte = self.criaCaixaDeTexto(self.painel, pos=(1, y), label='Total Aporte',
                                                        tamanho = (12, 1),  align='direita' )
        label02, self.txtRetirada = self.criaCaixaDeTexto(self.painel, pos=(16, y), label='Total Retirada',
                                                        tamanho = (12, 1),  align='direita' )
        label04, self.txtProvento = self.criaCaixaDeTexto(self.painel, pos=(46, y), label='Total Proventos',
                                                        tamanho = (12, 1),  align='direita' )
        label03, self.txtRenda = self.criaCaixaDeTexto(self.painel, pos=(31, y), label='Total Renda',
                                                        tamanho = (12, 1),  align='direita' )
        label05, self.txtDespesa = self.criaCaixaDeTexto(self.painel, pos=(61, y), label='Total despesa',
                                                        tamanho = (12, 1),  align='direita' )
        label06, self.txtResultado = self.criaCaixaDeTexto(self.painel, pos=(76, y), label='Resultado',
                                                        tamanho = (12, 1),  align='direita' )
        label08, self.txtComprado = self.criaCaixaDeTexto(self.painel, pos=(91, y), label='Comprado',
                                                        tamanho = (12, 1),  align='direita' )
        label09, self.txtPatrimonio = self.criaCaixaDeTexto(self.painel, pos=(106, y), label='Patrimônio',
                                                        tamanho = (12, 1),  align='direita' )
        label07, self.txtDisponivel = self.criaCaixaDeTexto(self.painel, pos=(130, y), label='Saldo bancário',
                                                        tamanho = (12, 1),  align='direita' )

        self.getConexao()
        self.botaoSalva.Hide()
        self.botaoDelete.Hide()
        self.botaoNovo.Hide()
        self.botaoCancela.Hide()

        self.getConexao()
        self.buscaListaAtivos()
        self.buscaRendaPorAtivo()
        self.buscaProventos()
        self.buscaDespesas()
        self.buscaCapital()
        self.juntaListas()
        self.montaGrid()

        self.Show()

    def getConexao(self):
        self.conexao = psycopg2.connect(dbname=self.dbname, user="postgres", password="seriate", host="localhost",
                                            port="5432")
    def buscaListaAtivos(self):
        clausulaSql = 'select distinct idativo from ativonegociado;'

        cursor = self.conexao.cursor()
        try:
            cursor.execute(clausulaSql)
        except  Exception as e:
            dlg = wx.MessageDialog(None, clausulaSql + '\n' + str(e), 'Erro ao buscar ativos negociados', wx.OK | wx.ICON_ERROR)
            result = dlg.ShowModal()

        self.listaAtivos = cursor.fetchall()

    def buscaRendaPorAtivo(self):
        self.listaRendaAcoes.clear()
        self.listaRendaProventos.clear()
        self.listaRendaDespesas.clear()

        self.totalComprado = 0.0
        self.totalCompras = 0.0
        self.totalVendas = 0.0
        for row in self.listaAtivos:
            self.buscaNegociacoes(row[0])

            comprado, compras, vendas = self.encheListaRendaAcoes()
            self.totalComprado += comprado
            self.totalCompras += compras
            self.totalVendas += vendas
            #self.acumulaListas()

        a = 0
        #lista1.extend(lista2)

    def buscaNegociacoes(self, arg):
        self.listaNegociacoes.clear()
        cursor = self.conexao.cursor()

        clausulaSql = 'select a.id, a.dataoperacao, a.operacao, a.qtdeoperacao, a.valoroperacao  ' \
                  'from ativonegociado as a ' \
                  'where a.idativo = ' + str(arg) +  ' '\
                  'order by a.dataoperacao, a.ordemdia, a.id;'

        try:
            cursor.execute(clausulaSql)
        except  Exception as e:
            dlg = wx.MessageDialog(None, clausulaSql + '\n' + str(e), 'Erro ao ler ativos negociados', wx.OK | wx.ICON_ERROR)
            result = dlg.ShowModal()

        self.listaNegociacoes = cursor.fetchall()

    def estabeleceRendimentoPorAcoes(self):
        saldoQtde = 0
        saldoValor = 0.0
        resultado = 0.0
        precomedio = 0.0
        compras = 0.0
        vendas = 0.0
        negocios = 0
        linha = 0
        listaProvisoria = []
        for row in self.listaNegociacoes:
            dataOperacao = row[1]
            numoperacao = devolveInteger(row[2])
            valorOperacao = devolveFloat(row[4])
            qtdeOperacao = devolveInteger(row[3])
            valorCompraStr = ''
            valorVendaStr = ''
            ganho = 0.0
            strGanho = ""
            strResultado = ''
            resultado = 0.0
            if numoperacao == 1:
                totalOperacao = qtdeOperacao * valorOperacao
                compras += totalOperacao
                if precomedio == 0:
                    precomedio = valorOperacao
                else:
                    precomedio = ((precomedio * saldoQtde) + totalOperacao) / (saldoQtde + qtdeOperacao)
                saldoQtde += qtdeOperacao

            else:
                totalOperacao = valorOperacao * qtdeOperacao
                vendas += totalOperacao
                resultado = totalOperacao - (qtdeOperacao * precomedio)
                # resultado = float(int(resultado*100.0)) / 100.0

                saldoQtde -= qtdeOperacao
                if saldoQtde == 0:
                    precomedio = 0.0

                if resultado != 0.0:
                    listaProvisoria.append([dataOperacao, resultado])
        comprado = saldoQtde * precomedio
        return comprado, compras, vendas, listaProvisoria

    def encheListaRendaAcoes(self):
        # a.dataoperacao, a.operacao, a.qtdeoperacao, a.valoroperacao
        comprado, compras, vendas, listaProvisoria = self.estabeleceRendimentoPorAcoes()
        for row in listaProvisoria:
            dataOperacao = row[0].strftime("%Y/%m")
            # valorRendimento = float(int(row[1] * 100.0) / 100.0)
            valorRendimento = float(row[1])
            if len(self.listaRendaAcoes) == 0:
                self.listaRendaAcoes.append([dataOperacao, valorRendimento])
            else:
                indice = next((i for i, linha in enumerate(self.listaRendaAcoes) if linha[0] == dataOperacao), -1)
                if indice < 0:
                    self.listaRendaAcoes.append([dataOperacao, valorRendimento])
                else:
                    self.listaRendaAcoes[indice][1] += valorRendimento
        return comprado, compras, vendas

    def buscaProventos(self):
        cursor = self.conexao.cursor()

        clausulaSql = 'select p.id, p.datarecebimento as "datar", ' \
                  '(p.valorbruto - p.valorir) as "valor", ' \
                  'tp.nometipoprovento as "provento", p.pago  ' \
                  'from proventos as p join  tipoprovento as tp on tp.id = p.idtipoprovento ' \
                  'where p.pago = True; '

        try:
            cursor.execute(clausulaSql)
        except  Exception as e:
            dlg = wx.MessageDialog(None, clausulaSql + '\n' + str(e), 'Erro ao ler proventos!', wx.OK | wx.ICON_ERROR)
            result = dlg.ShowModal()

        row = cursor.fetchone()

        self.listaRendaProventos.clear()
        while row != None:
            dataOperacao = row[1].strftime("%Y/%m")
            valorRendimento = float(int(row[2] * 100.0) / 100.0)
            if len(self.listaRendaProventos) == 0:
                self.listaRendaProventos.append([dataOperacao, valorRendimento])
            else:
                for item in self.listaRendaProventos:
                    if item[0] == dataOperacao:
                        item[1] += valorRendimento
                        break
                else:
                    self.listaRendaProventos.append([dataOperacao, valorRendimento])
            row = cursor.fetchone()

    def buscaDespesas(self):
        cursor = self.conexao.cursor()
        self.listaDespesas.clear()

        clausulaSql = 'select datalancamento, valor from despesas order by datalancamento;'

        try:
            cursor.execute(clausulaSql)
        except  Exception as e:
            dlg = wx.MessageDialog(None, clausulaSql + '\n' + str(e), 'Erro ao ler despesas!', wx.OK | wx.ICON_ERROR)
            result = dlg.ShowModal()

        lista = cursor.fetchall()

        for row in lista:
            dataOperacao = row[0].strftime("%Y/%m")
            valor = float(int(row[1] * 100.0) / 100.0)
            if len(self.listaDespesas) == 0:
                self.listaDespesas.append([dataOperacao, valor])
            else:
                for item in self.listaDespesas:
                    if item[0] == dataOperacao:
                        item[1] += valor
                        break
                else:
                    self.listaDespesas.append([dataOperacao, valor])

    def buscaCapital(self):
        cursor = self.conexao.cursor()
        clausulaSql = 'select datalancamento, valor from capital order by datalancamento;'

        try:
            cursor.execute(clausulaSql)
        except  Exception as e:
            dlg = wx.MessageDialog(None, clausulaSql + '\n' + str(e), 'Erro ao ler alterações de Capital!', wx.OK | wx.ICON_ERROR)
            result = dlg.ShowModal()

        lista = cursor.fetchall()

        self.listaCapital.clear()
        self.listaRetirada.clear()

        for row in lista:
            dataOperacao = row[0].strftime("%Y/%m")
            valor = float(int(row[1] * 100.0) / 100.0)
            if valor < 0:
                if len(self.listaRetirada) == 0:
                    self.listaRetirada.append([dataOperacao, valor])
                else:
                    for item in self.listaRetirada:
                        if item[0] == dataOperacao:
                            item[1] += valor
                            break
                    else:
                        self.listaRetirada.append([dataOperacao, valor])
            else:
                if len(self.listaCapital) == 0:
                    self.listaCapital.append([dataOperacao, valor])
                else:
                    for item in self.listaCapital:
                        if item[0] == dataOperacao:
                            item[1] += valor
                            break
                    else:
                        self.listaCapital.append([dataOperacao, valor])

    def juntaListas(self):
        for ref, valor in self.listaCapital:
            if len(self.listaGeral) == 0:
                #self.listaGeral.append([[ref], [valor], [], [], [], []])
                self.listaGeral.append([ref, valor, 0, 0, 0, 0])
            else:
                linha = (-1)
                for item in self.listaGeral:
                    linha += 1
                    if item[0] == ref:
                        self.listaGeral[linha][1] = valor
                        break
                else:
                    self.listaGeral.append([ref, valor, 0, 0, 0, 0])

        for ref, valor in self.listaRetirada:
            if len(self.listaGeral) == 0:
                self.listaGeral.append([ref, 0, valor, 0, 0, 0])
            else:
                linha = (-1)
                for item in self.listaGeral:
                    linha += 1
                    if item[0] == ref:
                        self.listaGeral[linha][2] = valor
                        break
                else:
                    self.listaGeral.append([ref, 0, valor, 0, 0, 0])

        for ref, valor in self.listaRendaAcoes:
            if len(self.listaGeral) == 0:
                self.listaGeral.append([ref, 0, 0, valor, 0, 0])
            else:
                linha = (-1)
                for item in self.listaGeral:
                    linha += 1
                    if item[0] == ref:
                        self.listaGeral[linha][3] = valor
                        break
                else:
                    self.listaGeral.append([ref, 0, 0, valor, 0, 0])

        for ref, valor in self.listaRendaProventos:
            if len(self.listaGeral) == 0:
                self.listaGeral.append([ref, 0, 0, 0, valor, 0])
            else:
                linha = (-1)
                for item in self.listaGeral:
                    linha += 1
                    if item[0] == ref:
                        self.listaGeral[linha][4] = valor
                        break
                else:
                    self.listaGeral.append([ref, 0, 0, 0, valor])

        for ref, valor in self.listaDespesas:
            if len(self.listaGeral) == 0:
                self.listaGeral.append([ref, 0, 0, 0, 0, valor])
            else:
                linha = (-1)
                for item in self.listaGeral:
                    linha += 1
                    if item[0] == ref:
                        self.listaGeral[linha][5] = valor
                        break
                else:
                    self.listaGeral.append([ref, 0, 0, 0, 0, valor])

    def montaGrid(self):
        listaOrdenada = sorted(self.listaGeral, key=lambda x: x[0])

        self.grid.ClearGrid()
        if self.grid.GetNumberRows() > 0:
            self.grid.DeleteRows(0, self.grid.GetNumberRows())
        linha = (-1)
        rendaAcumulada = 0.0
        inicial = 0.0
        saldo = 0.0
        rendPercAcm = 0.0
        rendaMedia = 0.0
        for row in listaOrdenada:

            linha += 1
            self.grid.AppendRows()
            self.grid.SetCellValue(linha, 0, str(row[0]))

            aporte = float(row[1])
            retirada = row[2] * (-1.0)
            rendimento = row[3]
            provento = row[4]
            despesa = row [5]
            rendaMes = rendimento + provento - despesa
            inicial = saldo + aporte - retirada
            #saldo = saldo + aporte - retirada + rendimento + provento - despesa
            saldo = inicial + rendimento + provento - despesa
            rendaAcumulada = rendaAcumulada + rendimento + provento - despesa
            if inicial != 0.0:
                rendperc = (rendimento + provento - despesa) / inicial
            else:
                rendperc = 0.0
            if linha > 0:
               rendPercAcm = (1 + rendperc) * (1 + rendPercAcm) - 1
               rendaMedia = ((1 + rendPercAcm) ** (1 / linha)) - 1
            else:
               rendPercAcm = rendperc
               rendaMedia = rendperc

            self.totalAporte += aporte
            self.totalRetirada += retirada
            self.totalProventos += provento
            self.totalRenda += rendimento
            self.totalDespesas += despesa
            self.totalResultado += rendaMes

            rendimento = float(int(rendimento * 100.0) / 100.0)

            self.grid.SetCellValue(linha, 1, formata_numero(inicial))
            self.grid.SetCellValue(linha, 2, formata_numero(aporte))
            self.grid.SetCellValue(linha, 3, formata_numero(retirada))
            self.grid.SetCellValue(linha, 4, formata_numero(rendimento))
            if rendimento < 0 : self.grid.SetCellTextColour(linha, 4, wx.RED)
            self.grid.SetCellValue(linha, 5, formata_numero(provento))
            self.grid.SetCellValue(linha, 6, formata_numero(despesa))
            self.grid.SetCellValue(linha, 7, formata_numero(rendaMes))
            if rendaMes < 0: self.grid.SetCellTextColour(linha, 7, wx.RED)
            self.grid.SetCellValue(linha, 8, formata_numero(rendaAcumulada))
            if rendaAcumulada < 0: self.grid.SetCellTextColour(linha, 8, wx.RED)
            self.grid.SetCellValue(linha, 9, formata_numero(saldo))
            self.grid.SetCellValue(linha, 10, formata_numero(rendperc * 100.0))
            if rendperc < 0: self.grid.SetCellTextColour(linha, 10, wx.RED)
            self.grid.SetCellValue(linha, 11, formata_numero(rendPercAcm * 100.0))
            if rendPercAcm < 0: self.grid.SetCellTextColour(linha, 11, wx.RED)
            self.grid.SetCellValue(linha, 12, formata_numero(rendaMedia * 100.0))
            if rendaMedia < 0: self.grid.SetCellTextColour(linha, 12, wx.RED)

            self.grid.SetCellAlignment(linha,  0, wx.ALIGN_CENTRE, wx.ALIGN_CENTRE)
            self.grid.SetCellAlignment(linha,  1, wx.ALIGN_RIGHT, wx.ALIGN_RIGHT)
            self.grid.SetCellAlignment(linha,  2, wx.ALIGN_RIGHT, wx.ALIGN_RIGHT)
            self.grid.SetCellAlignment(linha,  3, wx.ALIGN_RIGHT, wx.ALIGN_RIGHT)
            self.grid.SetCellAlignment(linha,  4, wx.ALIGN_RIGHT, wx.ALIGN_RIGHT)
            self.grid.SetCellAlignment(linha,  5, wx.ALIGN_RIGHT, wx.ALIGN_RIGHT)
            self.grid.SetCellAlignment(linha,  6, wx.ALIGN_RIGHT, wx.ALIGN_RIGHT)
            self.grid.SetCellAlignment(linha,  7, wx.ALIGN_RIGHT, wx.ALIGN_RIGHT)
            self.grid.SetCellAlignment(linha,  8, wx.ALIGN_RIGHT, wx.ALIGN_RIGHT)
            self.grid.SetCellAlignment(linha,  9, wx.ALIGN_RIGHT, wx.ALIGN_RIGHT)
            self.grid.SetCellAlignment(linha, 10, wx.ALIGN_CENTRE, wx.ALIGN_CENTRE)
            self.grid.SetCellAlignment(linha, 11, wx.ALIGN_CENTRE, wx.ALIGN_CENTRE)
            self.grid.SetCellAlignment(linha, 12, wx.ALIGN_CENTRE, wx.ALIGN_CENTRE)

            if linha % 2 != 0:
                for i in range(0, 13):
                    self.grid.SetCellBackgroundColour(linha, i, wx.Colour(230, 255, 255))

        #self.totalDisponivel = saldo - self.totalComprado
        self.totalDisponivel = self.totalAporte - self.totalRetirada - self.totalDespesas + self.totalProventos + self.totalVendas - self.totalCompras
        self.totalPatrimonio = self.totalDisponivel + self.totalComprado
        self.txtAporte.SetValue(formata_numero(self.totalAporte))
        self.txtRetirada.SetValue(formata_numero(self.totalRetirada))
        self.txtProvento.SetValue(formata_numero(self.totalProventos))
        self.txtRenda.SetValue(formata_numero(self.totalRenda))
        self.txtDespesa.SetValue(formata_numero(self.totalDespesas))
        self.txtResultado.SetValue(formata_numero(self.totalResultado))
        self.txtDisponivel.SetValue(formata_numero(self.totalDisponivel))
        self.txtComprado.SetValue(formata_numero(self.totalComprado))
        self.txtPatrimonio.SetValue(formata_numero(self.totalPatrimonio))

def main():
    app = wx.App()
    frmRendaTotal = FrmRendaTotal()
    app.MainLoop()


if __name__ == '__main__':
    main()



