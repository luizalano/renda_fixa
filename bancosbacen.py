# coding: utf-8
from databasefunctions import *

class BancosBacen:
    def __init__(self):
        self.numero = -1
        self.nome = ''
        self.getConexao()

    def getConexao(self):
        try:
            self.con = ConectaBD.retornaConexao()
            self.cursor = self.con.cursor()
            return True
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
        self.getConexao()
        self.cursor.execute("INSERT INTO bancosbacen (numero, nome) VALUES (%s, %s)", (self.numero, self.nome))
        self.con.commit()
        self.con.close()

    def update(self):
        self.getConexao()
        self.cursor.execute("UPDATE bancosbacen SET nome = %s  WHERE numero = %s", (self.nome, self.numero))
        self.con.commit()
        self.con.close()

    def delete(self):
        self.getConexao()
        self.cursor.execute("DELETE FROM bancosbacen WHERE numero = %s", (self.numero,))
        self.con.commit()
        self.con.close()

    def selectbyNumero(self, numero):
        self.getConexao()
        self.set_numero(-1)
        self.set_nome('')
        self.cursor.execute("SELECT numero, nome FROM bancosbacen WHERE numero = %s", (numero,))
        row = self.cursor.fetchone()
        if row:
            self.set_numero(row[0])
            self.set_nome(row[1])
        self.con.close()

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
