import math


class PerfilBase:
    def __init__(self, t: float, fy: float, fu: float = None):
        self.t = t
        self.fy = fy
        self.fu = fu if fu else fy * 1.15
        self.A = None
        self.tipo_perfil = ""
        self.avisos = []  # Armazena os avisos de limites recomendados
        self._calcular_parametros_comuns()

    def _calcular_parametros_comuns(self):
        if self.t <= 6.3:
            self.ri = self.t
        else:
            self.ri = 1.5 * self.t
        self.rm = self.ri + 0.5 * self.t
        self.u1 = 1.571 * self.rm
        self.u2 = 0.785 * self.rm

    def validar_dimensoes_basicas(self):
        if hasattr(self, 'a_plana') and self.a_plana <= 0:
            raise ValueError(
                "Erro Geométrico: Espessura e raios excessivos. O trecho plano da alma (a) resultou negativo ou nulo.")
        if hasattr(self, 'b_plana') and self.b_plana <= 0:
            raise ValueError(
                "Erro Geométrico: Espessura e raios excessivos. O trecho plano da mesa (b) resultou negativo ou nulo.")


class USimples(PerfilBase):
    def __init__(self, t: float, fy: float, bw: float, bf: float, fu: float = None):
        super().__init__(t, fy, fu)
        self.tipo_perfil = "U simples"
        self.bw = bw
        self.bf = bf
        self.calcular_propriedades()
        self.validar_dimensoes_basicas()
        self.validar_dimensoes()

    def validar_dimensoes(self):
        if self.bw <= 0 or self.bw > 2000:
            raise ValueError("Altura total (bw) do U Simples deve estar entre 0 e 2000 mm.")
        if self.bf <= 0 or self.bf > 600:
            raise ValueError("Largura da mesa (bf) do U Simples deve estar entre 0 e 600 mm.")

        rel_a = self.a_plana / self.t
        if rel_a > 200:
            self.avisos.append(f"Relação b/t da alma ({rel_a:.2f}) acima do limite normativo (b/t_max = 200).")

        rel_b = self.b_plana / self.t
        if rel_b > 60:
            self.avisos.append(f"Relação b/t da mesa ({rel_b:.2f}) acima do limite normativo (b/t_max = 60).")

    def calcular_propriedades(self):
        am = self.bw - self.t
        a = self.bw - self.t*2 - self.ri*2
        bm = self.bf - 0.5 * self.t
        b = self.bf - (self.rm + 0.5 * self.t)

        self.a_plana, self.b_plana, self.c_plana = a, b, 0
        self.am, self.bm, self.cm = am, bm, 0
        self.a_total, self.b_total, self.c_total = self.bw, self.bf, 0
        self.angulo = 90

        self.A = self.t * (a + 2 * b + 2*self.u1)
        self.xg = (2 * self.t / self.A) * (b * (0.5 * b + self.rm) +
                                           self.u1 * (0.363 * self.rm)) + 0.5 * self.t
        self.yg = 0.5 * self.bw
        self.x0 = bm*((3 * am**2 * bm) / (am**3 + 6 * am**2 * bm)
                      ) + self.xg - 0.5 * self.t
        self.y0 = 0

        Ix_term = 0.042 * a**3 + b * \
            (0.5 * a + self.rm)**2 + self.u1 * \
            (0.5 * a + 0.637 * self.rm)**2 + 0.149 * self.rm**3
        self.Ix = 2 * self.t * Ix_term
        Iy_term = b * (0.5 * b + self.rm)**2 + 0.083 * \
            b**3 + 0.356 * self.rm**3
        self.Iy = 2 * self.t * Iy_term - self.A * (self.xg - 0.5 * self.t)**2
        self.Ixy = 0
        self.It = self.t**3 * (a + 2 * b + 2 * self.u1) / 3
        self.Cw = (am**2 * bm**2 * self.t / 12) * ((2 * am**3 *
                                                    bm + 3 * am**2 * bm**2) / (6 * am**2 * bm + am**3))

        self.rx = math.sqrt(self.Ix / self.A)
        self.ry = math.sqrt(self.Iy / self.A)
        self.r0 = (self.rx**2 + self.ry**2 + self.x0**2 + self.y0**2)**0.5


