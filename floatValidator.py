import re
import wx

class FloatValidator(wx.Validator):

    def __init__(self, allow_empty=False):
        super().__init__()
        self.allow_empty = allow_empty
        self.pattern = re.compile(r'^\d+([.,]\d{1,2})?$')

    def Clone(self):
        return FloatValidator(self.allow_empty)

    def Validate(self, parent):
        ctrl = self.GetWindow()
        value = ctrl.GetValue().strip()

        if self.allow_empty and value == "":
            return True

        if self.pattern.match(value):
            return True

        wx.MessageBox("Digite um valor numérico válido.\nEx: 123.45",
                      "Erro",
                      wx.OK | wx.ICON_ERROR)
        ctrl.SetFocus()
        return False

    def TransferToWindow(self):
        return True

    def TransferFromWindow(self):
        return True
