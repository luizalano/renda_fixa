# coding: utf-8
from databasefunctions import *

class Bolsa:
    def __init__(self):
        self.id = -1
        self.sigla = ''
        self.nome_bolsa = ''
        self.nome_indice = ''
        self.id_moeda = 2
        self.con = None

    @staticmethod
    def getConexao():
        try:
            con = ConectaBD.retornaConexao()
            return con
        except Exception as e:
            print(f"Erro ao conectar com o banco: {e}")
            return False

    def set_nome_bolsa(self, arg):
        if isinstance(arg, (str)): self.nome_bolsa = arg
    def set_nome_indice(self, arg):
        if isinstance(arg, (str)): self.nome_indice = arg
    def set_sigla(self, arg):
        if isinstance(arg, (str)): self.sigla = arg
    def set_id_moeda(self, arg):
        self.id_moeda = 2
        if isinstance(arg, (int)):
            self.con = self.getConexao()
            with self.con.cursor() as cursor:
                cursor.execute("SELECT id FROM moeda WHERE id = %s", (arg,))
                resultado = cursor.fetchone()
                if resultado:
                    self.idmoeda = arg
                #else:
                #    raise ValueError("Moda não encontrada")
            self.con.close()

    def insert(self):
        self.con = self.getConexao()
        if len(self.nome_bolsa) > 0:
            with self.con.cursor() as cursor:
                cursor.execute(
                    "INSERT INTO bolsa (nomebolsa, sigla, nomeindice, idmoeda) VALUES (%s, %s, %s, %s) RETURNING id",
                    (self.nome_bolsa, self.sigla, self.nome_indice, self.id_moeda),
                )
                self.id = cursor.fetchone()[0]
                self.con.commit()
                self.con.close()

    def update(self):
        self.con = self.getConexao()
        with self.con.cursor() as cursor:
            cursor.execute("UPDATE bolsa SET nomebolsa = %s, "
                           "sigla = %s, "
                           "nomeindice = %s, "
                           "idmoeda = %s, "
                           "WHERE id = %s", (self.nome_bolsa, self.sigla, self.nome_indice, self.id_moeda, self.id))
            self.con.commit()
            self.con.close()

    def delete(self):
        self.con = self.getConexao()
        with self.con.cursor() as cursor:
            cursor.execute("DELETE FROM bolsa WHERE id = %s", (self.id,))
            self.con.commit()
            self.clear()
            self.con.close()

    def clear(self):
        self.id = -1
        self.set_nome_bolsa('')
        self.set_nome_indice('')
        self.set_sigla('')
        self.set_id_moeda(-1)

    def selectById(self, arg):
        self.con = self.getConexao()
        cursor = self.con.cursor()
        self.clear()
        #with self.conexao.cursor as cursor:
        cursor.execute("SELECT id, sigla, nomebolsa, nomeindice, idmoeda FROM bolsa WHERE id = %s", (arg,))
        row = cursor.fetchone()
        if row:
            self.id = row[0]
            self.set_sigla(row[1])
            self.set_nome_bolsa(row[2])
            self.set_nome_indice(row[3])
            self.set_id_moeda(row[4])
        self.con.close()

    def selectByNomeBolsa(self, arg):
        self.con = self.getConexao()
        cursor = self.con.cursor()
        self.clear()
        #with self.conexao.cursor as cursor:
        cursor.execute("SELECT id, sigla, nomebolsa, nomeindice, idmoeda FROM Bolsa WHERE upper(nomebolsa) = upper(%s)", (arg,))
        row = cursor.fetchone()
        if row:
            self.id = row[0]
            self.set_sigla(row[1])
            self.set_nome_bolsa(row[2])
            self.set_nome_indice(row[3])
            self.set_id_moeda(row[4])
        self.con.close()

    @staticmethod
    def selectOneById(id):
        try:
            conexao = ConectaBD.retornaConexao()
        except Exception as e:
            print(f"Erro ao conectar com o banco: {e}")
            return False
        cursor = conexao.cursor()
        cursor.execute("SELECT b.id, b.sigla, b.nomebolsa, b.nomeindice, b.idmoeda, m.nomemoeda "
                       "FROM bolsa as b join moeda as m on m.id = b.idmoeda WHERE b.id = %s", (id,))
        lista = cursor.fetchone()
        if lista:
            return lista
        else: return None

    @staticmethod
    def selectOneByNome(nome):
        try:
            conexao = ConectaBD.retornaConexao()
        except Exception as e:
            print(f"Erro ao conectar com o banco: {e}")
            return False
        cursor = conexao.cursor()
        #with self.conexao.cursor as cursor:
        cursor.execute("SELECT b.id, b.sigla, b.nomebolsa, b.nomeindice, b.idmoeda, m.nomemoeda  "
                       "FROM bolsa as b join moeda as m on m.id = c.idmoeda WHERE c.nomeBolsa = %s", (nome,))
        lista = cursor.fetchone()
        if lista:
            return lista
        else:
            return None

    @staticmethod
    def selectAll():
        try:
            conexao = ConectaBD.retornaConexao()
        except Exception as e:
            print(f"Erro ao conectar com o banco: {e}")
            return False
        cursor = conexao.cursor()
        #with self.conexao.cursor as cursor:
        clausulaSql = "SELECTid, sigla, nomebolsa, nomeindice, idmoeda " \
                      "FROM blsa order by nomeBolsa"
        cursor.execute(clausulaSql)
        lista = cursor.fetchall()
        if lista:
            return lista


def main():
    bolsa = Bolsa()
    bolsa.selectById(1)
    print('')
    print(bolsa.nome_bolsa)
    print(bolsa.sigla)
    print(' ')
    bolsa.set_nome_bolsa('NOME NOVO')
    bolsa.set_sigla('PPP')
    print(bolsa.nome_bolsa)
    print(bolsa.id_moeda)
    print('Inserindo uma Bolsa nova')

    bolsa.selectById(-2)
    print(str(bolsa.id) + ' - ' + bolsa.nome_bolsa)

    bolsa.set_nome_bolsa('Bolsa Nova')
    bolsa.set_id_moeda(1)
    bolsa.set_sigla('ppk')
    bolsa.insert()
    print (bolsa.id)

    bolsa.delete()

    print('acabou')


if __name__ == '__main__':
    main()
