import hashlib
import os
import re
import tkinter as tk
from tkinter import filedialog, messagebox, ttk


def natural_key(name: str):
    return [int(t) if t.isdigit() else t.lower() for t in re.split(r"(\d+)", name)]


def file_hash(path: str, block_size: int = 65536) -> str:
    h = hashlib.md5()
    with open(path, "rb") as f:
        for block in iter(lambda: f.read(block_size), b""):
            h.update(block)
    return h.hexdigest()


class RenameApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Renomeador de Arquivos por Ordem Numérica")
        self.geometry("640x480")
        self.minsize(560, 420)

        self.folder_path = tk.StringVar()
        self.status_var = tk.StringVar(value="Selecione uma pasta para começar.")
        self.count_var = tk.StringVar(value="Arquivos encontrados: 0")

        self._build_ui()

    def _build_ui(self):
        top = ttk.Frame(self, padding=10)
        top.pack(fill="x")

        ttk.Label(top, text="Pasta:").pack(side="left")
        entry = ttk.Entry(top, textvariable=self.folder_path)
        entry.pack(side="left", fill="x", expand=True, padx=6)
        ttk.Button(top, text="Procurar...", command=self.browse_folder).pack(side="left")

        mid = ttk.Frame(self, padding=(10, 0))
        mid.pack(fill="both", expand=True)

        ttk.Label(mid, textvariable=self.count_var).pack(anchor="w")

        list_frame = ttk.Frame(mid)
        list_frame.pack(fill="both", expand=True, pady=6)

        scrollbar = ttk.Scrollbar(list_frame, orient="vertical")
        self.listbox = tk.Listbox(list_frame, yscrollcommand=scrollbar.set)
        scrollbar.config(command=self.listbox.yview)
        self.listbox.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        bottom = ttk.Frame(self, padding=10)
        bottom.pack(fill="x")

        ttk.Button(bottom, text="Atualizar Lista", command=self.refresh_list).pack(side="left")
        ttk.Button(bottom, text="Renomear em Ordem Numérica", command=self.rename_files).pack(
            side="left", padx=6
        )

        status = ttk.Label(self, textvariable=self.status_var, relief="sunken", anchor="w", padding=4)
        status.pack(fill="x", side="bottom")

    def browse_folder(self):
        path = filedialog.askdirectory(title="Selecione a pasta com os arquivos")
        if path:
            self.folder_path.set(path)
            self.refresh_list()

    def get_files(self):
        folder = self.folder_path.get()
        if not folder or not os.path.isdir(folder):
            return []
        entries = [
            f for f in os.listdir(folder)
            if os.path.isfile(os.path.join(folder, f))
        ]
        entries.sort(key=natural_key)
        return entries

    def refresh_list(self):
        folder = self.folder_path.get()
        if not folder or not os.path.isdir(folder):
            messagebox.showwarning("Pasta inválida", "Selecione uma pasta válida primeiro.")
            return

        files = self.get_files()
        self.listbox.delete(0, tk.END)
        for f in files:
            self.listbox.insert(tk.END, f)
        self.count_var.set(f"Arquivos encontrados: {len(files)}")
        self.status_var.set("Lista atualizada.")

    def find_duplicates(self, folder, files):
        hashes = {}
        groups = {}
        for f in files:
            full = os.path.join(folder, f)
            try:
                h = file_hash(full)
            except OSError:
                continue
            hashes.setdefault(h, []).append(f)
        for h, names in hashes.items():
            if len(names) > 1:
                groups[h] = names
        return groups

    def rename_files(self):
        folder = self.folder_path.get()
        if not folder or not os.path.isdir(folder):
            messagebox.showwarning("Pasta inválida", "Selecione uma pasta válida primeiro.")
            return

        files = self.get_files()
        if not files:
            messagebox.showinfo("Nada a fazer", "Nenhum arquivo encontrado nesta pasta.")
            return

        duplicate_groups = self.find_duplicates(folder, files)
        skip_set = set()

        if duplicate_groups:
            details = "\n".join(
                f"- {', '.join(names)}" for names in duplicate_groups.values()
            )
            message = (
                "Foram encontrados arquivos duplicados (conteúdo idêntico):\n\n"
                f"{details}\n\n"
                "Deseja SOBRESCREVER (manter apenas o primeiro de cada grupo e remover "
                "as cópias) ou DUPLICAR (manter todos os arquivos e renomear normalmente)?\n\n"
                "Sim = Sobrescrever | Não = Duplicar | Cancelar = Abortar"
            )
            choice = messagebox.askyesnocancel("Arquivos duplicados detectados", message)
            if choice is None:
                self.status_var.set("Operação cancelada pelo usuário.")
                return
            if choice is True:
                for names in duplicate_groups.values():
                    for extra in names[1:]:
                        skip_set.add(extra)

        final_files = [f for f in files if f not in skip_set]
        if not final_files:
            messagebox.showinfo("Nada a fazer", "Nenhum arquivo restante para renomear.")
            return

        if skip_set:
            for name in skip_set:
                try:
                    os.remove(os.path.join(folder, name))
                except OSError as e:
                    messagebox.showerror("Erro ao remover", f"Falha ao remover {name}: {e}")
                    return

        try:
            temp_names = []
            for i, name in enumerate(final_files):
                ext = os.path.splitext(name)[1]
                temp_name = f"__tmp_rename_{i}__{ext}"
                os.rename(os.path.join(folder, name), os.path.join(folder, temp_name))
                temp_names.append((temp_name, ext))

            for i, (temp_name, ext) in enumerate(temp_names, start=1):
                final_name = f"{i}{ext}"
                os.rename(os.path.join(folder, temp_name), os.path.join(folder, final_name))
        except OSError as e:
            messagebox.showerror("Erro ao renomear", str(e))
            self.status_var.set("Erro durante a renomeação.")
            return

        self.status_var.set(f"{len(final_files)} arquivo(s) renomeado(s) com sucesso.")
        messagebox.showinfo("Concluído", f"{len(final_files)} arquivo(s) renomeado(s) com sucesso.")
        self.refresh_list()


if __name__ == "__main__":
    app = RenameApp()
    app.mainloop()
