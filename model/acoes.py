# -*- coding: utf-8 -*-
from model.pesquisa.pesquisa_db import Pesquisa
from datetime import datetime
from decimal import Decimal
import simplejson as json


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
                d = datetime.strptime(data, '%Y-%m-%d')
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
        sd = (c/(len(dados) - 1)).sqrt()
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
        for i in range(len(dados_princ)):
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
        # query[9] -> v.data_str
        emp_princ = self._p.busca_acoes(
            empresas=dados['id_empresa'], dt_init=dados['dt_init'],
            dt_fim=dados['dt_fim'])

        if len(emp_princ) == 0:
            return {}

        sd_emp_princ = self.std_dev(dados=emp_princ)
        mean_emp_princ = self.mean_calc(dados=emp_princ)

        emp_comp = self._p.busca_acoes(
            empresas=dados['id_empresa_comp'], dt_init=dados['dt_init'],
            dt_fim=dados['dt_fim'])

        emp_comp = self.agrupar_dados(lista=emp_comp, indice=1)

        if str(emp_princ[0][1]) in emp_comp.keys():
            del emp_comp[emp_princ[0][1]]

        if len(emp_comp.keys()) == 0:
            return {}

        saida = {'corr_geral': {}, 'corr_periodo': {}, 'corr_prog': {},
                 'qtd_dias': len(emp_princ), 'emp_princ': emp_princ[0][1],
                 'emp_comp': emp_comp.keys(), 'dt_init': emp_princ[0][9],
                 'dt_fim': emp_princ[-1][9]}

        for empresa in emp_comp.keys():
            sd_empresa = self.std_dev(dados=emp_comp[empresa])
            cov_empresa = self.covariance_calc(
                dados_princ=emp_princ, dados_comp=emp_comp[empresa])
            corr = cov_empresa / (sd_emp_princ*sd_empresa)

            d = {'qtd_dias': len(emp_princ), 'dt_init': saida['dt_init'],
                 'dt_fim': saida['dt_fim'],
                 'corr': corr}

            saida['corr_geral'][empresa] = d

            saida_periodo = []
            init = 0
            while init < len(emp_princ):
                periodo_emp_princ = emp_princ[init:init+90]
                periodo = emp_comp[empresa][init:init+90]

                init += 90

                if init > len(emp_princ):
                    init = len(emp_princ)

                sd_empresa = self.std_dev(dados=periodo)
                cov_empresa = self.covariance_calc(
                    dados_princ=periodo_emp_princ, dados_comp=periodo)
                corr = cov_empresa / (sd_emp_princ*sd_empresa)

                d = {'qtd_dias': init, 'intervalo': len(periodo_emp_princ),
                     'dt_init': periodo_emp_princ[0][9], 'corr': corr,
                     'dt_fim': periodo_emp_princ[-1][9]}

                if init <= 90:
                    d['var'] = 0
                else:
                    if corr > saida_periodo[-1]:
                        d['var'] = 1
                    elif corr == saida_periodo[-1]:
                        d['var'] = 0
                    else:
                        d['var'] = -1

                d['json'] = json.dumps(d)

                saida_periodo.append(d)

            saida['corr_periodo'][empresa] = saida_periodo

            saida_periodo = []
            end = 0
            while end < len(emp_princ):
                end += 90

                periodo_emp_princ = emp_princ[0:end]
                periodo = emp_comp[empresa][0:end]

                if end > len(emp_princ):
                    end = len(emp_princ)

                sd_empresa = self.std_dev(dados=periodo)
                cov_empresa = self.covariance_calc(
                    dados_princ=periodo_emp_princ, dados_comp=periodo)

                corr = cov_empresa / (sd_emp_princ*sd_empresa)

                d = {'qtd_dias': end, 'intervalo': len(periodo_emp_princ),
                     'dt_init': saida['dt_init'], 'corr': corr,
                     'dt_fim': periodo_emp_princ[-1][9]}

                if end <= 90:
                    d['var'] = 0
                else:
                    if corr > saida_periodo[-1]:
                        d['var'] = 1
                    elif corr == saida_periodo[-1]:
                        d['var'] = 0
                    else:
                        d['var'] = -1

                d['json'] = json.dumps(d)

                saida_periodo.append(d)

            saida['corr_prog'][empresa] = saida_periodo

        return saida
