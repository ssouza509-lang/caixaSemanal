import os
import re
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from fpdf import FPDF


class AnalisadorCaixaApp:

    def __init__(self, root):
        self.root = root
        self.root.title("Bananinha Materiais para Construção - Relatórios")
        self.root.geometry("600x550")
        self.root.configure(bg="#f4f6f9")

        self.pasta_selecionada = ""
        self.dados_consolidados = []
        self.totais_gerais = {"vendas": 0.0, "lucro": 0.0}

        self.criar_interface()

    def criar_interface(self):
        # Cabeçalho da Empresa
        header = tk.Frame(self.root, bg="#1e3d59", height=70)
        header.pack(fill="x", side="top")

        lbl_empresa = tk.Label(
            header,
            text="Bananinha Materiais para Construção",
            fg="white",
            bg="#1e3d59",
            font=("Arial", 14, "bold"),
        )
        lbl_empresa.pack(pady=5)

        lbl_titulo = tk.Label(
            header,
            text="Fechamento de Vendas & Lucro",
            fg="#ffc107",
            bg="#1e3d59",
            font=("Arial", 11, "italic"),
        )
        lbl_titulo.pack()

        # Painel de Controle
        painel_busca = tk.Frame(self.root, bg="#f4f6f9")
        painel_busca.pack(fill="x", padx=20, pady=15)

        self.btn_pasta = tk.Button(
            painel_busca,
            text="📁 Selecionar Pasta",
            command=self.selecionar_pasta,
            bg="#17b978",
            fg="white",
            font=("Arial", 10, "bold"),
            relief="flat",
            padx=10,
            pady=5,
        )
        self.btn_pasta.pack(side="left")

        self.btn_pdf = tk.Button(
            painel_busca,
            text="📄 Gerar PDF",
            command=self.gerar_pdf_relatorio,
            bg="#ff5722",
            fg="white",
            font=("Arial", 10, "bold"),
            relief="flat",
            padx=10,
            pady=5,
            state="disabled",
        )
        self.btn_pdf.pack(side="right")

        self.lbl_pasta_caminho = tk.Label(
            painel_busca,
            text="Nenhuma pasta selecionada",
            bg="#f4f6f9",
            fg="#666666",
            font=("Arial", 10, "italic"),
        )
        self.lbl_pasta_caminho.pack(side="left", padx=15)

        # Tabela Grid Simplificada (Apenas Data, Vendas e Lucro)
        painel_tabela = tk.Frame(self.root, bg="#f4f6f9")
        painel_tabela.pack(fill="both", expand=True, padx=20, pady=5)

        colunas = ("data", "vendas", "lucro")
        self.tabela = ttk.Treeview(
            painel_tabela, columns=colunas, show="headings"
        )

        config_colunas = {
            "data": ("Data", 150),
            "vendas": ("Valor de Vendas", 200),
            "lucro": ("Valor de Lucro", 200),
        }

        for col, (nome, largura) in config_colunas.items():
            self.tabela.heading(col, text=nome)
            self.tabela.column(col, width=largura, anchor="center")

        scroll = ttk.Scrollbar(
            painel_tabela, orient="vertical", command=self.tabela.yview
        )
        self.tabela.configure(yscrollcommand=scroll.set)
        self.tabela.pack(side="left", fill="both", expand=True)
        scroll.pack(side="right", fill="y")

        # Painel de Resultados Consolidados
        self.painel_totais = tk.LabelFrame(
            self.root,
            text=" Totais Acumulados do Período ",
            font=("Arial", 11, "bold"),
            bg="#ffffff",
            fg="#1e3d59",
            padx=15,
            pady=10,
        )
        self.painel_totais.pack(fill="x", padx=20, pady=20)

        self.lbl_tot_vendas = tk.Label(
            self.painel_totais,
            text="Total Vendas: R$ 0,00",
            bg="#ffffff",
            font=("Arial", 10, "bold"),
            fg="#333",
        )
        self.lbl_tot_vendas.pack(side="left", expand=True)

        self.lbl_tot_lucro = tk.Label(
            self.painel_totais,
            text="Total Lucro: R$ 0,00",
            bg="#ffffff",
            font=("Arial", 10, "bold"),
            fg="#17b978",
        )
        self.lbl_tot_lucro.pack(side="right", expand=True)

    def limpar_valor(self, texto_valor):
        if not texto_valor:
            return 0.0
        limpo = texto_valor.replace(".", "").replace(",", ".").strip()
        try:
            return float(limpo)
        except ValueError:
            return 0.0

    def formatar_brl(self, valor):
        return f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace(
            "X", "."
        )

    def extrair_dados_txt(self, caminho_arquivo):
        with open(caminho_arquivo, "r", encoding="utf-8") as f:
            conteudo = f.read()

        reg_data = re.search(r"(\d{2}/\d{2}/\d{4})", conteudo)
        reg_vendas = re.search(r"VENDAS\s*=\s*R\$\s*([\d.,]+)", conteudo)
        reg_lucro = re.search(r"LUCRO\s*=\s*R\$\s*([\d.,]+)", conteudo)

        data = reg_data.group(1) if reg_data else os.path.basename(caminho_arquivo)

        return {
            "data": data,
            "vendas": self.limpar_valor(
                reg_vendas.group(1) if reg_vendas else "0"
            ),
            "lucro": self.limpar_valor(reg_lucro.group(1) if reg_lucro else "0"),
        }

    def selecionar_pasta(self):
        pasta = filedialog.askdirectory()
        if not pasta:
            return

        self.pasta_selecionada = pasta
        self.lbl_pasta_caminho.config(
            text=os.path.basename(pasta) or pasta, fg="#333333"
        )

        for item in self.tabela.get_children():
            self.tabela.delete(item)

        self.dados_consolidados.clear()
        self.totais_gerais = {"vendas": 0.0, "lucro": 0.0}

        arquivos = [f for f in os.listdir(pasta) if f.lower().endswith(".txt")]

        if not arquivos:
            messagebox.showinfo(
                "Aviso", "Nenhum arquivo .txt foi localizado nesta pasta."
            )
            self.btn_pdf.config(state="disabled")
            return

        for arquivo in arquivos:
            caminho_completo = os.path.join(pasta, arquivo)
            try:
                dados = self.extrair_dados_txt(caminho_completo)
                self.dados_consolidados.append(dados)

                self.totais_gerais["vendas"] += dados["vendas"]
                self.totais_gerais["lucro"] += dados["lucro"]

                self.tabela.insert(
                    "",
                    "end",
                    values=(
                        dados["data"],
                        self.formatar_brl(dados["vendas"]),
                        self.formatar_brl(dados["lucro"]),
                    ),
                )
            except Exception as erro:
                print(f"Erro ao processar o arquivo {arquivo}: {erro}")

        self.lbl_tot_vendas.config(
            text=f"Total Vendas: {self.formatar_brl(self.totais_gerais['vendas'])}"
        )
        self.lbl_tot_lucro.config(
            text=f"Total Lucro: {self.formatar_brl(self.totais_gerais['lucro'])}"
        )

        if self.dados_consolidados:
            self.btn_pdf.config(state="normal")

    def gerar_pdf_relatorio(self):
        if not self.dados_consolidados:
            return

        destino_arquivo = filedialog.asksaveasfilename(
            defaultextension=".pdf",
            filetypes=[("Arquivos PDF", "*.pdf")],
            title="Salvar Relatório Semanal",
            initialfile="Relatorio_Bananinha.pdf",
        )

        if not destino_arquivo:
            return

        try:
            pdf = FPDF(orientation="P", unit="mm", format="A4")
            pdf.add_page()

            # Cabeçalho Customizado da Empresa
            pdf.set_fill_color(30, 61, 89)
            pdf.rect(0, 0, 210, 38, "F")

            pdf.set_text_color(255, 255, 255)
            pdf.set_font("Helvetica", style="B", size=16)
            pdf.cell(
                190,
                10,
                "BANANINHA MATERIAIS PARA CONSTRUÇÃO",
                ln=True,
                align="C",
            )

            pdf.set_font("Helvetica", style="I", size=11)
            pdf.cell(
                190,
                5,
                "Relatório Consolidado de Vendas e Lucro",
                ln=True,
                align="C",
            )
            pdf.ln(15)

            # Tabela de registros
            pdf.set_text_color(0, 0, 0)
            pdf.set_font("Helvetica", style="B", size=12)
            pdf.cell(190, 8, "Movimentações Diárias:", ln=True)
            pdf.ln(2)

            pdf.set_font("Helvetica", style="B", size=10)
            pdf.set_fill_color(230, 235, 240)

            # 3 Colunas: Data (50mm), Vendas (70mm), Lucro (70mm)
            larguras = [50, 70, 70]
            titulos = ["Data", "Valor de Vendas", "Valor de Lucro"]

            for idx, tit in enumerate(titulos):
                pdf.cell(larguras[idx], 8, tit, border=1, align="C", fill=True)
            pdf.ln()

            pdf.set_font("Helvetica", style="", size=10)
            for linha in self.dados_consolidados:
                pdf.cell(larguras[0], 7, str(linha["data"]), border=1, align="C")
                pdf.cell(
                    larguras[1],
                    7,
                    self.formatar_brl(linha["vendas"]),
                    border=1,
                    align="C",
                )
                pdf.cell(
                    larguras[2],
                    7,
                    self.formatar_brl(linha["lucro"]),
                    border=1,
                    align="C",
                )
                pdf.ln()

            pdf.ln(10)

            # Bloco Simplificado de Totais
            pdf.set_font("Helvetica", style="B", size=12)
            pdf.set_fill_color(245, 247, 250)
            pdf.cell(
                190,
                8,
                " Resumo Acumulado do Período",
                border=1,
                ln=True,

                fill=True, )
            pdf.set_font("Helvetica", style="", size=11)
            pdf.cell(190, 8, f" Faturamento Comercial Bruto: {self.formatar_brl(self.totais_gerais['vendas'])}",
                     border=1, ln=True, )
        pdf.set_font("Helvetica", style="B", size=11)
        pdf.cell(190, 8, f" Lucro Líquido do Período: {self.formatar_brl(self.totais_gerais['lucro'])}", border=1,
                 ln=True, )
        pdf.output(destino_arquivo)
        messagebox.showinfo("Sucesso", f"O relatório em PDF foi gerado em:\n{destino_arquivo}")
        except Exception as e: messagebox.showerror("Erro", f"Falha ao gerar o arquivo PDF:\n{str(e)}")

if name == "main": root = tk.Tk()
app = AnalisadorCaixaApp(root)
root.mainloop()