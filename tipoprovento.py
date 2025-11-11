# coding: utf-8
from databasefunctions import *

class TipoProvento:
    def __init__(self):
        self.id = -1
        self.nome_tipo_provento = ''

    def set_nome_tipo_provento(self, arg):
        if isinstance(arg, (str)): self.nome_tipo_provento = arg

    def insert(self):
        con = self.getConexao()
        if len(self.nome_tipo_provento) > 0:
            with con.cursor() as cursor:
                cursor.execute(
                    "INSERT INTO tipoprovento (nometipoprovento) VALUES (%s) RETURNING id",
                    (self.nome_tipo_provento, ),
                )
                self.id = cursor.fetchone()[0]
                con.commit()
                con.close()

    def update(self):
        con = self.getConexao()
        with con.cursor() as cursor:
            cursor.execute("UPDATE tipoprovento SET nometipoprovento = %s, "                           
                           "WHERE id = %s", (self.nome_tipo_provento, self.id))
            con.commit()
            con.close()

    def delete(self):
        con = self.getConexao()
        with con.cursor() as cursor:
            cursor.execute("DELETE FROM tipoprovento WHERE id = %s", (self.id,))
            con.commit()
            self.clear()
            con.close()

    def clear(self):
        self.id = -1
        self.set_nome_tipo_provento('')

    def selectById(self, arg):
        con = self.getConexao()
        cursor = con.cursor()
        self.clear()
        cursor.execute("SELECT id, nometipoprovento FROM tipoprovento WHERE id = %s", (arg,))
        row = cursor.fetchone()
        if row:
            self.id = row[0]
            self.set_nome_tipo_provento(row[1])
        con.close()

    def selectByNomeTipoProvento(self, arg):
        con = self.getConexao()
        cursor = con.cursor()
        self.clear()
        #with self.conexao.cursor as cursor:
        cursor.execute("SELECT id, nometipoprovento FROM tipoprovento WHERE upper(nometipoprovento) = upper(%s)", (arg,))
        row = cursor.fetchone()
        if row:
            self.id = row[0]
            self.set_nome_tipo_provento(row[1])
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
        con = TipoProvento.getConexao()
        cursor = con.cursor()
        #with self.conexao.cursor as cursor:
        cursor.execute("SELECT id, nometipoprovento FROM tipoprovento order by nometipoprovento")
        lista = cursor.fetchall()
        if lista:
            con.close()
            return lista
            
        con.close()


def main():
    bolsa = TipoProvento()
    bolsa.selectById(1)
    print('')
    print(bolsa.nome_tipo_provento)
    print(' ')
    bolsa.set_nome_tipo_provento('NOME NOVO')
    print(bolsa.nome_tipo_provento)
    print('Inserindo uma TipoProvento nova')

    bolsa.selectById(-2)
    print(bolsa.nome_tipo_provento)

    bolsa.set_nome_tipo_provento('TipoProvento Nova')
    bolsa.insert()
    print (bolsa.id)

    bolsa.delete()

    lista = TipoProvento.classe_selectAll()
    print(lista)
    print('acabou')


if __name__ == '__main__':
    main()
