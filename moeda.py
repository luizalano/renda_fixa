# coding: utf-8
from databasefunctions import *

class Moeda:
    def __init__(self):
        self.id = -1
        self.nome_moeda = ''
        self.sigla = ''

    def set_nome_moeda(self, arg):
        if isinstance(arg, (str)): self.nome_moeda = arg

    def set_sigla(self, arg):
        if isinstance(arg, (str)): self.sigla = arg

    def insert(self):
        con = self.getConexao()
        if len(self.nome_moeda) > 0:
            with con.cursor() as cursor:
                cursor.execute(
                    "INSERT INTO moeda (nomemoeda, sigla) VALUES (%s, %s) RETURNING id",
                    (self.nome_moeda, self.sigla),
                )
                self.id = cursor.fetchone()[0]
                con.commit()
                con.close()

    def update(self):
        con = self.getConexao()
        with con.cursor() as cursor:
            cursor.execute("UPDATE moeda SET nomemoeda = %s, sigla = %s"
                           "WHERE id = %s", (self.nome_moeda, self.sigla, self.id))
            con.commit()
            con.close()

    def delete(self):
        con = self.getConexao()
        with con.cursor() as cursor:
            cursor.execute("DELETE FROM moeda WHERE id = %s", (self.id,))
            con.commit()
            self.clear()
            con.close()

    def clear(self):
        self.id = -1
        self.set_nome_moeda('')
        self.set_sigla('')

    def selectById(self, arg):
        con = self.getConexao()
        cursor = con.cursor()
        self.clear()
        cursor.execute("SELECT id, nomemoeda, sigla FROM moeda WHERE id = %s", (arg,))
        row = cursor.fetchone()
        if row:
            self.id = row[0]
            self.set_nome_moeda(row[1])
            self.set_sigla(row[2])
        con.close()

    def selectByNomeMoeda(self, arg):
        con = self.getConexao()
        cursor = con.cursor()
        self.clear()
        #with self.conexao.cursor as cursor:
        cursor.execute("SELECT id, nomemoeda, sigla FROM moeda WHERE upper(nomemoeda) = upper(%s)", (arg,))
        row = cursor.fetchone()
        if row:
            self.id = row[0]
            self.set_nome_moeda(row[1])
            self.set_sigla(row[2])
        con.close()
    @staticmethod
    def getConexao():
        try:
            con = ConectaBD.retornaConexao()
            return con
        except Exception as e:
            print(f"Erro ao conectar com o banco: {e}")
            return False


    @staticmethod
    def classe_selectAll():
        con = Moeda.getConexao()
        cursor = con.cursor()
        #with self.conexao.cursor as cursor:
        cursor.execute("SELECT id, nomemoeda, sigla FROM moeda order by nomemoeda")
        lista = cursor.fetchall()
        if lista:
            con.close()
            return lista
            
        con.close()


def main():
    bolsa = Moeda()
    bolsa.selectById(1)
    print('')
    print(bolsa.nome_moeda)
    print(' ')
    bolsa.set_nome_moeda('NOME NOVO')
    print(bolsa.nome_moeda)
    print('Inserindo uma Moeda nova')

    bolsa.selectById(-2)
    print(bolsa.nome_moeda)

    bolsa.set_nome_moeda('Moeda Nova')
    bolsa.insert()
    print (bolsa.id)

    bolsa.delete()

    lista = Moeda.classe_selectAll()
    print(lista)
    print('acabou')


if __name__ == '__main__':
    main()
