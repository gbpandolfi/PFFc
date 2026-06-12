import math


class FlexaoMLE:
    E = 200000

    TIPOLOGIA_ELEMENTOS = {
        "U simples": [
            {'nome': 'Alma (a)', 'dim': 'a', 'tipo': 'AA',
             'enrijecido': False, 'dim_total': 'bw'},
            {'nome': 'Mesa Sup (b)', 'dim': 'b', 'tipo': 'AL',
             'enrijecido': False, 'dim_total': 'bf'},
            {'nome': 'Mesa Inf (b)', 'dim': 'b', 'tipo': 'AL',
             'enrijecido': False, 'dim_total': 'bf'},
        ],
        "U enrijecido": [
            {'nome': 'Alma (a)', 'dim': 'a', 'tipo': 'AA',
             'enrijecido': False, 'dim_total': 'bw'},
            {'nome': 'Mesa Sup (b)', 'dim': 'b', 'tipo': 'AA',
             'enrijecido': True, 'dim_total': 'bf'},
            {'nome': 'Mesa Inf (b)', 'dim': 'b', 'tipo': 'AA',
             'enrijecido': True, 'dim_total': 'bf'},
            {'nome': 'Enrijecedor Sup (c)', 'dim': 'c', 'tipo': 'AL',
             'enrijecido': False, 'dim_total': 'd'},
            {'nome': 'Enrijecedor Inf (c)', 'dim': 'c', 'tipo': 'AL',
             'enrijecido': False, 'dim_total': 'd'},
        ],
        "Cartola": [
            {'nome': 'Mesa Sup (b)', 'dim': 'b', 'tipo': 'AA',
             'enrijecido': False, 'dim_total': 'bf'},
            {'nome': 'Alma Esquerda (a)', 'dim': 'a', 'tipo': 'AA',
             'enrijecido': True, 'dim_total': 'bw'},
            {'nome': 'Alma Direita (a)', 'dim': 'a', 'tipo': 'AA',
             'enrijecido': True, 'dim_total': 'bw'},
            {'nome': 'Enrijecedor Inf Esq (c)', 'dim': 'c',
             'tipo': 'AL', 'enrijecido': False, 'dim_total': 'd'},
            {'nome': 'Enrijecedor Inf Dir (c)', 'dim': 'c',
             'tipo': 'AL', 'enrijecido': False, 'dim_total': 'd'},
        ]
    }

    def __init__(self, perfil_geom, estabilidade_obj, cb: float = 1.0, mxsd: float = 0.0):
        self.perfil = perfil_geom
        self.estabilidade = estabilidade_obj
        self.cb = cb
        self.mxsd = mxsd
        self.chi_flt = self.calculate_chi_flt()
        self.desloc_ln = 0.0
        self.fy = self.perfil.fy / 10.0
        self.t = self.perfil.t / 10.0
        self.ri = self.perfil.ri / 10.0
        self.yg = self.perfil.yg / 10.0
        self.tensao = self.chi_flt * self.fy
        self.resultados = []
        self.dimplanas = {}

    def get_dimplanas(self):
        if hasattr(self.perfil, 'a_plana') and self.perfil.a_plana > 0:
            self.dimplanas['a'] = self.perfil.a_plana / 10.0
        if hasattr(self.perfil, 'b_plana') and self.perfil.b_plana > 0:
            self.dimplanas['b'] = self.perfil.b_plana / 10.0
        if hasattr(self.perfil, 'c_plana') and self.perfil.c_plana > 0:
            self.dimplanas['c'] = self.perfil.c_plana / 10.0
        return self.dimplanas

    def calculate_chi_flt(self):
        r0 = self.perfil.r0 / 10.0
        ney = self.estabilidade.Ney / 1000.0
        nez = self.estabilidade.Nez1 / 1000.0
        ix = (self.perfil.Ix / 10.0**4)
        wc = ix / (self.perfil.yg / 10.0)
        fy = self.perfil.fy / 10.0
        t = self.perfil.t / 10.0
        self.me = 0.0

        if "U" in self.perfil.tipo_perfil:
            self.me = self.cb * r0 * (ney * nez)**0.5
        elif "Cartola" in self.perfil.tipo_perfil:
            am, bm, cm = self.perfil.bm/10, self.perfil.am/10, self.perfil.cm/10 # No Anexo E da ABNT NBR 14762:2010, os eixos X e Y para a seção cartola estão trocados. Sendo assim, inverteu-se os valores de bm e am, Nex, Ney, x0 e y0.
            xm = (bm*(bm+2*cm))/(am+2*bm+2*cm)
            x0 = xm+bm*((bm*3*am**2+cm*(6*am**2-8*cm**2)) /
                        (am**3+bm*6*am**2+cm*(8*cm**2+12*am*cm+6*am**2)))
            bl = 2*cm*t*(bm-xm)**3 + (2/3)*t*(bm-xm)*(((am/2)+cm)**3-(am/2)**3)
            bf = (t/2)*((bm-xm)**4-xm**4) + ((t*am**2)/4)*((bm-xm)**2-xm**2)
            bw_ = (t*xm*am**3)/12 + (am*t*xm**3)
            j = (1/(2*ix))*(bw_+bf+bl)+x0

            if self.mxsd > 0:
                cs = 1
            else:
                cs = -1
            self.me = cs*ney * (j+cs*math.sqrt(j**2+(nez/ney)*r0**2))

        if self.me < 0:
            return 1.0

        self.lambdapo = math.sqrt(wc * fy / self.me)
        if self.lambdapo < 0.6:
            return 1.0
        elif 0.6 <= self.lambdapo <= 1.336:
            return 1.11 * (1 - 0.278 * self.lambdapo**2)
        else:
            return 1 / (self.lambdapo**2)

    def calculate_psi(self, desloc_ln, c_plana):
        dist1 = self.yg + abs(desloc_ln)
        dist1_ = dist1 - self.t - self.ri
        dist1c_ = dist1_ - c_plana

        dist2 = self.perfil.a_total/10 - self.yg - abs(desloc_ln)
        dist2_ = dist2 - self.t - self.ri

        if dist2 >= self.perfil.a_total/20:
            self.tensao_s = - self.fy * dist1/dist2
            self.tensao_i = self.fy
            self.tensao2 = self.tensao_i * dist2_ / dist2
            self.tensao1 = self.tensao_s * dist1_ / dist1
            self.tensao1c = self.tensao_s * dist1c_ / dist1
        else:
            self.tensao_i = self.fy * dist2/dist1
            self.tensao_s = - self.fy
            self.tensao2 = self.tensao_i * dist2_ / dist2
            self.tensao1 = self.tensao_s * dist1_ / dist1
            self.tensao1c = self.tensao_s * dist1c_ / dist1

        psi = self.tensao2 / self.tensao1 if self.tensao1 != 0 else 1
        self.psi_c = self.tensao1c / self.tensao1 if self.tensao1 != 0 else 1
        return psi

    def calculate_sigma(self, nome):
        if "Alma" in nome:
            sigma = min(self.tensao1, self.tensao2)
        elif "Mesa Sup" in nome:
            sigma = self.tensao_s
        elif "Mesa Inf" in nome:
            sigma = self.tensao_i
        elif "Enrijecedor Sup" in nome:
            sigma = self.tensao1
        elif "Enrijecedor Inf" in nome:
            sigma = self.tensao2
        return sigma

    def calculate_k(self, enrijecido, tipo, lambdapo, b_plana, c_plana, c_total, nome, psi):
        k = 0
        if tipo == 'AA' and "Mesa" not in nome:
            k = 4+2*(1-psi)+2*(1-psi)**3
        elif "Enrijecedor" in nome:
            psi_c = self.psi_c
            if 0 <= psi_c < 1:
                k = 0.578/(psi_c+0.34)
            elif -1 <= psi_c < 0:
                k = 1.7 - 5*psi_c + 17.1*psi_c**2
        elif not enrijecido:
            k = 0.43 if tipo == 'AL' else 4.00
        elif enrijecido:
            angulo_rad = math.radians(self.perfil.angulo)
            self.inercia_s = (self.t*(c_plana**3) * (math.sin(angulo_rad))**2)/12
            self.inercia_a = min(399*self.t**4 * (0.487*lambdapo-0.328)
                            ** 3, (self.t**4 * (56*lambdapo+5)))
            n = 0.582-0.122*lambdapo
            if n < 1/3:
                aviso = f"Valor de 'n' menor que 1/3 para o elemento {nome}. Adotado n=1/3 para o cálculo de k."
                if aviso not in self.perfil.avisos:
                    self.perfil.avisos.append(aviso)
                n = 1/3
            termo_inercias = max(0, min(self.inercia_s/self.inercia_a, 1))

            if c_total/b_plana <= 0.25:
                k = min(3.57*(termo_inercias)**n + 0.43, 4)
            elif 0.25 < c_total/b_plana <= 0.8:
                k = min((4.82 - 5*c_total/b_plana) *
                        (termo_inercias)**n + 0.43, 4)
            else:
                k=4
        return k

    def calculate_lambdapo(self, dimplana, sigma):
        try:
            return (dimplana / self.t) / (0.623*math.sqrt((self.E/10)/abs(sigma)))
        except:
            return 0

    def calculate_lambdap(self, k, dimplana, sigma):
        try:
            return (dimplana / self.t) / (0.95*math.sqrt((k*self.E/10)/abs(sigma)))
        except:
            return 0

    def calculate_bef(self, dimplana, lambdap, lambdapo, nome, c_plana, enrijecido, psi):
        if 'Inf' in nome:
            return dimplana
        elif "Alma" in nome:
            bef = dimplana*(1-0.22/lambdap) / \
                lambdap if lambdap > 0.673 else dimplana
            if 0 <= psi < 1 or -0.236 < psi < 0:
                bef1 = bef/(3-psi)
                bef2 = bef-bef1
            elif psi <= -0.236:
                bef1 = bef/(3-psi)
                bef2 = 0.5*bef
            else:
                return dimplana
            bc = (self.yg - self.t - self.ri) + abs(self.desloc_ln)
            bef = min((bef1+bef2), bc)
            self.b_nef_alma = bc - bef
            self.yg_alma = abs(self.desloc_ln)+self.yg - \
                (self.t+self.ri)-bef1-self.b_nef_alma/2
            return dimplana - self.b_nef_alma
        elif not enrijecido and 'Erijecedor' not in nome:
            return dimplana*(1-0.22/lambdap)/lambdap if lambdap > 0.673 else dimplana
        elif enrijecido and 'Erijecedor' not in nome:
            angulo_rad = math.radians(self.perfil.angulo)
            inercia_s = (self.t*(c_plana**3) * (math.sin(angulo_rad))**2)/12
            inercia_a = min((399*self.t**4 * (0.487*lambdapo-0.328)
                            ** 3), (self.t**4 * (56*lambdapo+5)))
            termo_inercias = max(0, inercia_s/inercia_a)
            if lambdapo > 0.673:
                bef = dimplana*(1-0.22/lambdap) / \
                    lambdap if lambdap > 0.673 else dimplana
                bef1 = min(termo_inercias*(bef/2), bef/2)
                bef2 = bef - bef1
                return bef1 + bef2
            return dimplana
        elif 'Erijecedor' in nome:
            angulo_rad = math.radians(self.perfil.angulo)
            inercia_s = (self.t*(c_plana**3) * (math.sin(angulo_rad))**2)/12
            inercia_a = min((399*self.t**4 * (0.487*lambdapo-0.328)
                            ** 3), (self.t**4 * (56*lambdapo+5)))
            termo_inercias = max(0, inercia_s/inercia_a)
            if lambdapo > 0.673:
                bef = dimplana*(1-0.22/lambdap)/lambdap
                return min((termo_inercias*(bef)), bef)
            return dimplana

    def calculate_desloc(self, resultados_iteracao):
        area_bruta = self.perfil.A / 100.0
        soma_momentos_inef, soma_areas_inef = 0.0, 0.0

        for res in resultados_iteracao:
            b_nef, nome = res['dimnefetiva'], res['Elemento']
            if "Enrijecedor Sup" in nome:
                self.yg_enrijecedor = self.yg - (self.ri + self.t) - b_nef/2
                soma_momentos_inef += (b_nef * self.t) * self.yg_enrijecedor
                soma_areas_inef += b_nef * self.t
            elif "Mesa Sup" in nome:
                yg_mesa = self.yg - (self.t / 2.0)
                soma_momentos_inef += (b_nef * self.t) * yg_mesa
                soma_areas_inef += b_nef * self.t
            elif "Alma" in nome:
                soma_momentos_inef += (b_nef * self.t) * self.yg_alma
                soma_areas_inef += b_nef * self.t

        try:
            area_efetiva = area_bruta - soma_areas_inef
            if area_efetiva <= 0:
                return 0.0
            return -soma_momentos_inef / area_efetiva
        except:
            return 0.0

    def run_calculation(self) -> dict:
        dimensoes = self.get_dimplanas()
        max_iter, tolerancia = 50, 0.01
        self.desloc_ln = 0.0
        config_elementos = self.TIPOLOGIA_ELEMENTOS.get(
            self.perfil.tipo_perfil)
        a_plana, b_plana, c_plana = dimensoes.get(
            'a', 0.0), dimensoes.get('b', 0.0), dimensoes.get('c', 0.0)
        c_total = self.perfil.c_total / 10.0

        for i in range(max_iter):
            old_desloc = self.desloc_ln
            self.resultados = []

            for config in config_elementos:
                nome, dim, tipo, enrijecido = config['nome'], config['dim'], config['tipo'], config['enrijecido']
                dimplana = dimensoes.get(dim, 0.0)
                psi = self.calculate_psi(self.desloc_ln, c_plana)
                sigma = self.calculate_sigma(nome)
                lambdapo = self.calculate_lambdapo(dimplana, sigma)
                k = self.calculate_k(
                    enrijecido, tipo, lambdapo, b_plana, c_plana, c_total, nome, psi)
                lambdap = self.calculate_lambdap(k, dimplana, sigma)
                bef = self.calculate_bef(
                    dimplana, lambdap, lambdapo, nome, c_plana, enrijecido, psi)

                self.resultados.append({
                    'Elemento': nome, 'Tipo': tipo, 'k': k, 'sigma': sigma, 'lambdap': lambdapo if ("Mesa" in nome and enrijecido) else lambdap,
                    'dimplana': dimplana, 'dimefetiva': bef, 'dimnefetiva': dimplana - bef
                })

            self.desloc_ln = self.calculate_desloc(self.resultados)
            if abs(self.desloc_ln - old_desloc) <= tolerancia:
                break

        self.ix_nef_total = 0.0
        for res in self.resultados:
            b_nef, nome = res['dimnefetiva'], res['Elemento']
            ix_nef = 0
            if "Mesa" in nome:
                ix_nef = ((b_nef*10 * self.perfil.t**3 / 12) + (b_nef*10 * self.perfil.t *
                          (self.perfil.yg + abs(self.desloc_ln*10) - self.perfil.t/2)**2))
            elif "Alma" in nome:
                ix_nef = (self.perfil.t * (b_nef*10)**3 / 12) + \
                    ((b_nef*10)*self.perfil.t*(self.yg_alma*10)**2)
            elif "Enrijecedor Sup" in nome:
                ix_nef = (self.perfil.t * (b_nef*10)**3 / 12) + \
                    ((b_nef*10)*self.perfil.t*(self.yg_enrijecedor*10)**2)
            self.ix_nef_total += ix_nef

        dist1 = self.perfil.yg + abs(self.desloc_ln)*10
        dist2 = self.perfil.a_total - self.perfil.yg - abs(self.desloc_ln*10)
        ix_ln = self.perfil.Ix + self.perfil.A * abs(self.desloc_ln*10)**2
        ix_ef = ix_ln - self.ix_nef_total
        self.wef = ix_ef / max(dist1, dist2)
        self.wcef = ix_ef / dist1

        mrd1 = (self.wef * self.fy / 1.1) / 1000
        mrd2 = (self.chi_flt * self.wcef * self.fy / 1.1) / 1000
        mrd = min(mrd1, mrd2)

        detalhes = []
        for res in self.resultados:
            detalhes.append({
                'elemento': res['Elemento'],
                'k': round(res['k'], 2) if res['k'] else 0.0,
                'sigma': round(res['sigma'], 2) if res['sigma'] else 0.0,
                'lambda_p': round(res['lambdap'], 3) if res['lambdap'] else 0.0,
                'b_plana': round(res['dimplana'], 3),
                'b_efetiva': round(res['dimefetiva'], 3),
                'b_inefetiva': round(res['dimnefetiva'], 3)
            })

        return {
            "geometria_efetiva": {
                "desloc_ln": round(self.desloc_ln*10, 2),  # mm
                "wef": round(self.wef, 2),  # mm³
                "wcef": round(self.wcef, 2), # mm³
                "iteracoes": i + 1
            },
            "grafico tensoes": {  # Dados para o Matplotlib
                "sigma_sup": round(getattr(self, 'tensao_s', 0), 2),
                "sigma_inf": round(getattr(self, 'tensao_i', 0), 2),
                "sigma1": round(getattr(self, 'tensao1', 0), 2),
                "sigma2": round(getattr(self, 'tensao2', 0), 2),
                "unidade": "kN/cm²"
            },
            "flambagem_flt": {
                "Me": round(self.me, 2),  # kN.cm
                "lambda_0": round(self.lambdapo, 4),
                "chi_flt": round(self.chi_flt, 4)
            },
            "elementos": detalhes,
            "final": {
                "mrd1": round(mrd1, 2),
                "mrd2": round(mrd2, 2),
                "m_rd": round(mrd, 2),
                "unidade": "kN.cm"
            }
        }
