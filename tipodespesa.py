# coding: utf-8
from databasefunctions import *

class TipoDespesa:
    def __init__(self):
        self.id = -1
        self.nome_tipo_despesa = ''

    def set_nome_tipo_despesa(self, arg):
        if isinstance(arg, (str)): self.nome_tipo_despesa = arg

    def insert(self):
        con = self.getConexao()
        if len(self.nome_tipo_despesa) > 0:
            with con.cursor() as cursor:
                cursor.execute(
                    "INSERT INTO tipodespesa (nomedespesa) VALUES (%s) RETURNING id",
                    (self.nome_tipo_despesa, ),
                )
                self.id = cursor.fetchone()[0]
                con.commit()
                con.close()

    def update(self):
        con = self.getConexao()
        with con.cursor() as cursor:
            cursor.execute("UPDATE tipodespesa SET nomedespesa = %s, "                           
                           "WHERE id = %s", (self.nome_tipo_despesa, self.id))
            con.commit()
            con.close()

    def delete(self):
        con = self.getConexao()
        with con.cursor() as cursor:
            cursor.execute("DELETE FROM tipodespesa WHERE id = %s", (self.id,))
            con.commit()
            self.clear()
            con.close()

    def clear(self):
        self.id = -1
        self.set_nome_tipo_despesa('')

    def selectById(self, arg):
        con = self.getConexao()
        cursor = con.cursor()
        self.clear()
        cursor.execute("SELECT id, nomedespesa FROM tipodespesa WHERE id = %s", (arg,))
        row = cursor.fetchone()
        if row:
            self.id = row[0]
            self.set_nome_tipo_despesa(row[1])
        con.close()

    def selectByNomeTipoDespesa(self, arg):
        con = self.getConexao()
        cursor = con.cursor()
        self.clear()
        #with self.conexao.cursor as cursor:
        cursor.execute("SELECT id, nomedespesa FROM tipodespesa WHERE upper(nomedespesa) = upper(%s)", (arg,))
        row = cursor.fetchone()
        if row:
            self.id = row[0]
            self.set_nome_tipo_despesa(row[1])
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
        con = TipoDespesa.getConexao()
        cursor = con.cursor()
        #with self.conexao.cursor as cursor:
        cursor.execute("SELECT id, nomedespesa FROM tipodespesa order by nomedespesa")
        lista = cursor.fetchall()
        if lista:
            con.close()
            return lista
            
        con.close()

    @staticmethod
    def mc_select_by_id(self, arg):
        con = TipoDespesa.getConexao()
        cursor = con.cursor()
        self.clear()
        cursor.execute("SELECT id, nomedespesa FROM tipodespesa WHERE id = %s", (arg,))
        lista = cursor.fetchone()
        con.close()
        return lista



def main():
    bolsa = TipoDespesa()
    bolsa.selectById(1)
    print('')
    print(bolsa.nome_tipo_despesa)
    print(' ')
    bolsa.set_nome_tipo_despesa('NOME NOVO')
    print(bolsa.nome_tipo_despesa)
    print('Inserindo uma TipoDespesa nova')

    bolsa.selectById(-2)
    print(bolsa.nome_tipo_despesa)

    bolsa.set_nome_tipo_despesa('TipoDespesa Nova')
    bolsa.insert()
    print (bolsa.id)

    bolsa.delete()

    lista = TipoDespesa.classe_selectAll()
    print(lista)
    print('acabou')


if __name__ == '__main__':
    main()
