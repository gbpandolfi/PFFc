class EsforcosCombinados:
    @staticmethod
    def flexao_composta(nsd: float, nrd: float, mxsd: float, mxrd: float) -> dict:
        """Verifica a interação (Nsd/Nrd) + (Mxsd/Mxrd) <= 1.0."""
        try:
            ratio = (nsd / nrd) + (mxsd / mxrd)
            aprovado = ratio <= 1.0
        except ZeroDivisionError:
            ratio = 999.0
            aprovado = False

        return {
            "verificacao": "Flexão Composta (Tração/Compressão + Flexão Eixo X)",
            "nsd": nsd, "nrd": nrd, "mxsd": mxsd, "mxrd": mxrd,
            "ratio": round(ratio, 4),
            "aprovado": aprovado,
            "mensagem": "ATENDIDA" if aprovado else "NÃO ATENDIDA"
        }

    @staticmethod
    def flexao_cortante(mxsd: float, mxrd: float, vsd: float, vrd: float) -> dict:
        """Verifica a interação (Mxsd/Mxrd)² + (Vsd/Vrd)² <= 1.0."""
        try:
            ratio = (mxsd / mxrd)**2 + (vsd / vrd)**2
            aprovado = ratio <= 1.0
        except ZeroDivisionError:
            ratio = 999.0
            aprovado = False

        return {
            "verificacao": "Flexão e Cortante Combinados",
            "mxsd": mxsd, "mxrd": mxrd, "vsd": vsd, "vrd": vrd,
            "ratio": round(ratio, 4),
            "aprovado": aprovado,
            "mensagem": "ATENDIDA" if aprovado else "NÃO ATENDIDA"
        }
