class ResistenciaCortante:
    def __init__(self, perfil_geom):
        self.perfil = perfil_geom
        self.E = 200000
        self.fy = self.perfil.fy / 10.0  # kN/cm²
        self.t = self.perfil.t / 10.0    # cm

    def run_calculation(self) -> dict:
        h = self.perfil.a_plana / 10.0   # cm
        h_t = h / self.t
        termo1 = 1.08 * (self.E / 10.0 * 5 / self.fy)**0.5
        termo2 = 1.4 * (self.E / 10.0 * 5 / self.fy)**0.5

        vrd = 0.0
        if h_t <= termo1:
            vrd = (0.6 * self.fy * h * self.t) / 1.1
        elif termo1 < h_t <= termo2:
            vrd = ((0.65 * self.t**2) * (5 * self.fy * self.E / 10.0)**0.5) / 1.1
        elif h_t > termo2:
            vrd = ((0.905 * (self.E / 10.0) * 5 * self.t**3) / h) / 1.1

        # Multiplica pelas almas disponíveis no perfil
        multiplicador_alma = 2 if self.perfil.tipo_perfil == "Cartola" else 1
        vrd_total = vrd * multiplicador_alma

        return {
            "h_t_relacao": round(h_t, 2),
            "limite_1": round(termo1, 2),
            "limite_2": round(termo2, 2),
            "almas_consideradas": multiplicador_alma,
            "final": {
                "v_rd": round(vrd_total, 2),
                "unidade": "kN"
            }
        }
