# coding: utf-8
from databasefunctions import *

from bancosbacen import BancosBacen

class Conta:
    def __init__(self):
        self.id = -1
        self.numero_banco = -1
        self.numero_agencia = ''
        self.iban = ''
        self.nome_conta = ''
        self.numero_conta = -1
        self.digito_conta = ''
        self.id_moeda = 2
        self.bancoBacen = BancosBacen()
        self.con = None

    @staticmethod
    def getConexao():
        try:
            con = ConectaBD.retornaConexao()
            return con
        except Exception as e:
            print(f"Erro ao conectar com o banco: {e}")
            return False

    def set_numero_banco(self, numero_banco):
        self.bancoBacen.selectbyNumero(numero_banco)
        if self.bancoBacen.numero > 0:
            self.numero_banco = numero_banco
        else:
            #raise ValueError("Banco não encontrado")
            self.numero_banco = -1

    def set_nome_conta(self, arg):
        if isinstance(arg, (str)): self.nome_conta = arg
    def set_numero_agencia(self, arg):
        if isinstance(arg, (str)): self.numero_agencia = arg
    def set_iban(self, arg):
        if isinstance(arg, (str)): self.iban = arg
    def set_numero_conta(self, arg):
        if isinstance(arg, (int)): self.numero_conta = arg
    def set_digito_conta(self, arg):
        if isinstance(arg, (str)): self.digito_conta = arg
    def set_id_moeda(self, arg):
        self.id_moeda = 2
        if isinstance(arg, (int)):
            con = self.getConexao()
            with con.cursor() as cursor:
                cursor.execute("SELECT id FROM moeda WHERE id = %s", (arg,))
                resultado = cursor.fetchone()
                if resultado:
                    self.id_moeda = arg
                #else:
                #    raise ValueError("Moda não encontrada")
            con.close()

    def insert(self):
        self.con = self.getConexao()
        if len(self.nome_conta) > 0:
            with self.con.cursor() as cursor:
                cursor.execute(
                    "INSERT INTO conta (numerobanco, numeroagencia, iban, nomeconta, numeroconta, digitoconta, idmoeda) VALUES (%s, %s, %s, %s, %s, %s, %s) RETURNING id",
                    (self.numero_banco, self.numero_agencia, self.iban, self.nome_conta, self.numero_conta, self.digito_conta, self.id_moeda,),
                )
                self.id = cursor.fetchone()[0]
                self.con.commit()
                self.con.close()

    def update(self):
        self.con = self.getConexao()
        with self.con.cursor() as cursor:
            cursor.execute("UPDATE conta SET numerobanco = %s, "
                           "numeroagencia = %s, "
                           "iban = %s, "
                           "nomeconta = %s, "
                           "numeroconta = %s, "
                           "digitoconta = %s, "
                           "idmoeda = %s "
                           "WHERE id = %s", (self.numero_banco, self.numero_agencia, self.iban, self.nome_conta, self.numero_conta, self.digito_conta, self.id_moeda, self.id))
            self.con.commit()
            self.con.close()

    def delete(self):
        self.con = self.getConexao()
        with self.con.cursor() as cursor:
            cursor.execute("DELETE FROM conta WHERE id = %s", (self.id,))
            self.con.commit()
            self.clear()
            self.con.close()

    def clear(self):
        self.id = -1
        self.numero_banco = -1
        self.set_numero_agencia(-1)
        self.set_iban('')
        self.set_nome_conta('')
        self.set_numero_conta(-1)
        self.set_digito_conta('')
        self.set_id_moeda(-1)

    def select_by_id(self, arg):
        self.con = self.getConexao()
        cursor = self.con.cursor()
        self.clear()
        #with self.conexao.cursor as cursor:
        cursor.execute("SELECT id, numerobanco, numeroagencia, iban, nomeconta, numeroconta, digitoconta, idmoeda FROM conta WHERE id = %s", (arg,))
        row = cursor.fetchone()
        if row:
            self.id = row[0]
            self.bancoBacen.selectbyNumero(row[1])
            if self.bancoBacen:
                self.numero_banco = row[1]
            self.set_numero_agencia(row[2])
            self.set_iban(row[3])
            self.set_nome_conta(row[4])
            self.set_numero_conta(row[5])
            self.set_digito_conta(row[6])
            self.set_id_moeda(row[7])
        self.con.close()

    def select_by_nome_conta(self, arg):
        self.con = self.getConexao()
        cursor = self.con.cursor()
        self.clear()
        #with self.conexao.cursor as cursor:
        cursor.execute("SELECT id, numerobanco, numeroagencia, iban, nomeconta, numeroconta, digitoconta, idmoeda FROM conta WHERE upper(nomeconta) = upper(%s)", (arg,))
        row = cursor.fetchone()
        if row:
            self.id = row[0]
            self.bancoBacen.selectbyNumero(row[1])
            if self.bancoBacen:
                self.numero_banco = row[1]
            self.set_numero_agencia(row[2])
            self.set_iban(row[3])
            self.set_nome_conta(row[4])
            self.set_numero_conta(row[5])
            self.set_digito_conta(row[6])
            self.set_id_moeda(row[7])
        self.con.close()

    @staticmethod
    def mc_select_one_by_id(id):
        try:
            conexao = ConectaBD.retornaConexao()
        except Exception as e:
            print(f"Erro ao conectar com o banco: {e}")
            return False
        cursor = conexao.cursor()
        #with self.conexao.cursor as cursor:
        cursor.execute("SELECT c.id, c.numerobanco, c.numeroagencia, c.iban, c.nomeconta, c.numeroconta, c.digitoconta, c.idmoeda, m.nomemoeda "
                       "FROM conta as c join moeda as m on m.id = c.idmoeda WHERE c.id = %s", (id,))
        lista = cursor.fetchone()
        if lista:
            return lista
        else: return None

    @staticmethod
    def mc_select_one_by_nome(nome):
        try:
            conexao = ConectaBD.retornaConexao()
        except Exception as e:
            print(f"Erro ao conectar com o banco: {e}")
            return False
        cursor = conexao.cursor()
        #with self.conexao.cursor as cursor:
        cursor.execute("SELECT c.id, c.numerobanco, c.numeroagencia, c.iban, c.nomeconta, c.numeroconta, "
                       "c.digitoconta, c.idmoeda, m.nomemoeda "
                       "FROM conta as c join moeda as m on m.id = c.idmoeda WHERE c.nomeconta = %s", (nome,))
        lista = cursor.fetchone()
        if lista:
            return lista
        else:
            return None

    @staticmethod
    def mc_select_all():
        try:
            conexao = ConectaBD.retornaConexao()
        except Exception as e:
            print(f"Erro ao conectar com o banco: {e}")
            return False
        cursor = conexao.cursor()
        #with self.conexao.cursor as cursor:
        clausulaSql = "SELECT id, numerobanco, numeroagencia, iban, nomeconta, numeroconta, digitoconta, idmoeda " \
                      "FROM conta order by nomeconta"
        cursor.execute(clausulaSql)
        lista = cursor.fetchall()
        if lista:
            return lista

    @staticmethod
    def mc_get_saldo_bancario(conta):
        try:
            conexao = ConectaBD.retornaConexao()
        except Exception as e:
            print(f"Erro ao conectar com o banco: {e}")
            return False

        with conexao.cursor() as cursor:
            clausulaSql = 'WITH valores AS (    ' \
                          'SELECT ' \
                             '(SELECT COALESCE(SUM(valorbruto) - SUM(valorir), 0) FROM proventos WHERE pago = TRUE and idconta = %s) AS proventos, ' \
                             '(SELECT COALESCE(SUM(valor), 0) FROM despesas where idconta = %s) AS despesas, '\
                             '(SELECT COALESCE(SUM(valor), 0) FROM capital where idconta = %s) AS aportes '\
                           '), ' \
                          'transacoes AS ( ' \
                          'SELECT ' \
                             'COALESCE(SUM(CASE WHEN operacao = 1 THEN valoroperacao * qtdeoperacao ELSE 0 END), 0) AS compras, ' \
                             'COALESCE(SUM(CASE WHEN operacao = 2 THEN valoroperacao * qtdeoperacao ELSE 0 END), 0) AS vendas ' \
                          'FROM ativonegociado where simulado = false and idconta = %s' \
                          '), ' \
                          'rendafixa AS ( ' \
                          'SELECT ' \
                             'COALESCE(SUM(CASE WHEN valor > 0 THEN valor ELSE 0 END), 0) AS investimento, ' \
                             'COALESCE(SUM(CASE WHEN valor < 0 THEN valor * (-1) ELSE 0 END), 0) AS resgate ' \
                          'FROM rendafixa where alterasaldobancario = true and idconta = %s' \
                          ') ' \
                          'SELECT ' \
                             ' v.proventos, v.despesas, v.aportes, t.compras, t.vendas, rf.investimento, rf.resgate,  ' \
                             '(v.proventos - v.despesas + v.aportes - t.compras + t.vendas - rf.investimento + rf.resgate) AS saldo ' \
                          'FROM valores v, transacoes t, rendafixa rf;'

            cursor.execute(clausulaSql, (conta, conta, conta, conta, conta))
            lista = cursor.fetchone()
            if lista:
                return lista[7]
            else:
                return None
    
    @staticmethod
    def mc_get_saldo_bancario_teorico(conta):
        try:
            conexao = ConectaBD.retornaConexao()
        except Exception as e:
            print(f"Erro ao conectar com o banco: {e}")
            return False
        with conexao.cursor() as cursor:
            clausulaSql = 'WITH valores AS (    ' \
                          'SELECT ' \
                             '(SELECT COALESCE(SUM(valorbruto) - SUM(valorir), 0) FROM proventos WHERE pago = TRUE and idconta = %s) AS proventos, ' \
                             '(SELECT COALESCE(SUM(valor), 0) FROM despesas where idconta = %s) AS despesas, '\
                             '(SELECT COALESCE(SUM(valor), 0) FROM capital where idconta = %s) AS aportes '\
                           '), ' \
                          'transacoes AS ( ' \
                          'SELECT ' \
                             'COALESCE(SUM(CASE WHEN operacao = 1 THEN valoroperacao * qtdeoperacao ELSE 0 END), 0) AS compras, ' \
                             'COALESCE(SUM(CASE WHEN operacao = 2 THEN valoroperacao * qtdeoperacao ELSE 0 END), 0) AS vendas ' \
                          'FROM ativonegociado where idconta = %s' \
                          '), ' \
                          'rendafixa AS ( ' \
                          'SELECT ' \
                             'COALESCE(SUM(CASE WHEN valor > 0 THEN valor ELSE 0 END), 0) AS investimento, ' \
                             'COALESCE(SUM(CASE WHEN valor < 0 THEN valor * (-1) ELSE 0 END), 0) AS resgate ' \
                          'FROM rendafixa where alterasaldobancario = true and idconta = %s' \
                          ') ' \
                          'SELECT ' \
                             ' v.proventos, v.despesas, v.aportes, t.compras, t.vendas, rf.investimento, rf.resgate, ' \
                             '(v.proventos - v.despesas + v.aportes - t.compras + t.vendas - rf.investimento + rf.resgate) AS saldo ' \
                          'FROM valores v, transacoes t, rendafixa rf;'

            cursor.execute(clausulaSql, (conta, conta, conta, conta, conta))
            lista = cursor.fetchone()
            if lista:
                return lista[7]
            else:
                return None

        self.con.close()

    @staticmethod
    def mc_busca_contas_e_ultimacotacao():
        # 
        # Retorna uma lista com:
        #   id da conta
        #   nome da conta
        #   nome da moeda
        #   valor da última cotação da moeda
        #
        try:
            conexao = ConectaBD.retornaConexao()
        except Exception as e:
            print(f"Erro ao conectar com o banco: {e}")
            return False

        with conexao.cursor() as cursor:
            clausulaSql = 'SELECT c.id, c.nomeconta, (select upper(m.nomemoeda) from moeda as m where m.id = c.idmoeda), ' \
                            '(SELECT cot.valorcotacao FROM cotacao as cot join moeda as m on m.id = cot.idmoeda ' \
                            'WHERE cot.datacotacao = (SELECT MAX(datacotacao) FROM cotacao) and cot.idmoeda = c.idmoeda) ' \
                            'FROM conta as c ORDER BY nomeconta;'
            
            clausulaSql = 'SELECT c.id, c.nomeconta, (select upper(m.nomemoeda) from moeda as m where m.id = c.idmoeda), ' \
                            '(SELECT cot.valorcotacao FROM cotacao as cot join moeda as m on m.id = cot.idmoeda ' \
                            'WHERE cot.datacotacao = (SELECT MAX(datacotacao) FROM cotacao) and cot.idmoeda = c.idmoeda) ' \
                            'FROM conta as c ORDER BY nomeconta;'


            cursor.execute(clausulaSql)

            contas = cursor.fetchall()
        
        conexao.close()
        return contas

def main():
    conta = Conta()
    conta.select_by_id(1)
    print(conta.nome_conta)
    print(conta.id_moeda)
    print(' ')
    conta.set_nome_conta('NOME NOVO')
    conta.set_numero_conta(55)
    print(conta.nome_conta)
    print(conta.id_moeda)
    print('Inserindo uma conta nova')

    conta.select_by_id(-2)
    print(str(conta.id) + ' - ' + conta.nome_conta)

    conta.set_nome_conta('Conta Nova')
    conta.set_numero_conta(888)
    conta.set_numero_agencia('1111')
    conta.set_iban('12313545648798789789')
    conta.set_id_moeda(89)
    conta.set_id_moeda(1)
    conta.set_digito_conta('X')
    conta.set_numero_banco(9999)
    conta.set_numero_banco(138)
    conta.insert()
    print (conta.id)

    conta.delete()

    print('acabou')


if __name__ == '__main__':
    main()
