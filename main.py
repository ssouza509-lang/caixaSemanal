import os
import re
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from fpdf import FPDF


class AnalisadorCaixaApp:

    def __init__(self, root):
        self.root = root
        self.root.title("Consolidador de Relatórios Semanais")
        self.root.geometry("520x540")
        self.root.configure(bg="#f4f6f9")

        self.arquivos_selecionados = []
        self.dados_consolidados = []
        self.totais_gerais = {"vendas": 0.0, "lucro": 0.0}

        self.criar_interface()

    def criar_interface(self):
        header = tk.Frame(self.root, bg="#1e3d59", height=60)
        header.pack(fill="x", side="top")

        lbl_titulo = tk.Label(
            header,
            text="Fechamento de Caixa Semanal",
            fg="white",
            bg="#1e3d59",
            font=("Arial", 16, "bold"),
        )
        lbl_titulo.pack(pady=15)

        painel_busca = tk.Frame(self.root, bg="#f4f6f9")
        painel_busca.pack(fill="x", padx=20, pady=15)

        self.btn_arquivos = tk.Button(
            painel_busca,
            text="📁 Selecionar Arquivos TXT",
            command=self.selecionar_arquivos,
            bg="#17b978",
            fg="white",
            font=("Arial", 10, "bold"),
            relief="flat",
            padx=10,
            pady=5,
        )
        self.btn_arquivos.pack(side="left")

        self.btn_pdf = tk.Button(
            painel_busca,
            text="📄 Exportar para PDF",
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

        self.lbl_arquivos_info = tk.Label(
            painel_busca,
            text="Nenhum arquivo selecionado",
            bg="#f4f6f9",
            fg="#666666",
            font=("Arial", 10, "italic"),
        )
        self.lbl_arquivos_info.pack(side="left", padx=15)

        painel_tabela = tk.Frame(self.root, bg="#f4f6f9")
        painel_tabela.pack(fill="both", expand=True, padx=20, pady=5)

        colunas = ("data", "vendas", "lucro")
        self.tabela = ttk.Treeview(
            painel_tabela, columns=colunas, show="headings"
        )

        config_colunas = {
            "data": ("Data", 130),
            "vendas": ("Vendas", 160),
            "lucro": ("Lucro", 160),
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

        self.painel_totais = tk.LabelFrame(
            self.root,
            text=" Resumo Consolidado do Período ",
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
        self.lbl_tot_vendas.grid(row=0, column=0, padx=20, pady=5, sticky="w")

        self.lbl_tot_lucro = tk.Label(
            self.painel_totais,
            text="Total Lucro: R$ 0,00",
            bg="#ffffff",
            font=("Arial", 10, "bold"),
            fg="#17b978",
        )
        self.lbl_tot_lucro.grid(row=0, column=1, padx=20, pady=5, sticky="w")

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

    def selecionar_arquivos(self):
        arquivos = filedialog.askopenfilenames(
            title="Selecionar arquivos de caixa",
            filetypes=[("Arquivos de texto", "*.txt"), ("Todos os arquivos", "*.*")]
        )
        if not arquivos:
            return

        self.arquivos_selecionados = list(arquivos)
        qtd = len(self.arquivos_selecionados)
        self.lbl_arquivos_info.config(
            text=f"{qtd} arquivo(s) selecionado(s)", fg="#333333"
        )

        for item in self.tabela.get_children():
            self.tabela.delete(item)

        self.dados_consolidados.clear()
        self.totais_gerais = {"vendas": 0.0, "lucro": 0.0}

        for caminho_completo in self.arquivos_selecionados:
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
                print(f"Erro ao processar o arquivo {caminho_completo}: {erro}")

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
            initialfile="Relatorio_Caixa_Semanal.pdf"
        )

        if not destino_arquivo:
            return

        try:
            pdf = FPDF(orientation="P", unit="mm", format="A4")
            pdf.add_page()
            pdf.set_margins(20, 20, 20)

            # Cabeçalho
            pdf.set_font("Helvetica", style="B", size=14)
            pdf.set_text_color(30, 61, 89)
            pdf.cell(0, 10, "Fechamento de Caixa Semanal", ln=True, align="C")
            pdf.set_draw_color(30, 61, 89)
            pdf.set_line_width(0.5)
            pdf.line(20, pdf.get_y(), 190, pdf.get_y())
            pdf.ln(6)

            # Cabeçalho da tabela
            pdf.set_font("Helvetica", style="B", size=10)
            pdf.set_fill_color(230, 235, 240)
            pdf.set_text_color(0, 0, 0)

            col_data = 60
            col_vendas = 60
            col_lucro = 50

            pdf.cell(col_data, 8, "Data", border=1, align="C", fill=True)
            pdf.cell(col_vendas, 8, "Vendas", border=1, align="C", fill=True)
            pdf.cell(col_lucro, 8, "Lucro", border=1, align="C", fill=True)
            pdf.ln()

            # Linhas de dados
            pdf.set_font("Helvetica", size=10)
            for i, linha in enumerate(self.dados_consolidados):
                fill = i % 2 == 0
                pdf.set_fill_color(248, 250, 252) if fill else pdf.set_fill_color(255, 255, 255)
                pdf.cell(col_data, 7, str(linha["data"]), border=1, align="C", fill=True)
                pdf.cell(col_vendas, 7, self.formatar_brl(linha["vendas"]), border=1, align="C", fill=True)
                pdf.cell(col_lucro, 7, self.formatar_brl(linha["lucro"]), border=1, align="C", fill=True)
                pdf.ln()

            # Linha de totais
            pdf.ln(4)
            pdf.set_font("Helvetica", style="B", size=10)
            pdf.set_fill_color(30, 61, 89)
            pdf.set_text_color(255, 255, 255)
            pdf.cell(col_data, 8, "TOTAL DA SEMANA", border=1, align="C", fill=True)
            pdf.cell(col_vendas, 8, self.formatar_brl(self.totais_gerais["vendas"]), border=1, align="C", fill=True)
            pdf.cell(col_lucro, 8, self.formatar_brl(self.totais_gerais["lucro"]), border=1, align="C", fill=True)
            pdf.ln()

            pdf.output(destino_arquivo)
            messagebox.showinfo("Sucesso", f"Relatório gerado em:\n{destino_arquivo}")

        except Exception as e:
            messagebox.showerror("Erro", f"Falha ao gerar o PDF:\n{str(e)}")


if __name__ == "__main__":
    root = tk.Tk()
    app = AnalisadorCaixaApp(root)
    root.mainloop()
