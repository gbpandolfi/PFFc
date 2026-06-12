import tkinter as tk
from tkinter import ttk, messagebox
from propriedades import USimples, UEnrijecido, Cartola
from estabilidade_global import EstabilidadeGlobal
from compressao_mle import CompressaoMLE
from flexao_mle import FlexaoMLE
from cortante import ResistenciaCortante
from tracao import CapacidadeTracao
from combinados import EsforcosCombinados


class InterfacePFF:
    def __init__(self, root):
        self.root = root
        self.root.title("PFFc | Verificação de perfis formados a frio")
        self.root.geometry("900x850")

        self.notebook = ttk.Notebook(root)
        self.notebook.pack(fill="both", expand=True, padx=10, pady=10)

        self.tab_inputs = ttk.Frame(self.notebook)
        self.tab_resultados = ttk.Frame(self.notebook)

        self.notebook.add(self.tab_inputs, text="Parâmetros de Entrada")
        self.notebook.add(self.tab_resultados,
                          text="Memória de Cálculo (Detalhada)")

        self._build_inputs()
        self._build_resultados()

    def _build_inputs(self):
        container_geo = ttk.Frame(self.tab_inputs)
        container_geo.pack(fill="x", pady=5, padx=5)
        frame_geo = ttk.LabelFrame(container_geo, text="Dados da Seção Transversal e Material", padding=10)
        frame_geo.pack(side="left", fill="both", expand=True, padx=(0, 5))
        ttk.Label(frame_geo, text="Tipo de Perfil:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        self.combo_perfil = ttk.Combobox(frame_geo, values=["U Simples", "U Enrijecido", "Cartola"], state="readonly", width=15)
        self.combo_perfil.current(0)
        self.combo_perfil.grid(row=0, column=1, sticky="w", padx=5, pady=5)
        self.combo_perfil.bind("<<ComboboxSelected>>", self._atualizar_campos_geometria)
        self.vars = {}
        campos = [
            ("Espessura (t) [mm]:", "t", "0.8"),
            ("Altura (bw) [mm]:", "bw", "140"),
            ("Mesa (bf) [mm]:", "bf", "40"),
            ("Enrijecedor (d) [mm]:", "d", ""),
            ("Lim. Escoamento (fy) [MPa]:", "fy", "350"),
            ("Lim. Ruptura (fu) [MPa]:", "fu", "400")
        ]
        
        for i, (label, var, default) in enumerate(campos):
            row_idx = (i // 2) + 1
            col_idx = (i % 2) * 2
            ttk.Label(frame_geo, text=label).grid(row=row_idx, column=col_idx, sticky="w", pady=5, padx=5)
            ent = ttk.Entry(frame_geo, width=12)
            ent.insert(0, default)
            ent.grid(row=row_idx, column=col_idx+1, padx=5, pady=5)
            self.vars[var] = ent
            if var in ["bw", "bf", "d"]:
                ent.bind("<KeyRelease>", self._desenhar_perfil)

        self.ent_d = self.vars["d"]
        self.ent_d.config(state="disabled") 
        frame_preview = ttk.LabelFrame(container_geo, text="Seção do Perfil", padding=10)
        frame_preview.pack(side="right", fill="both")
        self.canvas_perfil = tk.Canvas(frame_preview, width=220, height=180, bg="#f9f9f9", highlightthickness=1, highlightbackground="#cccccc")
        self.canvas_perfil.pack(padx=5, pady=5)
        frame_condicoes = ttk.LabelFrame(
            self.tab_inputs, text="Comprimentos, fatores e ligações", padding=10)
        frame_condicoes.pack(fill="x", pady=5, padx=5)

        ttk.Label(frame_condicoes, text="Lx [cm]:").grid(
            row=0, column=0, sticky="w", padx=5)
        self.ent_lx = ttk.Entry(frame_condicoes, width=8)
        self.ent_lx.insert(0, "150")
        self.ent_lx.grid(row=0, column=1, pady=2)

        ttk.Label(frame_condicoes, text="Ly [cm]:").grid(
            row=0, column=2, sticky="w", padx=5)
        self.ent_ly = ttk.Entry(frame_condicoes, width=8)
        self.ent_ly.insert(0, "150")
        self.ent_ly.grid(row=0, column=3, pady=2)

        ttk.Label(frame_condicoes, text="Lz [cm]:").grid(
            row=0, column=4, sticky="w", padx=5)
        self.ent_lz = ttk.Entry(frame_condicoes, width=8)
        self.ent_lz.insert(0, "150")
        self.ent_lz.grid(row=0, column=5, pady=2)

        ttk.Separator(frame_condicoes, orient='horizontal').grid(
            row=1, columnspan=6, sticky='ew', pady=8)

        ttk.Label(frame_condicoes, text="Fator Cb (Flexão):").grid(
            row=2, column=0, sticky="w", padx=5)
        self.ent_cb = ttk.Entry(frame_condicoes, width=8)
        self.ent_cb.insert(0, "1.0")
        self.ent_cb.grid(row=2, column=1)

        ttk.Label(frame_condicoes, text="Área Liq. Ligação (An) [mm²]:").grid(
            row=2, column=2, sticky="w", padx=5)
        self.ent_an = ttk.Entry(frame_condicoes, width=8)
        self.ent_an.grid(row=2, column=3)

        ttk.Label(frame_condicoes, text="Área Liq. Fora (An0) [mm²]:").grid(
            row=3, column=2, sticky="w", padx=5)
        self.ent_an0 = ttk.Entry(frame_condicoes, width=8)
        self.ent_an0.grid(row=3, column=3)

        ttk.Label(frame_condicoes, text="Coef. Redução (Ct):").grid(
            row=2, column=4, sticky="w", padx=5)
        self.ent_ct = ttk.Entry(frame_condicoes, width=8)
        self.ent_ct.insert(0, "1.0")
        self.ent_ct.grid(row=2, column=5)

        ttk.Label(frame_condicoes, text="*(An e An0: vazio usará Área Bruta)").grid(
            row=3, column=4, columnspan=2, sticky="w", padx=5)

        self.trac_entries = {"an": self.ent_an,
                             "an0": self.ent_an0, "ct": self.ent_ct}

        frame_esf = ttk.LabelFrame(
            self.tab_inputs, text="Esforços Solicitantes", padding=10)
        frame_esf.pack(fill="x", pady=5, padx=5)

        ttk.Label(frame_esf, text="Normal (Nsd) [kN]:").grid(
            row=0, column=0, sticky="w", padx=5)
        self.ent_nsd = ttk.Entry(frame_esf, width=10)
        self.ent_nsd.insert(0, "15.0")
        self.ent_nsd.grid(row=0, column=1)

        self.tipo_normal = tk.StringVar(value="compressao")
        ttk.Radiobutton(frame_esf, text="Compressão", variable=self.tipo_normal,
                        value="compressao", command=self._on_tipo_normal_changed).grid(row=0, column=2, sticky="w")
        ttk.Radiobutton(frame_esf, text="Tração", variable=self.tipo_normal,
                        value="tracao", command=self._on_tipo_normal_changed).grid(row=0, column=3, sticky="w")

        ttk.Label(frame_esf, text="Momento (Mxsd) [kN.cm]:").grid(
            row=1, column=0, sticky="w", padx=5)
        self.ent_msd = ttk.Entry(frame_esf, width=10)
        self.ent_msd.insert(0, "120.0")
        self.ent_msd.grid(row=1, column=1, pady=5)

        ttk.Label(frame_esf, text="Cortante (Vsd) [kN]:").grid(
            row=2, column=0, sticky="w", padx=5)
        self.ent_vsd = ttk.Entry(frame_esf, width=10)
        self.ent_vsd.insert(0, "5.0")
        self.ent_vsd.grid(row=2, column=1, pady=5)

        frame_verif = ttk.LabelFrame(
            self.tab_inputs, text="Verificações a Processar", padding=10)
        frame_verif.pack(fill="x", pady=5, padx=5)

        self.chk_comp = tk.BooleanVar(value=False)
        self.chk_trac = tk.BooleanVar(value=False)
        self.chk_flex = tk.BooleanVar(value=False)
        self.chk_cort = tk.BooleanVar(value=False)
        self.chk_comb_fc = tk.BooleanVar(value=False)
        self.chk_comb_fv = tk.BooleanVar(value=False)

        ttk.Checkbutton(frame_verif, text="Compressão", variable=self.chk_comp,
                        command=self._on_base_changed).grid(row=0, column=0, padx=10, sticky="w")
        ttk.Checkbutton(frame_verif, text="Tração", variable=self.chk_trac,
                        command=self._on_base_changed).grid(row=0, column=1, padx=10, sticky="w")
        ttk.Checkbutton(frame_verif, text="Momento Fletor", variable=self.chk_flex,
                        command=self._on_base_changed).grid(row=0, column=2, padx=10, sticky="w")
        ttk.Checkbutton(frame_verif, text="Força Cortante", variable=self.chk_cort,
                        command=self._on_base_changed).grid(row=0, column=3, padx=10, sticky="w")

        ttk.Checkbutton(frame_verif, text="Combinação: Fletor + Axial", variable=self.chk_comb_fc,
                        command=self._on_comb_fc_changed).grid(row=1, column=0, columnspan=2, pady=5, sticky="w")
        ttk.Checkbutton(frame_verif, text="Combinação: Fletor + Cortante", variable=self.chk_comb_fv,
                        command=self._on_comb_fv_changed).grid(row=1, column=2, columnspan=2, pady=5, sticky="w")

        btn_calc = ttk.Button(
            self.tab_inputs, text="Calcular", command=self.executar_calculo)
        btn_calc.pack(pady=10)

        frame_resumo = ttk.LabelFrame(
            self.tab_inputs, text="Resumo do Dimensionamento", padding=10)
        frame_resumo.pack(fill="both", expand=True, pady=10, padx=5)

        self.txt_resumo = tk.Text(
            frame_resumo, height=20, font=("Consolas", 10), bg="#e8f4f8")
        self.txt_resumo.pack(fill="both", expand=True)
        self.txt_resumo.insert(tk.END, "")

        self._on_base_changed()
        self._desenhar_perfil()

    def _on_base_changed(self):
        estado_flex = "normal" if self.chk_flex.get() else "disabled"
        self.ent_cb.config(state=estado_flex)

        estado_trac = "normal" if self.chk_trac.get() else "disabled"
        for ent in self.trac_entries.values():
            ent.config(state=estado_trac)

        self.vars["fu"].config(state=estado_trac)

        if not (self.chk_comp.get() or self.chk_trac.get()) or not self.chk_flex.get():
            self.chk_comb_fc.set(False)

        if not self.chk_flex.get() or not self.chk_cort.get():
            self.chk_comb_fv.set(False)

    def _on_tipo_normal_changed(self):
        if self.tipo_normal.get() == "compressao":
            self.chk_comp.set(True)
            self.chk_trac.set(False)
        else:
            self.chk_trac.set(True)
            self.chk_comp.set(False)
        self._on_base_changed()

    def _on_comb_fc_changed(self):
        if self.chk_comb_fc.get():
            self.chk_flex.set(True)
            if self.tipo_normal.get() == "compressao":
                self.chk_comp.set(True)
                self.chk_trac.set(False)
            else:
                self.chk_trac.set(True)
                self.chk_comp.set(False)
        self._on_base_changed()

    def _on_comb_fv_changed(self):
        if self.chk_comb_fv.get():
            self.chk_flex.set(True)
            self.chk_cort.set(True)
        self._on_base_changed()

    def _atualizar_campos_geometria(self, event=None):
        if self.combo_perfil.get() == "U Simples":
            self.ent_d.config(state="normal")
            self.ent_d.delete(0, tk.END)
            self.ent_d.config(state="disabled")
        else:
            self.ent_d.config(state="normal")
            if self.ent_d.get() == "":
                self.ent_d.insert(0, "20")
            
        self._desenhar_perfil()

    def _desenhar_perfil(self, event=None):
        self.canvas_perfil.delete("all")
        
        try:
            tipo = self.combo_perfil.get()
            bw = float(self.vars["bw"].get()) if self.vars["bw"].get() else 0
            bf = float(self.vars["bf"].get()) if self.vars["bf"].get() else 0
            d = 0
            
            if tipo != "U Simples" and self.vars["d"].get():
                d = float(self.vars["d"].get())
                
            if bw <= 0 or bf <= 0:
                return

            w_canvas, h_canvas = 220, 180
            cx, cy = w_canvas / 2, h_canvas / 2
            margin = 25
            
            w_perfil = (bf + 2 * d) if tipo == "Cartola" else bf
            h_perfil = bw
            max_dim = max(w_perfil, h_perfil)
            
            if max_dim == 0: return

            escala = (min(w_canvas, h_canvas) - 2 * margin) / max_dim
            
            bw_px = bw * escala
            bf_px = bf * escala
            d_px = d * escala
            
            pts = []
            if tipo == "U Simples":
                pts = [
                    (cx + bf_px/2, cy - bw_px/2), 
                    (cx - bf_px/2, cy - bw_px/2), 
                    (cx - bf_px/2, cy + bw_px/2), 
                    (cx + bf_px/2, cy + bw_px/2)  
                ]
            elif tipo == "U Enrijecido":
                pts = [
                    (cx + bf_px/2, cy - bw_px/2 + d_px), 
                    (cx + bf_px/2, cy - bw_px/2),        
                    (cx - bf_px/2, cy - bw_px/2),        
                    (cx - bf_px/2, cy + bw_px/2),        
                    (cx + bf_px/2, cy + bw_px/2),        
                    (cx + bf_px/2, cy + bw_px/2 - d_px)  
                ]
            elif tipo == "Cartola":
                pts = [
                    (cx - bf_px/2 - d_px, cy + bw_px/2), 
                    (cx - bf_px/2, cy + bw_px/2),        
                    (cx - bf_px/2, cy - bw_px/2),        
                    (cx + bf_px/2, cy - bw_px/2),        
                    (cx + bf_px/2, cy + bw_px/2),        
                    (cx + bf_px/2 + d_px, cy + bw_px/2)  
                ]
                
            self.canvas_perfil.create_line(pts, width=4, fill="#0055a4", joinstyle=tk.ROUND, capstyle=tk.ROUND)
            
        except ValueError:
            pass
    
    def exibir_grafico_tensoes(self, tensoes, desloc_ln, perfil):
        top = tk.Toplevel(self.root)
        top.title("Diagrama de Tensões - Flexão (MLE)")
        top.geometry("650x580")
        top.configure(bg="white")
        
        w, h = 650, 580
        canvas = tk.Canvas(top, width=w, height=h, bg="white", highlightthickness=0)
        canvas.pack(fill="both", expand=True, padx=10, pady=10)
        
        sigma_sup = tensoes.get("sigma_sup", 0.0)
        sigma_inf = tensoes.get("sigma_inf", 0.0)
        sigma1 = tensoes.get("sigma1", 0.0)
        sigma2 = tensoes.get("sigma2", 0.0)
        
        if sigma_sup == 0 and sigma_inf == 0:
            canvas.create_text(w//2, h//2, text="Tensões nulas.", font=("Consolas", 12))
            return

        margin_y = 70
        draw_h = h - 2 * margin_y
        center_x = 420 
        max_sigma = max(abs(sigma_sup), abs(sigma_inf))
        escala_x = 120 / max_sigma if max_sigma > 0 else 1
        
        y_topo = margin_y
        y_base = h - margin_y
        
        x_sup = center_x + (sigma_sup * escala_x)
        x_inf = center_x + (sigma_inf * escala_x)
        
        delta_sigma = abs(sigma_sup) + abs(sigma_inf)
        if delta_sigma > 0:
            prop_ln = abs(sigma_sup) / delta_sigma
            y_ln = y_topo + (prop_ln * draw_h)
        else:
            y_ln = y_topo + draw_h / 2

        def calc_y(sigma_val):
            if sigma_inf == sigma_sup: return y_topo
            return y_topo + ((sigma_val - sigma_sup) / (sigma_inf - sigma_sup)) * draw_h

        y_s1 = calc_y(sigma1)
        x_s1 = center_x + (sigma1 * escala_x)

        y_s2 = calc_y(sigma2)
        x_s2 = center_x + (sigma2 * escala_x)

        yg_mm = perfil.yg
        t_mm = perfil.t
        ri_mm = perfil.ri
        bw_mm = perfil.bw
        
        dist1 = yg_mm + abs(desloc_ln)
        dist2 = bw_mm - dist1
        dist1_plana = max(0.0, dist1 - t_mm - ri_mm)
        dist2_plana = max(0.0, dist2 - t_mm - ri_mm)

        x_cadeia_part_plana = 250
        x_cadeia_ln = 160
        x_cadeia_total = 70

        def desenhar_cota(x_cote, y1, y2, texto):
            canvas.create_line(center_x, y1, x_cote, y1, fill="#dddddd", width=1, dash=(2, 2))
            canvas.create_line(center_x, y2, x_cote, y2, fill="#dddddd", width=1, dash=(2, 2))
            canvas.create_line(x_cote, y1, x_cote, y2, arrow=tk.BOTH, fill="#444444", width=1)
            canvas.create_text(x_cote - 8, (y1 + y2) / 2, text=texto, anchor="e", 
                               font=("Consolas", 8), fill="#222222", justify=tk.RIGHT)

        desenhar_cota(x_cadeia_part_plana, y_s1, y_ln, f"dist1_\n{dist1_plana:.1f}mm")
        desenhar_cota(x_cadeia_part_plana, y_ln, y_s2, f"dist2_\n{dist2_plana:.1f}mm")
        
        desenhar_cota(x_cadeia_ln, y_topo, y_ln, f"dist1\n{dist1:.1f}mm")
        desenhar_cota(x_cadeia_ln, y_ln, y_base, f"dist2\n{dist2:.1f}mm")
        
        desenhar_cota(x_cadeia_total, y_topo, y_base, f"bw\n{bw_mm:.1f} mm")

        cor_sup = "#ffcccc" if sigma_sup < 0 else "#cce6ff"
        cor_inf = "#ffcccc" if sigma_inf < 0 else "#cce6ff"
        
        canvas.create_polygon(center_x, y_ln, center_x, y_topo, x_sup, y_topo, 
                              fill=cor_sup, outline="black", width=1)
        canvas.create_polygon(center_x, y_ln, center_x, y_base, x_inf, y_base, 
                              fill=cor_inf, outline="black", width=1)
        
        canvas.create_line(center_x, y_topo - 20, center_x, y_base + 20, width=2, dash=(4, 4))
        canvas.create_line(center_x - 140, y_ln, center_x + 140, y_ln, width=1, dash=(2, 2), fill="gray")
        canvas.create_text(center_x + 145, y_ln, text="L.N.", anchor="w", fill="gray", font=("Consolas", 9, "bold"))

        canvas.create_line(center_x, y_s1, x_s1, y_s1, width=1, dash=(2,2), fill="black")
        canvas.create_oval(x_s1 - 3, y_s1 - 3, x_s1 + 3, y_s1 + 3, fill="black")

        canvas.create_line(center_x, y_s2, x_s2, y_s2, width=1, dash=(2,2), fill="black")
        canvas.create_oval(x_s2 - 3, y_s2 - 3, x_s2 + 3, y_s2 + 3, fill="black")

        def formata_tensao(val):
            sinal = "-" if val < 0 else "+"
            return f"{sinal}{abs(val):.2f}"

        canvas.create_text(x_sup + (8 if sigma_sup >= 0 else -8), y_topo - 15,
                           text=f"σ1: {formata_tensao(sigma_sup)} kN/cm²",
                           anchor="w" if sigma_sup >= 0 else "e", font=("Consolas", 10, "bold"), fill="black")

        canvas.create_text(x_inf + (8 if sigma_inf >= 0 else -8), y_base + 15,
                           text=f"σ2: {formata_tensao(sigma_inf)} kN/cm²",
                           anchor="w" if sigma_inf >= 0 else "e", font=("Consolas", 10, "bold"), fill="black")

        canvas.create_text(x_s1 + (8 if sigma1 >= 0 else -8), y_s1,
                           text=f"σ1': {formata_tensao(sigma1)}",
                           anchor="w" if sigma1 >= 0 else "e", font=("Consolas", 9), fill="#222222")

        canvas.create_text(x_s2 + (8 if sigma2 >= 0 else -8), y_s2,
                           text=f"σ2': {formata_tensao(sigma2)}",
                           anchor="w" if sigma2 >= 0 else "e", font=("Consolas", 9), fill="#222222")
        
        canvas.create_rectangle(w - 110, 15, w - 95, 28, fill="#ffcccc", outline="black")
        canvas.create_text(w - 85, 21, text="Compressão", anchor="w", font=("Consolas", 8))
        canvas.create_rectangle(w - 110, 33, w - 95, 46, fill="#cce6ff", outline="black")
        canvas.create_text(w - 85, 39, text="Tração", anchor="w", font=("Consolas", 8))

    def _build_resultados(self):
        self.txt_out = tk.Text(self.tab_resultados, wrap="word", font=(
            "Consolas", 10), bg="#f4f4f4")
        self.txt_out.pack(fill="both", expand=True, padx=5, pady=5)
        self.btn_grafico = ttk.Button(self.tab_resultados, text="GRÁFICO DE TENSÕES", state="disabled")
        self.btn_grafico.pack(pady=5)

    def _formatar_estab(self, mem, tipo="compressao"):
        c = mem.get('cargas_criticas', {})
        p = mem.get('parametros_chi', {})
        tipo_perfil = self.combo_perfil.get()

        if tipo == "flexao" and tipo_perfil == "Cartola":
            return (f"\n\n=== FLAMBAGEM GLOBAL ===\n"
                    f" - Nex: {c.get('Nex', 0)} {c.get('unidade', 'kN')} | Nez: {c.get('Nez', 0)} {c.get('unidade', 'kN')}\n")
        
        elif tipo == "flexao":
            return (f"\n\n=== FLAMBAGEM GLOBAL ===\n"
                    f" - Ney: {c.get('Ney', 0)} {c.get('unidade', 'kN')} | Nez: {c.get('Nez', 0)} {c.get('unidade', 'kN')}\n")

        linha_cargas = f" - Nex: {c.get('Nex', 0)} {c.get('unidade', 'kN')} | Ney: {c.get('Ney', 0)} {c.get('unidade', 'kN')} | Nez: {c.get('Nez', 0)} {c.get('unidade', 'kN')}"
        nexz = c.get('Nexz', 0)
        if nexz:
            linha_cargas += f" | Nexz: {nexz} {c.get('unidade', 'kN')}"
        neyz = c.get('Neyz', 0)
        if neyz:
            linha_cargas += f" | Neyz: {neyz} {c.get('unidade', 'kN')}"
            
        return (f"\n\n=== ESTABILIDADE GLOBAL ===\n"
                f"{linha_cargas}\n"
                f" - Carga crítica (Ne_min): {c.get('Ne_min', 0)} {c.get('unidade', 'kN')}\n"
                f" - λ0 (flambagem global): {p.get('lambda_0', 0)}\n"
                f" - χ (flambagem global): {p.get('chi_global', 1)}\n")

    def _formatar_compressao(self, res):
        geo = res.get('geometria', {})
        est = res.get('estabilidade', {})
        txt = (f"Área Efetiva: {geo.get('a_efetiva', 0):.3f} cm² (Área Bruta: {geo.get('area_bruta', 0):.2f} cm²)\n"
               f"Tensão Atuante: {est.get('sigma_atuante', 0):.2f} kN/cm² | χ Global: {est.get('chi_global', 1):.4f}\n\n"
               f"Detalhamento dos Elementos (MLE):\n")

        for el in res.get('elementos', []):
            txt += f" • {el.get('elemento', '')}:\n"
            txt += f"   - Largura Plana (b): {el.get('b_plana', 0)*10:.2f} mm | Largura efetiva (bef): {el.get('b_efetiva', 0)*10:.2f} mm\n"
            txt += f"   - Coef. de flambagem local (k): {el.get('k', 0):.3f}\n"
            txt += f"   - Esbeltez (λp): {el.get('lambda_p', 0):.3f}\n"

        final = res.get('final', {})
        txt += f"\n>> RESISTÊNCIA À COMPRESSÃO (Nc,Rd): {final.get('n_rd', 0):.2f} {final.get('unidade', 'kN')}\n"
        return txt

    def _formatar_tracao(self, res):
        geo = res.get('geometria', {})
        parc = res.get('parcelas', {})
        txt = (f"Área Bruta (Ag): {geo.get('area_bruta', 0):.3f} cm²\n"
               f"Área Líquida (An0): {geo.get('area_liquida_fora', 0):.3f} cm² | An (Ligação): {geo.get('area_liquida_ligacao', 0):.3f} cm²\n\n"
               f"Verificações Parciais:\n"
               f" - Escoamento da Seção Bruta: {parc.get('ntrd_bruta', 0):.2f} kN\n"
               f" - Ruptura na Ligação: {parc.get('ntrd_liq_lig', 0):.2f} kN\n"
               f" - Ruptura Fora da Ligação: {parc.get('ntrd_liq_fora', 0):.2f} kN\n"
               f"\n>> RESISTÊNCIA À TRAÇÃO (Nt,Rd): {res.get('final', {}).get('n_rd', 0):.2f} {res.get('final', {}).get('unidade', 'kN')}\n")
        return txt

    def _formatar_flexao(self, res):
        tipo_perfil = self.combo_perfil.get()
        geo = res.get('geometria_efetiva', {})
        flt = res.get('flambagem_flt', {})
        
        if tipo_perfil =="Cartola":
            txt = (f" - Deslocamento da Linha Neutra: {geo.get('desloc_ln', 0):.2f} mm\n"
                f" - Número de iterações para convergência: {geo.get('iteracoes', 0)}\n"
                f" - Módulo Resistente Elástico Efetivo (Wef): {geo.get('wef', 0):.2f} mm³\n"
                f" - Wef da fibra comprimida (Wcef): {geo.get('wcef', 0):.2f} mm³\n"
                f" - Momento Crítico (Me): {flt.get('Me', 0):.2f} kN.cm\n"
                f" - λ0 (flt): {flt.get('lambda_0', 0):.4f}\n"
                f" - χ (flt): {flt.get('chi_flt', 1):.4f}\n\n"
                f"Detalhamento dos Elementos (MLE):\n")
        else:
            txt = (f" - Deslocamento da Linha Neutra: {geo.get('desloc_ln', 0):.2f} mm\n"
                f" - Número de iterações para convergência: {geo.get('iteracoes', 0)}\n"
                f" - Módulo Resistente Elástico Efetivo (Wef): {geo.get('wef', 0):.2f} mm³\n"
                f" - Momento Crítico (Me): {flt.get('Me', 0):.2f} kN.cm\n"
                f" - λ0 (flt): {flt.get('lambda_0', 0):.4f}\n"
                f" - χ (flt): {flt.get('chi_flt', 1):.4f}\n\n"
                f"Detalhamento dos Elementos (MLE):\n")

        for el in res.get('elementos', []):
            txt += f" • {el.get('elemento', '')}:\n"
            txt += f"   - Largura Plana (b): {el.get('b_plana', 0)*10:.2f} mm | Largura efetiva (bef): {el.get('b_efetiva', 0)*10:.2f} mm\n"
            txt += f"   - Tensão (σ): {el.get('sigma', 0):.2f} kN/cm²\n"
            txt += f"   - Coef. de flambagem (k): {el.get('k', 0):.3f}\n"
            txt += f"   - Esbeltez (λp): {el.get('lambda_p', 0):.3f}\n"

        final = res.get('final', {})
        txt += f"\n>> Mx_ef,Rd (Escoamento da seção efetiva): {final.get('mrd1', 0):.2f} {final.get('unidade', 'kN.cm')}\n"
        txt += f">> Mx_flt,Rd (Flambagem lateral com torção): {final.get('mrd2', 0):.2f} {final.get('unidade', 'kN.cm')}\n"
        txt += f">> RESISTÊNCIA À FLEXÃO (Mx,Rd): {final.get('m_rd', 0):.2f} {final.get('unidade', 'kN.cm')}\n"

        return txt

    def _formatar_cortante(self, res):
        txt = (f"Relação Esbeltez da Alma (h/t): {res.get('h_t_relacao', 0):.2f}\n"
               f"Limites Normativos (λ1, λ2): {res.get('limite_1', 0):.2f}, {res.get('limite_2', 0):.2f}\n"
               f"Número de Almas Consideradas: {res.get('almas_consideradas', 1)}\n"
               f"\n>> RESISTÊNCIA AO CORTANTE (V,Rd): {res.get('final', {}).get('v_rd', 0):.2f} {res.get('final', {}).get('unidade', 'kN')}\n")
        return txt

    def executar_calculo(self):
        try:
            campos_validacao = [
                (self.vars["t"],
                 "Espessura (t)"), (self.vars["bw"], "Altura (bw)"),
                (self.vars["bf"], "Mesa (bf)"), (self.vars["d"],
                                                 "Enrijecedor (d)"),
                (self.vars["fy"],
                 "Escoamento (fy)"), (self.vars["fu"], "Ruptura (fu)"),
                (self.ent_lx, "Lx"), (self.ent_ly, "Ly"), (self.ent_lz, "Lz"),
                (self.ent_cb, "Cb"), (self.ent_ct, "Ct"),
                (self.ent_nsd, "Nsd"), (self.ent_msd, "Mxsd"), (self.ent_vsd, "Vsd")
            ]
            for widget, nome in campos_validacao:
                if str(widget.cget("state")) == "normal" and not widget.get().strip():
                    raise ValueError(
                        f"O campo '{nome}' não pode estar vazio para a verificação selecionada.")

            tipo_perfil = self.combo_perfil.get()
            t = float(self.vars["t"].get())
            if not (0 < t <= 10):
                raise ValueError(
                    "Valor inválido. A espessura do perfil (t) deve estar entre 0 e 10 mm.")
            bw = float(self.vars["bw"].get())
            bf = float(self.vars["bf"].get())
            fy = float(self.vars["fy"].get())
            if not (180 <= fy <= 450):
                raise ValueError(
                    "Valor inválido. fy deve estar entre 180 MPa e 450 MPa.")
            fu = float(self.vars["fu"].get())
            if not (300 <= fu <= 550):
                raise ValueError(
                    "Valor inválido. fu deve estar entre 180 MPa e 550 MPa.")

            lx_mm = float(self.ent_lx.get()) * 10
            ly_mm = float(self.ent_ly.get()) * 10
            lz_mm = float(self.ent_lz.get()) * 10

            nsd = float(self.ent_nsd.get())
            if nsd < 0:
                raise ValueError(
                    "O esforço normal (Nsd) não pode ser negativo. Utilize a seleção de 'Compressão' ou 'Tração' ao lado para indicar o sentido da força.")

            mxsd = float(self.ent_msd.get())
            vsd = float(self.ent_vsd.get())
            is_comp = self.tipo_normal.get() == "compressao"

            cb_val = float(self.ent_cb.get())
            if cb_val < 1.0 or cb_val == None:
                raise ValueError(
                    "O fator Cb deve ser igual ou maior que 1.0.")
            ct_val = float(self.ent_ct.get())
            if ct_val > 1.0 or ct_val < 0 or ct_val == None:
                raise ValueError(
                    "O fator Ct deve estare entre 0.0 e 1.0.")

            calc_comb_fc = self.chk_comb_fc.get()
            calc_comb_fv = self.chk_comb_fv.get()
            calc_flex = self.chk_flex.get() or calc_comb_fc or calc_comb_fv
            calc_cort = self.chk_cort.get() or calc_comb_fv
            calc_comp = self.chk_comp.get()
            calc_trac = self.chk_trac.get()

            self.txt_out.delete(1.0, tk.END)

            if tipo_perfil == "U Simples":
                perfil = USimples(t=t, fy=fy, bw=bw, bf=bf, fu=fu)
            elif tipo_perfil == "U Enrijecido":
                d = float(self.vars["d"].get())
                perfil = UEnrijecido(t=t, fy=fy, bw=bw, bf=bf, d=d, fu=fu)
            elif tipo_perfil == "Cartola":
                d = float(self.vars["d"].get())
                perfil = Cartola(t=t, fy=fy, bw=bw, bf=bf, d=d, fu=fu)
            
            if getattr(perfil, 'avisos', []):
                msg_avisos = "\n".join([f"• {aviso}" for aviso in perfil.avisos])
                pergunta = (
                    f"Foram detectadas inconformidades com os limites da NBR 6355:\n\n"
                    f"{msg_avisos}\n\n"
                    f"Deseja ignorar as restrições normativas e prosseguir com o cálculo mesmo assim?"
                )
                prosseguir = messagebox.askyesno("Avisos Dimensionais", pergunta)
                if not prosseguir:
                    self.txt_out.insert(tk.END, "Cálculo cancelado pelo usuário devido a violações de b/t.\n")
                    return
            
            estab = EstabilidadeGlobal(perfil, lx=lx_mm, ly=ly_mm, lz=lz_mm)
            memoria_estab = estab.get_memoria()

            self.txt_out.insert(
                tk.END, "=== PROPRIEDADES GEOMÉTRICAS ===\n\n")
            self.txt_out.insert(
                tk.END, f"Perfil: {perfil.tipo_perfil.upper()}\n")

            if getattr(perfil, 'A', None) is not None:
                self.txt_out.insert(
                    tk.END, f"Área bruta (Ag): {perfil.A:.2f} mm²\n")
            if getattr(perfil, 'xg', None) is not None:
                self.txt_out.insert(
                    tk.END, f"Distância do centroide (xg): {perfil.xg:.2f} mm\n")
            if getattr(perfil, 'yg', None) is not None:
                self.txt_out.insert(
                    tk.END, f"Distância do centroide (yg): {perfil.yg:.2f} mm\n")
            if getattr(perfil, 'x0', None) is not None and perfil.x0 != 0:
                self.txt_out.insert(
                    tk.END, f"Distância do centro de torção (x0): {perfil.x0:.2f} mm\n")
            if getattr(perfil, 'y0', None) is not None and perfil.y0 != 0:
                self.txt_out.insert(
                    tk.END, f"Distância do centro de torção (y0): {perfil.y0:.2f} mm\n")
            if getattr(perfil, 'Ix', None) is not None:
                self.txt_out.insert(
                    tk.END, f"Momento de inércia (Ix): {perfil.Ix:.2f} mm⁴\n")
            if getattr(perfil, 'Iy', None) is not None:
                self.txt_out.insert(
                    tk.END, f"Momento de inércia (Iy): {perfil.Iy:.2f} mm⁴\n")
            if getattr(perfil, 'It', None) is not None:
                self.txt_out.insert(
                    tk.END, f"Momento de inércia à torção (It): {perfil.It:.2f} mm⁴\n")
            if getattr(perfil, 'Cw', None) is not None:
                self.txt_out.insert(
                    tk.END, f"Constante de empenamento (Cw): {perfil.Cw:.2f} mm⁶\n")
            if getattr(perfil, 'rx', None) is not None:
                self.txt_out.insert(
                    tk.END, f"Raio de giração (rx): {perfil.rx:.2f} mm\n")
            if getattr(perfil, 'ry', None) is not None:
                self.txt_out.insert(
                    tk.END, f"Raio de giração (ry): {perfil.ry:.2f} mm\n")
            if getattr(perfil, 'r0', None) is not None:
                self.txt_out.insert(
                    tk.END, f"Raio de giração polar (r0): {perfil.r0:.2f} mm\n")
            
            nrd = mxrd = vrd = 0.0
            texto_resumo = ""
            if calc_comp:
                comp = CompressaoMLE(perfil, estab.chi_global)
                res_comp = comp.run_calculation()
                nrd = res_comp["final"]["n_rd"]
                self.txt_out.insert(tk.END, self._formatar_estab(memoria_estab, tipo="compressao"))
                self.txt_out.insert(
                    tk.END, "\n\n=== COMPRESSÃO ===\n" + self._formatar_compressao(res_comp) + "\n\n")
                texto_resumo += f"Resistência à Compressão (Nc,Rd): {nrd:.2f} kN\n"

            if calc_trac:
                an = float(self.trac_entries["an"].get(
                )) if self.trac_entries["an"].get() else perfil.A
                an0 = float(self.trac_entries["an0"].get(
                )) if self.trac_entries["an0"].get() else perfil.A
                ct = float(self.trac_entries["ct"].get())
                trac = CapacidadeTracao(perfil, An0=an0, An=an, Ct=ct)
                res_trac = trac.run_calculation()
                nrd = res_trac["final"]["n_rd"]
                self.txt_out.insert(
                    tk.END, "\n\n=== TRAÇÃO ===\n" + self._formatar_tracao(res_trac) + "\n\n")
                texto_resumo += f"Resistência à Tração (Nt,Rd): {nrd:.2f} kN\n"

            if calc_flex:
                flexao = FlexaoMLE(perfil, estab, cb=cb_val, mxsd=mxsd)
                res_flex = flexao.run_calculation()
                mxrd = res_flex["final"]["m_rd"]
                self.txt_out.insert(tk.END, self._formatar_estab(memoria_estab, tipo="flexao"))
                self.txt_out.insert(tk.END, "\n\n=== FLEXÃO EIXO X ===\n")
                self.txt_out.insert(
                    tk.END, self._formatar_flexao(res_flex) + "\n\n")
                texto_resumo += f"Resistência à Flexão (Mx,Rd): {mxrd:.2f} kN.cm\n"
                tensoes_dict = res_flex["grafico tensoes"]
                self.btn_grafico.config(
                    state="normal", 
                    command=lambda: self.exibir_grafico_tensoes(
                        tensoes_dict, 
                        res_flex["geometria_efetiva"]["desloc_ln"], 
                        perfil
                    )
                )
            if calc_cort:
                cortante = ResistenciaCortante(perfil)
                res_cort = cortante.run_calculation()
                vrd = res_cort["final"]["v_rd"]
                self.txt_out.insert(tk.END, "\n\n=== CORTANTE ===\n")
                self.txt_out.insert(
                    tk.END, self._formatar_cortante(res_cort) + "\n\n")
                texto_resumo += f"Resistência ao Cortante (V,Rd): {vrd:.2f} kN\n"

            if calc_comb_fc:
                res_fc = EsforcosCombinados.flexao_composta(
                    nsd, nrd, mxsd, mxrd)
                self.txt_out.insert(
                    tk.END, f"Fletor + Normal -> Relação: {res_fc['ratio']} | Status: {res_fc['mensagem']}\n")
                texto_resumo += f"Fletor + Normal -> Relação: {res_fc['ratio']:.3f} [{res_fc['mensagem']}]\n"

            if calc_comb_fv:
                res_fv = EsforcosCombinados.flexao_cortante(
                    mxsd, mxrd, vsd, vrd)
                self.txt_out.insert(
                    tk.END, f"Fletor + Cortante -> Relação: {res_fv['ratio']} | Status: {res_fv['mensagem']}\n\n")
                texto_resumo += f"Fletor + Cortante -> Relação: {res_fv['ratio']:.3f} [{res_fv['mensagem']}]\n"

            self.txt_resumo.delete(1.0, tk.END)
            self.txt_resumo.insert(tk.END, texto_resumo)

            if getattr(perfil, 'avisos', []):
                self.txt_out.insert(
                    tk.END, "=== AVISOS NORMATIVOS (GEOMETRIA E CÁLCULO) ===\n")
                for aviso in perfil.avisos:
                    self.txt_out.insert(tk.END, f"[!] {aviso}\n")
                self.txt_out.insert(tk.END, "\n")
            

        except ValueError as ve:
            messagebox.showerror("Erro de Dimensionamento", str(ve))
        except Exception as e:
            messagebox.showerror(
                "Erro Crítico", f"Verifique os dados de entrada.\nDetalhe: {str(e)}")


if __name__ == "__main__":
    root = tk.Tk()
    app = InterfacePFF(root)
    root.mainloop()
