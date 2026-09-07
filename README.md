# Renomeador de Arquivos por Ordem Numérica

Aplicativo com interface gráfica (Tkinter) para renomear todos os arquivos de uma pasta
em ordem numérica sequencial (`1.ext`, `2.ext`, `3.ext`, ...), com detecção de arquivos
duplicados por conteúdo.

## Funcionalidades

- Explorador de pastas integrado para selecionar o diretório
- Lista os arquivos encontrados com contador
- Renomeia todos os arquivos em ordem numérica sequencial, preservando a extensão
- Detecta arquivos duplicados (mesmo conteúdo, via hash MD5) e pergunta se deseja:
  - **Sobrescrever**: mantém apenas uma cópia de cada grupo duplicado
  - **Duplicar**: mantém todos os arquivos e renumera normalmente
- Renomeação em duas etapas (nomes temporários → nomes finais) para evitar conflitos

## Requisitos

- Python 3.8+ (testado com Python 3.14)
- Tkinter (já incluso na instalação padrão do Python)

## Executando a partir do código-fonte

```bash
python rename_gui.py
```

## Gerando o executável (.exe)

Instale o PyInstaller:

```bash
pip install pyinstaller
```

Gere o executável (sem console, arquivo único):

```bash
python -m PyInstaller --onefile --windowed --name RenomeadorArquivos rename_gui.py
```

O executável final ficará em `dist/RenomeadorArquivos.exe`. Basta dar duplo clique para abrir —
nenhuma janela de terminal é exibida.

As pastas `build/`, `dist/` e o arquivo `*.spec` são gerados automaticamente pelo PyInstaller
e não precisam ser versionados (já estão no `.gitignore`).
