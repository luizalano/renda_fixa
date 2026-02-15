# coding: utf-8
from wx import *
from wx import adv
import wx.grid

class FrameMG(wx.Frame):
    # Extendendo a classe Frame
    avanco = 0
    avancinho = 17
    avancoX = 7
    avancoY = 19
    bordaX = 8
    bordaY = 8
    alturaCaixaDeTexto = 22
    tamLinha = 42
    caminho = '.\\icones\\'

    '''
    inincializando os parâmetros do construtor
    '''
    pai = None
    titulo = ''
    lar = 800
    alt = 600
    xInicialBotoes = 0
    split = False

    key_shift = False

    ID_EXIT = 110
    '''
    MAC nao aceita fechar de outra maneira que nao no X
    mudando o padrao de saida dá pra enganar o sistema
    '''

    def __init__(self, **kwargs):
        '''
        :param kwargs:
            pai     -> nome do pai da tela
            titulo  -> Título da tela a ser criada
            lar     -> largura da tela em pontos
            alt     -> altura  da tela em pontos
            xibot   -> Posição onde os botões devem iniciar (novo, salva, deleta, cancela)
        '''

        if len(kwargs) > 0:
            if 'pai' in kwargs:
                self.pai = kwargs['pai']
            if 'titulo' in kwargs:
                self.titulo = kwargs['titulo']
            if 'lar' in kwargs:
                self.lar = kwargs['lar']
            if 'alt' in kwargs:
                self.alt = kwargs['alt']
            if 'xibot' in kwargs:
                self.xInicialBotoes = kwargs['xibot']

        if self.pai is None:
            estilo = wx.DEFAULT_FRAME_STYLE & ~(wx.RESIZE_BORDER | wx.MAXIMIZE_BOX)
        else:
            estilo = wx.DEFAULT_FRAME_STYLE & wx.FRAME_FLOAT_ON_PARENT & ~(wx.RESIZE_BORDER | wx.MAXIMIZE_BOX)

        super(FrameMG, self).__init__(self.pai, -1, title=self.titulo, size=(self.lar, self.alt), style=estilo)

        self.SetIcon(wx.Icon(self.caminho + 'iconeMG.ico'))

        self.alt = self.alt - 39

        self.painel = wx.Panel(self, pos=(0, 0), size=(self.lar, self.alt))

        self.larguraPainel, self.alturaPainel = self.painel.GetSize()

        self.criaBotoes()
        if self.split:
            self.criaBotoesPainel2()

        self.Centre()

        self.fontnegrito = wx.Font(8, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD)

    def negrita(self, controle):
        font_atual = controle.GetFont()
        fonte_negrito = wx.Font(
            font_atual.GetPointSize(),  # Mantém o tamanho original
            font_atual.GetFamily(),  # Mantém a família da fonte
            font_atual.GetStyle(),  # Mantém o estilo (normal, itálico, etc.)
            wx.FONTWEIGHT_BOLD  # Define o peso como BOLD
        )
        controle.SetFont(fonte_negrito)

    def formatar_celula_grid(grid, linha, coluna, **kwargs):
        """
        Formata uma célula da grid com estilos opcionais.
        
        Parâmetros:
        - bold (bool): aplica negrito (padrão True)
        - italic (bool): aplica itálico (padrão True)
        - font_size (int): tamanho da fonte (padrão 10)
        - text_color (wx.Colour ou (r,g,b)): cor do texto
        - background_color (wx.Colour ou (r,g,b)): cor do fundo
        """
        attr = wx.gridlib.GridCellAttr()

        bold = kwargs.get("bold", False)
        italic = kwargs.get("italic", False)
        font_size = kwargs.get("font_size", 10)

        font = wx.Font(
            font_size,
            wx.FONTFAMILY_DEFAULT,
            wx.FONTSTYLE_ITALIC if italic else wx.FONTSTYLE_NORMAL,
            wx.FONTWEIGHT_BOLD if bold else wx.FONTWEIGHT_NORMAL
        )
        attr.SetFont(font)

        # Cores (opcional)
        if "text_color" in kwargs:
            cor = kwargs["text_color"]
            attr.SetTextColour(wx.Colour(*cor) if isinstance(cor, tuple) else cor)

        if "background_color" in kwargs:
            cor = kwargs["background_color"]
            attr.SetBackgroundColour(wx.Colour(*cor) if isinstance(cor, tuple) else cor)

        # Aplica o atributo à célula
        grid.SetAttr(linha, coluna, attr)

    def setAvancoVertical(self, arg):
        self.avanco = arg

    def criaBotoes(self):
        gapx = 40
        gapy = 20

        lp = self.larguraPainel
        ap = self.alturaPainel

        self.iconeNovo = wx.Bitmap(self.caminho + 'new32.ico')
        lb, ab = self.iconeNovo.GetSize()
        self.botaoNovo = wx.BitmapButton(self.painel, id=102, bitmap=self.iconeNovo, pos=(10 + self.xInicialBotoes, ap - ab - gapy))
        self.Bind(wx.EVT_BUTTON, self.habilita_novo, self.botaoNovo)

        self.iconeSalva = wx.Bitmap(self.caminho + 'save32.ico')
        lb, ab = self.iconeSalva.GetSize()
        self.botaoSalva = wx.BitmapButton(self.painel, id=103, bitmap=self.iconeSalva, pos=(50 + self.xInicialBotoes, ap - ab - gapy))
        self.botaoSalva.Disable()
        self.Bind(wx.EVT_BUTTON, self.salva_elemento, self.botaoSalva)

        self.iconeDelete = wx.Bitmap(self.caminho + 'delete32.ico')
        lb, ab = self.iconeDelete.GetSize()
        self.botaoDelete = wx.BitmapButton(self.painel, id=104, bitmap=self.iconeDelete, pos=(90 + self.xInicialBotoes, ap - ab - gapy))
        self.botaoDelete.Disable()
        self.Bind(wx.EVT_BUTTON, self.deleta_elemento, self.botaoDelete)

        self.iconeCancela = wx.Bitmap(self.caminho + 'cancel32.ico')
        lb, ab = self.iconeCancela.GetSize()
        self.botaoCancela = wx.BitmapButton(self.painel, id=105, bitmap=self.iconeCancela, pos=(130 + self.xInicialBotoes, ap - ab - gapy))
        self.Bind(wx.EVT_BUTTON, self.cancela_operacao, self.botaoCancela)

        self.Bind(wx.EVT_CHAR_HOOK, self.teclaPressionada)

        self.Bind(wx.EVT_CHAR, self.OnChar, self)

    def teclaPressionada(self, event):
        tecla = event.GetKeyCode()
        if tecla == wx.WXK_F2:
            if self.botaoSalva.Enabled is True:
                self.salva_elemento(event)
        if tecla == wx.WXK_ESCAPE:
            if self.botaoCancela.Enabled is True:
                self.cancela_operacao(event)
        if tecla == wx.WXK_F10:
            self.habilita_novo(event)

        if self.key_shift is True:
            self.key_shift = False
            if tecla == wx.WXK_DELETE:
                self.deleta_elemento(event)
        if tecla == wx.WXK_SHIFT:
            self.key_shift = True

        event.Skip()

    def OnChar(self, event):
        keycode = event.GetUnicodeKey()
        if not self.split:
            if keycode == wx.WXK_NONE:

                # It's a special key, deal with all the known ones:
                if keycode == wx.WXK_DELETE:
                    if self.botaoDelete.Enable():
                        self.deleta_elemento(event)
                elif keycode == wx.WXK_F2:
                    if self.botaoSalva.Enable():
                        self.salva_elemento(event)

    def habilita_novo(self, event):
        self.botaoSalva.Enable()

    def salva_elemento(self, event):
        a = 0

    def deleta_elemento(self, event):
        '''

        :param event:
        :return:

        A classe que extende esta deve chamar o método da super classe, antes de proseguir
        a eliminação, como alinha a seguir:

        super(FrmVinhoProdutor, self).deletaElemento(event)

        esta linha deve vir antes que executar qualquer oisa, para confirmar a deleção
        '''

        self.prossegueEliminacao = False
        dlg = wx.MessageDialog(None, 'Confirma a eliminação dos dados?',
                               'Prestes a eliminar definitivamente!',
                               wx.YES_NO | wx.NO_DEFAULT | wx.ICON_QUESTION)
        if dlg.ShowModal() == wx.ID_YES:
            self.prossegueEliminacao = True

    def cancela_operacao(self, event):
        a = 0

    def posy(self, linha):
        # Retorna uma posição em pixelsa partir do número de linhas
        return (linha * (self.tamLinha + self.avanco)) + self.bordaY

    def posx(self, argColuna):
        # Retorna uma posição em pixelsa partir do número de colunas
        return (argColuna * self.avancoX) + self.bordaX

    def larguraEmPx(self, argColunas):
        return (argColunas * self.avancoX) + (2 * self.avancoX)

    def alturaEmPx(self, argLinhas):
        # return (argLinhas * self.avancoY) + (1 * self.avancoX)
        return (argLinhas * self.tamLinha) - self.avancinho

    def criaCombobox(self, argPainel, **kwargs):
        '''
        :param argPainel:   -> Qual o objeto pai
        :param kwargs:
            label   -> Qual o label, posicionado acima da caixa
            coluna  -> Posição X, em colunas. Cada coluna, considera como o espaco para uma letra W
            linha   -> Posição Y, em colunas. Cada Linha comporta a caixa de texto mais o label acima
            tamanho -> Tamanho da caixa, em colunas
        :return:    -> Retorna dois objetos criados pelo método:
                        Um label
                        Uma Combobox
        '''

        X = 0
        Y = 0
        tamanhoX = 0
        maximo = 0
        rotulo = ''

        if len(kwargs) > 0:
            if 'pos' in kwargs:
                X, Y = kwargs['pos']
                X = self.posx(X)
                Y = self.posy(Y)
            if 'tamanho' in kwargs:
                tamanhoX = self.larguraEmPx(kwargs['tamanho'])
            if 'label' in kwargs:
                rotulo = kwargs['label']

        label = wx.StaticText(argPainel, -1, rotulo, (X, Y))
        caixaDeTexto = wx.ComboBox(argPainel, id=wx.ID_ANY, pos=(X, (Y + self.avancinho)), size=(tamanhoX, self.alturaCaixaDeTexto), style=wx.CB_READONLY)

        return label, caixaDeTexto

    def criaCaixaDeTexto(self, argPainel, **kwargs):
        '''
        :param argPainel:   -> Qual o objeto pai
        :param kwargs:
            pos     -> Posição X e Y, em colunas e linha . Cada coluna, considera como o espaço para uma letra W
            tamanho -> Tamanho da caixa, em colunas e linha. Se vier 0, assume o tamanho padrao
            label   -> Qual o label, posicionado acima da caixa
            max     -> Tamanho máximo do texto. Se for 0, não considera
            multi   -> Se True, é uma caixa multi linhas
            align   -> Alinhamento
            readonly -> Se True, readonly
            tipodate -> Se True, é um DatePickerCtrl
            tipoint  -> Se True, é um TextCtrl que aceita apenas inteiros
            tipofloat -> Se True, é um TextCtrl que aceita apenas float
        :return:    -> Retorna dois objetos criados pelo método:
                        Um label
                        Uma caixa de texto
        '''

        X = 0
        Y = 0
        tamanhoX = 15
        tamanhoY = self.alturaCaixaDeTexto
        labelTxt = ''
        alinhamento = ''
        maximo = 0
        multi = False
        tipoDate = False
        tipoInt = False
        tipoFloat = False
        readonly = False

        if len(kwargs) > 0:
            if 'pos' in kwargs:
                X, Y = kwargs['pos']
            if 'tamanho' in kwargs:
                tamanhoX, tamanhoY = kwargs['tamanho']
            if 'label' in kwargs:
                labelTxt = kwargs['label']
            if 'max' in kwargs:
                maximo = kwargs['max']
            if 'multi' in kwargs:
                multi = kwargs['multi']
            if 'align' in kwargs:
                alinhamento = kwargs['align']
            if 'tipodate' in kwargs:
                tipoDate = kwargs['tipodate']
            if 'tipoint' in kwargs:
                tipoInt = kwargs['tipoint']
            if 'tipofloat' in kwargs:
                tipoFloat = kwargs['tipofloat']
            if 'readonly' in kwargs:
                readonly = kwargs['readonly']

        if tamanhoY == 0:
            tamanhoY = self.alturaCaixaDeTexto
        else:
            tamanhoY = self.alturaEmPx(tamanhoY)
        tamanhoX = self.larguraEmPx(tamanhoX)

        X = self.posx(X)
        Y = self.posy(Y)

        estilo = None

        label = wx.StaticText(argPainel, -1, labelTxt, (X, Y))

        if multi:
            caixaDeTexto = wx.TextCtrl(argPainel, pos=(X, (Y + self.avancinho)), size=(tamanhoX, tamanhoY), style=wx.TE_MULTILINE)
            caixaDeTexto.SetMaxLength(maximo)
            return label, caixaDeTexto
        else:
            if tipoDate:
                caixaDeTexto = adv.DatePickerCtrl(self.painel, pos=(X, (Y + self.avancinho)),
                                                  size=(tamanhoX, self.alturaCaixaDeTexto),
                                                  style=adv.DP_DROPDOWN | adv.DP_SHOWCENTURY)
            elif tipoInt:
                caixaDeTexto = wx.TextCtrl(argPainel, pos=(X, (Y + self.avancinho)), size=(tamanhoX, tamanhoY),
                                           style=wx.TE_RIGHT)
                caixaDeTexto.Bind(wx.EVT_CHAR, self.on_char_int)
            elif tipoFloat:
                if readonly:
                    estilo = wx.TE_READONLY | wx.TE_RIGHT
                else: 
                    estilo = wx.TE_RIGHT
                caixaDeTexto = wx.TextCtrl(argPainel, pos=(X, (Y + self.avancinho)), size=(tamanhoX, tamanhoY),
                                           style=estilo)
                caixaDeTexto.Bind(wx.EVT_CHAR, self.on_char_float)
            else:
                if alinhamento == 'direita':
                    caixaDeTexto = wx.TextCtrl(argPainel, pos=(X, (Y + self.avancinho)), size=(tamanhoX, tamanhoY),
                                               style=wx.TE_RIGHT)
                else:
                    caixaDeTexto = wx.TextCtrl(argPainel, pos=(X, (Y + self.avancinho)), size=(tamanhoX, tamanhoY))
                caixaDeTexto.SetMaxLength(maximo)
            return label, caixaDeTexto

    def on_char_float(self, event):
        keycode = event.GetKeyCode()

        permitidos = (
            wx.WXK_BACK, wx.WXK_RETURN, wx.WXK_DELETE, wx.WXK_INSERT,
            wx.WXK_LEFT, wx.WXK_RIGHT, wx.WXK_HOME, wx.WXK_END,
            wx.WXK_TAB, wx.WXK_ESCAPE, wx.WXK_PAGEUP, wx.WXK_PAGEDOWN,
            wx.WXK_UP, wx.WXK_DOWN
        )

        char = chr(keycode)

        if keycode in permitidos or char.isdigit() or char in ('.', '-', ','):
            if char == ',':
                event.Skip(False)
                event.GetEventObject().WriteText('.')
            else:
                event.Skip()
        else:
            wx.Bell()

    def on_char_int(self, event):
        keycode = event.GetKeyCode()

        if keycode in (
            wx.WXK_BACK, wx.WXK_RETURN, wx.WXK_DELETE, wx.WXK_INSERT,
            wx.WXK_LEFT, wx.WXK_RIGHT, wx.WXK_HOME, wx.WXK_END,
            wx.WXK_TAB, wx.WXK_ESCAPE, wx.WXK_PAGEUP, wx.WXK_PAGEDOWN,
            wx.WXK_UP, wx.WXK_DOWN
        ) or chr(keycode).isdigit():
            event.Skip()
        else:
            wx.Bell()
            
    def encerraAplicacao(self, e):
        self.Close()

