#import wx
from decimal import *
import wx.grid
from ativoNegociado import AtivoNegociado
from cotacao import *
from despesa import Despesa
from conta import Conta
from capital import Capital
from diversos import *
#from collections import defaultdict
from collections import deque

from provento import Provento

class FrmRendaTotal(wx.Frame):
    def __init__(self):
        super().__init__(None, title="Rendimento total de Renda Variável", size=(1350, 730),
                         style=wx.DEFAULT_FRAME_STYLE & ~wx.RESIZE_BORDER & ~wx.MAXIMIZE_BOX)
        self.SetPosition((1, 1))  # Define a posição inicial da janela

        self.tabs_data = {}  # Dicionário para armazenar referências dos componentes por aba
        #self.nome_conta = []
        self.cotacao = []
        self.listaMedas = []
        self.listaContas = []
        self.listaAtivos = []
        self.listaDespesas = []
        self.listaCapital = []
        self.listaRetirada = []
        self.listaRendaAcoes = []
        self.listaRendaProventos = []
        self.listaRendaDespesas = []
        self.listaRendaMesMovel = deque(maxlen=12)
        self.listaGeral = []
        self.lan = []
        self.proventos = []

        self.listaCotacaoAtual = Decimal('1.0')
        self.cotacaoAtual = Decimal('1.0')

        self.totalComprado = Decimal('0.0')
        self.totalCompras = Decimal('0.0')
        self.totalVendas = Decimal('0.0')
        self.totalCompradoReal = Decimal('0.0')
        self.totalComprasReal = Decimal('0.0')
        self.totalVendasReal = Decimal('0.0')

        # Criar Notebook para abas
        self.notebook = wx.Notebook(self)

        # Criar a aba "Total" e componentes base
        self.tab_total = wx.Panel(self.notebook)
        self.notebook.AddPage(self.tab_total, "Total")
        self.criaComponentes(self.tab_total, "Total")

        # Criar abas dinâmicas para cada conta
        self.create_dynamic_tabs()

        self.rendaTotal()

        self.Show()

    def criaComponentes(self, parent, nome_tab):
        """Cria os componentes da aba e adiciona labels acima das caixas de texto"""
        sizer = wx.BoxSizer(wx.VERTICAL)

        # Criar Grid
        grid = wx.grid.Grid(parent, size=(1300, 550))
        grid.CreateGrid(0, 15)

        colunas = ["Ref", "Inicial", "Aporte", "Retirada", "Rendimento", "Provento",
                   "Despesa", "Renda Mês", "Acumulado", "Saldo", "Renda %", "Acum %", "Média %", "12 meses", "12 média"]

        for i, label in enumerate(colunas):
            grid.SetColLabelValue(i, label)

        sizer.Add(grid, 0, wx.ALL, 11)

        self.tabs_data[nome_tab] = {}  # Garante que a aba existe no dicionário
        self.tabs_data[nome_tab]["grid"] = grid  # Salva a referência da grid

        # Lista com os nomes dos campos
        labels = ["Aporte", "Retirada", "Provento", "Renda", "Despesa",
                  "Resultado", "Disponivel", "Comprado", "Patrimonio"]

        # Criar um sizer horizontal para alinhar os labels e textctrls
        h_sizer = wx.BoxSizer(wx.HORIZONTAL)

        #self.tabs_data[nome_tab] = {}  # Dicionário para armazenar referências dos componentes desta aba

        for label in labels:
            v_sizer = wx.BoxSizer(wx.VERTICAL)  # Sizer para alinhar label e campo

            # Criar Label
            lbl = wx.StaticText(parent, label=label, size=(120, 20), style=wx.TE_RIGHT)  # Altura fixa para os labels
            v_sizer.Add(lbl, 0, wx.ALIGN_CENTER | wx.BOTTOM, 2)

            # Criar Campo de Entrada
            #txt = wx.TextCtrl(parent, style=wx.TE_RIGHT, size=(120, -1))
            txt = wx.TextCtrl(parent, style=wx.TE_RIGHT, size=(120, 25))  # Altura fixa para os campos
            v_sizer.Add(txt, 0, wx.EXPAND)

            self.tabs_data[nome_tab][f"txt{label}"] = txt  # Armazena o campo no dicionário

            h_sizer.Add(v_sizer, 0, wx.ALL, 5)

        sizer.Add(h_sizer, 0, wx.ALL | wx.EXPAND, 10)
        parent.SetSizer(sizer)

        #return grid

    def create_dynamic_tabs(self):
        contas = Conta.mc_busca_contas_e_ultimacotacao()

        for id_conta, nomeconta, nomemoeda, cotacaoMoeda in contas:
            if cotacaoMoeda is None:
                valor = Decimal(1.0)
            else:
                valor = cotacaoMoeda
            self.listaContas.append([id_conta, nomeconta, nomemoeda, valor])

            tab = wx.Panel(self.notebook)
            self.notebook.AddPage(tab, nomeconta)

            # cria os componentes e retorna o grid
            grid = self.criaComponentes(tab, nomeconta)

            # adiciona informações extras na aba
            self.tabs_data[nomeconta]["id"] = id_conta
            self.tabs_data[nomeconta]["moeda"] = nomemoeda
            self.tabs_data[nomeconta]["cotacao"] = valor #devolveFloatDeDecimal(valor, 6)

    def removeTab(self, nome_tab):
        """Remove uma aba do Notebook pelo nome"""
        for index in range(self.notebook.GetPageCount()):
            if self.notebook.GetPageText(index) == nome_tab:
                self.notebook.RemovePage(index)
                return  # Para evitar problemas ao alterar os índices dinamicamente

    def encheListaCotacao(self):
        listaMoedas = Cotacao.getListaMoedas()
        cotacao = 0.0
        for nomemoeda, id in listaMoedas:
            if nomemoeda == 'REAL':
                cotacao, nome = 1, nomemoeda
            else:
                cotacao, nome = Cotacao.mc_get_ultima_cotacao(id)
            self.cotacao.append([id, nomemoeda, cotacao])

    def buscaCotacao(self, conta):
        cotacao = 1.0
        for row in self.listaContas:
            if row[0] == conta:
                nomeMoeda = row[2]
                for linha in self.cotacao:
                    if linha[1] == nomeMoeda:
                        cotacao = linha[2]
                        break
        return cotacao

    def rendaTotal(self):
        for row in self.listaContas:
            self.listaAtivos = AtivoNegociado.mc_devolve_id_ativo_negociado_por_conta(idconta=row[0])
            if len(self.listaAtivos) == 0:
                self.removeTab(row[1])
            else:
                self.listaGeral.clear()
                self.listaRendaMesMovel.clear()
                self.cotacaoAtual = row[3]  #devolveFloatDeDecimal(row[3], 2)
                self.buscaRendaPorAtivo(row[0])
                self.buscaDespesas(row[0])
                self.buscaCapital(row[0])
                self.juntaListas()
                self.montaGrid(row[1])

        self.listaRendaMesMovel.clear()
        self.consolidaRendimentos()

    def buscaRendaPorAtivo(self, idconta):
        self.listaRendaAcoes.clear()
        self.listaRendaProventos.clear()
        self.listaRendaDespesas.clear()
        self.totalComprado = Decimal('0.0')
        self.totalCompras = Decimal('0.0')
        self.totalVendas = Decimal('0.0')

        for row in self.listaAtivos:
            self.lan = AtivoNegociado.mc_devolve_lancamentos_ativo__por_conta(idativo=row[0], idconta=idconta)
            self.proventos = Provento.mc_busca_proventos_por_conta_ativo(row[0], idconta, True)
            comprado, compras, vendas = self.encheListaRendaAcoes()
            self.encheListaRendaProventos()
            self.totalComprado += comprado
            self.totalCompras += compras
            self.totalVendas += vendas
            self.totalCompradoReal += comprado * self.cotacaoAtual
            self.totalComprasReal += compras * self.cotacaoAtual
            self.totalVendasReal += vendas * self.cotacaoAtual

    def getCotacaoTab(self, nomeTab):
        """
        Retorna a cotação associada a uma aba pelo nome.
        Se não existir ou não tiver cotação, retorna 1.
        """
        if nomeTab in self.tabs_data:
            return self.tabs_data[nomeTab].get("cotacao", 1)
        return Decimal('1.0')

    def encheListaRendaAcoes(self):
        saldoQtde = 0
        precomedio = Decimal('0.0')
        compras = Decimal('0.0')
        vendas = Decimal('0.0')
        listaProvisoria = []
        for  row in self.lan:
            dataOperacao = row[1]
            numoperacao = int(row[2])
            valorOperacao = row[4]  #devolveFloatDeDecimal(row[4], 2) 
            qtdeOperacao = int(row[3])
            if numoperacao == 1:
                totalOperacao = qtdeOperacao * valorOperacao
                compras += totalOperacao
                if precomedio > 0:
                    precomedio = ((precomedio * saldoQtde) + totalOperacao) / (saldoQtde + qtdeOperacao)
                else:
                    precomedio = valorOperacao
                    
                saldoQtde += qtdeOperacao

            else:
                totalOperacao = valorOperacao * qtdeOperacao
                vendas += totalOperacao
                resultado = totalOperacao - (qtdeOperacao * precomedio)

                saldoQtde -= qtdeOperacao
                if saldoQtde == 0:
                    precomedio = Decimal('0.0')

                if resultado != Decimal('0.0'):
                    listaProvisoria.append([dataOperacao, resultado])
                
        comprado = saldoQtde * precomedio

        for row in listaProvisoria:
            dataOperacao = row[0].strftime("%Y/%m")
            valorRendimento = row[1] #devolveFloatDeDecimal(row[1], 2) 
            if len(self.listaRendaAcoes) == 0:
                self.listaRendaAcoes.append([dataOperacao, valorRendimento])
            else:
                indice = next((i for i, linha in enumerate(self.listaRendaAcoes) if linha[0] == dataOperacao), -1)
                if indice < 0:
                    self.listaRendaAcoes.append([dataOperacao, valorRendimento])
                else:
                    self.listaRendaAcoes[indice][1] += valorRendimento
        return comprado, compras, vendas

    def encheListaRendaProventos(self):
        for row in self.proventos:
            dataOperacao = row[1].strftime("%Y/%m")
            valorRendimento = row[2] #devolveFloatDeDecimal(row[2], 2) 
            if len(self.listaRendaProventos) == 0:
                self.listaRendaProventos.append([dataOperacao, valorRendimento])
            else:
                for item in self.listaRendaProventos:
                    if item[0] == dataOperacao:
                        item[1] += valorRendimento
                        break
                else:
                    self.listaRendaProventos.append([dataOperacao, valorRendimento])

    def buscaDespesas(self, idconta):
        self.listaDespesas.clear()
        lista = Despesa.mc_busca_despesas_por_conta(idconta)
        for row in lista:
            dataOperacao = row[0].strftime("%Y/%m")
            #valor = float(int(row[1] * 100.0) / 100.0)# * self.cotacaoAtual
            #cem = Decimal('100.00')
            valor = row[1] #devolveFloatDeDecimal(row[1], 2) 
            if len(self.listaDespesas) == 0:
                self.listaDespesas.append([dataOperacao, valor])
            else:
                for item in self.listaDespesas:
                    if item[0] == dataOperacao:
                        item[1] += valor
                        break
                else:
                    self.listaDespesas.append([dataOperacao, valor])
    
    def buscaCapital(self, idconta):
        lista = Capital.mc_busca_capital_por_conta(idconta)
        self.listaCapital.clear()
        self.listaRetirada.clear()
        for row in lista:
            dataOperacao = row[0].strftime("%Y/%m")
            valor = row[1] #devolveFloatDeDecimal(row[1], 2) 
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
                    self.listaGeral.append([ref, 0, 0, 0, valor, 0])

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

    def devolve_renda_media_movel(self, rendimento_mes):
        # adiciona o novo rendimento (já faz o shift automático se passar de 12)
        self.listaRendaMesMovel.append(rendimento_mes)

        # cálculo do acumulado geométrico
        rendaPercAcm = 1.0
        for r in self.listaRendaMesMovel:
            rendaPercAcm *= (1 + r)
        rendaPercAcm -= 1

        # cálculo da média geométrica equivalente
        rendaMedia = (1 + rendaPercAcm) ** (1 / len(self.listaRendaMesMovel)) - 1

        # retorna apenas os cálculos, a lista já foi atualizada por referência
        return rendaMedia, rendaPercAcm

    def montaGrid(self, nometab):
        listaOrdenada = sorted(self.listaGeral, key=lambda x: x[0])

        grid = self.ponteiroGrid(nometab)
        grid.ClearGrid()
        if grid.GetNumberRows() > 0:
            grid.DeleteRows(0, grid.GetNumberRows())
        linha = (-1)
        rendaAcumulada = Decimal('0.0')
        inicial = Decimal('0.0')
        saldo = Decimal('0.0')
        rendPercAcm = 0.0
        rendaMedia = 0.0
        rendaAno = zero

        totalAporte  = Decimal('0.0')
        totalRetirada = Decimal('0.0')
        totalProventos = Decimal('0.0')
        totalRenda = Decimal('0.0')
        totalDespesas = Decimal('0.0')
        totalResultado = Decimal('0.0')
        if nometab == "XP - Neovalor":
            a = 9
        for row in listaOrdenada:

            linha += 1
            grid.AppendRows()
            grid.SetCellValue(linha, 0, str(row[0]))

            aporte = row[1]
            retirada = row[2] * Decimal('-1.0')
            rendimento = row[3]
            provento = row[4]
            despesa = row [5]
            rendaMes = rendimento + provento - despesa
            inicial = saldo + aporte - retirada
            #saldo = saldo + aporte - retirada + rendimento + provento - despesa
            saldo = inicial + rendimento + provento - despesa
            rendaAcumulada = rendaAcumulada + rendimento + provento - despesa
            if inicial != Decimal('0.0'):
                auxDecimal = ((inicial + rendimento + provento - despesa) / inicial) -1
                rendperc = devolveFloatDeDecimal(auxDecimal, 6)
            else:
                rendperc = 0.0
            if linha > 0:
                rendPercAcm = (1 + rendperc) * (1 + rendPercAcm) - 1
                rendaMedia = ((1 + rendPercAcm) ** (1 / (linha + 1))) - 1
                
            else:
               rendPercAcm = rendperc
               rendaMedia = rendperc
               rendaAno = rendaMes
               
            rendaMediaAno, rendaAno = self.devolve_renda_media_movel(rendperc)

            totalAporte += aporte
            totalRetirada += retirada
            totalProventos += provento
            totalRenda += rendimento
            totalDespesas += despesa
            totalResultado += rendaMes

            #rendimento = float(int(rendimento * 100.0) / 100.0)

            grid.SetCellValue(linha, 1, formata_numero(inicial))
            grid.SetCellValue(linha, 2, formata_numero(aporte))
            grid.SetCellValue(linha, 3, formata_numero(retirada))
            grid.SetCellValue(linha, 4, formata_numero(rendimento))
            if rendimento < 0 : grid.SetCellTextColour(linha, 4, wx.RED)
            grid.SetCellValue(linha, 5, formata_numero(provento))
            grid.SetCellValue(linha, 6, formata_numero(despesa))
            grid.SetCellValue(linha, 7, formata_numero(rendaMes))
            if rendaMes < 0: grid.SetCellTextColour(linha, 7, wx.RED)
            grid.SetCellValue(linha, 8, formata_numero(rendaAcumulada))
            if rendaAcumulada < 0: grid.SetCellTextColour(linha, 8, wx.RED)
            grid.SetCellValue(linha, 9, formata_numero(saldo))
            grid.SetCellValue(linha, 10, formata_numero(rendperc * 100.0))
            if rendperc < 0: grid.SetCellTextColour(linha, 10, wx.RED)
            grid.SetCellValue(linha, 11, formata_numero(rendPercAcm * 100.0))
            if rendPercAcm < 0: grid.SetCellTextColour(linha, 11, wx.RED)
            grid.SetCellValue(linha, 12, formata_numero(rendaMedia * 100.0))
            try:
                if rendaMedia < zero: 
                    grid.SetCellTextColour(linha, 12, wx.RED)
            except Exception as e:
                print(e)
                print("Na linha " + str(linha))
            grid.SetCellValue(linha, 13, formata_numero(rendaAno * 100.0))
            if rendaAno < zero: 
                grid.SetCellTextColour(linha, 13, wx.RED)
            grid.SetCellValue(linha, 14, formata_numero(rendaMediaAno * 100.0))
            if rendaMediaAno < zero: 
                grid.SetCellTextColour(linha, 14, wx.RED)

            grid.SetCellAlignment(linha,  0, wx.ALIGN_CENTRE, wx.ALIGN_CENTRE)
            grid.SetCellAlignment(linha,  1, wx.ALIGN_RIGHT, wx.ALIGN_RIGHT)
            grid.SetCellAlignment(linha,  2, wx.ALIGN_RIGHT, wx.ALIGN_RIGHT)
            grid.SetCellAlignment(linha,  3, wx.ALIGN_RIGHT, wx.ALIGN_RIGHT)
            grid.SetCellAlignment(linha,  4, wx.ALIGN_RIGHT, wx.ALIGN_RIGHT)
            grid.SetCellAlignment(linha,  5, wx.ALIGN_RIGHT, wx.ALIGN_RIGHT)
            grid.SetCellAlignment(linha,  6, wx.ALIGN_RIGHT, wx.ALIGN_RIGHT)
            grid.SetCellAlignment(linha,  7, wx.ALIGN_RIGHT, wx.ALIGN_RIGHT)
            grid.SetCellAlignment(linha,  8, wx.ALIGN_RIGHT, wx.ALIGN_RIGHT)
            grid.SetCellAlignment(linha,  9, wx.ALIGN_RIGHT, wx.ALIGN_RIGHT)
            grid.SetCellAlignment(linha, 10, wx.ALIGN_CENTRE, wx.ALIGN_CENTRE)
            grid.SetCellAlignment(linha, 11, wx.ALIGN_CENTRE, wx.ALIGN_CENTRE)
            grid.SetCellAlignment(linha, 12, wx.ALIGN_CENTRE, wx.ALIGN_CENTRE)
            grid.SetCellAlignment(linha, 13, wx.ALIGN_CENTRE, wx.ALIGN_CENTRE)
            grid.SetCellAlignment(linha, 14, wx.ALIGN_CENTRE, wx.ALIGN_CENTRE)

            if linha % 2 != 0:
                for i in range(0, 15):
                    grid.SetCellBackgroundColour(linha, i, wx.Colour(230, 255, 255))

        #self.totalDisponivel = saldo - self.totalComprado
        self.totalDisponivel = totalAporte - totalRetirada - totalDespesas + totalProventos + self.totalVendas - self.totalCompras
        self.totalPatrimonio = self.totalDisponivel + self.totalComprado

        self.atualiza_valor(nometab, "txtAporte", formata_numero(totalAporte))
        self.atualiza_valor(nometab, "txtRetirada", formata_numero(totalRetirada))
        self.atualiza_valor(nometab, "txtProvento", formata_numero(totalProventos))
        self.atualiza_valor(nometab, "txtRenda", formata_numero(totalRenda))
        self.atualiza_valor(nometab, "txtDespesa", formata_numero(totalDespesas))
        self.atualiza_valor(nometab, "txtResultado", formata_numero(totalResultado))
        self.atualiza_valor(nometab, "txtDisponivel", formata_numero(self.totalDisponivel))
        self.atualiza_valor(nometab, "txtComprado", formata_numero(self.totalComprado))
        self.atualiza_valor(nometab, "txtPatrimonio", formata_numero(self.totalPatrimonio))


    def consolidaRendimentos(self):
        """
        Consolida os valores das abas individuais na aba 'Total'.
        Soma por data e aplica a cotação de cada conta.
        """

        # garante que a aba Total existe
        if "Total" not in self.tabs_data:
            return

        grid_total = self.tabs_data["Total"]["grid"]

        # dicionário: {data: {coluna: valor}}
        consolidados = {}

        # percorre todas as abas (menos a Total)
        for nome_tab, componentes in self.tabs_data.items():
            if nome_tab == "Total":
                continue

            grid = componentes["grid"]
            cotacao = componentes.get("cotacao", 1)

            # percorre as linhas da grid
            for row in range(grid.GetNumberRows()):
                data = grid.GetCellValue(row, 0).strip()
                if not data:
                    continue

                if data not in consolidados:
                    consolidados[data] = {"Inicial": 0,"Aporte": 0,"Retirada": 0,"Rendimento": 0,"Provento": 0,"Despesa": 0,}

                # mapeia colunas fixas
                for col_nome, col_idx in {"Inicial": 1,"Aporte": 2,"Retirada": 3,"Rendimento": 4,"Provento": 5,"Despesa": 6,}.items():
                    valor_str = grid.GetCellValue(row, col_idx)
                    valor_str = valor_str.replace(".", "")
                    valor_str = valor_str.replace(",", ".")
                    #valor_str = grid.GetCellValue(row, col_idx).replace(",", ".")
                    try:
                        valor = Decimal(valor_str) if valor_str else zero
                    except ValueError:
                        valor = zero
                    if valor == 0:
                        valor = Decimal('0.00')
                    consolidados[data][col_nome] += valor * cotacao

        # limpa a grid Total
        grid_total.ClearGrid()
        if grid_total.GetNumberRows() > 0:
            grid_total.DeleteRows(0, grid_total.GetNumberRows())

        # insere as linhas consolidadas ordenadas por data
        for data in sorted(consolidados.keys()):
            linha = grid_total.GetNumberRows()
            grid_total.AppendRows(1)
            grid_total.SetCellValue(linha, 0, data)

            grid_total.SetCellValue(linha, 1, f"{consolidados[data]['Inicial']:.2f}")
            grid_total.SetCellValue(linha, 2, f"{consolidados[data]['Aporte']:.2f}")
            grid_total.SetCellValue(linha, 3, f"{consolidados[data]['Retirada']:.2f}")
            grid_total.SetCellValue(linha, 4, f"{consolidados[data]['Rendimento']:.2f}")
            grid_total.SetCellValue(linha, 5, f"{consolidados[data]['Provento']:.2f}")
            grid_total.SetCellValue(linha, 6, f"{consolidados[data]['Despesa']:.2f}")

        # aqui você pode recalcular as demais colunas da aba Total (Renda Mês, Acumulado, % etc)

        linha = (-1)
        rendaAcumulada = zero
        inicial = zero
        saldo = zero
        rendPercAcm = 0.0
        rendaMedia = 0.0

        totalAporte  = zero       
        totalRetirada = zero
        totalProventos = zero
        totalRenda = zero
        totalDespesas = zero
        totalResultado = zero

        for row in range(grid_total.GetNumberRows()):
            
            linha += 1
            aporte = devolveDecimalDeFloat(grid_total.GetCellValue(row, 2), 2)
            retirada = devolveDecimalDeFloat(grid_total.GetCellValue(row, 3), 2)
            rendimento = devolveDecimalDeFloat(grid_total.GetCellValue(row, 4), 2)
            provento = devolveDecimalDeFloat(grid_total.GetCellValue(row, 5), 2)
            despesa = devolveDecimalDeFloat(grid_total.GetCellValue(row, 6), 2)
            rendaMes = rendimento + provento - despesa

            inicial = saldo + aporte - retirada
            saldo = inicial + rendimento + provento - despesa
            rendaAcumulada = rendaAcumulada + rendimento + provento - despesa
            if inicial != zero:
                auxdecimal = ((inicial + rendimento + provento - despesa) / inicial) -1
                rendperc = devolveFloatDeDecimal(auxdecimal, 6)  
            else:
                rendperc = 0.0
            if linha > 0:
               rendPercAcm = (1 + rendperc) * (1 + rendPercAcm) - 1
               rendaMedia = ((1 + rendPercAcm) ** (1 / (linha + 1))) - 1
            else:
               rendPercAcm = rendperc
               rendaMedia = rendperc

            rendaMediaAno, rendaAno = self.devolve_renda_media_movel(rendperc)

            totalAporte += aporte
            totalRetirada += retirada
            totalProventos += provento
            totalRenda += rendimento
            totalDespesas += despesa
            totalResultado += rendaMes

            #rendimento = float(int(rendimento * 100.0) / 100.0)

            grid_total.SetCellValue(row, 1, formata_numero(inicial))
            grid_total.SetCellValue(row, 2, formata_numero(aporte))
            grid_total.SetCellValue(row, 3, formata_numero(retirada))
            grid_total.SetCellValue(row, 4, formata_numero(rendimento))
            if rendimento < 0 : grid_total.SetCellTextColour(row, 4, wx.RED)
            grid_total.SetCellValue(row, 5, formata_numero(provento))
            grid_total.SetCellValue(row, 6, formata_numero(despesa))
            grid_total.SetCellValue(linha, 7, formata_numero(rendaMes))
            if rendaMes < 0: grid_total.SetCellTextColour(row, 7, wx.RED)
            grid_total.SetCellValue(row, 8, formata_numero(rendaAcumulada))
            if rendaAcumulada < 0: grid_total.SetCellTextColour(row, 8, wx.RED)
            grid_total.SetCellValue(row, 9, formata_numero(saldo))
            grid_total.SetCellValue(row, 10, formata_numero(rendperc * 100.0))
            if rendperc < 0: grid_total.SetCellTextColour(row, 10, wx.RED)
            grid_total.SetCellValue(row, 11, formata_numero(rendPercAcm * 100.0))
            if rendPercAcm < 0: grid_total.SetCellTextColour(row, 11, wx.RED)
            grid_total.SetCellValue(row, 12, formata_numero(rendaMedia * 100.0))
            if rendaMedia < 0: 
                grid_total.SetCellTextColour(row, 12, wx.RED)
            grid_total.SetCellValue(row, 13, formata_numero(rendaAno * 100.0))
            if rendaAno < 0: 
                grid_total.SetCellTextColour(row, 13, wx.RED)
            grid_total.SetCellValue(row, 14, formata_numero(rendaMediaAno * 100.0))
            if rendaMediaAno < 0: 
                grid_total.SetCellTextColour(row, 14, wx.RED)

            grid_total.SetCellAlignment(row,  0, wx.ALIGN_CENTRE, wx.ALIGN_CENTRE)
            grid_total.SetCellAlignment(row,  1, wx.ALIGN_RIGHT, wx.ALIGN_RIGHT)
            grid_total.SetCellAlignment(row,  2, wx.ALIGN_RIGHT, wx.ALIGN_RIGHT)
            grid_total.SetCellAlignment(row,  3, wx.ALIGN_RIGHT, wx.ALIGN_RIGHT)
            grid_total.SetCellAlignment(row,  4, wx.ALIGN_RIGHT, wx.ALIGN_RIGHT)
            grid_total.SetCellAlignment(row,  5, wx.ALIGN_RIGHT, wx.ALIGN_RIGHT)
            grid_total.SetCellAlignment(row,  6, wx.ALIGN_RIGHT, wx.ALIGN_RIGHT)
            grid_total.SetCellAlignment(row,  7, wx.ALIGN_RIGHT, wx.ALIGN_RIGHT)
            grid_total.SetCellAlignment(row,  8, wx.ALIGN_RIGHT, wx.ALIGN_RIGHT)
            grid_total.SetCellAlignment(row,  9, wx.ALIGN_RIGHT, wx.ALIGN_RIGHT)
            grid_total.SetCellAlignment(row, 10, wx.ALIGN_CENTRE, wx.ALIGN_CENTRE)
            grid_total.SetCellAlignment(row, 11, wx.ALIGN_CENTRE, wx.ALIGN_CENTRE)
            grid_total.SetCellAlignment(row, 12, wx.ALIGN_CENTRE, wx.ALIGN_CENTRE)
            grid_total.SetCellAlignment(row, 13, wx.ALIGN_CENTRE, wx.ALIGN_CENTRE)
            grid_total.SetCellAlignment(row, 14, wx.ALIGN_CENTRE, wx.ALIGN_CENTRE)

            if linha % 2 != 0:
                for i in range(0, 15):
                    grid_total.SetCellBackgroundColour(row, i, wx.Colour(230, 255, 255))

        self.totalDisponivel = totalAporte - totalRetirada - totalDespesas + totalProventos + self.totalVendasReal - self.totalComprasReal
        self.totalPatrimonio = self.totalDisponivel + self.totalCompradoReal

        self.atualiza_valor('Total', "txtAporte", formata_numero(totalAporte))
        self.atualiza_valor('Total', "txtRetirada", formata_numero(totalRetirada))
        self.atualiza_valor('Total', "txtProvento", formata_numero(totalProventos))
        self.atualiza_valor('Total', "txtRenda", formata_numero(totalRenda))
        self.atualiza_valor('Total', "txtDespesa", formata_numero(totalDespesas))
        self.atualiza_valor('Total', "txtResultado", formata_numero(totalResultado))
        self.atualiza_valor('Total', "txtDisponivel", formata_numero(self.totalDisponivel))
        self.atualiza_valor('Total', "txtComprado", formata_numero(self.totalCompradoReal))
        self.atualiza_valor('Total', "txtPatrimonio", formata_numero(self.totalPatrimonio))

    def atualiza_valor(self, nome_tab, campo, valor):
        """Atualiza o valor de um campo na aba correta"""
        trimmedCampo = str(campo).strip()
        if nome_tab in self.tabs_data and trimmedCampo in self.tabs_data[nome_tab]:
            self.tabs_data[nome_tab][trimmedCampo].SetValue(str(valor))

    def ponteiroGrid(self, nome_tab):
        if nome_tab in self.tabs_data and "grid" in self.tabs_data[nome_tab]:
            return self.tabs_data[nome_tab]["grid"]
        else:
            return None

    def listaGridsAtivos(self):
        """Retorna uma lista com os ponteiros das grids das tabs ativas."""
        grids_ativos = []

        for nome_tab, componentes in self.tabs_data.items():
            if "grid" in componentes:
                grids_ativos.append(componentes["grid"])

        return grids_ativos

def main():

    app = wx.App(False)
    frame = FrmRendaTotal()

    # Exemplo de atualização de valores em diferentes abas
    #frame.atualiza_valor("Total", "txtAporte", 5000)
    #frame.atualiza_valor(frame.nome_conta[0], "txtAporte", 3000)
    #frame.atualiza_valor(frame.nome_conta[2], "txtAporte", 2000)

    app.MainLoop()

if __name__ == '__main__':
    main()