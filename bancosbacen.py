# coding: utf-8
from databasefunctions import *

class BancosBacen:
    def __init__(self):
        self.numero = -1
        self.nome = ''

    @staticmethod
    def getConexao():
        try:
            con = ConectaBD.retornaConexao()
            return con
        except Exception as e:
            print(f"Erro ao conectar com o banco: {e}")
            return False

    def set_numero(self, arg):
        if isinstance(arg, (int)) and arg >= 0:
            self.numero = arg
        else:
            self.numero = -1

    def set_nome(self, arg):
        if isinstance(arg, (str)): self.nome = arg

    def insert(self):
        con = self.getConexao()
        cursor = con.cursor()
        cursor.execute("INSERT INTO bancosbacen (numero, nome) VALUES (%s, %s)", (self.numero, self.nome))
        con.commit()
        con.close()

    def update(self):
        con = self.getConexao()
        cursor = con.cursor()
        cursor.execute("UPDATE bancosbacen SET nome = %s  WHERE numero = %s", (self.nome, self.numero))
        con.commit()
        con.close()

    def delete(self):
        con = self.getConexao()
        cursor = con.cursor()
        cursor.execute("DELETE FROM bancosbacen WHERE numero = %s", (self.numero,))
        con.commit()
        con.close()

    def selectbyNumero(self, numero):
        con = self.getConexao()
        cursor = con.cursor()
        self.set_numero(-1)
        self.set_nome('')
        cursor.execute("SELECT numero, nome FROM bancosbacen WHERE numero = %s", (numero,))
        row = cursor.fetchone()
        if row:
            self.set_numero(row[0])
            self.set_nome(row[1])
        con.close()

def main():
    bb = BancosBacen()
    bb.selectbyNumero(1)
    print(bb.numero)
    print(bb.nome)

    bb.set_numero(99999)
    bb.set_nome('Para Deletar')
    bb.insert()

    bb.selectbyNumero(99999)
    print(bb.numero)
    print(bb.nome)

    bb.set_nome('Para Deletar alterado')
    bb.update()

    bb.selectbyNumero(99999)
    print(bb.numero)
    print(bb.nome)

    bb.delete()





if __name__ == '__main__':
    main()
