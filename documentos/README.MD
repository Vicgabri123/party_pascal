# 🎮 Party Pascal — A Jornada da Governança de TI

**Party Pascal** é um jogo educativo desenvolvido para ensinar conceitos fundamentais de Governança de TI, COBIT e ITIL de forma interativa e divertida. Através de uma série de minigames desafiadores, o jogador assume o papel de um Guardião da Governança, guiado pelo mascote Pascal.

---

## 🚀 Sobre o Projeto

O jogo combina elementos de **Visual Novel** com **Arcade**, testando conhecimentos teóricos e tomadas de decisão rápida.

### 🕹️ Minigames Incluídos:
* **Show do Bilhão (COBIT Edition):** Teste seus conhecimentos teóricos.
* **Batalha Naval:** Encontre as ameaças à infraestrutura.
* **Maleta Certa:** Tome as decisões estratégicas corretas.
* **Roleta de Risco:** Gerencie incidentes e eventos aleatórios.
* **Perseguição:** Agilidade para capturar boas práticas.
* **STOP:** Vocabulário rápido de governança.

---

## 🛠️ Tecnologias Utilizadas

* **Linguagem:** Python 3.11+
* **Engine Gráfica:** Pygame (SDL)
* **Estrutura:** Modular (MVC-like), com gerenciamento de estados, áudio e dificuldade dinâmica.

---

## ⚙️ Instalação e Como Jogar

Siga os passos abaixo para rodar o jogo em sua máquina (Windows/Linux/Mac).

### 1️⃣ Pré-requisitos
Certifique-se de ter instalado:
* **Python 3.11 ou superior** ([Baixar aqui](https://www.python.org/downloads/))
* **VS Code** (Recomendado para edição/execução)

### 2️⃣ Configuração do Ambiente

1.  Baixe ou clone este repositório.
2.  Abra a **pasta raiz do projeto** no VS Code (a pasta que contém o arquivo `main.py`).
3.  Abra o terminal do VS Code e verifique a versão do Python:
    ```bash
    python --version
    ```

### 3️⃣ Instalando Dependências

Execute o comando abaixo para instalar as bibliotecas necessárias:

```bash
pip install -r requirements.txt
pip install pygame

Solução de problemas: Se o comando pip não for reconhecido, tente reparar a instalação do Python
python -m ensurepip --upgrade

Para Desenvolvedores (Manutenção)

Caso você adicione novas bibliotecas ao projeto e precise criar ou atualizar o arquivo requirements.txt para que outros consigam instalar tudo automaticamente, use o comando:

pip freeze > requirements.txt

▶️ Executando o Jogo

Para iniciar a aventura, certifique-se de estar na pasta do projeto e execute no terminal:
python main.py

🏆 Créditos e Equipe de Desenvolvimento

Este projeto foi idealizado e desenvolvido com dedicação pela seguinte equipe:

Cleidison Raimundo dos Santos Lima: UI/UX Design e Identidade Visual.

Marcelo Felipe Beckman: Idealização, Roteiro e Game Design.

Victor Gabriel Cabral da Silva: Desenvolvimento e Plataformas.

Marcos França Gino Gonçalves: Trilha Sonora, Efeitos Sonoros e Áudio.

Fernando Luiz Jales Da Rocha: Suporte Técnico e Operacional.

                      © 2025 Party Pascal Team. Desenvolvido para fins educacionais.