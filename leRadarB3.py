# coding: utf-8
import wx
import os
import shutil
import pandas as pd
import psycopg2
from datetime import datetime

class LeRadarB3(wx.Frame):
    def __init__(self, parent=None, title="Importar radar de proventos - B3"):
        super().__init__(parent, title=title, size=(500, 200))

        panel = wx.Panel(self)
        vbox = wx.BoxSizer(wx.VERTICAL)

        self.btnSelecionar = wx.Button(panel, label="Selecionar arquivo de radar")
        self.btnSelecionar.Bind(wx.EVT_BUTTON, self.onSelecionarArquivo)
        vbox.Add(self.btnSelecionar, flag=wx.EXPAND | wx.ALL, border=10)

        self.gauge = wx.Gauge(panel, range=100000, style=wx.GA_HORIZONTAL)
        vbox.Add(self.gauge, flag=wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM, border=10)

        self.label_progresso = wx.StaticText(panel, label="Progresso: 0%")
        vbox.Add(self.label_progresso, flag=wx.ALIGN_CENTER | wx.BOTTOM, border=10)

        panel.SetSizer(vbox)
        self.Centre()
        self.Show()

    def onSelecionarArquivo(self, event):
        dlg = wx.FileDialog(self, "Escolha o arquivo CSV", 
                            defaultDir=r"C:\\Users\\luiza\\OneDrive\\Documentos\\VidaDeProgramador\\Python\\b3-VS\\b3\\negociosdodia",
                            wildcard="Arquivos XLSX (*.xlsx)|*.xlsx",
                            style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST)

        if dlg.ShowModal() == wx.ID_OK:
            caminho_arquivo = dlg.GetPath()
            self.importarArquivo(caminho_arquivo)

        dlg.Destroy()

    def moverArquivo(self, origem):
        destino_dir = os.path.join(os.path.dirname(origem), "importados")
        if not os.path.exists(destino_dir):
            os.makedirs(destino_dir)

        nome_arquivo = os.path.basename(origem)
        destino = os.path.join(destino_dir, nome_arquivo)
        shutil.move(origem, destino)

        wx.MessageBox(f"Arquivo movido", "Fim de processo", wx.OK | wx.ICON_INFORMATION)


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
    
    def importarArquivo(self, caminho):
        try:
            df = pd.read_excel(caminho)

            total = len(df)

            self.gauge.SetRange(total)

            conn = psycopg2.connect(dbname="b3", user="postgres", password="seriate", host="localhost", port="5432")
            cursor = conn.cursor()

            today = datetime.now().date()
            cursor.execute("DELETE FROM radar WHERE datacom >= %s and idbolsa = %s", (today, 1))

            for index, row in df.iterrows():
                self.gauge.SetValue(index + 1)

                porcentagem = int(((index + 1) / total) * 100)
                self.label_progresso.SetLabel(f"Progresso: {porcentagem}%")

                wx.Yield()
                
                continua = True
                # Processar colunas
                dataprovavel = row['Data de Pagamento']
                datacom = row['Data COM']
                tipoprovento = row['Tipo de Evento']
                valorprovento = str.replace(row['Preço Unitário Bruto'],',', '.')
                ultimacotacao = str.replace(row['Preço Fechamento'],',', '.')
                dy = str.replace(row['DY'],',', '.')

                # Separar sigla e razão social
                produto = row['Produto']

                sigla, razaosocial = produto.split(' - ', 1)
                #if len(dataprovavel) <= 9: continua = False
                #if len(datacom) <= 9: continua = False
                if len(tipoprovento) <= 0: continua = False
                if len(valorprovento) <= 0: continua = False
                if len(ultimacotacao) <= 0: continua = False
                if len(sigla) <= 0: continua = False

                if continua:
                    try:
                        cursor.execute("SAVEPOINT before_insert")  # Cria um ponto de salvamento

                        # Buscar idativo na tabela ativo
                        cursor.execute("SELECT id FROM ativo WHERE UPPER(sigla) = UPPER(%s) and idbolsa = %s", (sigla, 1))
                        ativo_result = cursor.fetchone()

                        if ativo_result:
                            idativo = ativo_result[0]
                        else:
                            # Inserir novo ativo
                            cursor.execute(
                                "INSERT INTO ativo (sigla, razaosocial, idbolsa) VALUES (%s, %s, %s) RETURNING id",
                                (str.upper(sigla), razaosocial, 1)
                            )
                            idativo = cursor.fetchone()[0]
                            #conn.commit()

                        # Inserir na tabela radar
                        cursor.execute(
                            """
                            INSERT INTO radar (dataprovavel, idativo, tipoprovento, valorprovento, ultimacotacao, dy, datacom, idbolsa)
                            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                            """,
                            (dataprovavel, idativo, tipoprovento, valorprovento, ultimacotacao, dy, datacom, 1)
                        )
                    except Exception as e:
                        print(f"Erro ao processar {sigla}: {e}")
                        cursor.execute("ROLLBACK TO SAVEPOINT before_insert")  # Reverte apenas esta tentativa
                    finally:
                        cursor.execute("RELEASE SAVEPOINT before_insert")  # Libera o savepoint
                        

            conn.commit()
            cursor.close()
            conn.close()

            self.moverArquivo(caminho)

            wx.MessageBox("Importação concluída com sucesso!", "Sucesso", wx.OK | wx.ICON_INFORMATION)

        except Exception as e:
            wx.MessageBox(f"Erro durante a importação: {e}", "Erro", wx.OK | wx.ICON_ERROR)

    def moverArquivo(self, origem):
        destino_dir = os.path.join(os.path.dirname(origem), "importados")
        if not os.path.exists(destino_dir):
            os.makedirs(destino_dir)

        nome_arquivo = os.path.basename(origem)
        destino = os.path.join(destino_dir, nome_arquivo)
        shutil.move(origem, destino)

        wx.MessageBox(f"Arquivo movido", "Fim de processo", wx.OK | wx.ICON_INFORMATION)

if __name__ == '__main__':
    app = wx.App()
    LeRadarB3()
    app.MainLoop()
