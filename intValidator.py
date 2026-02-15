import wx

class IntValidator(wx.Validator):

    def __init__(self, allow_empty=False):
        super().__init__()
        self.allow_empty = allow_empty

    def Clone(self):
        return IntValidator(self.allow_empty)

    def Validate(self, parent):
        ctrl = self.GetWindow()
        value = ctrl.GetValue()

        if self.allow_empty and value == "":
            return True

        if value.isdigit():
            return True

        wx.MessageBox("Digite apenas números inteiros.",
                      "Erro",
                      wx.OK | wx.ICON_ERROR)
        ctrl.SetFocus()
        return False

    def TransferToWindow(self):
        return True

    def TransferFromWindow(self):
        return True
