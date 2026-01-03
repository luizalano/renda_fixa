# coding: utf-8
from ativoNegociado import AtivoNegociado
from databasefunctions import *

class NotaNegociacao:
    def __init__(self):
        self.id = -1
        self.numero_nota = ''
        self.data_operacao = ''
        self.id_conta = -1
        self.con = None

    @staticmethod
    def getConexao():
        try:
            con = ConectaBD.retornaConexao()
            return con
        except Exception as e:
            print(f"Erro ao conectar com o banco: {e}")
            return False

    def set_numero_nota(self, arg):
        if isinstance(arg, (str)): self.numero_nota = arg
    def set_data_operacao(self, arg):
        if isinstance(arg, (str)): self.data_operacao = arg
    def set_id_conta(self, arg):
        self.id_conta = -1
        if isinstance(arg, (int)):
            self.con = self.getConexao()
            with self.con.cursor() as cursor:
                cursor.execute("SELECT id FROM conta WHERE id = %s", (arg,))
                resultado = cursor.fetchone()
                if resultado:
                    self.id_conta = arg
                #else:
                #    raise ValueError("Moda não encontrada")
        if isinstance(arg, (str)):
            self.con = self.getConexao()
            with self.con.cursor() as cursor:
                cursor.execute("SELECT id FROM conta WHERE upper(sigla) = upper(%s)", (arg,))
                resultado = cursor.fetchone()
                if resultado:
                    self.id_conta = arg
            self.con.close()

    def insert(self):
        self.con = self.getConexao()
        retorno = -1
        if len(self.numero_nota) > 0:
            with self.con.cursor() as cursor:
                cursor.execute(
                    "INSERT INTO notanegocicao (numero_nota, data_operacao, id_conta) VALUES (%s, %s, %s) RETURNING id",
                    (self.numero_nota, self.data_operacao, self.id_conta),
                )
                self.id = cursor.fetchone()[0]
                retorno = self.id
                self.con.commit()
                self.con.close()
        return retorno

    def update(self):
        self.con = self.getConexao()
        with self.con.cursor() as cursor:
            cursor.execute("UPDATE notanegociacao SET numero_nota = %s, "
                           "data_operacao = %s, "
                           "id_conta = %s "
                           "WHERE id = %s", (self.numero_nota, self.data_operacao, self.id_conta, self.id))
            self.con.commit()
            self.con.close()

    def delete(self):
        self.con = self.getConexao()
        with self.con.cursor() as cursor:
            cursor.execute("DELETE FROM notanegociacao WHERE id = %s", (self.id,))
            self.con.commit()
            self.clear()
            self.con.close()

    def clear(self):
        self.id = -1
        self.set_numero_nota('')
        self.set_data_operacao('')
        self.set_id_conta(-1)

    def selectById(self, arg):
        self.con = self.getConexao()
        cursor = self.con.cursor()
        self.clear()
        #with self.conexao.cursor as cursor:
        cursor.execute("SELECT id, numeronota, dataoperacao, idconta FROM notanegociacao WHERE id = %s", (arg,))
        row = cursor.fetchone()
        if row:
            self.id = row[0]
            self.set_numero_nota(row[1])
            self.set_data_operacao(row[2])
            self.set_id_conta(row[3])
        self.con.close()

    def selectByNumeroNota(self, arg):
        self.con = self.getConexao()
        cursor = self.con.cursor()
        self.clear()
        cursor.execute("SELECT id, numeronota, dataoperacao, idconta FROM notanegociacao WHERE numeronota = %s", (arg,))
        row = cursor.fetchone()
        if row:
            self.id = row[0]
            self.set_numero_nota(row[1])
            self.set_data_operacao(row[2])
            self.set_id_conta(row[3])
        self.con.close()

    def criaNotaNegociao(self, numero_nota, data_operacao, id_conta):
        self.selectByNumeroNota(numero_nota)
        if self.id == -1:
            self.set_numero_nota(numero_nota)
            self.set_data_operacao(data_operacao)
            self.set_id_conta(id_conta)
            id = self.insert()

            AtivoNegociado().insere_numero_nota_negociaco(id, numero_nota, data_operacao, id_conta)


