# coding: utf-8
from datetime import datetime
from decimal import Decimal, ROUND_HALF_UP, ROUND_DOWN, getcontext
from datetime import *
import locale
import math
import wx
import wx.grid as gridlib

# alter table itemvenda add column calculado numeric (12,2) generated always as (valorunitario * valortotal) stored;

cor_rosinha = wx.Colour(255, 204, 238)
cor_azulzinho = wx.Colour(230, 255, 251)
cor_branco = wx.Colour(255, 255, 255)
cor_verdinho = wx.Colour(221, 255, 204)
cor_amarelinho = wx.Colour(255, 255, 179)
cor_cinzaclaro = wx.Colour(210, 219, 180)
cem = Decimal('100.0')
zero = Decimal('0.0')

def redimensionaBitMap(bitmapin, largura, altura):
    imagem = bitmapin.ConvertToImage()
    imagem = imagem.Scale(largura, altura, wx.IMAGE_QUALITY_HIGH)
    return wx.Bitmap(imagem)


def tiraAspas(stringa):
    resultado = stringa.replace("'", "''")
    return resultado.replace('"', '\"')


def salvaEmArquivo(oque, onde):
    arquivo = open(onde, "w")
    arquivo.write(oque)
    arquivo.close()


def enche(var, oque, onde, quanto):
    tam = len(var)
    aux = var
    noFim = False
    if onde in "fF":
        noFim = True
    for i in range(tam, quanto):
        if noFim is True:
            aux = aux + oque
        else:
            aux = oque + aux
    return aux


def devolveData(arg):
    tipo = type(arg)

    if str(tipo) == "<class 'str'>":
        aux = arg.strip()
        tam = len(aux)
        if tam < 10:
            return None
        else:
            aux = aux.replace('/', '-')
            try:
                return datetime.datetime.strptime(aux, '%Y-%m-%d %H:%M:%S')
            except  Exception as e:
                try:
                    return datetime.datetime.strptime(aux, '%d-%m-%Y %H:%M:%S')
                except  Exception as e:
                    return None
    if str(tipo) == "<class 'datetime.datetime'>" or str(tipo) == "<class 'datetime.date'>":
        return arg

    return None

def eh_data_validadmy(data_str, formato="%d/%m/%Y"):
    try:
        datetime.strptime(data_str, formato)
        return True  # A data é válida
    except ValueError:
        return False  # A data é inválida

def eh_data_validaymd(data_str, formato="%Y/%m/%d"):
    try:
        datetime.strptime(data_str, formato)
        return True  # A data é válida
    except ValueError:
        return False  # A data é inválida

def _quantize_exp(precisao: int) -> Decimal:
    """Retorna Decimal('0.01') para precisao=2, Decimal('0.1') para 1, etc."""
    if precisao <= 0:
        return Decimal('1')
    return Decimal('1').scaleb(-precisao)  # 10**-precisao as Decimal

def semZeroNegativo(valor: Decimal, casas: int = 2) -> Decimal:
    """
    Remove o sinal negativo de zeros e ajusta para o número de casas decimais desejado.
    """
    # arredonda para o número de casas decimais
    quantize_str = "0." + "0" * casas
    valor = valor.quantize(Decimal(quantize_str))
    
    # se for zero, força para positivo
    if valor == 0:
        valor = Decimal(quantize_str)
    return valor


def devolve_decimal_de_formatacao_completa(arg):
    aux = arg    
    aux = aux.replace('.', '')
    aux = aux.replace(',', '.')
    try:
        retorno = float(aux)
    except  Exception as e:
        retorno = 0.0
    return devolveDecimalDeFloat(retorno, 2)

def devolveDecimalDeFloat(valor: float, precisao: int, rounding=ROUND_DOWN) -> Decimal:
    """
    Recebe um float e devolve Decimal com 'precisao' casas decimais.
    - Constrói o Decimal a partir de str(valor) para evitar imprecisões binárias.
    - Usa quantize para aplicar o arredondamento desejado.
    """
    if valor is None:
        return None
    tipo = type(valor)
    if str(tipo) == "<class 'decimal.Decimal'>":
        return valor
    elif str(tipo) == "<class 'int'>":
        valor = float(valor)
    
    # criar Decimal a partir da string do float 
    # para preservar representação decimal
    d = Decimal(str(valor))
    exp = _quantize_exp(precisao)
    return d.quantize(exp, rounding=rounding)

