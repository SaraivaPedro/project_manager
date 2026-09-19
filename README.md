# Gestor de Projetos

Aplicativo desktop para organizar projetos e tarefas em seções personalizadas. Com ele, é possível acompanhar o andamento das atividades, definir prazos, receber alertas dentro do aplicativo e consultar estatísticas.

## Recursos

- Criação, renomeação, exclusão e ordenação de seções;
- Cadastro de projetos com status e prazo opcional;
- Filtros por status, prazo, tarefas atrasadas e tarefas sem prazo;
- Alertas para prazos próximos, vencendo no dia ou atrasados;
- Estatísticas gerais e por seção;
- Dados salvos localmente em um arquivo JSON.

## Tecnologias utilizadas

- Python
- [CustomTkinter](https://github.com/TomSchimansky/CustomTkinter) para a interface gráfica
- [tkcalendar](https://github.com/j4321/tkcalendar) para seleção de datas no calendário
- PyInstaller para geração do executável Windows

## Como baixar e usar

1. Abra a aba **Releases** deste repositório no GitHub.
2. Baixe o arquivo `main.exe` da versão mais recente.
3. Coloque o executável em uma pasta de sua preferência e abra-o com dois cliques.
4. O arquivo `dados.json` será criado na mesma pasta para guardar seus projetos e seções.

> Mantenha o arquivo `dados.json` junto ao executável para preservar suas informações ao atualizar o aplicativo.

## Para desenvolvedores

### Baixar o projeto

```bash
git clone https://github.com/SaraivaPedro/project_manager.git
cd project_manager
```

Também é possível usar o botão **Code > Download ZIP** no GitHub e extrair os arquivos em uma pasta local.

### Preparar o ambiente

É recomendado usar Python 3.10 ou superior.

```bash
python -m venv .venv
.venv\Scripts\activate
python -m pip install -r requirements.txt
```

### Executar o aplicativo

```bash
python main.py
```

### Gerar o executável

```bash
python -m PyInstaller --noconfirm --clean main.spec
```

O executável será criado na pasta `dist`.

## Estrutura do projeto

```text
project_manager/
├── main.py             # Interface gráfica
├── gerenciador.py      # Regras de negócio e persistência
├── dados.json          # Dados locais do aplicativo
├── requirements.txt    # Dependências Python
├── main.spec           # Configuração do executável
└── README.md
```

### Desenvlvido by Pedro Saraiva 2026