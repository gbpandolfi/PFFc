import math


class EstabilidadeGlobal:
    E = 200000
    G = 77000

    def __init__(self, perfil_obj, lx: float, ly: float, lz: float):
        self.perfil = perfil_obj
        self.Lx = lx
        self.Ly = ly
        self.Lz = lz
        self.Nex = None
        self.Ney = None
        self.Nez1 = None
        self.Nez2 = None
        self.Nez3 = None
        self.Ne_min = None
        self.lambda0 = None
        self.chi_global = 1.0
        self.run_analysis()

    def run_analysis(self):
        P = self.perfil
        E, G = self.E, self.G
        Lmax = max(self.Lx, self.Ly, self.Lz)
        r = min(P.r0, P.rx, P.ry)
        if Lmax/r >=200:
            raise ValueError(f"Perfil muito esbelto. A relação L/r ({Lmax/r:.2f}) deve ser menor que 200.") 
    
        self.Nex = (math.pi**2 * E * P.Ix) / (self.Lx)**2
        self.Ney = (math.pi**2 * E * P.Iy) / (self.Ly)**2
        self.Nez1 = (1 / P.r0**2) * \
            ((math.pi**2 * E * P.Cw / (self.Lz)**2) + G * P.It)

        if P.tipo_perfil in ["U simples", "U enrijecido"]:
            self.Nez2 = ((self.Nex + self.Nez1)/(2*(1-(P.x0/P.r0)**2)))*(1-math.sqrt(
                1-((4*self.Nez1*self.Nex*(1-(P.x0/P.r0)**2))/(self.Nex + self.Nez1)**2)))
            self.Ne_min = min(self.Ney, self.Nez2)

        elif P.tipo_perfil == "Cartola":
            self.Nez3 = ((self.Ney + self.Nez1)/(2*(1-(P.y0/P.r0)**2)))*(1-math.sqrt(
                1-((4*self.Nez1*self.Ney*(1-(P.y0/P.r0)**2))/(self.Ney + self.Nez1)**2)))
            self.Ne_min = min(self.Nex, self.Nez3)

        if self.Ne_min:
            self.lambda0 = math.sqrt((P.A * P.fy) / self.Ne_min)
            if self.lambda0 <= 1.5:
                self.chi_global = 0.658**(self.lambda0**2)
            else:
                self.chi_global = 0.877 / (self.lambda0**2)

    def get_memoria(self):
        P = self.perfil
        if P.tipo_perfil in ["U simples", "U enrijecido"]:
            cargas_criticas = {
                "Nex": round(self.Nex/1000, 2),
                "Ney": round(self.Ney/1000, 2),
                "Nez": round(self.Nez1/1000, 2),
                "Nexz": round(self.Nez2/1000, 2),
                "Ne_min": round(self.Ne_min/1000, 2),
                "unidade": "kN"
            }
        elif P.tipo_perfil == "Cartola":
            cargas_criticas = {
                "Nex": round(self.Nex/1000, 2),
                "Ney": round(self.Ney/1000, 2),
                "Nez": round(self.Nez1/1000, 2),
                "Neyz": round(self.Nez3/1000, 2),
                "Ne_min": round(self.Ne_min/1000, 2),
                "unidade": "kN"
            }
        else:
            cargas_criticas = {
                "Ne_min": round(self.Ne_min/1000, 2),
                "unidade": "kN"
            }

        return {
            "cargas_criticas": cargas_criticas,
            "parametros_chi": {
                "lambda_0": round(self.lambda0, 4),
                "chi_global": round(self.chi_global, 4)
            }
        }
