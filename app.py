import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
import os
import csv
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

import logging

logging.basicConfig(level=logging.DEBUG, filename="log.txt")
logging.info("Script iniciado")

# Funções de manipulação de dados
def carregar_gastos():
    if not os.path.exists("gastos.txt"):
        return []
    gastos = []
    with open("gastos.txt", "r") as f:
        reader = csv.reader(f)
        for linha in reader:
            if len(linha) == 6:
                descricao, valor, data, modificado, situacao, data_pagamento = linha
                try:
                    valor = float(valor)
                    gastos.append((descricao, valor, data, modificado, situacao, data_pagamento))
                except ValueError:
                    continue
    return gastos

def salvar_gastos():
    with open("gastos.txt", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerows(gastos)

def adicionar_gasto():
    descricao = entry_descricao.get().upper()
    try:
        valor = float(entry_valor.get())
    except ValueError:
        messagebox.showerror("Erro", "Valor inválido. Digite um número.")
        return

    data = entry_data.get()
    modificado = datetime.now().strftime("%d-%m-%Y")
    situacao = "Não Pago"
    data_pagamento = ""

    if descricao and valor > 0 and validar_data(data):
        gastos.append((descricao, valor, data, modificado, situacao, data_pagamento))
        salvar_gastos()
        atualizar_tabela()
        atualizar_total()
        atualizar_grafico()
        limpar_campos()
    else:
        messagebox.showerror("Erro", "Dados inválidos ou incompletos.")

def limpar_campos():
    entry_descricao.delete(0, tk.END)
    entry_valor.delete(0, tk.END)
    entry_data.delete(0, tk.END)

def validar_data(data):
    try:
        datetime.strptime(data, "%d-%m-%Y")
        return True
    except ValueError:
        messagebox.showerror("Erro", "Data inválida. Use o formato DD-MM-YYYY.")
        return False

def editar_gasto():
    try:
        item_selecionado = tree.selection()[0]
        valores = tree.item(item_selecionado, "values")

        entry_descricao.delete(0, tk.END)
        entry_descricao.insert(0, valores[0])

        entry_valor.delete(0, tk.END)
        entry_valor.insert(0, valores[1].replace("R$", "").strip())

        entry_data.delete(0, tk.END)
        entry_data.insert(0, valores[2])

        # Localiza o índice do gasto selecionado para editar
        for i, gasto in enumerate(gastos):
            if gasto[0] == valores[0] and gasto[2] == valores[2]:
                gastos.pop(i)  # Remove o gasto antigo
                break
        salvar_gastos()
        atualizar_tabela()
    except IndexError:
        messagebox.showerror("Erro", "Selecione um gasto para editar.")

def marcar_como_pago(event):
    try:
        item_selecionado = tree.selection()[0]
        valores = tree.item(item_selecionado, "values")
        situacao_atual = valores[4]

        resposta = messagebox.askquestion(
            "Confirmar",
            f"Marcar como {'Não Pago' if situacao_atual == 'Pago' else 'Pago'}?"
        )
        if resposta == "yes":
            for i, gasto in enumerate(gastos):
                if gasto[0] == valores[0] and gasto[2] == valores[2]:
                    nova_situacao = "Pago" if situacao_atual == "Não Pago" else "Não Pago"
                    nova_data_pagamento = datetime.now().strftime("%d-%m-%Y") if nova_situacao == "Pago" else ""
                    gastos[i] = (*gasto[:4], nova_situacao, nova_data_pagamento)
                    salvar_gastos()
                    atualizar_tabela()
                    atualizar_total()
                    break
    except IndexError:
        messagebox.showerror("Erro", "Selecione uma linha para marcar como Pago/Não Pago.")

def atualizar_tabela():
    for item in tree.get_children():
        tree.delete(item)

    mes_selecionado = combobox_mes.get()  # Pega o mês selecionado

    for descricao, valor, data, modificado, situacao, data_pagamento in gastos:
        if mes_selecionado == "Todos os Meses" or int(data.split("-")[1]) == int(mes_selecionado):
            tree.insert("", "end", values=(descricao, f"R${valor:.2f}", data, modificado, situacao, data_pagamento))

def atualizar_total():
    total_pago = sum(g[1] for g in gastos if g[4] == "Pago")
    total_nao_pago = sum(g[1] for g in gastos if g[4] == "Não Pago")
    label_total_pago.config(text=f"Total Pago: R${total_pago:.2f}")
    label_total_nao_pago.config(text=f"Total Não Pago: R${total_nao_pago:.2f}")

def atualizar_grafico():
    valores_por_mes = [0] * 12

    for _, valor, data, _, _, _ in gastos:
        mes = int(data.split("-")[1])
        valores_por_mes[mes - 1] += valor

    fig.clear()
    ax = fig.add_subplot(111)
    ax.bar(range(1, 13), valores_por_mes, color="skyblue")
    ax.set_title("Gastos Mensais")
    ax.set_xlabel("Mês")
    ax.set_ylabel("Total (R$)")
    ax.set_xticks(range(1, 13))

    canvas_grafico.draw()

# Interface gráfica
root = tk.Tk()
root.title("Gerenciador de Gastos")
root.geometry("1200x800")

gastos = carregar_gastos()

# Layout - Parte Superior
frame_top = tk.Frame(root)
frame_top.pack(fill=tk.X, padx=10, pady=10)

frame_inputs = tk.Frame(frame_top)
frame_inputs.pack(side=tk.LEFT, padx=10, pady=10)

label_descricao = ttk.Label(frame_inputs, text="Descrição:")
label_descricao.grid(row=0, column=0, padx=5, pady=5, sticky="w")

entry_descricao = ttk.Entry(frame_inputs)
entry_descricao.grid(row=0, column=1, padx=5, pady=5)

label_valor = ttk.Label(frame_inputs, text="Valor:")
label_valor.grid(row=1, column=0, padx=5, pady=5, sticky="w")

entry_valor = ttk.Entry(frame_inputs)
entry_valor.grid(row=1, column=1, padx=5, pady=5)

label_data = ttk.Label(frame_inputs, text="Data (DD-MM-YYYY):")
label_data.grid(row=2, column=0, padx=5, pady=5, sticky="w")

entry_data = ttk.Entry(frame_inputs)
entry_data.grid(row=2, column=1, padx=5, pady=5)

button_adicionar = ttk.Button(frame_inputs, text="Adicionar Gasto", command=adicionar_gasto)
button_adicionar.grid(row=3, column=0, columnspan=2, pady=5)

button_limpar = ttk.Button(frame_inputs, text="Limpar Campos", command=limpar_campos)
button_limpar.grid(row=4, column=0, columnspan=2, pady=5)

button_editar = ttk.Button(frame_inputs, text="Editar Gasto", command=editar_gasto)
button_editar.grid(row=5, column=0, columnspan=2, pady=5)

# Combobox para selecionar o mês
label_mes = ttk.Label(frame_inputs, text="Selecione o Mês:")
label_mes.grid(row=7, column=0, padx=5, pady=5, sticky="w")

meses = ["Todos os Meses"] + [str(i) for i in range(1, 13)]
combobox_mes = ttk.Combobox(frame_inputs, values=meses, state="readonly")
combobox_mes.set("Todos os Meses")
combobox_mes.grid(row=7, column=1, padx=5, pady=5)
combobox_mes.bind("<<ComboboxSelected>>", lambda _: atualizar_tabela())

# Layout - Parte Inferior
frame_bottom = tk.Frame(root)
frame_bottom.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

colunas = ("Descrição", "Valor", "Data", "Modificado", "Situação", "Data de Pagamento")
tree = ttk.Treeview(frame_bottom, columns=colunas, show="headings", height=10)
tree.heading("Descrição", text="Descrição")
tree.heading("Valor", text="Valor")
tree.heading("Data", text="Data")
tree.heading("Modificado", text="Modificado")
tree.heading("Situação", text="Situação")
tree.heading("Data de Pagamento", text="Data de Pagamento")
tree.pack(fill=tk.BOTH, expand=True)

tree.bind("<Double-1>", marcar_como_pago)

# Totalizadores
label_total_pago = ttk.Label(root, text="Total Pago: R$0.00", font=("Arial", 12))
label_total_pago.pack()

label_total_nao_pago = ttk.Label(root, text="Total Não Pago: R$0.00", font=("Arial", 12))
label_total_nao_pago.pack()

# Gráfico de barras
fig = plt.Figure(figsize=(6, 3), dpi=100)
canvas_grafico = FigureCanvasTkAgg(fig, master=frame_top)
canvas_grafico.get_tk_widget().pack(side=tk.RIGHT, padx=10, pady=10)

# Inicializações
atualizar_tabela()
atualizar_total()
atualizar_grafico()

root.mainloop()
