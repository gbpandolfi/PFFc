class CapacidadeTracao:
    def __init__(self, perfil_geom, An0: float, An: float, Ct: float):
        self.perfil = perfil_geom
        self.A = self.perfil.A / 100.0        # cm²
        self.fy = self.perfil.fy / 10.0       # kN/cm²
        self.fu = self.perfil.fu / 10.0       # kN/cm²
        self.An0 = An0 / 100.0                # cm²
        self.An = An / 100.0                  # cm²
        self.Ct = Ct
        self.ntrd_1 = 0.0
        self.ntrd_2 = 0.0
        self.ntrd_3 = 0.0
        self.ntrd = 0.0

    def run_calculation(self) -> dict:
        self.ntrd_1 = self.A * self.fy / 1.1
        self.ntrd_2 = self.An0 * self.fu / 1.35
        self.ntrd_3 = self.Ct * self.An * self.fu / 1.65
        self.ntrd = min(self.ntrd_1, self.ntrd_2, self.ntrd_3)

        return {
            "geometria": {
                "area_bruta": self.A,
                "area_liquida_fora": self.An0,
                "area_liquida_ligacao": self.An
            },
            "parcelas": {
                "ntrd_bruta": round(self.ntrd_1, 2),
                "ntrd_liq_fora": round(self.ntrd_2, 2),
                "ntrd_liq_lig": round(self.ntrd_3, 2)
            },
            "final": {
                "n_rd": round(self.ntrd, 2),
                "unidade": "kN"
            }
        }
