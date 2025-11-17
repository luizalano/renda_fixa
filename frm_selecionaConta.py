# coding: utf-8

import wx
from databasefunctions import ConectaBD

class SelecionaContaDialog(wx.Dialog):
    def __init__(self, parent):
        super().__init__(parent, title="Escolha a conta bancária", size=(400, 200))

        self.selected_id = None  # Para armazenar o ID da conta selecionada
        self.selected_nome = None

        # Layout
        vbox = wx.BoxSizer(wx.VERTICAL)
        self.combo = wx.ComboBox(self, style=wx.CB_READONLY)

        vbox.Add(wx.StaticText(self, label="Selecione uma conta:"), flag=wx.ALL, border=10)
        vbox.Add(self.combo, flag=wx.EXPAND | wx.ALL, border=10)

        btn_sizer = wx.BoxSizer(wx.HORIZONTAL)
        btn_ok = wx.Button(self, wx.ID_OK, "Confirmar")
        btn_cancel = wx.Button(self, wx.ID_CANCEL, "Cancelar")

        btn_sizer.Add(btn_ok, flag=wx.ALL, border=5)
        btn_sizer.Add(btn_cancel, flag=wx.ALL, border=5)
        vbox.Add(btn_sizer, flag=wx.ALIGN_CENTER | wx.ALL, border=10)

        self.SetSizer(vbox)

        # Preenchendo a ComboBox com os dados do banco
        self.preencher_contas()

        # Evento para capturar seleção
        self.combo.Bind(wx.EVT_COMBOBOX, self.on_selecionar)

    def getConexao(self):
        try:
            con = ConectaBD.retornaConexao()
            return con
        except Exception as e:
            print(f"Erro ao conectar com o banco: {e}")
            return False

    def preencher_contas(self):
        conn = self.getConexao()
        if conn:
            try:
                cur = conn.cursor()
                cur.execute("SELECT id, nomeconta FROM conta ORDER BY nomeconta")
                self.dados_contas = {nome: id for id, nome in cur.fetchall()}  # Dicionário {nome: id}
                cur.close()
                conn.close()

                self.combo.AppendItems(list(self.dados_contas.keys()))
            except Exception as e:
                wx.MessageBox(f"Erro ao buscar contas:\n{e}", "Erro", wx.ICON_ERROR)

    def on_selecionar(self, event):
        """Salva o ID da conta ao selecionar"""
        nome_conta = self.combo.GetValue()
        self.selected_id = self.dados_contas.get(nome_conta)
        self.selected_nome = nome_conta


# 🔹 **Chamando o diálogo**
def chamar_dialogo():
    app = wx.App(False)
    dlg = SelecionaContaDialog(None)
    if dlg.ShowModal() == wx.ID_OK and dlg.selected_id:
        print(f"Conta selecionada: ID {dlg.selected_id}")
    dlg.Destroy()
    app.MainLoop()

# 🔹 Executando
if __name__ == "__main__":
    chamar_dialogo()
