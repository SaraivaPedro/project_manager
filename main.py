import json
from datetime import datetime, timedelta

historico = {}
projetosPessoais = {}
tarefasAcademicas = {}
tarefasDomiciliares = {}

def carregar():
    global historico, projetosPessoais, tarefasAcademicas, tarefasDomiciliares
    try:
        with open("dados.json", "r", encoding="utf-8") as arquivo:
            dados = json.load(arquivo)
            projetosPessoais = dados.get("projetosPessoais", {})
            tarefasAcademicas = dados.get("tarefasAcademicas", {})
            tarefasDomiciliares = dados.get("tarefasDomiciliares", {})
            historico = dados.get("historico", {})
    except (FileNotFoundError, json.JSONDecodeError):
        persistencia()

def persistencia():
    with open("dados.json", "w", encoding="utf-8") as dados:
        json.dump(
            {
                "projetosPessoais": projetosPessoais,
                "tarefasAcademicas": tarefasAcademicas,
                "tarefasDomiciliares": tarefasDomiciliares,
                "historico": historico
            },
            dados,
            indent=4,
            ensure_ascii=False
        )

def listar(lista_projetos, historico):
    result = []
    if lista_projetos == {}:
        return "Parece que não há nenhum projeto nessa seção no momento."
    else:
        for nome_projeto, status in lista_projetos.items():
            hist = ', -> '.join(item["status"] for item in historico.get(nome_projeto, []))
            result.append(f"{nome_projeto}: {status}, histórico: -> {hist.upper()} ->")
        return '\n'.join(result)

def encontrar_projeto(lista_projetos, nome_projeto):
    if nome_projeto in lista_projetos:
        return lista_projetos[nome_projeto]
    else:
        return None
    
def buscar(nome_secao, nome_projeto, lista_projetos):
    nome_projeto = input(f"Digite o nome do projeto a ser buscado em {nome_secao}: ").upper()
    if nome_projeto in lista_projetos:
        print(f"Projeto: {nome_projeto} - Status: {lista_projetos[nome_projeto]}")
    else:
        print("Projeto não encontrado.")

def estatisticas(lista_projetos, historico):
    pendentes = []
    em_andamento = []
    concluidos = []
    total_projetos = len(lista_projetos)
    print(f"Total de projetos: {total_projetos}")
    for projeto, status in lista_projetos.items():
        if status == "PENDENTE":
            pendentes.append(projeto)
        elif status == "EM ANDAMENTO":
            em_andamento.append(projeto)
        elif status == "CONCLUÍDO":
            concluidos.append(projeto)
    print("Projetos pendentes:", ", ".join(pendentes) if pendentes else "Nenhum projeto pendente no momento.")
    print("Projetos em andamento:", ", ".join(em_andamento) if em_andamento else "Nenhum projeto em andamento no momento.")
    print("Projetos concluídos:", ", ".join(concluidos) if concluidos else "Nenhum projeto concluído no momento.")
    finalizados_semana = []
    finalizados_mes = []
    agora = datetime.now()
    semana_passada = agora - timedelta(days = 7)
    mes_passado = agora - timedelta(days = 30)
    for projeto, eventos in historico.items():
        for evento in eventos:
            data = datetime.fromisoformat(evento["data"])
            if evento["status"] == "CONCLUÍDO": 
                if data >= semana_passada:
                    finalizados_semana.append(projeto)
            if evento["status"] == "CONCLUÍDO":
                if data >= mes_passado:
                    finalizados_mes.append(projeto)
    print("Projetos conlcuídos nos últimos sete dias:", ", ".join(finalizados_semana) if finalizados_semana else "Nenhum projeto concluído nos últimos sete dias.")
    print("Projetos finalizados nos últimos trinta dias:", ", ".join(finalizados_mes) if finalizados_mes else "Nenhum projeto concluído nos últimos trinta dias.")
    ultimo_projeto = None
    ultima_data = None
    for projeto, eventos in historico.items():
        for evento in eventos:
            if evento["status"] == "CONCLUÍDO":
                data = datetime.fromisoformat(evento["data"])
                if ultima_data is None or data > ultima_data:
                    ultima_data = data
                    ultimo_projeto = projeto
    if ultimo_projeto:
        print(f"Último projeto: {ultimo_projeto}, concluído em {ultima_data.day}:{ultima_data.month}:{ultima_data.year} às {ultima_data.hour}:{ultima_data.minute}h")
    else:
        print("Nenhum projeto concluído até o momento")

def limpar(nome_secao, lista_projetos, historico):
    clear = input(f"Tem certeza que deseja limpar a {nome_secao}? S/N: ")
    if clear.upper() == "S":
        lista_projetos.clear()
        historico.clear()
        print(f"Lista de {nome_secao} apagada.")
    elif clear.upper() == "N":
        print("Operação cancelada.")
    else:
        print("Resposta inválida. Cancelando operação.")

