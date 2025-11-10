# coding: utf-8
from databasefunctions import *

class Corretora:
    def __init__(self):
        self.id = -1
        self.nome_corretora = ''
        self.con = None

    def getConexao(self):
        try:
            self.con = ConectaBD.retornaConexao()
            self.cursor = self.con.cursor()
            return True
        except Exception as e:
            print(f"Erro ao conectar com o banco: {e}")
            return False

    def set_nome_corretora(self, arg):
        if isinstance(arg, (str)): self.nome_corretora = arg

    def insert(self):
        self.getConexao()
        if len(self.nome_corretora) > 0:
            with self.con.cursor() as cursor:
                cursor.execute(
                    "INSERT INTO corretora (nome) VALUES (%s) RETURNING id",
                    (self.nome_corretora, ),
                )
                self.id = cursor.fetchone()[0]
                self.con.commit()
                self.con.close()

    def update(self):
        self.getConexao()
        with self.con.cursor() as cursor:
            cursor.execute("UPDATE corretora SET nome = %s, "                           
                           "WHERE id = %s", (self.nome_corretora, ))
            self.con.commit()
            self.con.close()

    def delete(self):
        self.getConexao()
        with self.con.cursor() as cursor:
            cursor.execute("DELETE FROM corretora WHERE id = %s", (self.id,))
            self.con.commit()
            self.clear()
            self.con.close()

    def clear(self):
        self.id = -1
        self.set_nome_corretora('')

    def selectById(self, arg):
        self.getConexao()
        cursor = self.con.cursor()
        self.clear()
        #with self.conexao.cursor as cursor:
        cursor.execute("SELECT id, nome FROM corretora WHERE id = %s", (arg,))
        row = cursor.fetchone()
        if row:
            self.id = row[0]
            self.set_nome_corretora(row[1])
        self.con.close()

    def selectByNomeCorretora(self, arg):
        self.getConexao()
        cursor = self.con.cursor()
        self.clear()
        #with self.conexao.cursor as cursor:
        cursor.execute("SELECT id, nome FROM corretora WHERE upper(nome) = upper(%s)", (arg,))
        row = cursor.fetchone()
        if row:
            self.id = row[0]
            self.set_nome_corretora(row[1])
        self.con.close()


def main():
    bolsa = Corretora()
    bolsa.selectById(1)
    print('')
    print(bolsa.nome_corretora)
    print(' ')
    bolsa.set_nome_corretora('NOME NOVO')
    print(bolsa.nome_corretora)
    print('Inserindo uma Corretora nova')

    bolsa.selectById(-2)
    print(bolsa.nome_corretora)

    bolsa.set_nome_corretora('Corretora Nova')
    bolsa.insert()
    print (bolsa.id)

    bolsa.delete()

    print('acabou')


if __name__ == '__main__':
    main()
