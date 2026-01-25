#import wx
from decimal import *
import wx.grid
from ativoNegociado import AtivoNegociado
from cotacao import *
from despesa import Despesa
from conta import Conta
from capital import Capital
from diversos import *
from collections import defaultdict
from collections import deque

from provento import Provento

class FrmRendaDiaria(wx.Frame):
    def __init__(self):
        super().__init__(None, title="Consolidação de rendimentos - Renda Variável", size=(1350, 730),
                         style=wx.DEFAULT_FRAME_STYLE & ~wx.RESIZE_BORDER & ~wx.MAXIMIZE_BOX)
        self.SetPosition((1, 1))  # Define a posição inicial da janela

        self.tabs_data = {}  # Dicionário para armazenar referências dos componentes por aba
        self.dados_por_mes = {}   
        self.dados_total = defaultdict(lambda: {
            "aporte": zero,
            "retirada": zero,
            "rendimento": zero,
            "provento": zero,
            "despesa": zero,
            "capital_base": zero,
            "resultado_dia": zero,
            "resultado_acumulado": zero,
            "renda_pct": zero,
            "renda_acumulada": zero,
            "saldo_fim": zero,
            "renda_media": zero,
            "no_ano": zero,
            "no_ano_media": zero,
        })
  
        self.meses_expandidos = {}   
        self.nome_conta = []
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

        self.meses_expandidos = {}


        # Criar abas dinâmicas para cada conta
        self.create_dynamic_tabs()

        self.rendaTotal()

        self.Show()

    def novo_registro(self):
        return {
            "aporte": zero,
            "retirada": zero,
            "rendimento": zero,
            "provento": zero,
            "despesa": zero,
            "capital_base": zero,
            "resultado_dia": zero,
            "resultado_acumulado": zero,
            "renda_pct": zero,
            "renda_acumulada": zero,
            "saldo_fim": zero,
            "renda_media": zero,
            "no_ano": zero,
            "no_ano_media": zero,
        }

    def criaComponentes(self, parent, nome_tab):
        """Cria os componentes da aba e adiciona labels acima das caixas de texto"""
        sizer = wx.BoxSizer(wx.VERTICAL)

        # Criar Grid
        grid = wx.grid.Grid(parent, size=(1300, 550))
        grid.CreateGrid(0, 15)
        grid.Bind(wx.grid.EVT_GRID_CELL_RIGHT_CLICK, self.onRightClickGrid)


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

    def onRightClickGrid(self, event):
        grid = event.GetEventObject()
        row = event.GetRow()

        #valor = grid.GetCellValue(row, 0)
        texto = grid.GetCellValue(row, 0)
        valor = texto.replace(ICONE_FECHADO, "").replace(ICONE_ABERTO, "").strip()


        # descobre o nome da aba a partir do grid
        nome_tab = None
        for tab, data in self.tabs_data.items():
            if data.get("grid") is grid:
                nome_tab = tab
                break

        if nome_tab is None:
            return

        # só reage a linhas de mês
        if "/" in valor and len(valor) == 7:  # "YYYY/MM"
            menu = wx.Menu()

            if valor in self.meses_expandidos:
                item = menu.Append(wx.ID_ANY, "Recolher dias")
            else:
                item = menu.Append(wx.ID_ANY, "Expandir dias")

            self.Bind(
                wx.EVT_MENU,
                lambda evt, mes=valor, tab=nome_tab: self.toggleMes(mes, tab),
                item
            )

            grid.PopupMenu(menu)
            menu.Destroy()

    def toggleMes(self, mes, nome_tab):
        if nome_tab not in self.meses_expandidos:
            self.meses_expandidos[nome_tab] = set()

        if mes in self.meses_expandidos[nome_tab]:
            self.meses_expandidos[nome_tab].remove(mes)
        else:
            self.meses_expandidos[nome_tab].add(mes)

        self.montaGrid(nome_tab)


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
        
        #self.dados_por_mes = defaultdict(lambda: {
        #    "dias": defaultdict(self.novo_registro),
        #    "consolidado": self.novo_registro()
        #})

        self.dados_por_mes.clear()

        for row in self.listaContas:
            id_conta = row[0]
            nome_tab = row[1]

            self.dados_por_mes[nome_tab] = defaultdict(lambda: {
                "dias": defaultdict(self.novo_registro),
                "consolidado": self.novo_registro()
            })

            self.listaAtivos = AtivoNegociado.mc_devolve_id_ativo_negociado_por_conta(idconta=row[0])
            if len(self.listaAtivos) == 0:
                self.removeTab(row[1])
            else:
                self.listaGeral.clear()
                self.listaRendaMesMovel.clear()
                self.cotacaoAtual = row[3]  #devolveFloatDeDecimal(row[3], 2)
                self.buscaRendaPorAtivo(row[0], nome_tab)
                self.buscaDespesas(row[0], nome_tab)
                self.buscaCapital(row[0], nome_tab)
                self.calcula_rendimento_diario(nome_tab)
                self.consolida_por_mes(nome_tab)
                self.consolida_percentual_mensal(nome_tab)
                self.montaGrid(nome_tab)

        self.consolida_total()
        self.montaGridTotal()

    def buscaRendaPorAtivo(self, idconta, nome_tab):
        """
        Processa todos os ativos da conta, acumulando:
        - rendimentos por DIA
        - proventos por DIA
        - totais de comprado, compras e vendas

        NÃO consolida por mês
        NÃO mexe em grid
        """

        # ==========================
        # ZERA ESTADO DA CONTA
        # ==========================

        self.totalComprado = zero
        self.totalCompras = zero
        self.totalVendas = zero

        self.totalCompradoReal = zero
        self.totalComprasReal = zero
        self.totalVendasReal = zero

        # ==========================
        # PROCESSA ATIVOS
        # ==========================
        for ativo in self.listaAtivos:
            id_ativo = ativo[0]

            # lançamentos de compra/venda
            lancamentos = AtivoNegociado.mc_devolve_lancamentos_ativo__por_conta(
                idativo=id_ativo,
                idconta=idconta
            )

            # proventos pagos
            proventos = Provento.mc_busca_proventos_por_conta_ativo(
                id_ativo, idconta, True
            )

            comprado, compras, vendas = self._processa_lancamentos_ativo(lancamentos, nome_tab)
            self._processa_proventos_ativo(proventos, nome_tab)

            # ==========================
            # TOTAIS DA CONTA
            # ==========================
            self.totalComprado += comprado
            self.totalCompras += compras
            self.totalVendas += vendas

            self.totalCompradoReal += comprado * self.cotacaoAtual
            self.totalComprasReal += compras * self.cotacaoAtual
            self.totalVendasReal += vendas * self.cotacaoAtual

    def _processa_lancamentos_ativo(self, lancamentos, nome_tab):
        saldo_qtde = 0
        preco_medio = zero

        compras = zero
        vendas = zero
        comprado = zero

        for row in lancamentos:
            data = row[1]
            operacao = int(row[2])   # 1 compra / 2 venda
            qtde = int(row[3])
            preco = row[4]

            dia = data.strftime("%Y/%m/%d")
            mes = data.strftime("%Y/%m")

            if operacao == 1:  # COMPRA
                total = qtde * preco
                compras += total

                if saldo_qtde > 0:
                    preco_medio = ((preco_medio * saldo_qtde) + total) / (saldo_qtde + qtde)
                else:
                    preco_medio = preco

                saldo_qtde += qtde

            else:  # VENDA
                total = qtde * preco
                vendas += total

                resultado = total - (qtde * preco_medio)

                saldo_qtde -= qtde
                if saldo_qtde == 0:
                    preco_medio = zero

                if resultado != 0:
                    self.dados_por_mes[nome_tab][mes]["dias"][dia]["rendimento"] += resultado

        comprado = saldo_qtde * preco_medio
        return comprado, compras, vendas

    def _processa_proventos_ativo(self, proventos, nome_tab):
        for row in proventos:
            data = row[1]
            valor = row[2]

            dia = data.strftime("%Y/%m/%d")
            mes = data.strftime("%Y/%m")

            self.dados_por_mes[nome_tab][mes]["dias"][dia]["provento"] += valor

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
            dataOperacao = row[0].strftime("%Y/%m/%d")
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
            dataOperacao = row[1].strftime("%Y/%m/%d")
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

    def buscaDespesas(self, idconta, nome_tab):
        
        lista = Despesa.mc_busca_despesas_por_conta(idconta)
        for row in lista:
            data = row[0]
            valor = row[1]

            dia = data.strftime("%Y/%m/%d")
            mes = data.strftime("%Y/%m")

            self.dados_por_mes[nome_tab][mes]["dias"][dia]["despesa"] += valor

    def buscaCapital(self, idconta, nome_tab):
        
        #Processa aportes e retiradas da conta.
        #Registra valores POR DIA dentro de self.dados_por_mes.
        

        lista = Capital.mc_busca_capital_por_conta(idconta)

        for row in lista:
            data = row[0]
            valor = row[1]

            dia = data.strftime("%Y/%m/%d")
            mes = data.strftime("%Y/%m")

            if valor >= 0:
                self.dados_por_mes[nome_tab][mes]["dias"][dia]["aporte"] += valor
            else:
                # retirada sempre positiva no modelo
                self.dados_por_mes[nome_tab][mes]["dias"][dia]["retirada"] += valor * -1

    def devolve_renda_media_movel(self, rendimento_mes):
        # adiciona o novo rendimento (já faz o shift automático se passar de 12)
        self.listaRendaMesMovel.append(rendimento_mes)

        # cálculo do acumulado geométrico
        rendaPercAcm = um
        for r in self.listaRendaMesMovel:
            rendaPercAcm *= (1 + r)
        rendaPercAcm -= 1

        # cálculo da média geométrica equivalente
        rendaMedia = (1 + rendaPercAcm) ** (1 / Decimal(len(self.listaRendaMesMovel))) - 1

        # retorna apenas os cálculos, a lista já foi atualizada por referência
        return rendaMedia, rendaPercAcm

    def montaGrid(self, nometab):
        grid = self.ponteiroGrid(nometab)

        grid.ClearGrid()
        if grid.GetNumberRows() > 0:
            grid.DeleteRows(0, grid.GetNumberRows())

        linha = -1
        rendaAcumulada = zero
        rendPercAcm = zero

        saldo = zero

        for mes in sorted(self.dados_por_mes[nometab].keys()):
            dados = self.dados_por_mes[nometab][mes]
            cons = dados["consolidado"]

            aporte = cons["aporte"]
            retirada = cons["retirada"]
            rendimento = cons["rendimento"]
            provento = cons["provento"]
            despesa = cons["despesa"]
            rendaMes = cons["resultado_dia"]
            rendaAcumulada = cons["resultado_acumulado"]
            rendPercAcm = cons['renda_acumulada']
            renda_media = cons['renda_media']
            renda_ano = cons['no_ano']
            renda_ano_media = cons['no_ano_media']
            rend_mensal = cons["renda_pct"]
            saldo_fim = cons["saldo_fim"]

            """
            rendaMes = rendimento + provento - despesa
            rendaAcumulada += rendaMes

            ultimo_dia = sorted(dados["dias"].keys())[-1]
            saldo = dados["dias"][ultimo_dia]["saldo_fim"]

            rend_mensal = cons["renda_pct"]

            if linha >= 0:
                rendPercAcm = (Decimal("1") + rend_mensal) * (Decimal("1") + rendPercAcm) - Decimal("1")
            else:
                rendPercAcm = rend_mensal
            """

            linha += 1
            grid.AppendRows(1)

            #grid.SetCellValue(linha, 0, mes)
            meses_abertos = self.meses_expandidos.get(nometab, set())
            icone = ICONE_ABERTO if mes in meses_abertos else ICONE_FECHADO

            grid.SetCellValue(linha, 0, f"{icone} {mes}")

            grid.SetCellValue(linha, 1, formata_numero(saldo_fim - rendaMes))
            grid.SetCellValue(linha, 2, formata_numero(aporte))
            grid.SetCellValue(linha, 3, formata_numero(retirada))
            grid.SetCellValue(linha, 4, formata_numero(rendimento))
            grid.SetCellValue(linha, 5, formata_numero(provento))
            grid.SetCellValue(linha, 6, formata_numero(despesa))
            grid.SetCellValue(linha, 7, formata_numero(rendaMes))
            grid.SetCellValue(linha, 8, formata_numero(rendaAcumulada))
            grid.SetCellValue(linha, 9, formata_numero(saldo_fim))
            grid.SetCellValue(linha,10, formata_numero(rend_mensal * 100))
            grid.SetCellValue(linha,11, formata_numero(rendPercAcm * 100))
            grid.SetCellValue(linha,12, formata_numero(renda_media * 100))
            grid.SetCellValue(linha,13, formata_numero(renda_ano * 100))
            grid.SetCellValue(linha,14, formata_numero(renda_ano_media * 100))

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
                    grid.SetCellBackgroundColour(linha, i, wx.Colour(cor_azulzinho))

            # marca visualmente linha de mês
            grid.SetCellFont(linha, 0, wx.Font(9, wx.FONTFAMILY_DEFAULT,
                                            wx.FONTSTYLE_NORMAL,
                                            wx.FONTWEIGHT_BOLD))

            # ---- DIAS DO MÊS (se expandido) ----
            
            if mes in meses_abertos:
                for dia in sorted(dados["dias"].keys()):
                    d = dados["dias"][dia]

                    linha += 1
                    grid.AppendRows(1)

                    grid.SetCellValue(linha, 0, "   " + dia)
                    grid.SetCellValue(linha, 1, formata_numero(d["capital_base"]))
                    grid.SetCellValue(linha, 2, formata_numero(d["aporte"]))
                    grid.SetCellValue(linha, 3, formata_numero(d["retirada"]))
                    grid.SetCellValue(linha, 4, formata_numero(d["rendimento"]))
                    grid.SetCellValue(linha, 5, formata_numero(d["provento"]))
                    grid.SetCellValue(linha, 6, formata_numero(d["despesa"]))
                    grid.SetCellValue(linha, 7, formata_numero(d["resultado_dia"]))
                    grid.SetCellValue(linha, 8, formata_numero(d["resultado_acumulado"]))
                    grid.SetCellValue(linha, 9, formata_numero(d["saldo_fim"]))
                    grid.SetCellValue(linha,10, formata_numero(d["renda_pct"] * 100))
                    grid.SetCellValue(linha,11, formata_numero(d["renda_acumulada"] * 100))

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
                            grid.SetCellBackgroundColour(linha, i, wx.Colour(cor_verdinho))

                    grid.SetCellTextColour(linha, 0, wx.Colour(90, 90, 90))

    def montaGridTotal(self):
        grid = self.ponteiroGrid('Total')

        grid.ClearGrid()
        if grid.GetNumberRows() > 0:
            grid.DeleteRows(0, grid.GetNumberRows())

        linha = -1
        rendaAcumulada = zero
        rendPercAcm = zero

        saldo = zero

        for mes in sorted(self.dados_total.keys()):
            cons = self.dados_total[mes]

            aporte = cons["aporte"]
            retirada = cons["retirada"]
            rendimento = cons["rendimento"]
            provento = cons["provento"]
            despesa = cons["despesa"]

            rendaMes = rendimento + provento - despesa
            rendaAcumulada += rendaMes

            rend_mensal = cons["renda_pct"]

            if linha >= 0:
                rendPercAcm = (Decimal("1") + rend_mensal) * (Decimal("1") + rendPercAcm) - Decimal("1")
            else:
                rendPercAcm = rend_mensal

            linha += 1
            grid.AppendRows(1)

            grid.SetCellValue(linha, 0, f"{mes}")
            grid.SetCellValue(linha, 1, formata_numero(saldo - rendaMes))   # Errado
            grid.SetCellValue(linha, 2, formata_numero(aporte))
            grid.SetCellValue(linha, 3, formata_numero(retirada))
            grid.SetCellValue(linha, 4, formata_numero(rendimento))
            grid.SetCellValue(linha, 5, formata_numero(provento))
            grid.SetCellValue(linha, 6, formata_numero(despesa))
            grid.SetCellValue(linha, 7, formata_numero(rendaMes))
            grid.SetCellValue(linha, 8, formata_numero(rendaAcumulada))
            grid.SetCellValue(linha, 9, formata_numero(saldo))
            grid.SetCellValue(linha,10, formata_numero(rend_mensal * 100))
            grid.SetCellValue(linha,11, formata_numero(rendPercAcm * 100))

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
                    grid.SetCellBackgroundColour(linha, i, wx.Colour(cor_azulzinho))


    def calcula_rendimento_diario(self, nome_tab):
        
        #Calcula rendimento diário correto, considerando:
        #- aportes e retiradas alteram capital base
        #- compras e vendas NÃO alteram capital base
        #- rendimento percentual diário é calculado sobre o capital do dia
        #

        saldo_corrente = zero

        # percorre meses e dias em ordem cronológica
        for mes in sorted(self.dados_por_mes[nome_tab].keys()):
            dias = self.dados_por_mes[nome_tab][mes]["dias"]
            resultado_acumulado = zero
            renda_acumulada = zero
            for dia in sorted(dias.keys()):
                d = dias[dia]

                aporte = d["aporte"]
                retirada = d["retirada"]
                rendimento = d["rendimento"]
                provento = d["provento"]
                despesa = d["despesa"]

                # capital disponível no início do dia
                capital_base = saldo_corrente + aporte - retirada

                # resultado financeiro do dia
                resultado_dia = rendimento + provento - despesa
                resultado_acumulado += resultado_dia

                # rendimento percentual diário
                if capital_base != 0:
                    renda_pct = resultado_dia / capital_base
                else:
                    renda_pct = zero
                renda_acumulada = (1 + renda_acumulada) * (1 + renda_pct) - 1
                # saldo final do dia
                saldo_fim = capital_base + resultado_dia

                # grava no modelo
                d["capital_base"] = capital_base
                d["resultado_dia"] = resultado_dia
                d["renda_pct"] = renda_pct
                d["saldo_fim"] = saldo_fim
                d["resultado_acumulado"] = resultado_acumulado
                d["renda_acumulada"] = renda_acumulada

                # prepara para o próximo dia
                saldo_corrente = saldo_fim

    def consolida_por_mes(self, nome_tab):
        # """
        # Consolida os valores diários em totais mensais.
        # Deve ser chamada APÓS:
        # - buscaRendaPorAtivo
        # - buscaCapital
        # - buscaDespesas
        # """
        n = zero
        rend_mensal_pct = zero
        renda_acm_pct = zero
        rendaAcumulada = zero
        
        for mes, dados in sorted(self.dados_por_mes[nome_tab].items()):
            n += 1            
            consolidado = dados["consolidado"]

            # zera explicitamente (segurança)
            for campo in consolidado:
                consolidado[campo] = zero

            # soma todos os dias do mês
            for dia, valores in sorted(dados["dias"].items()):
                for campo in consolidado:
                    consolidado[campo] += valores[campo]

            aporte = consolidado["aporte"]
            retirada = consolidado["retirada"]
            rendimento = consolidado["rendimento"]
            provento = consolidado["provento"]
            despesa = consolidado["despesa"]

            rendaMes = rendimento + provento - despesa
            rendaAcumulada += rendaMes

            ultimo_dia = sorted(dados["dias"].keys())[-1]
            saldo = dados["dias"][ultimo_dia]["saldo_fim"]

            renda_mensal_pct = consolidado["renda_pct"]
            renda_acm_pct = (Decimal("1") + renda_mensal_pct) * (Decimal("1") + renda_acm_pct) - Decimal("1")

            renda_media = (1 + renda_acm_pct) ** (um / n) - 1
            rendaMediaAno, rendaAno = self.devolve_renda_media_movel(renda_mensal_pct)

            consolidado['resultado_acumulado'] = rendaAcumulada
            consolidado['renda_acumulada'] = renda_acm_pct
            consolidado['renda_media'] = renda_media
            consolidado['no_ano'] = rendaAno
            consolidado["no_ano_media"] = rendaMediaAno
            consolidado['saldo_fim'] = saldo

    def consolida_percentual_mensal(self, nome_tab):
        """
        Consolida o rendimento percentual mensal
        a partir da composição dos rendimentos diários.
        """

        for mes, dados in self.dados_por_mes[nome_tab].items():
            dias = dados["dias"]

            fator = zero
            for dia in sorted(dias.keys()):
                fator = ((um + fator) * (um + dias[dia]["renda_pct"])) - um

            dados["consolidado"]["renda_pct"] = fator

    def consolida_total(self):
        """
        Consolida todas as contas na aba Total,
        convertendo valores para reais conforme cotação.
        """

        self.dados_total.clear()

        # cria mapa nome_conta -> cotacao
        cotacoes = {
            row[1]: Decimal(row[3])
            for row in self.listaContas
        }

        for nome_tab, dados_conta in self.dados_por_mes.items():

            # ignora a própria aba Total, se existir
            if nome_tab == "Total":
                continue

            cotacao = cotacoes.get(nome_tab, Decimal("1"))

            for mes, dados in dados_conta.items():
                cons = dados["consolidado"]

                self.dados_total[mes]["aporte"] += cons["aporte"] * cotacao
                self.dados_total[mes]["retirada"] += cons["retirada"] * cotacao
                self.dados_total[mes]["rendimento"] += cons["rendimento"] * cotacao
                self.dados_total[mes]["provento"] += cons["provento"] * cotacao
                self.dados_total[mes]["despesa"] += cons["despesa"] * cotacao


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
    frame = FrmRendaDiaria()

    app.MainLoop()

if __name__ == '__main__':
    main()