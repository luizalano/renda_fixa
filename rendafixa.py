# coding: utf-8


import datetime

from diversos import *
from databasefunctions import *
from conta import Conta
from titulorendafixa import TituloRendaFixa 
import psycopg2
from datetime import datetime

class RendaFixa:
    def __init__(self):
        self.id = -1
        self.data_lancamento = None
        self.valor = zero
        self.descricao = ''
        self.id_titulo_renda_fixa = -1
        self.nome_titulo_renda_fixa = ''
        self.id_conta = -1
        self.nome_conta = ''
        self.altera_saldo_bancario = None
        self.tipo_lancamento = -1
        self.nome_tipo_lancamento = ''
        self.tipos_lancamento = ['Aporte', 'Retirada', 'Despesa', 'Rendimento']

        self.conexao = None

    @staticmethod
    def getConexao():
        try:
            con = ConectaBD.retornaConexao()
            return con
        except Exception as e:
            print(f"Erro ao conectar com o banco: {e}")
            return False

    def set_id_conta(self, arg):
        lista = Conta.mc_select_one_by_id(arg)
        if lista:
            self.id_conta = arg
            self.nome_conta = lista[4]
        else:
            self.id_conta = -1
            self.nome_conta = ''

    def set_nome_conta(self, arg):
        lista = Conta.mc_select_one_by_nome(arg)
        if lista:
            self.id_conta = lista[0]
            self.nome_conta = lista[4]
        else:
            self.id_conta = -1
            self.nome_conta = ''

    def set_id_titulo_renda_fixa(self, arg):
        lista = TituloRendaFixa.mc_select_one_by_id(arg)
        if lista:
            self.id_titulo_renda_fixa = arg
            self.nome_titulo_renda_fixa = lista[1]
        else:
            self.id_titulo_renda_fixa = -1
            self.nome_titulo_renda_fixa = ''

    def set_nome_titulo_renda_fixa(self, arg):
        lista = TituloRendaFixa.mc_select_one_by_nome(arg)
        if lista:
            self.id_titulo_renda_fixa = lista[0]
            self.nome_titulo_renda_fixa = lista[1]
        else:
            self.id_titulo_renda_fixa = -1
            self.nome_titulo_renda_fixa = ''
    
    def set_descricao(self, arg):
        self.descricao = str(arg).strip()

    def set_altera_saldo_bancario(self, arg):   
        try:
            self.altera_saldo_bancario = bool(arg)
        except:
            self.altera_saldo_bancario = None
        
    def set_valor(self, arg):
        tipo = type(arg)
        valor = zero
        if str(tipo) == "<class 'int'>":
            valor = devolveDecimalDeFloat(float(arg))
        if str(tipo) == "<class 'float'>":
            valor = devolveDecimalDeFloat(arg)
        elif str(tipo) == "<class 'decimal.Decimal'>":
            valor = arg
        self.valor = valor

    def set_data_lancamento(self, arg):
        self.data_lancamento = devolveDate(arg)

    def set_tipo_lancamento(self, arg):
        self.nome_tipo_lancamento
        if isinstance(arg, str):
            try:
                self.tipo_lancamento = int(arg)
            except:
                self.tipo_lancamento = -1
        else:
            try:
                self.tipo_lancamento = int(arg)
            except:
                self.tipo_lancamento = -1   
        if self.tipo_lancamento < 0 or self.tipo_lancamento > 3:
            self.tipo_lancamento = -1
        else:
            self.nome_tipo_lancamento = self.tipos_lancamento[self.tipo_lancamento]

    def clear(self):
        self.id = -1
        self.data_lancamento = None
        self.valor = zero
        self.descricao = ''
        self.id_titulo_renda_fixa = -1
        self.nome_titulo_renda_fixa = ''
        self.id_conta = -1
        self.nome_conta = ''
        self.altera_saldo_bancario = None
        self.tipo_lancamento = -1
        self.nome_tipo_lancamento = ''

    def insert(self):
        self.conexao = RendaFixa.getConexao()
        try:
            with self.conexao.cursor() as cursor:
                cursor.execute(
                    "INSERT INTO rendafixa (datalancamento, valor, descricao, idtitulorendafixa, idconta, alterasaldobancario, tipolancamento) VALUES (%s, %s, %s, %s, %s, %s, %s) RETURNING id",
                    (self.data_lancamento, self.valor, self.descricao, self.id_titulo_renda_fixa, self.id_conta, self.altera_saldo_bancario, self.tipo_lancamento),
                )
                self.id = cursor.fetchone()[0]
                self.conexao.commit()
                self.conexao.close()
        except Exception as e:
            raise

    def update(self):
        self.conexao = RendaFixa.getConexao()
        cursor = self.conexao.cursor()
        try:
            cursor.execute(
                "UPDATE rendafixa set datalancamento = %s, valor = %s, descricao = %s, idtitulorendafixa = %s, " \
                "idconta = %s, alterasaldobancario = %s, tipolancamento = %s where id = %s;",
                (self.data_lancamento, self.valor, self.descricao, self.id_titulo_renda_fixa, self.id_conta, self.altera_saldo_bancario, self.tipo_lancamento, self.id),
            )
            self.conexao.commit()
            self.conexao.close()
        except Exception as e:
            raise

    def delete(self):
        self.conexao = RendaFixa.getConexao()
        with self.conexao.cursor() as cursor:
            cursor.execute("delete from rendafixa where id = %s;", (self.id,),)
            self.conexao.commit()
            self.conexao.close()

    def select_by_id(self, id):
        self.clear()
        self.conexao = RendaFixa.getConexao()
        retorno = False
        with self.conexao.cursor() as cursor:
            cursor.execute("SELECT id, datalancamento, valor, descricao, idtitulorendafixa, idconta, alterasaldobancario, tipolancamento FROM rendafixa WHERE id = %s", (id,))
            row = cursor.fetchone()
            if row:
                self.id = row[0]
                self.set_data_lancamento(row[1])
                self.set_valor(row[2])
                self.set_descricao(row[3])
                self.set_id_titulo_renda_fixa(row[4])
                self.set_id_conta(row[5])
                self.set_altera_saldo_bancario(row[6])
                self.set_tipo_lancamento(row[7])
                retorno = True
            self.conexao.close()
        return retorno

    def get_all(self):
        self.clear()
        self.conexao = RendaFixa.getConexao()
        with self.conexao.cursor() as cursor:
            cursor.execute("SELECT rf.id, rf.datalancamento, rf.valor, rf.descricao, rf.idtitulorendafixa, rf.idconta, rf.alterasaldobancario, "
                           "trf.nometitulo, c.nomeconta, rf.tipolancamento FROM rendafixa as rf "                       
                           "join titulorendafixa as trf on rf.idtitulorendafixa = trf.id "
                           "join conta as c on rf.idconta = c.id "
                           "order by datalancamento, id")
            lista = cursor.fetchall()
            self.conexao.close()
            if lista: return lista
            else: return None

    @staticmethod
    def sm_busca_por_id_conta(id_conta):
        conexao = RendaFixa.getConexao()
        with conexao.cursor() as cursor:
            cursor.execute("SELECT rf.id, rf.datalancamento, rf.valor, rf.descricao, rf.idtitulorendafixa, rf.idconta, rf.alterasaldobancario, "
                           "trf.nometitulo, c.nomeconta, rf.tipolancamento FROM rendafixa as rf "                       
                           "join titulorendafixa as trf on rf.idtitulorendafixa = trf.id "
                           "join conta as c on rf.idconta = c.id "
                           "where rf.idconta = %s "
                           "order by datalancamento, id", (id_conta,))
            lista = cursor.fetchall()
            conexao.close()
            if lista: return lista
            else: return None

    @staticmethod
    def sm_busca_por_nome_conta(nome_conta):
        conexao = RendaFixa.getConexao()
        with conexao.cursor() as cursor:
            cursor.execute("SELECT rf.id, rf.datalancamento, rf.valor, rf.descricao, rf.idtitulorendafixa, rf.idconta, rf.alterasaldobancario,  "
                           "trf.nometitulo, c.nomeconta, rf.tipolancamento FROM rendafixa as rf "                       
                           "join titulorendafixa as trf on rf.idtitulorendafixa = trf.id "
                           "join conta as c on rf.idconta = c.id "
                           "where rf.idconta = (select idconta from conta where upper(nomeconta) = upper(%s)) "
                           "order by datalancamento, id", (nome_conta,))
            lista = cursor.fetchall()
            conexao.close()
            if lista: return lista
            else: return None

    @staticmethod
    def sm_busca_por_id_conta_id_titulo(id_conta, id_titulo):
        conexao = RendaFixa.getConexao()
        with conexao.cursor() as cursor:
            cursor.execute("SELECT rf.id, rf.datalancamento, rf.valor, rf.descricao, rf.idtitulorendafixa, rf.idconta, rf.alterasaldobancario, "
                           "trf.nometitulo, c.nomeconta, rf.tipolancamento FROM rendafixa as rf "                       
                           "join titulorendafixa as trf on rf.idtitulorendafixa = trf.id "
                           "join conta as c on rf.idconta = c.id "
                           "where rf.idconta = %s and rf.idtitulorendafixa = %s "
                           "order by datalancamento, id", (id_conta, id_titulo))
            lista = cursor.fetchall()
            conexao.close()
            if lista: return lista
            else: return None

    @staticmethod
    def sm_busca_por_nome_conta_nome_titulo(nome_conta, nome_titulo):
        conexao = RendaFixa.getConexao()
        with conexao.cursor() as cursor:
            cursor.execute("SELECT rf.id, rf.datalancamento, rf.valor, rf.descricao, rf.idtitulorendafixa, rf.idconta, rf.alterasaldobancario, "
                           "trf.nometitulo, c.nomeconta, rf.tipolancamento FROM rendafixa as rf "                       
                           "join titulorendafixa as trf on rf.idtitulorendafixa = trf.id "
                           "join conta as c on rf.idconta = c.id "
                           "where rf.idconta = (select id from conta where upper(nomeconta) = upper(%s)) "
                           "and rf.idtitulorendafixa = (select id from titulorendafixa where upper(nometitulo) = upper(%s)) "
                           "order by datalancamento, id", (nome_conta, nome_titulo))
            lista = cursor.fetchall()
            conexao.close()
            if lista: return lista
            else: return None
        
    @staticmethod
    def sm_tipos_lancamento():
        renda_fixa = RendaFixa()
        return renda_fixa.tipos_lancamento

    @staticmethod
    def sm_nome_tipo_lancamento(qual):
        renda_fixa = RendaFixa()
        return renda_fixa.tipos_lancamento[qual]