def devolveFloatDeDecimal(valor: Decimal, precisao: int, rounding=ROUND_DOWN) -> float:
    """
    Recebe um Decimal e devolve float com 'precisao' casas decimais.
    - Mantém a operação em Decimal e converte para float apenas no final.
    """
    if valor is None:
        return None
    tipo = type(valor)
    if str(tipo) == "<class 'decimal.Decimal'>":
        exp = _quantize_exp(precisao)
        d = valor.quantize(exp, rounding=rounding)
        return float(d)
    elif str(tipo) == "<class 'float'>":
        return valor
    elif str(tipo) == "<class 'int'>":
        return float(valor)
    return None

def devolveDate(arg):
    tipo = type(arg)

    if str(tipo) == "<class 'str'>":
        aux = arg.strip()
        aux = aux.replace('/', '-')
        try:
            return datetime.strptime(aux, '%Y-%m-%d')
        except  Exception as e:
            try:
                return datetime.strptime(aux, '%d-%m-%Y')
            except  Exception as e:
                return None
    
    if str(tipo) == "<class 'datetime.datetime'>" or str(tipo) == "<class 'datetime.date'>":
        return arg

    return None

def devolveDateTime(arg):
    tipo = type(arg)

    if str(tipo) == "<class 'str'>":
        aux = arg.strip()
        try:
            return datetime.strptime(aux, '%Y-%m-%d %H:%M:%S')
        except  Exception as e:
            try:
                return datetime.strptime(aux, '%d-%m-%Y %H:%M:%S')
            except  Exception as e:
                return None
    
    if str(tipo) == "<class 'datetime.datetime'>" or str(tipo) == "<class 'datetime.date'>":
        return arg

    return None


def devolveDataDMY(arg):
    locale.setlocale(locale.LC_ALL, 'C') # pt-BR.UTF-8
    tipo = type(arg)

    if str(tipo) == "<class 'str'>":
        aux = arg.strip()
        tam = len(aux)
        if tam < 10:
            return None
        else:
            aux = aux.replace('/', '-')
            try:
                return datetime.datetime.strptime(aux, '%Y-%m-%d')
            except  Exception as e:
                try:
                    # return datetime.datetime.strptime(aux, '%d-%m-%Y')
                    return datetime.datetime.strptime(aux, '%d-%m-%Y').date()
                except  Exception as e:
                    return None
    if str(tipo) == "<class 'datetime.datetime'>":
        aux = devolveDateStr(arg)
        aux = aux.replace('/', '-')
        try:
            return datetime.datetime.strptime(aux, '%Y-%m-%d')
        except  Exception as e:
            try:
                return datetime.datetime.strptime(aux, '%d-%m-%Y')
            except  Exception as e:
                return None
    if str(tipo) == "<class 'datetime.date'>":
        return arg

    return None

def formatar_celula_grid(grid, linha, coluna, **kwargs):
    """
    Formata uma célula da grid com estilos opcionais.
    
    Parâmetros:
    - bold (bool): aplica negrito (padrão True)
    - italic (bool): aplica itálico (padrão True)
    - font_size (int): tamanho da fonte (padrão 10)
    - text_color (wx.Colour ou (r,g,b)): cor do texto
    - background_color (wx.Colour ou (r,g,b)): cor do fundo
    - align: alinhamento
    """
    attr = gridlib.GridCellAttr()

    bold = kwargs.get("bold", False)
    italic = kwargs.get("italic", False)
    font_size = kwargs.get("font_size", 8)

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
            #self.grid.SetCellAlignment(row_idx, 4, wx.ALIGN_CENTRE, wx.ALIGN_CENTRE)
    # Aplica o atributo à célula
    grid.SetAttr(linha, coluna, attr)

    if "align" in kwargs:
        alinhamento = kwargs["align"]
        align = None
        if alinhamento == 'centro': align = wx.ALIGN_CENTRE
        elif alinhamento == 'esquerda': align = wx.ALIGN_LEFT
        elif alinhamento == 'direita': align = wx.ALIGN_RIGHT

        if align: 
            grid.SetCellAlignment(linha, coluna, align, align)
            

def devolveDateStr(arg):
    aux = arg
    tipo = type(aux)
    if str(tipo) == "<class 'str'>":
        aux = devolveData(arg)
    tipo = type(aux)
    if str(tipo) == "<class 'datetime.datetime'>" or str(tipo) == "<class 'datetime.date'>":
        try:
            return aux.strftime('%d/%m/%Y')
        except  Exception as e:
            return ''

    else:
        return ''


def devolveDateTimeStr(arg):
    aux = arg
    tipo = type(aux)
    if str(tipo) == "<class 'str'>":
        aux = devolveData(arg)
    tipo = type(aux)
    if str(tipo) == "<class 'datetime.datetime'>" or str(tipo) == "<class 'datetime.date'>":
        try:
            return aux.strftime('%d/%m/%Y %H:%M:%S')
        except  Exception as e:
            return ''

    else:
        return ''


