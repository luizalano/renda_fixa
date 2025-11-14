# coding: utf-8
import wx
import psycopg2

class SelecionaBolsaDialog(wx.Dialog):
    def __init__(self, parent):
        super().__init__(parent, title="Escolha a bolsa", size=(400, 200))

        self.selected_id = None  # Para armazenar o ID da conta selecionada
        self.selected_nome = None

        # Layout
        vbox = wx.BoxSizer(wx.VERTICAL)
        self.combo = wx.ComboBox(self, style=wx.CB_READONLY)

        vbox.Add(wx.StaticText(self, label="Selecione uma bolsa:"), flag=wx.ALL, border=10)
        vbox.Add(self.combo, flag=wx.EXPAND | wx.ALL, border=10)

        btn_sizer = wx.BoxSizer(wx.HORIZONTAL)
        btn_ok = wx.Button(self, wx.ID_OK, "Confirmar")
        btn_cancel = wx.Button(self, wx.ID_CANCEL, "Cancelar")

        btn_sizer.Add(btn_ok, flag=wx.ALL, border=5)
        btn_sizer.Add(btn_cancel, flag=wx.ALL, border=5)
        vbox.Add(btn_sizer, flag=wx.ALIGN_CENTER | wx.ALL, border=10)

        self.SetSizer(vbox)

        # Preenchendo a ComboBox com os dados do banco
        self.preencher_bolsas()

        # Evento para capturar seleção
        self.combo.Bind(wx.EVT_COMBOBOX, self.on_selecionar)

    def get_conexao(self):
        """Conecta ao PostgreSQL"""
        try:
            return psycopg2.connect(
                dbname="b3",
                user="postgres",
                password="seriate",
                host="localhost",
                port="5432"
            )
        except psycopg2.Error as e:
            wx.MessageBox(f"Erro ao conectar ao banco:\n{e}", "Erro", wx.ICON_ERROR)
            return None

    def preencher_bolsas(self):
        conn = self.get_conexao()
        if conn:
            try:
                cur = conn.cursor()
                cur.execute("SELECT id, sigla FROM bolsa ORDER BY sigla")
                self.dados_bolsas = {nome: id for id, nome in cur.fetchall()}  # Dicionário {nome: id}
                cur.close()
                conn.close()

                self.combo.AppendItems(list(self.dados_bolsas.keys()))
            except psycopg2.Error as e:
                wx.MessageBox(f"Erro ao buscar contas:\n{e}", "Erro", wx.ICON_ERROR)

    def on_selecionar(self, event):
        """Salva o ID da conta ao selecionar"""
        nome_bolsa = self.combo.GetValue()
        self.selected_id = self.dados_bolsas.get(nome_bolsa)
        self.selected_nome = nome_bolsa


# 🔹 **Chamando o diálogo**
def chamar_dialogo():
    app = wx.App(False)
    dlg = SelecionaBolsaDialog(None)
    if dlg.ShowModal() == wx.ID_OK and dlg.selected_id:
        print(f"Bolsa selecionada: ID {dlg.selected_id}")
    dlg.Destroy()
    app.MainLoop()

# 🔹 Executando
if __name__ == "__main__":
    chamar_dialogo()
