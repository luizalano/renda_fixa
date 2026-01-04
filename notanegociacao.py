# coding: utf-8
from ativoNegociado import AtivoNegociado
from conta import Conta
from databasefunctions import *
from diversos import *

class NotaNegociacao:
    def __init__(self):
        self.numero_nota = ''
        self.data_operacao = ''
        self.data_efetivacao = ''
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
        self.data_operacao = devolveDataDMY(arg)
    def set_data_efetivacao(self, arg):
        self.data_efetivacao = devolveDataDMY(arg)
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
                    "INSERT INTO notanegocicao (numero_nota, data_operacao, id_conta, dataefetivacao) VALUES (%s, %s, %s, %s)",
                    (self.numero_nota, self.data_operacao, self.id_conta, self.data_efetivacao),
                )
                self.con.commit()
                self.con.close()

    def update(self):
        self.con = self.getConexao()
        with self.con.cursor() as cursor:
            cursor.execute("UPDATE notanegociacao SET numeronota = %s, "
                           "data_operacao = %s, "
                           "id_conta = %s, "
                           "dataefetivacao = %s "
                           "WHERE numeronota = %s", (self.numero_nota, self.data_operacao, self.id_conta, self.data_efetivacao, self.numero_nota))
            self.con.commit()
            self.con.close()

    def delete(self):
        self.con = self.getConexao()
        with self.con.cursor() as cursor:
            cursor.execute("DELETE FROM notanegociacao WHERE numeronota = %s", (self.numero_nota,))
            self.con.commit()
            self.clear()
            self.con.close()

    def clear(self):
        self.set_numero_nota('')
        self.set_data_operacao('')
        self.set_data_efetivacao('')
        self.set_id_conta(-1)

    def selectByNumeroNota(self, arg):
        self.con = self.getConexao()
        cursor = self.con.cursor()
        self.clear()
        cursor.execute("SELECT numeronota, dataoperacao, idconta, dataefetivacao FROM notanegociacao WHERE numeronota = %s", (arg,))
        row = cursor.fetchone()
        if row:
            self.set_numero_nota(row[0])
            self.set_data_operacao(row[1])
            self.set_id_conta(row[2])
            self.set_data_efetivacao(row[3])
        self.con.close()

    def criaNotaNegociao(self, numero_nota, data_operacao, id_conta, data_efetivacao):
        if len(numero_nota) == 0:
            return
        self.selectByNumeroNota(numero_nota)
        if self.numero_nota == '':
            self.set_numero_nota(numero_nota)
            self.set_data_operacao(data_operacao)
            self.set_id_conta(id_conta)
            self.set_data_efetivacao(data_efetivacao)
            id = self.insert()

            AtivoNegociado().insere_numero_nota_negociaco(numero_nota, data_operacao, id_conta)

    @staticmethod
    def mc_busca_todas(dias):
        conexao = NotaNegociacao.getConexao()

        with conexao.cursor() as cursor:
            clausulaSql = "select n.numeronota, n.dataoperacao, n.idconta, n.dataefetivacao " \
                          "from notanegociacao as n join conta as c on c.id = n.idconta " \
                          "where n.dataoperacao >= current_date - interval '%s days'"
            cursor.execute(clausulaSql, (dias,))
            resultado = cursor.fetchall()
            conexao.close()
            return resultado

    @staticmethod
    def mc_saldo_por_nota(idconta):
        conexao = NotaNegociacao.getConexao()
        with conexao.cursor() as cursor:
            clausulaSql = "WITH operacoes AS (SELECT numeronota, idconta, " \
                          "    SUM(CASE operacao WHEN 1 THEN qtdeoperacao * valoroperacao * -1" \
                          "                      WHEN 2 THEN qtdeoperacao * valoroperacao ELSE 0" \
                          "            END) AS total_operacoes" \
                          "    FROM ativonegociado WHERE numeronota IS NOT NULL GROUP BY numeronota, idconta), " \
                          "despesas_nota AS (SELECT numeronota, idconta, SUM(valor * -1) AS total_despesas " \
                          "    FROM despesas WHERE numeronota IS NOT NULL GROUP BY numeronota, idconta) " \
                          "SELECT nn.numeronota, nn.dataefetivacao, nn.dataoperacao, " \
                          "      COALESCE(o.total_operacoes, 0) " \
                          "    + COALESCE(d.total_despesas, 0) AS valorliquido " \
                          "FROM notanegociacao nn LEFT JOIN operacoes o ON o.numeronota = nn.numeronota AND o.idconta = nn.idconta " \
                          "LEFT JOIN despesas_nota d ON d.numeronota = nn.numeronota AND d.idconta = nn.idconta " \
                          "WHERE nn.idconta = %s ORDER BY nn.dataoperacao, nn.numeronota;"
            cursor.execute(clausulaSql, (idconta,))
            resultado = cursor.fetchall()
            conexao.close()
            return resultado

    @staticmethod
    def mc_saldo_da_nota(conta, nota):
        conexao = NotaNegociacao.getConexao()

        lista = Conta.mc_select_one_by_nome(conta)
        if len(lista) == 0:
            conexao.close()
            return None
        idconta = lista[0]
        with conexao.cursor() as cursor:
            clausulaSql = "WITH operacoes AS (SELECT numeronota, idconta, " \
                          "    SUM(CASE operacao WHEN 1 THEN qtdeoperacao * valoroperacao * -1" \
                          "                      WHEN 2 THEN qtdeoperacao * valoroperacao ELSE 0" \
                          "            END) AS total_operacoes" \
                          "    FROM ativonegociado WHERE numeronota IS NOT NULL GROUP BY numeronota, idconta), " \
                          "despesas_nota AS (SELECT numeronota, idconta, SUM(valor * -1) AS total_despesas " \
                          "    FROM despesas WHERE numeronota IS NOT NULL GROUP BY numeronota, idconta) " \
                          "SELECT nn.numeronota, nn.dataefetivacao, nn.dataoperacao, " \
                          "      COALESCE(o.total_operacoes, 0) " \
                          "    + COALESCE(d.total_despesas, 0) AS valorliquido " \
                          "FROM notanegociacao nn LEFT JOIN operacoes o ON o.numeronota = nn.numeronota AND o.idconta = nn.idconta " \
                          "LEFT JOIN despesas_nota d ON d.numeronota = nn.numeronota AND d.idconta = nn.idconta " \
                          "WHERE nn.idconta = %s and nn.numeronota = %s ORDER BY nn.dataoperacao, nn.numeronota;"
            cursor.execute(clausulaSql, (idconta, nota))
            resultado = cursor.fetchone()
            conexao.close()
            return resultado[3]

def main():
    resultado = NotaNegociacao.mc_saldo_por_nota(12)
    for row in resultado:
        print(row)
    saldo = NotaNegociacao.mc_saldo_da_nota('XP - Neovalor', '126963194')
    print(saldo)

if __name__ == '__main__':
    main()