class UEnrijecido(PerfilBase):
    def __init__(self, t: float, fy: float, bw: float, bf: float, d: float, fu: float = None):
        super().__init__(t, fy, fu)
        self.tipo_perfil = "U enrijecido"
        self.bw = bw
        self.bf = bf
        self.d = d
        self.calcular_propriedades()
        self.validar_dimensoes_basicas()
        self.validar_dimensoes()

    def validar_dimensoes(self):
        if self.bw <= 0 or self.bw > 2500:
            raise ValueError("Altura total (bw) do U Enrijecido deve estar entre 0 e 2500 mm.")
        if self.bf <= 0 or self.bf > 600:
            raise ValueError("Largura da mesa (bf) do U Enrijecido deve estar entre 0 e 600 mm.")
        if self.d <= 0 or self.d > 600:
            raise ValueError("Enrijecedor de borda (d) deve estar entre 0 e 600 mm.")

        rel_a = self.a_plana / self.t
        if rel_a > 500:
            self.avisos.append(f"Relação b/t da alma ({rel_a:.2f}) acima do limite absoluto (500).")
        elif rel_a > 250:
            self.avisos.append(f"Relação b/t da alma ({rel_a:.2f}) acima do recomendado (250).")

        rel_b = self.b_plana / self.t
        if rel_b > 60:
            self.avisos.append(f"Relação b/t da mesa ({rel_b:.2f}) acima do limite absoluto (60).")
        elif rel_b > 30:
            self.avisos.append(f"Relação b/t da mesa ({rel_b:.2f}) acima do recomendado (30).")

    def calcular_propriedades(self):
        am = self.bw - self.t
        a = self.bw - self.t*2 - self.ri*2
        bm = self.bf - self.t
        b = self.bf - 2 * (self.rm + 0.5 * self.t)
        cm = self.d - self.t/2
        c = self.d - self.t - self.ri

        self.a_plana, self.b_plana, self.c_plana = a, b, c
        self.am, self.bm, self.cm = am, bm, cm
        self.a_total, self.b_total, self.c_total = self.bw, self.bf, self.d
        self.angulo = 90

        self.A = self.t * (a + 2 * b + 2 * c + 4 * self.u1)
        self.xg = (2 * self.t / self.A) * (b * (0.5 * b + self.rm) +
                                           (self.u1 + c) * (b + 2 * self.rm)) + 0.5 * self.t
        self.yg = 0.5 * self.bw
        self.x0 = bm * ((3 * am**2 * bm + cm * (6 * am**2 - 8 * cm**2))/(
            am**3 + 6 * am**2 * bm + cm * (8 * cm**2 - 12 * am * cm + 6 * am**2))) + self.xg - 0.5 * self.t
        self.y0 = 0

        Ix_term = 0.042 * a**3 + b * (0.5 * a + self.rm)**2 + 2 * self.u1 * (
            0.5 * a + 0.637 * self.rm)**2 + 0.298 * self.rm**3 + 0.083 * c**3 + 0.25 * c * (a - c)**2
        self.Ix = 2 * self.t * Ix_term

        Iy_term = b * (0.5 * b + self.rm)**2 + 0.083 * b**3 + 0.505 * self.rm**3 + \
            c * (b + 2 * self.rm)**2 + self.u1 * (b + 1.637 * self.rm)**2
        self.Iy = 2 * self.t * Iy_term - self.A * (self.xg - 0.5 * self.t)**2
        self.Ixy = 0
        self.It = self.t**3 * (a + 2 * b + 2 * c + 4 * self.u1) / 3

        Cw_num = 2 * am**3 * bm + 3 * am**2 * bm**2 + 48 * cm**4 + 112 * bm * cm**3 + 8 * am * \
            cm**3 + 48 * am * bm * cm**2 + 12 * am**2 * \
            cm**2 + 12 * am**2 * bm * cm + 6 * am**3 * cm
        Cw_den = 6 * am**2 * bm + (am + 2 * cm)**3 - 24 * am * cm**2
        self.Cw = (am**2 * bm**2 * self.t / 12) * (Cw_num / Cw_den)

        self.rx = math.sqrt(self.Ix / self.A)
        self.ry = math.sqrt(self.Iy / self.A)
        self.r0 = (self.rx**2 + self.ry**2 + self.x0**2 + self.y0**2)**0.5