def devolveDateTimeStrII(arg):
    aux = arg
    tipo = type(aux)
    if str(tipo) == "<class 'str'>":
        aux = devolveData(arg)
    tipo = type(aux)
    if str(tipo) == "<class 'datetime.datetime'>" or str(tipo) == "<class 'datetime.date'>":
        try:
            return aux.strftime('%d/%m/%Y %H:%M:%S:%f')
        except  Exception as e:
            return ''

    else:
        return ''


def formata_numero(valor):
    return formatar_valor(valor)
    # Define a localização para o formato brasileiro
    #locale.setlocale(locale.LC_ALL, 'C') # pt_BR.UTF-8

    # Se o valor for menor que 1 e maior que -1, garantir o formato "0,##"
    #retorno = ''
    #if 0.0 < valor < 1.0:
    #    retorno =  f"0{locale.format_string('%.2f', valor, grouping=True)}"
    #else:
    #    retorno = locale.format_string('%.2f', valor, grouping=True)

    #retorno = locale.format_string('%.2f', valor, grouping=True)
    #return retorno

def formata_numero_6(valor):
    # Define a localização para o formato brasileiro
    locale.setlocale(locale.LC_ALL, 'C')  #pt_BR.UTF-8

    # Se o valor for menor que 1 e maior que -1, garantir o formato "0,##"
    retorno = ''
    if 0 < valor < 1:
        retorno =  f"0{locale.format_string('%.6f', valor, grouping=True)}"
    else:
        retorno = locale.format_string('%.6f', valor, grouping=True)

    retorno = locale.format_string('%.6f', valor, grouping=True)
    return retorno

def formatar_valor(valor):
    retorno = ''
    tipo = type(valor)
    if str(tipo) == "<class 'float'>":
        retorno = f"{valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    elif str(tipo) == "<class 'decimal.Decimal'>":
        valor_float = float(valor)
        retorno = f"{valor_float:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    return retorno

def formatar_int(valor):
    return f"{valor:,.0f}".replace(",", "X").replace(".", ",").replace("X", ".")


def devolve_float_de_formatacao_completa(arg):
    aux = arg
    tipo = type(aux)
    if str(tipo) == "<class 'str'>":
        aux = aux.replace('.', '')
        aux = aux.replace(',', '.')
        try:
            return float(aux)
        except  Exception as e:
            return 0

    tipo = type(arg)
    if str(tipo) == "<class 'float'>":
        return float(aux)

    if str(tipo) == "<class 'decimal.Decimal'>":
        return float(arg)
    else:
        return 0

def devolve_float(arg):
    aux = arg
    tipo = type(aux)
    if str(tipo) == "<class 'str'>":
        aux = aux.replace(',', '.')
        try:
            return float(aux)
        except  Exception as e:
            return 0

    tipo = type(arg)
    if str(tipo) == "<class 'float'>":
        return float(aux)

    if str(tipo) == "<class 'decimal.Decimal'>":
        return float(arg)
    else:
        return 0


def devolveInteger(arg):
    aux = arg
    try:
        return int(aux)
    except  Exception as e:
        return 0


def arredondaFloat(valor, casas):
    num = devolve_float_de_formatacao_completa(valor)
    dec = devolveInteger(casas)
    multi = 10 ** dec
    num = float(int(round(valor, casas) * multi) / multi)
    return num


def formataFloat(numero, inteiros, decimais):
    numStr = str(numero)
    pos = numStr.find('.')
    parteInteira = numStr[:pos]
    parteDecimal = numStr[(pos + 1):]

    np = math.floor(len(parteInteira) / 3) - 1
    resto = len(parteInteira) % 3
    if resto > 0:
        np += 1

    while len(parteDecimal) < decimais:
        parteDecimal += '0'

    parteDecimal = parteDecimal[:decimais]

    jafoi = 0
    while jafoi < np:
        tam = len(parteInteira)
        pos = (tam - 3 * (jafoi + 1) + jafoi)
        parte1 = parteInteira[0:pos]
        parte2 = parteInteira[pos:tam]
        parteInteira = parte1 + '.' + parte2
        jafoi += 1

    if decimais > 0:
        retorno = parteInteira + '.' + parteDecimal
    else:
        retorno = parteInteira

    return retorno

def XemPixel(x):
    return int(x * 7)

def YemPixel(y):
    return int(y * 19)

def posicao(x, y):
    return (XemPixel(x), YemPixel(y))
def letrasEmPixels(arg):
    return int(arg * 9) + 5
