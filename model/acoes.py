# -*- coding: iso-8859-1 -*-
from model.pesquisa.pesquisa_db import Pesquisa
from datetime import datetime
import math


class Acoes(object):
    """Classe objeto acao."""

    def __init__(self):
        """Inicializa o objeto."""
        self._p = Pesquisa()

    def agrupar_dados(self, lista, indice):
        """Agrupa os dados de uma lista."""
        d = {}
        for item in lista:
            if str(item[indice]) in d.keys():
                d[str(item[indice])].append(item)
            else:
                d[str(item[indice])] = [item]

        return d

    def buscar_empresas(self, empresas=[]):
        """Busca as empresas disponiveis no banco."""
        return self._p.busca_empresa(empresas=empresas)

    def buscar_acoes_empresas(self, empresas=[], dt_init=None, dt_fim=None):
        """Busca as acoes das empresas solicitadas."""
        return self._p.busca_acoes(empresas=empresas, dt_init=dt_init,
                                   dt_fim=dt_fim)

    def validar_data(self, data):
        """Valida uma data e retorna como objeto Date."""
        d = None
        try:
            if data:
                d = datetime.strptime(data, '%d/%m/%Y')
        except ValueError:
            return (0, d)

        return (1, d)

    def validar_empresa(self, id_empresa):
        """Valida o id_empresa e retorna uma lista de int."""
        try:
            if isinstance(id_empresa, (list, tuple)):
                if len(id_empresa) == 0:
                    return (0, [])

                return (1, [int(x) for x in id_empresa])
            else:
                return (1, [int(id_empresa)])
        except:
            return (0, None)

    def std_dev(self, dados):
        """."""
        c = 0
        x = self.mean_calc(dados)
        for item in dados:
            c += (item[7] - x)**2
        sd = math.sqrt((c/(len(dados) - 1)))
        return sd

    def mean_calc(self, dados):
        """."""
        c = 0
        for item in dados:
            c += item[7]
        mean = c/len(dados)
        return mean

    def covariance_calc(self, dados_princ, dados_comp):
        c = 0
        m1 = self.mean_calc(dados_princ)
        m2 = self.mean_calc(dados_comp)
        for i in range(ran):
            c += (dados_princ[i][7] - m1)*(dados_comp[i][7] - m2)
        cov = c/(len(dados_princ) - 1)
        return cov

    def calcular(self, dados):
        """Recebe os dados necessarios para iniciar os calculos."""
        # query[0] -> v.id
        # query[1] -> e.nome
        # query[2] -> v.data
        # query[3] -> v.open
        # query[4] -> v.high
        # query[5] -> v.low
        # query[6] -> v.close
        # query[7] -> v.adj_close
        # query[8] -> v.volume
        emp_princ = self._p.busca_acoes(
            empresas=dados['id_empresa'], dt_init=dados['dt_init'],
            dt_fim=dados['dt_fim'])

        sd_emp_princ = self.std_dev(dados=emp_princ)
        mean_emp_princ = self.mean_calc(dados=emp_princ)

        emp_comp = self._p.busca_acoes(
            empresas=dados['id_empresa_comp'], dt_init=dados['dt_init'],
            dt_fim=dados['dt_fim'])

        emp_comp = self.agrupar_dados(lista=emp_comp, indice=1)

        if str(emp_princ[1]) in emp_comp.keys():
            del emp_comp[emp_princ[1]]

        saida = {}

        for empresa in emp_comp.keys():
            sd_empresa = self.std_dev(dados=emp_comp[empresa])
            cov_empresa = self.covariance_calc(
                dados_princ=emp_princ, dados_comp=emp_comp[empresa])
            saida[empresa] = cov_empresa/(sd_emp_princ*sd_empresa)

        return saida