class Cartola(PerfilBase):
    def __init__(self, t: float, fy: float, bw: float, bf: float, d: float, fu: float = None):
        super().__init__(t, fy, fu)
        self.tipo_perfil = "Cartola"
        self.bw = bw
        self.bf = bf
        self.d = d
        self.calcular_propriedades()
        self.validar_dimensoes_basicas()
        self.validar_dimensoes()

    def validar_dimensoes(self):
        if self.bw <= 0 or self.bw > 600:
            raise ValueError("Altura total (bw) do perfil Cartola deve estar entre 0 e 600 mm.")
        if self.bf <= 0 or self.bf > 5000:
            raise ValueError("Largura da mesa (bf) do perfil Cartola deve estar entre 0 e 5000 mm.")
        if self.d <= 0 or self.d > 300:
            raise ValueError("Enrijecedor (d) do perfil Cartola deve estar entre 0 e 300 mm.")

        rel_a = self.a_plana / self.t
        if rel_a > 60:
            self.avisos.append(f"Relação b/t da alma ({rel_a:.2f}) acima do limite absoluto (60).")
        elif rel_a > 30:
            self.avisos.append(f"Relação b/t da alma ({rel_a:.2f}) acima do recomendado (30).")

        rel_b = self.b_plana / self.t
        if rel_b > 500:
            self.avisos.append(f"Relação b/t da mesa ({rel_b:.2f}) acima do limite absoluto (500).")
        elif rel_b > 250:
            self.avisos.append(f"Relação b/t da mesa ({rel_b:.2f}) acima do recomendado (250).")
        
    def calcular_propriedades(self):
        a = self.bw - 2 * (self.rm + 0.5 * self.t)
        am = a + 2 * self.rm
        b = self.bf - 2 * (self.rm + 0.5 * self.t)
        bm = b + 2 * self.rm
        c = self.d - (self.rm + 0.5 * self.t)
        cm = c + self.rm

        self.a_plana, self.b_plana, self.c_plana = a, b, c
        self.am, self.bm, self.cm = am, bm, cm
        self.a_total, self.b_total, self.c_total = self.bw, self.bf, self.d
        self.angulo = 90

        self.A = self.t * (2 * a + b + 2 * c + 4 * self.u1)
        self.xg = 0.5 * self.bf
        self.yg = (2 * self.t / self.A) * (a * (0.5 * a + self.rm) +
                                           (self.u1 + c) * (a + 2 * self.rm)) + 0.5 * self.t
        self.x0 = 0
        y0_num = 3 * am * bm**2 + cm * (6 * bm**2 - 8 * cm**2)
        y0_den = bm**3 + 6 * am * bm**2 + cm * \
            (8 * cm + 12 * bm * cm + 6 * bm)**2
        self.y0 = am * (y0_num / y0_den) + self.yg - 0.5 * self.t

        Ix_term = (1/12) * a**3 + a * (0.5 * a + self.rm)**2 + 0.505 * self.rm**3 + \
            c * (a + 2 * self.rm)**2 + self.u1 * (a + 1.637 * self.rm)**2
        self.Ix = 2 * self.t * Ix_term - self.A * (self.yg - 0.5 * self.t)**2
        self.Iy = 2 * self.t * (1/24 * b**3 + a * (0.5 * b + self.rm)**2) + 2*self.t*(1/12 * c**3 + c * ((b + 2*c + 4 * self.rm)/2 - c/2) ** 2) + \
            2*self.t*self.u1 * (0.5 * b + 0.637 * self.rm)**2 + 2*self.t*self.u1 * (
                0.5 * b + 1.363 * self.rm)**2 + 2*self.t*0.298 * self.rm**3
        self.It = self.t**3 * (2 * a + b + 2 * c + 4 * self.u1) / 3

        Cw_num = 2 * am * bm**3 + 3 * am**2 * bm**2 + 48 * cm**4 + 112 * am * cm**3 + 8 * bm * \
            cm**3 - 48 * am * bm * cm**2 - 12 * bm**2 * \
            cm**2 + 12 * am * bm**2 * cm + 6 * bm**3 * cm
        Cw_den = 6 * am * bm**2 + (bm + 2 * cm)**3
        self.Cw = (am**2 * bm**2 * self.t / 12) * (Cw_num / Cw_den)

        self.rx = math.sqrt(self.Ix / self.A)
        self.ry = math.sqrt(self.Iy / self.A)
        self.r0 = (self.rx**2 + self.ry**2 + self.x0**2 + self.y0**2)**0.5
