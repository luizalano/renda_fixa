# coding: utf-8
import wx
import os
import shutil
import pandas as pd
from datetime import datetime, date
import re
from pathlib import Path

from databasefunctions import ConectaBD

class LeHistoricoB3(wx.Frame):
    def __init__(self, parent=None, title="Importar negociações do dia - B3"):
        super().__init__(parent, title=title, size=(500, 200))

        panel = wx.Panel(self)
        vbox = wx.BoxSizer(wx.VERTICAL)

        self.btnSelecionar = wx.Button(panel, label="Selecionar pasta onde estão as cotações")
        self.btnSelecionar.Bind(wx.EVT_BUTTON, self.on_selecionar_arquivo)
        vbox.Add(self.btnSelecionar, flag=wx.EXPAND | wx.ALL, border=10)

        self.gauge = wx.Gauge(panel, range=100000, style=wx.GA_HORIZONTAL)
        vbox.Add(self.gauge, flag=wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM, border=10)

        self.label_progresso = wx.StaticText(panel, label="Progresso: 0%")
        vbox.Add(self.label_progresso, flag=wx.ALIGN_CENTER | wx.BOTTOM, border=10)

        self.conta = 0
        panel.SetSizer(vbox)
        self.Centre()
        self.Show()


    def on_selecionar_arquivo(self, event):
        dlg = wx.DirDialog(self, "Escolha a pasta com arquivos CSV",
                        defaultPath=r"C:\Users\luiza\OneDrive\Documentos\VidaDeProgramador\Python\b3-VS\renda_fixa\negociosdodia",
                        style=wx.DD_DEFAULT_STYLE)

        if dlg.ShowModal() == wx.ID_OK:
            pasta = dlg.GetPath()

            import glob, os
            arquivos_csv = glob.glob(os.path.join(pasta, "*.csv"))
            self.conta = len (arquivos_csv)
            i = 0
            for caminho_arquivo in arquivos_csv:
                i += 1
                self.importar_arquivo(caminho_arquivo, i)
                #conta += 1
            
        mens = 'Importação de ' + str(self.conta) + ' arquivos finalizada!'
        wx.MessageBox(mens, "Fim de processo", wx.OK | wx.ICON_INFORMATION)
        dlg.Destroy()

    def devolve_data(self, datain):
        dataout = None
        try:
            dataout = datetime.strptime(datain, "%d/%m/%Y").date()
        except Exception as e:
            try:
                dataout = datetime.strptime(datain, "%Y/%m/%d").date()
            except Exception as e1:
                try:
                    dataout = datetime.strptime(datain, "%Y-%m-%d").date()
                except Exception as e2:
                    dataout = datetime.strptime(datain, "%d-%m-%Y").date()
        return dataout
    
    def getConexao(self):
        try:
            con = ConectaBD.retornaConexao()
            return con
        except Exception as e:
            print(f"Erro ao conectar com o banco: {e}")
            return False
        
    def extrai_data_do_nome(self, caminho):
        nome_arquivo = Path(caminho).stem  # remove caminho e extensão
        data_str = nome_arquivo[-10:]      # últimos 10 caracteres
        try:
            return datetime.strptime(data_str, "%d-%m-%Y").date()
        except Exception as e:
            print(f"Erro ao extrair data do nome do arquivo: {data_str}")
            return None

    def extrai_data_do_nome_regex(caminho: str) -> date:
        match = re.search(r"\d{2}-\d{2}-\d{4}", caminho)
        if not match:
            raise ValueError("Data não encontrada no nome do arquivo")
        return datetime.strptime(match.group(), "%d-%m-%Y").date()        
    
    def importar_arquivo(self, caminho, contador):
        try:
            df = pd.read_csv(caminho, skiprows=[0, 1], sep=';', dtype=str)
            #df = pd.read_csv(caminho, skiprows=2, sep=';', dtype=str) os dois comandos são semelhantes
            total = len(df)
            df = df[df['Segmento'].str.upper() == 'CASH']

            data_cotacao = self.extrai_data_do_nome(caminho)
            if data_cotacao is None:
                wx.MessageBox(f"Não foi possível extrair a data do arquivo: {caminho}", "Erro", wx.OK | wx.ICON_ERROR)
                return

            ativos_interesse = self.buscar_ativos_de_interesse()
            mapa_ativos = {sigla: idativo for idativo, sigla in ativos_interesse}

            self.gauge.SetRange(total)

            conn = self.getConexao()
            cursor = conn.cursor()

            for idx, row in df.iterrows():
                #print("Lendo linha " + str(idx))
                sigla = row['Instrumento financeiro'].strip()
                if sigla not in mapa_ativos:
                    continue
                self.gauge.SetValue(idx + 1)

                porcentagem = int(((idx + 1) / total) * 100)

                self.label_progresso.SetLabel(f"Progresso({contador} de {self.conta}): {porcentagem}%")

                wx.Yield()
                
                try:
                    id_ativo = mapa_ativos[sigla]
                    #data_cotacao = self.devolve_data(row['RptDt'].strip())
                    preco = self.parse_float(row['Preço de fechamento'])
                    minimo = self.parse_float(row['Preço mínimo'])
                    maximo = self.parse_float(row['Preço máximo'])
                    qtd_negocios_str = row['Quantidade de negócios'].replace('.','')
                    qtd_negocios = self.parse_int(qtd_negocios_str)
                    qtd_acoes_str = row['Quantidade de contratos'].replace('.','')
                    qtd_acoes = self.parse_int(qtd_acoes_str)
                    valor_negociado = self.parse_float(row['Volume financeiro'])

                    sql = '''
                        INSERT INTO cotacaoativo 
                        (idativo, datacotacao, preco, minimo, maximo, qtdnegocios, qtdacoesnegociadas, valornegociado)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                        ON CONFLICT (idativo, datacotacao)
                        DO UPDATE SET 
                            preco = EXCLUDED.preco,
                            minimo = EXCLUDED.minimo,
                            maximo = EXCLUDED.maximo,
                            qtdnegocios = EXCLUDED.qtdnegocios,
                            qtdacoesnegociadas = EXCLUDED.qtdacoesnegociadas,
                            valornegociado = EXCLUDED.valornegociado;
                    '''

                    cursor.execute(sql, (id_ativo, data_cotacao, preco, minimo, maximo, qtd_negocios, qtd_acoes, valor_negociado))
                except Exception as e0:
                     wx.MessageBox(f"Erro durante a inserção: {e0}", "Erro", wx.OK | wx.ICON_ERROR)

            conn.commit()
            cursor.close()
            conn.close()

            self.mover_arquivo(caminho)

        except Exception as e:
            wx.MessageBox(f"Erro durante a importação: {e}", "Erro", wx.OK | wx.ICON_ERROR)

    def buscar_ativos_de_interesse(self):
        conn = self.getConexao()
        cursor = conn.cursor()
        cursor.execute("SELECT id, sigla FROM ativo WHERE idbolsa = 1")
        ativos = cursor.fetchall()
        cursor.close()
        conn.close()
        return ativos

    def parse_float(self, val):
        if pd.isna(val): return 0.0
        return float(str(val).replace(',', '.').replace(' ', ''))

    def parse_int(self, val):
        if pd.isna(val): return 0
        return int(str(val).replace(' ', '').split('.')[0])

    def mover_arquivo(self, origem):
        destino_dir = os.path.join(os.path.dirname(origem), "importados")
        if not os.path.exists(destino_dir):
            os.makedirs(destino_dir)

        nome_arquivo = os.path.basename(origem)
        destino = os.path.join(destino_dir, nome_arquivo)
        shutil.move(origem, destino)
        
if __name__ == '__main__':
    app = wx.App()
    LeHistoricoB3()
    app.MainLoop()
