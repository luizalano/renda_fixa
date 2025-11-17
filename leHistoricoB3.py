# coding: utf-8
import wx
import os
import shutil
import pandas as pd
import psycopg2
from datetime import datetime

class LeHistoricoB3(wx.Frame):
    def __init__(self, parent=None, title="Importar negociações do dia - B3"):
        super().__init__(parent, title=title, size=(500, 200))

        panel = wx.Panel(self)
        vbox = wx.BoxSizer(wx.VERTICAL)

        self.btnSelecionar = wx.Button(panel, label="Selecionar arquivo de histórico")
        self.btnSelecionar.Bind(wx.EVT_BUTTON, self.onSelecionarArquivo)
        vbox.Add(self.btnSelecionar, flag=wx.EXPAND | wx.ALL, border=10)

        self.gauge = wx.Gauge(panel, range=100000, style=wx.GA_HORIZONTAL)
        vbox.Add(self.gauge, flag=wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM, border=10)

        self.label_progresso = wx.StaticText(panel, label="Progresso: 0%")
        vbox.Add(self.label_progresso, flag=wx.ALIGN_CENTER | wx.BOTTOM, border=10)

        self.conta = 0
        panel.SetSizer(vbox)
        self.Centre()
        self.Show()


    def onSelecionarArquivo(self, event):
        #dlg = wx.FileDialog(self, "Escolha o arquivo CSV", 
        #                    defaultDir=r"C:\\Users\\luiza\\OneDrive\\Documentos\\VidaDeProgramador\\Python\\b3-VS\\b3\\negociosdodia",
        #                    wildcard="Arquivos CSV (*.csv)|*.csv",
        #                    style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST)#
        #
        #if dlg.ShowModal() == wx.ID_OK:
        #    caminho_arquivo = dlg.GetPath()
        #    self.importarArquivo(caminho_arquivo)

        dlg = wx.DirDialog(self, "Escolha a pasta com arquivos CSV",
                        defaultPath=r"C:\Users\luiza\OneDrive\Documentos\VidaDeProgramador\Python\b3-VS\b3\negociosdodia",
                        style=wx.DD_DEFAULT_STYLE)

        if dlg.ShowModal() == wx.ID_OK:
            pasta = dlg.GetPath()

            import glob, os
            arquivos_csv = glob.glob(os.path.join(pasta, "*.csv"))
            self.conta = len (arquivos_csv)
            i = 0
            for caminho_arquivo in arquivos_csv:
                i += 1
                self.importarArquivo(caminho_arquivo, i)
                #conta += 1
            
        mens = 'Importação de ' + str(self.conta) + ' arquivos finalizada!'
        wx.MessageBox(mens, "Fim de processo", wx.OK | wx.ICON_INFORMATION)
        dlg.Destroy()

    def devolveData(self, datain):
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
    
    def importarArquivo(self, caminho, contador):
        try:
            df = pd.read_csv(caminho, skiprows=[0], sep=';', dtype=str)
            total = len(df)
            df = df[df['SgmtNm'].str.upper() == 'CASH']

            ativos_interesse = self.buscarAtivosDeInteresse()
            mapa_ativos = {sigla: idativo for idativo, sigla in ativos_interesse}

            self.gauge.SetRange(total)

            conn = psycopg2.connect(dbname="b3", user="postgres", password="seriate", host="localhost", port="5432")
            cursor = conn.cursor()

            for idx, row in df.iterrows():
                #print("Lendo linha " + str(idx))
                sigla = row['TckrSymb'].strip()
                if sigla not in mapa_ativos:
                    continue
                self.gauge.SetValue(idx + 1)

                porcentagem = int(((idx + 1) / total) * 100)

                self.label_progresso.SetLabel(f"Progresso({contador} de {self.conta}): {porcentagem}%")

                wx.Yield()
                
                try:
                    idativo = mapa_ativos[sigla]
                    datacotacao = self.devolveData(row['RptDt'].strip())
                    preco = self.parse_float(row['LastPric'])
                    minimo = self.parse_float(row['MinPric'])
                    maximo = self.parse_float(row['MaxPric'])
                    qtdnegocios = self.parse_int(row['TradQty'])
                    qtdacoes = self.parse_int(row['FinInstrmQty'])
                    valornegociado = self.parse_float(row['NtlFinVol'])

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

                    cursor.execute(sql, (idativo, datacotacao, preco, minimo, maximo, qtdnegocios, qtdacoes, valornegociado))
                except Exception as e0:
                     wx.MessageBox(f"Erro durante a inserção: {e0}", "Erro", wx.OK | wx.ICON_ERROR)

            conn.commit()
            cursor.close()
            conn.close()

            self.moverArquivo(caminho)
            #if not self.tudo: wx.MessageBox("Importação concluída com sucesso!", "Sucesso", wx.OK | wx.ICON_INFORMATION)

        except Exception as e:
            wx.MessageBox(f"Erro durante a importação: {e}", "Erro", wx.OK | wx.ICON_ERROR)

    def buscarAtivosDeInteresse(self):
        conn = psycopg2.connect(dbname="b3", user="postgres", password="seriate", host="localhost", port="5432")
        cursor = conn.cursor()
        #cursor.execute("SELECT id, sigla FROM ativo WHERE interesse = 1 AND idbolsa = 1")
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

    def moverArquivo(self, origem):
        destino_dir = os.path.join(os.path.dirname(origem), "importados")
        if not os.path.exists(destino_dir):
            os.makedirs(destino_dir)

        nome_arquivo = os.path.basename(origem)
        destino = os.path.join(destino_dir, nome_arquivo)
        shutil.move(origem, destino)

        #if not self.tudo: wx.MessageBox(f"Arquivo movido", "Fim de processo", wx.OK | wx.ICON_INFORMATION)

if __name__ == '__main__':
    app = wx.App()
    LeHistoricoB3()
    app.MainLoop()
