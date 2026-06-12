# PFFc | Dimensionamento de Perfis Formados a Frio

Ferramenta com interface gráfica (GUI) em Python para dimensionamento de perfis de aço formados a frio.

---

## Descrição

A ferramenta foi desenvolvida utilizando uma hierarquia de classes para representar as diferentes seções transversais e módulos independentes para encapsular as etapas de cálculo. O fluxo da verificação inicia com a definição das propriedades geométricas do perfil e continua para os demais módulos, que computam as capacidades resistentes.

**Propriedades Geométricas:** calculadas pelo Método Linear, a partir das equações propostas pela ABNT NBR 6355:2012, que representam simplificações e aproximações com desvios insignificantes para a aplicação em questão. 

**Capacidades Resistentes:** calculadas com base nas prescrições da ABNT NBR 14762:2010. Para estimar a capacidade resistente dos perfis submetidos à compressão, seja por compressão uniforme, seja por flexão, adotou-se o Método das Larguras Efetivas (MLE). Em sua versão atual, a ferramenta se limita à flexão em torno do eixo transversal ao eixo de simetria para as seções U e U enrijecido, e à flexão em torno do eixo de simetria para a seção cartola.

---

## Requisitos

- Python 3.8 ou superior
> Todos os módulos utilizam exclusivamente a biblioteca padrão do Python (tkinter e math), não sendo necessário instalar dependências externas.

---

## Estrutura do Projeto

```
.
├── main.py                  # Ponto de entrada da aplicação
├── README.md                # Descrição do repositório
├── LICENSE                  # Informações sobre a licença do projeto
├── pffc/                    # Módulos Python
└── exemplos/                # Documentação de uso e exemplos resolvidos
```

---

## Como usar

### Para utilizar a interface gráfica do PFFc:

1. No terminal do seu computador (ou Git Bash, caso use Windows), vá até a pasta onde deseja organizar e clone o repositório:

```bash
git clone https://github.com/gbpandolfi/PFFc.git
cd PFFc
```

2. Abra a pasta que contém os módulos: 

```bash
cd pffc
```

3. Execute o programa:

```bash
python pffc.py
```

4. A interface gráfica será aberta. Selecione o tipo de perfil, informe os parâmetros geométricos, os coeficientes, os esforços solicitantes e clique em "Calcular". O programa realizará o dimensionamento conforme a NBR 14762:2010.

### Para utilizar os módulos de forma independente:

- Recomenda-se a leitura do **Anexo B — Documentação de uso do PFFc**, localizado na pasta *examples*.

---

## Contribuições

Contribuições são bem-vindas! Para contribuir:

1. Faça um *fork* do projeto
2. Crie uma *branch* para sua feature (`git checkout -b feature/minha-feature`)
3. Faça o *commit* das suas alterações (`git commit -m 'Adiciona minha feature'`)
4. Faça o *push* para a *branch* (`git push origin feature/minha-feature`)
5. Abra um *Pull Request*

---

## Licença

Este projeto está licenciado sob a licença GNU General Public License v3.0 
Consulte o arquivo [LICENSE](LICENSE) para mais detalhes.

---

## Contato

Desenvolvido por **Gabriel Braga Pandolfi** durante seu Trabalho de Conclusão de Curso de Engenharia Civil pela Universidade Federal do Rio Grande do Sul (UFRGS).

📧 gb.pandolfi@hotmail.com
🔗 [linkedin.com/in/gabrielpandolfi/](https://linkedin.com)
