# coding: utf-8


from wx import *
import wx.grid
import psycopg2
from bolsa import Bolsa
from diversos import *
from datetime import *
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import dates as mdates
from buscaCotacoesAtivoPorDia import BuscaCotacaoBolsas
from matplotlib.backends.backend_wxagg import FigureCanvasWxAgg as FigureCanvas
from ativo import *
from frm_leHistoricoB3 import LeHistoricoB3

class VariacaoFrm(wx.Frame):
    objetoBusca = BuscaCotacaoBolsas()
    leHist = None

    def __init__(self, parent, ativo):
        super().__init__(parent, title="Variação diária de ativos", size=(1400, 720))
        self.ativo_inicial = ativo
        self.id_bolsa = -1
        self.sigla_bolsa = None
        self.sigla_moeda = None
        self.SetPosition((0, 0))
        self.horizontal_line = None
        self.horizontal_text = None

        self.init_ui()
        self.hoje = date.today()
        self.data_inicio = self.hoje - timedelta(days=30)
        self.mostra = 30
        self.ativo_selecionado = None

        # Crosshair inicializados invisíveis
        self.crosshair_vline = self.ax.axvline(np.nan, color='gray', linestyle='--', linewidth=0.5, visible=False)
        self.crosshair_hline = self.ax.axhline(np.nan, color='gray', linestyle='--', linewidth=0.5, visible=False)
        self.crosshair_text = self.ax.text(0, 0, '', fontsize=8, color='black', backgroundcolor='white', visible=False)

        self.canvas.mpl_connect("button_press_event", self.on_mouse_middle_click)

    def init_ui(self):
        # Painel principal
        panel = wx.Panel(self)
        vbox = wx.BoxSizer(wx.VERTICAL)

        # Área superior para entrada de dados
        top_panel = wx.Panel(panel)
        top_sizer = wx.BoxSizer(wx.HORIZONTAL)

        #self.text_ctrl = wx.TextCtrl(top_panel)

        self.cbBolsa = wx.ComboBox(top_panel)
        self.cbBolsa.Bind(wx.EVT_COMBOBOX, self.bolsa_selecionada)
        self.btnMostraTudo = wx.Button(top_panel, label="Mostra 2 anos")
        self.Bind(wx.EVT_BUTTON, self.mostraTodasCotacoes, self.btnMostraTudo)
        self.btnMostra60 = wx.Button(top_panel, label="Mostra 60 dias")
        self.Bind(wx.EVT_BUTTON, self.mostra60, self.btnMostra60)
        self.btnMostra30 = wx.Button(top_panel, label="Mostra 30 dias")
        self.Bind(wx.EVT_BUTTON, self.mostra30, self.btnMostra30)
        self.btnBuscaCotacoes = Button(top_panel, id=ID_ANY, label="Busca cotações", style=0)
        #self.Bind(wx.EVT_BUTTON, self.buscacotacaodoAtivo, self.btnBuscaCotacoes)
        self.Bind(wx.EVT_BUTTON, self.buscaCotacaoDosAtivos, self.btnBuscaCotacoes)
        # Botão limpar linha
        self.btnLimpaLinhaGrafico = Button(top_panel, id=ID_ANY, label="Limpa linha de cotação", style=0)
        #self.btnLimpaLinhaGrafico = wx.Button(panel, label="Limpar linha horizontal")
        self.btnLimpaLinhaGrafico.Bind(wx.EVT_BUTTON, self.limpar_linha_horizontal)
        #vbox.Add(self.btn_limpar, flag=wx.ALIGN_CENTER | wx.BOTTOM, border=10)

        top_sizer.Add(wx.StaticText(top_panel, label="Bolsa: "), flag=wx.LEFT | wx.RIGHT, border=5)
        top_sizer.Add(self.cbBolsa, proportion=1, flag=wx.EXPAND | wx.ALL, border=5)
        top_sizer.Add(self.btnMostraTudo, proportion = 1, flag=wx.ALL, border=5)
        top_sizer.Add(self.btnMostra60, proportion = 1, flag=wx.ALL, border=5)
        top_sizer.Add(self.btnMostra30, proportion = 1, flag=wx.ALL, border=5)
        top_sizer.Add(self.btnBuscaCotacoes, proportion = 1, flag=wx.ALL, border=5)
        top_sizer.Add(self.btnLimpaLinhaGrafico, proportion = 1, flag=wx.ALL, border=5)
        top_panel.SetSizer(top_sizer)

        vbox.Add(top_panel, flag=wx.EXPAND | wx.ALL, border=5)

        # Layout principal (grid + gráfico)
        main_sizer = wx.BoxSizer(wx.HORIZONTAL)

        # Grid de ativos
        self.gridAtivos = wx.grid.Grid(panel)
        self.gridAtivos.CreateGrid(0, 1)
        self.gridAtivos.SetColSize(0, 70)  # Aumentei um pouco a largura
        self.gridAtivos.SetColLabelValue(0, "Ativo")
        self.gridAtivos.Bind(wx.grid.EVT_GRID_CELL_LEFT_CLICK, self.on_mouse_click)

        # Aumenta o espaço da grid
        main_sizer.Add(self.gridAtivos, 1, wx.EXPAND | wx.ALL, 5)  # Antes era 2

        # Painel para gráfico
        self.graph_panel = wx.Panel(panel)
        graph_sizer = wx.BoxSizer(wx.VERTICAL)

        self.figure, self.ax = plt.subplots()
        self.canvas = FigureCanvas(self.graph_panel, -1, self.figure)  # Corrigi o self.self
        self.canvas.mpl_connect("button_press_event", self.on_right_click)

        graph_sizer.Add(self.canvas, proportion=1, flag=wx.EXPAND)
        self.graph_panel.SetSizer(graph_sizer)

        # Reduz espaço do gráfico para dar mais à grid
        main_sizer.Add(self.graph_panel, 6, wx.EXPAND | wx.ALL, 5)  # Antes era 3

        # Adiciona o layout horizontal ao vertical
        vbox.Add(main_sizer, proportion=1, flag=wx.EXPAND)

        # Define o layout final no painel principal
        panel.SetSizer(vbox)
        #self.busca.realizaBusca()
        self.monta_combo_bolsa()


        self.Show()

    def getConexao(self):
        try:
            con = ConectaBD.retornaConexao()
            return con
        except Exception as e:
            print(f"Erro ao conectar com o banco: {e}")
            return False

    def monta_combo_bolsa(self):
        lista = Bolsa.mc_select_all_order_sigla()
        self.cbBolsa.Clear()
        for row in lista:
            self.cbBolsa.Append(row[1])

    def bolsa_selecionada(self, event):
        self.sigla_bolsa = self.cbBolsa.GetStringSelection()
        if self.sigla_bolsa:
            self.montaGrid(self.sigla_bolsa)  
            self.busca_moeda_bolsa()

    def busca_moeda_bolsa(self):
        conexao = self.getConexao()
        
        clausulaSql = 'select b.idmoeda, m.sigla from bolsa as b join moeda as m on m.id = b.idmoeda where b.sigla = %s;'
        lista = []
        self.sigla_moeda = None
        try:
            with conexao.cursor() as cursor:
                cursor.execute(clausulaSql, (self.sigla_bolsa, ))
                lista = cursor.fetchone()
                self.sigla_moeda =  lista[1]

        except  Exception as e:
            dlg = wx.MessageDialog(None, clausulaSql + '\n' + str(e), 'Erro ao ler ativos com cotação', wx.OK | wx.ICON_ERROR)
            result = dlg.ShowModal()

        conexao.close()

    def busca_ativos(self, siglabolsa):
        conexao = self.getConexao()
        
        #clausulaSql = 'SELECT sigla FROM ativo where interesse = 1 and idbolsa = (select id from bolsa where sigla = %s) order by sigla;'
        clausulaSql = 'SELECT sigla FROM ativo where interesse >= 0 and idbolsa = (select id from bolsa where sigla = %s) order by sigla;'
        lista = []
        filtro = 0
        try:
            with conexao.cursor() as cursor:
                cursor.execute(clausulaSql, (siglabolsa, ))
                lista = cursor.fetchall()

        except  Exception as e:
            dlg = wx.MessageDialog(None, clausulaSql + '\n' + str(e), 'Erro ao ler ativos com cotação', wx.OK | wx.ICON_ERROR)
            result = dlg.ShowModal()

        conexao.close()
        return lista

    def busca_prineira_data_cotacao(self):
        conexao = self.getConexao()
        clausulaSql = 'SELECT min(datacotacao) FROM cotacaoativo;'

        lista = []
        try:
            with conexao.cursor() as cursor:
                cursor.execute(clausulaSql)
                lista = cursor.fetchone()

        except  Exception as e:
            conexao.close()
            return None

        conexao.close()
        return datetime.strptime(str(lista[0]), '%Y-%m-%d').date()

    def salva_cotacao(self, conexao, valor, minimo, maximo, data):
        clausulaSql = '''
            INSERT INTO cotacaoativo (idativo, datacotacao, preco, maximo, minimo)
            VALUES ((select id from ativo where sigla = upper(%s)), %s, %s, %s, %s)
            ON CONFLICT (idativo, datacotacao) DO UPDATE
            SET preco = EXCLUDED.preco,
                maximo = EXCLUDED.maximo,
                minimo = EXCLUDED.minimo;
        '''

        with conexao.cursor() as cursor:
            try:
                cursor.execute(clausulaSql, (self.ativo_selecionado, data, float(valor), float(maximo), float(minimo)))
            except  Exception as e:
                print(clausulaSql + ' -> ' + str(e))

        conexao.commit()

    def on_close(self, event, frame_attr):
        """Garante que o objeto seja destruído ao fechar a janela."""
        frame = getattr(self, frame_attr, None)  # Obtém a referência ao frame
        if frame:
            frame.Destroy()  # Destrói a janela
            setattr(self, frame_attr, None)  # Define como None


    def busca_cotacao_do_ativo(self, event):
        if self.ativo_selecionado is None: return None

        primeira_data = self.busca_prineira_data_cotacao()
        if primeira_data is None: return None

        sufixo = self.objetoBusca.get_sufixo_bolsa(self.sigla_bolsa)

        conexao = self.getConexao()
        valor = 0.0
        while True:
            if primeira_data.weekday() < 5:  # Não roda nos finais de semana
                cotacao = self.objetoBusca.get_cotacao_por_data(self.ativo_selecionado, primeira_data, sufixo)

                if cotacao:
                    preco = cotacao["fechamento"]
                    maxima = cotacao["maxima"]
                    minima = cotacao["minima"]
                    self.salva_cotacao(conexao, preco, minima, maxima, primeira_data)

            primeira_data = primeira_data + + timedelta(days=1)
            if primeira_data > self.hoje:
                break

        self.graficoDoAtivo(self.ativo_selecionado)

    def buscaCotacaoDosAtivos(self, event):
        if self.leHist is None:  # Se não existir, cria uma nova janela
            self.leHist = LeHistoricoB3()
            self.leHist.Bind(wx.EVT_CLOSE, lambda evt: self.on_close(evt, "leHist"))
            self.leHist.Show()
        else:
            self.leHist.Raise()  # Se já existir, apenas traz para frente
        

        self.graficoDoAtivo(self.ativo_selecionado)

    def mostraTodasCotacoes(self, event):
        self.mostra = 730
        if self.ativo_selecionado != None:
            self.graficoDoAtivo(self.ativo_selecionado)

    def mostra60(self, event):
        self.mostra = 60
        if self.ativo_selecionado != None:
            self.graficoDoAtivo(self.ativo_selecionado)

    def mostra30(self, event):
        self.mostra = 30
        if self.ativo_selecionado != None:
            self.graficoDoAtivo(self.ativo_selecionado)

    def montaGrid(self, siglaBolsa):
        numrows = self.gridAtivos.GetNumberRows()
        if numrows >0:
            self.gridAtivos.DeleteRows(pos=0, numRows=self.gridAtivos.GetNumberRows())
        lista = self.busca_ativos(siglaBolsa)
        linha = -1
        for row in lista:
            linha += 1
            self.gridAtivos.AppendRows()
            self.gridAtivos.SetCellValue(linha, 0, row[0])

    def buscacotacao(self, ativo):
        conexao = psycopg2.connect(dbname="b3", user="postgres", password="seriate", host="localhost",
                                   port="5432")
        
        clausulaSql = 'SELECT * FROM (select datacotacao, preco, maximo, minimo from cotacaoativo ' \
                      'where idativo = (select id from ativo where sigla = upper(%s)) ' \
                      'order by datacotacao DESC LIMIT %s) ORDER BY datacotacao ASC;'
        
        #if self.mostra == 0:
        #    clausulaSql = 'SELECT datacotacao, preco, maximo, minimo FROM cotacaoativo ' \
        #                  'where idativo = (select id from ativo where sigla = upper(%s)) ' \
        #                 ' order by datacotacao;'
        #else:
        #    self.data_inicio = self.hoje - timedelta(days=self.mostra)
        #    clausulaSql = 'SELECT datacotacao, preco, maximo, minimo FROM cotacaoativo ' \
        #              'where idativo = (select id from ativo where sigla = upper(%s)) ' \
        #              'and datacotacao >= %s order by datacotacao;'

        lista = []
        filtro = 0
        try:
            with conexao.cursor() as cursor:
                cursor.execute(clausulaSql, (ativo, self.mostra)) #self.data_inicio))
                lista = cursor.fetchall()

        except  Exception as e:
            dlg = wx.MessageDialog(None, clausulaSql + '\n' + str(e), 'Erro ao ler ativos com cotação', wx.OK | wx.ICON_ERROR)
            result = dlg.ShowModal()

        conexao.close()
        return lista

    def on_mouse_click(self, event):
        self.limpar_linha_horizontal(None)
        row = event.GetRow()  # Obtém o índice da linha clicada
        self.gridAtivos.SelectRow(row)
        self.ativo_selecionado = self.gridAtivos.GetCellValue(row, 0)  # Obtém o nome do ativo na coluna 0
        self.graficoDoAtivo(self.ativo_selecionado)

    def temAtivoInicial(self, ativo):
        conexao = psycopg2.connect(dbname="b3", user="postgres", password="seriate", host="localhost",
                                   port="5432")
        clausulaSql = 'select sigla from ativo where sigla = upper(%s);'

        lista = []
        filtro = 0
        try:
            with conexao.cursor() as cursor:
                cursor.execute(clausulaSql, (ativo,))
                lista = cursor.fetchone()
            conexao.close()
            ativoRetornado =  lista[0]
            if ativoRetornado:
                self.graficoDoAtivo(ativoRetornado)

        except  Exception as e:
            ativoRetornado = None

    def graficoDoAtivo(self, ativo):
        conexao = psycopg2.connect(dbname="b3", user="postgres", password="seriate", host="localhost", port="5432")
        clausulaSql = 'SELECT razaosocial from ativo where sigla = upper(%s);'

        nomeAtivo = "-"
        try:
            with conexao.cursor() as cursor:
                cursor.execute(clausulaSql, (ativo,))
                lista = cursor.fetchone()
                if lista:
                    nomeAtivo = lista[0]
        except Exception as e:
            dlg = wx.MessageDialog(None, clausulaSql + '\n' + str(e), 'Erro ao ler ativos com cotação', wx.OK | wx.ICON_ERROR)
            dlg.ShowModal()

        # Obtém os dados de mercado mais recentes
        clausulaSql = '''
            SELECT qtdnegocios, qtdacoesnegociadas, valornegociado
            FROM cotacaoativo
            WHERE datacotacao = (
                SELECT MAX(datacotacao)
                FROM cotacaoativo
                WHERE idativo = (SELECT id FROM ativo WHERE sigla = UPPER(%s))
            )
            AND idativo = (SELECT id FROM ativo WHERE sigla = UPPER(%s));
        '''
        try:
            with conexao.cursor() as cursor:
                cursor.execute(clausulaSql, (ativo, ativo))
                lista = cursor.fetchone()
        except Exception as e:
            dlg = wx.MessageDialog(None, clausulaSql + '\n' + str(e), 'Erro ao ler negócios do ativo', wx.OK | wx.ICON_ERROR)
            dlg.ShowModal()
            lista = None

        self.limpar_linha_horizontal()

        if lista:
            qtdNegocios, qtdAcoesNegociadas, volumeNegociado = lista
        else:
            qtdNegocios = qtdAcoesNegociadas = 0
            volumeNegociado = 0.0

        strNegocios = formatar_int(qtdNegocios)
        strAcoesNegociadas = formatar_int(qtdAcoesNegociadas)
        strVolume = formatar_valor(volumeNegociado)

        lista = self.buscacotacao(ativo)

        label_datas = []
        listax = []
        listay = []
        listamax = []
        listamin = []
        listavariacao = []

        precoant = 0.0
        for i, (datacotacao, preco, maximo, minimo) in enumerate(lista):
            label = datacotacao.strftime("%m-%d")
            label_datas.append(label)
            listax.append(i)  # valor numérico sequencial
            listay.append(round(preco, 2))
            listamax.append(maximo)
            listamin.append(minimo)

            if i == 0:
                listavariacao.append(0.0)
            else:
                variacao = ((preco / precoant - 1) * 100) if precoant else 0.0
                listavariacao.append(variacao)

            precoant = preco

        self.ax.clear()

        self.ax.plot(listax, listay, marker='o', color='black')
        self.ax.plot(listax, listamax, marker='^', linestyle='--', color='blue')
        self.ax.plot(listax, listamin, marker='v', linestyle='--', color='red')

        for i in range(1, len(listavariacao)):
            cor = 'green' if listavariacao[i] > 0 else 'red'
            self.ax.text(listax[i], listay[i], f"{listavariacao[i]:.1f}%", color=cor, fontsize=9, fontweight='bold')

        self.ax.set_xticks(listax)
        self.ax.set_xticklabels(label_datas, rotation=45)

        if self.mostra > 30:
            passo = int(self.mostra / 30)
            indices_visiveis = list(range(0, len(listax), passo))
            self.ax.set_xticks([listax[i] for i in indices_visiveis])
            plt.setp(self.ax.get_xticklabels(), rotation=45)

        valorMercado = Ativo.get_valor_mercado_yfinance(ativo, self.sigla_bolsa)
        strvalor = formata_numero(valorMercado)

        self.ax.set_title(
            f'Variação do ativo {nomeAtivo}  Valor de mercado {strvalor} em {self.sigla_moeda}\n'
            f'Negócios: {strNegocios}  Ações negociadas: {strAcoesNegociadas}  Volume financeiro: {strVolume}'
        )
        self.ax.legend()
        self.canvas.draw()

    def on_mouse_middle_click(self, event):
        if event.button != 2 or not event.inaxes or event.xdata is None or event.ydata is None:
            return

        self.limpar_linhas_do_ponto()
        x = event.xdata
        y = event.ydata

        # Redefine os elementos do crosshair a cada clique para garantir visibilidade após redraw
        self.crosshair_vline = self.ax.axvline(x, color='gray', linestyle='--', linewidth=0.5)
        self.crosshair_hline = self.ax.axhline(y, color='gray', linestyle='--', linewidth=0.5)
        self.crosshair_text = self.ax.text(
            self.ax.get_xlim()[0], y, f'{y:.2f}', fontsize=8, color='red', backgroundcolor='white'
        )
        #self.ax.text(-5, y, 'fora do gráfico', color='red', clip_on=False)


        self.canvas.draw_idle()
       

    def on_right_click(self, event):
        if event.button == 3 and event.ydata is not None:
            self.limpar_linha_horizontal()
            y = event.ydata
            self.horizontal_line = self.ax.axhline(y=y, color='gray', linestyle='--', linewidth=0.8)
            self.horizontal_text = self.ax.text(
                self.ax.get_xlim()[1], y, f'{y:.2f}', color='black', fontsize=8,
                va='center', ha='right', backgroundcolor='white')
            self.canvas.draw()

    def limpar_linhas_do_ponto(self, event=None):
        removeu = False

        if self.crosshair_vline in self.ax.lines:
            self.crosshair_vline.remove()
            self.crosshair_vline = None
            removeu = True
        if self.crosshair_hline in self.ax.lines:
            self.crosshair_hline.remove()
            self.crosshair_hline = None
            removeu = True
        if self.crosshair_text in self.ax.texts:
            self.crosshair_text.remove()
            self.crosshair_text = None
            removeu = True

        if removeu: self.canvas.draw()

    def limpar_linha_horizontal(self, event=None):
        removeu = False
        if self.horizontal_line:
            self.horizontal_line.remove()
            self.horizontal_line = None
            removeu = True
        if self.horizontal_text:
            self.horizontal_text.remove()
            self.horizontal_text = None
            removeu = True
        if removeu: self.canvas.draw()


if __name__ == "__main__":
    app = wx.App()
    objeto = VariacaoFrm(None, None)
    objeto.Show()
    app.MainLoop()