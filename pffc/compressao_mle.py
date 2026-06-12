import math


class CompressaoMLE:
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

    def __init__(self, perfil_geom, chi: float = 1.0):
        self.perfil = perfil_geom
        self.chi_global = chi
        self.fy = self.perfil.fy / 10.0
        self.t = self.perfil.t / 10.0
        self.tensao = self.chi_global * self.fy
        self.resultados = []
        self.dimplanas = {}
        self.aefetiva = 0.0
        self.nrd = 0.0

    def get_dimplanas(self):
        if hasattr(self.perfil, 'a_plana') and self.perfil.a_plana > 0:
            self.dimplanas['a'] = self.perfil.a_plana / 10.0
        if hasattr(self.perfil, 'b_plana') and self.perfil.b_plana > 0:
            self.dimplanas['b'] = self.perfil.b_plana / 10.0
        if hasattr(self.perfil, 'c_plana') and self.perfil.c_plana > 0:
            self.dimplanas['c'] = self.perfil.c_plana / 10.0
        return self.dimplanas

    def calculate_lamdapo(self, dimplana):
        try:
            lambdapo = (dimplana / self.t) / \
                (0.623*math.sqrt((self.E/10)/self.tensao))
            return lambdapo
        except (ValueError, ZeroDivisionError):
            return None

    def calculate_k(self, enrijecido, tipo, lambdapo, b_plana, c_plana, c_total, nome):
        k = 0
        if enrijecido == False:
            if tipo == 'AL':
                k = 0.43
            elif tipo == 'AA':
                k = 4.0
        elif enrijecido == True:
            angulo_rad = math.radians(self.perfil.angulo)
            inercia_s = (self.t*(c_plana**3) * (math.sin(angulo_rad))**2)/12
            inercia_a = min(399*self.t**4 * (0.487*lambdapo-0.328)
                            ** 3, (self.t**4 * (56*lambdapo+5)))
            n = 0.582-0.122*lambdapo
            if n < 1/3:
                aviso = f"Valor de 'n' menor que 1/3 para o elemento {nome}. Adotado n=1/3 para o cálculo de k."
                if aviso not in self.perfil.avisos:
                    self.perfil.avisos.append(aviso)
                n = 1/3
            termo_inercias = inercia_s/inercia_a
            if termo_inercias > 1:
                termo_inercias = 1
            if termo_inercias < 0:
                termo_inercias = 0

            if c_total/b_plana <= 0.25:
                k = min(3.57*(termo_inercias)**n + 0.43, 4)
            elif c_total/b_plana > 0.25 and c_total/b_plana <= 0.8:
                k = min((4.82 - 5*c_total/b_plana) *
                        (termo_inercias)**n + 0.43, 4)
            elif c_total/b_plana > 0.8:
                raise ValueError("ATENÇÃO! Relação D/b maior que 0.8, reduza o comprimento do enrijecedor ou aumente a largura da mesa para evitar instabilidade local.")
        return k

    def calculate_lambdap(self, k, dimplana):
        try:
            lambdap = (dimplana / self.t) / \
                (0.95*math.sqrt((k*self.E/10)/self.tensao))
            return lambdap
        except (ValueError, ZeroDivisionError):
            return None

    def calculate_bef(self, dimplana, lambdap, lambdapo, nome, c_plana, enrijecido):
        bef = dimplana
        if nome != 'Erijecedor' and enrijecido == False:
            if lambdap > 0.673:
                bef = dimplana*(1-0.22/lambdap)/lambdap
        elif nome != 'Erijecedor' and enrijecido == True:
            angulo_rad = math.radians(self.perfil.angulo)
            inercia_s = (self.t*(c_plana**3) * (math.sin(angulo_rad))**2)/12
            inercia_a = min((399*self.t**4 * (0.487*lambdapo-0.328)
                            ** 3), (self.t**4 * (56*lambdapo+5)))
            if lambdapo > 0.673:
                bef_temp = dimplana*(1-0.22/lambdap) / \
                    lambdap if lambdap > 0.673 else dimplana
                bef1 = min((inercia_s/inercia_a)*(bef_temp/2), bef_temp/2)
                bef2 = bef_temp - bef1
                bef = bef1 + bef2
        elif 'Erijecedor' in nome:
            angulo_rad = math.radians(self.perfil.angulo)
            inercia_s = (self.t*(c_plana**3) * (math.sin(angulo_rad))**2)/12
            inercia_a = min((399*self.t**4 * (0.487*lambdapo-0.328)
                            ** 3), (self.t**4 * (56*lambdapo+5)))
            bef_temp = dimplana*(1-0.22/lambdap) / \
                lambdap if lambdap > 0.673 else dimplana
            if lambdapo > 0.673:
                bef = min(((inercia_s/inercia_a)*(bef_temp)), bef_temp)
            else:
                bef = bef_temp
        return bef

    def run_calculation(self) -> dict:
        dimensoes = self.get_dimplanas()
        area_bruta = self.perfil.A / 100.0
        self.resultados = []
        soma_nefetivas = 0.0
        config_elementos = self.TIPOLOGIA_ELEMENTOS.get(
            self.perfil.tipo_perfil)

        a_plana = dimensoes.get('a', 0.0)
        b_plana = dimensoes.get('b', 0.0)
        c_plana = dimensoes.get('c', 0.0)
        c_total = self.perfil.c_total / 10.0

        for config in config_elementos:
            nome, dim, tipo, enrijecido = config['nome'], config['dim'], config['tipo'], config['enrijecido']
            dimplana = dimensoes.get(dim, 0.0)

            lambdapo = self.calculate_lamdapo(dimplana)
            k = self.calculate_k(enrijecido, tipo, lambdapo,
                                 b_plana, c_plana, c_total, nome)
            lambdap = self.calculate_lambdap(k, dimplana)
            bef = self.calculate_bef(
                dimplana, lambdap, lambdapo, nome, c_plana, enrijecido)

            lambdap_calculado = lambdapo if (
                "Mesa" in nome and enrijecido) else lambdap
            largura_nefetiva = dimplana - bef
            soma_nefetivas += largura_nefetiva

            self.resultados.append({
                'Elemento': nome, 'Tipo': tipo, 'k': k, 'lambdap': lambdap_calculado,
                'dimplana': dimplana, 'dimefetiva': bef, 'dimnefetiva': largura_nefetiva
            })

        area_nefetiva = soma_nefetivas * self.t
        self.aefetiva = area_bruta - area_nefetiva
        self.nrd = self.chi_global * self.aefetiva * self.fy / 1.2

        detalhes = []
        for res in self.resultados:
            detalhes.append({
                'elemento': res['Elemento'],
                'k': round(res['k'], 3) if res['k'] else 0.0,
                'lambda_p': round(res['lambdap'], 3) if res['lambdap'] else 0.0,
                'b_plana': round(res['dimplana'], 3),
                'b_efetiva': round(res['dimefetiva'], 3),
                'b_inefetiva': round(res['dimnefetiva'], 3)
            })

        return {
            "geometria": {"area_bruta": round(area_bruta, 3), "a_efetiva": round(self.aefetiva, 3)},
            "estabilidade": {"chi_global": round(self.chi_global, 4), "sigma_atuante": round(self.tensao, 3)},
            "elementos": detalhes,
            "final": {"n_rd": round(self.nrd, 3), "unidade": "kN"}
        }