def remover(nome_secao, lista_projetos, historico):
    nome_tarefa = input(f"Digite o nome do projeto a ser removido de {nome_secao}: ").upper()
    if nome_tarefa not in lista_projetos:
        print("Projeto não encontrado.")
    elif lista_projetos == {}:
        print("A lista de projetos está vazia.")
    else:
        lista_projetos.pop(nome_tarefa)
        historico.pop(nome_tarefa, None)
        print(f"Projeto {nome_tarefa} removido de {nome_secao} com sucesso.")    

def atualizar(lista_projetos, historico):
    nome_projeto = input("Digite o nome do projeto que deseja atualizar: ").upper()
    if (encontrar_projeto(lista_projetos, nome_projeto) is None):
        print("Erro: projeto não encontrado. Tente novamente.")
    else:
        novo_status = input("Digite o novo status entre 'Em andamento', 'Pendente' ou 'Concluído': ").upper()
        if novo_status not in ("EM ANDAMENTO", "PENDENTE", "CONCLUÍDO"):
            print("Status inválido. Tente novamente.")
        else:
            lista_projetos[nome_projeto] = novo_status
            historico[nome_projeto].append({
                "status": novo_status,
                "data": datetime.now().isoformat() 
            })
            print(f"Projeto {nome_projeto} atualizado com sucesso. Novo status: {novo_status.upper()}.")

def sobre(nome_secao):
    print(f"Software gestor de {nome_secao} desenvolvido by Pedro Saraiva")
    print(f"Aqui você poderá gerenciar seus {nome_secao}.")
    print("Através de comandos como ADD para adicionar, UPDATE para atualizar, REMOVE para remover, etc.")

def adicionar(nome_secao, status, lista_projetos):
    try:
        numero_projetos = int(input(f"Quantos projetos deseja adicionar em {nome_secao}? "))
        if numero_projetos <= 0:
            print("Número inválido. Tente novamente.")
        elif numero_projetos >10:
            print("Por favor, adicione até 10 projetos por vez.")
        else:
            for i in range(numero_projetos):
                nome_projeto = input(f"Digite o nome do projeto {i+1}: ").upper()
                status = input(f"Digite o status do projeto {i+1} entre 'Em andamento' ou 'Pendente'. Não é possível adicionar projetos já concluídos: ").upper()
                status = status.replace("Í", "I")
                if status not in ["EM ANDAMENTO", "PENDENTE"]:
                    print("Status inválido. Tente novamente.")
                else:
                    lista_projetos[nome_projeto] = status
                    historico[nome_projeto] = [{
                        "status": status,
                        "data": datetime.now().isoformat()
                    }]
    except ValueError:
        print("Erro: entrada inválida, por favor insira um número inteiro.")

def sair():
    persistencia()

def opcao():
    while True:
        print("Gostaria de gerenciar quais projetos hoje?")
        opcao = input("Projetos pessoais, tarefas acadêmicas ou tarefas domiciliares? Digite QUIT se deseja encerrar o programa. ")
        if opcao.upper() == "PROJETOS PESSOAIS":
            opcao_selecionada("projetos pessoais", projetosPessoais, historico)
        elif opcao.upper() == "TAREFAS ACADÊMICAS":
            opcao_selecionada("tarefas acadêmicas", tarefasAcademicas, historico)
        elif opcao.upper() == "TAREFAS DOMICILIARES":
            opcao_selecionada("tarefas domiciliares", tarefasDomiciliares, historico)
        elif opcao.upper() == "QUIT":
            sair()
            print("Dados salvos. Até logo!")
            break
        else:
            print("Erro: Opção não reconhecida. Tente novamente.")

def opcao_selecionada(nome_secao, lista_projetos, historico):
    print("\n")
    print(f"Gestor de {nome_secao} selecionado.")
    while True:
        comando = input("Digite um comando: ABOUT, ADD, LIST, SEARCH, UPDATE, STATS, CLEAR, REMOVE, RETURN: ")
        if comando.upper() == "ABOUT":
            sobre(nome_secao)
        elif comando.upper() == "ADD":
            adicionar(nome_secao, historico, lista_projetos)
            persistencia()
        elif comando.upper() == "LIST":
            print(listar(lista_projetos, historico))
        elif comando.upper() == "SEARCH":
            buscar(nome_secao, lista_projetos, historico)
        elif comando.upper() == "UPDATE":
            atualizar(lista_projetos, historico)
            persistencia()
        elif comando.upper() == "STATS":
            estatisticas(lista_projetos, historico)
            persistencia()
        elif comando.upper() == "CLEAR":
            limpar(nome_secao, lista_projetos, historico)
            persistencia()
        elif comando.upper() == "REMOVE":
            remover(nome_secao, lista_projetos, historico)
            persistencia()
        elif comando.upper() == "RETURN":
            print("\n")
            sair()
            break
        else:
            print("Comando não reconhecido. Tente novamente.")

carregar()
        
print("Gestor de projetos by Pedro Saraiva.")
opcao()