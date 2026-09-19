import customtkinter as ctk
from datetime import datetime

from tkcalendar import Calendar

from gerenciador import GerenciadorProjetos, STATUS_VALIDOS


class Confirmacao(ctk.CTkToplevel):
    def __init__(self, mestre, titulo: str, mensagem: str, acao: str):
        super().__init__(mestre)
        self.confirmado = False
        self.title(titulo)
        self.geometry("440x210")
        self.resizable(False, False)
        self.transient(mestre)
        self.grab_set()
        ctk.CTkLabel(self, text=titulo, font=ctk.CTkFont(size=19, weight="bold")).pack(padx=25, pady=(28, 8))
        ctk.CTkLabel(self, text=mensagem, wraplength=370, justify="center").pack(padx=25, pady=(0, 22))
        botoes = ctk.CTkFrame(self, fg_color="transparent")
        botoes.pack(pady=4)
        ctk.CTkButton(botoes, text="Não", width=130, command=self.destroy).pack(side="left", padx=6)
        ctk.CTkButton(
            botoes, text=acao, width=130, fg_color="#B42318", hover_color="#8E1B12", command=self._confirmar
        ).pack(side="left", padx=6)

    def _confirmar(self) -> None:
        self.confirmado = True
        self.destroy()


class SeletorCalendario(ctk.CTkToplevel):
    def __init__(self, mestre, titulo: str, permitir_remover: bool = False):
        super().__init__(mestre)
        self.data_selecionada = None
        self.title(titulo)
        self.geometry("340x410")
        self.resizable(False, False)
        self.transient(mestre)
        self.grab_set()
        ctk.CTkLabel(self, text=titulo, font=ctk.CTkFont(size=19, weight="bold")).pack(pady=(20, 10))
        self.calendario = Calendar(self, selectmode="day", mindate=datetime.now().date(), date_pattern="dd/MM/y")
        self.calendario.pack(padx=20, pady=4)
        if permitir_remover:
            ctk.CTkButton(self, text="Remover prazo", fg_color="#7A5D00", hover_color="#5D4600", command=self.remover).pack(
                fill="x", padx=30, pady=(12, 0)
            )
        ctk.CTkButton(self, text="Selecionar data", command=self.selecionar).pack(fill="x", padx=30, pady=(14, 20))

    def selecionar(self) -> None:
        self.data_selecionada = self.calendario.selection_get().strftime("%d/%m/%Y")
        self.destroy()

    def remover(self) -> None:
        self.data_selecionada = ""
        self.destroy()


class FormularioProjeto(ctk.CTkToplevel):
    def __init__(self, app):
        super().__init__(app)
        self.app = app
        self.title("Adicionar projeto")
        self.geometry("410x365")
        self.resizable(False, False)
        self.transient(app)
        self.grab_set()
        ctk.CTkLabel(self, text="Novo projeto", font=ctk.CTkFont(size=22, weight="bold")).pack(
            anchor="w", padx=28, pady=(26, 16)
        )
        self.nome = ctk.CTkEntry(self, placeholder_text="Nome do projeto")
        self.nome.pack(fill="x", padx=28, pady=6)
        self.status = ctk.CTkOptionMenu(self, values=["PENDENTE", "EM ANDAMENTO"])
        self.status.pack(fill="x", padx=28, pady=8)
        self.prazo = None
        self.texto_prazo = ctk.StringVar(value="Prazo: não definido")
        ctk.CTkLabel(self, textvariable=self.texto_prazo, anchor="w").pack(fill="x", padx=28, pady=(3, 0))
        ctk.CTkButton(self, text="Escolher prazo no calendário", command=self.escolher_prazo).pack(
            fill="x", padx=28, pady=6
        )
        ctk.CTkButton(self, text="Adicionar", command=self.salvar).pack(fill="x", padx=28, pady=(10, 22))
        self.nome.focus()

    def salvar(self) -> None:
        try:
            self.app.gerenciador.adicionar(
                self.app.secao_atual, self.nome.get(), self.status.get(), self.prazo
            )
        except ValueError as erro:
            self.app.mostrar_erro(str(erro))
            return
        self.app.atualizar_painel()
        self.destroy()

    def escolher_prazo(self) -> None:
        calendario = SeletorCalendario(self, "Escolher prazo")
        self.wait_window(calendario)
        if calendario.data_selecionada:
            self.prazo = calendario.data_selecionada
            self.texto_prazo.set(f"Prazo: {self.prazo}")


class GerenciarSecoes(ctk.CTkToplevel):
    def __init__(self, app):
        super().__init__(app)
        self.app = app
        self.title("Gerenciar seções")
        self.geometry("630x520")
        self.minsize(550, 400)
        self.transient(app)
        cabecalho = ctk.CTkFrame(self, fg_color="transparent")
        cabecalho.pack(fill="x", padx=24, pady=(24, 14))
        ctk.CTkLabel(cabecalho, text="Gerenciar seções", font=ctk.CTkFont(size=24, weight="bold")).pack(side="left")
        ctk.CTkButton(cabecalho, text="+ Nova seção", command=self.criar_secao).pack(side="right")
        ctk.CTkLabel(
            self, text="Use as setas para organizar a barra lateral.", text_color=("gray45", "gray70")
        ).pack(anchor="w", padx=24, pady=(0, 12))
        self.lista = ctk.CTkScrollableFrame(self)
        self.lista.pack(fill="both", expand=True, padx=24, pady=(0, 24))
        self.atualizar_lista()

    def atualizar_lista(self) -> None:
        for item in self.lista.winfo_children():
            item.destroy()
        secoes = self.app.gerenciador.listar_secoes()
        for indice, secao in enumerate(secoes):
            linha = ctk.CTkFrame(self.lista)
            linha.pack(fill="x", pady=5)
            ctk.CTkLabel(linha, text=secao["nome"], anchor="w", font=ctk.CTkFont(size=15)).pack(
                side="left", fill="x", expand=True, padx=(14, 8), pady=10
            )
            ctk.CTkButton(linha, text="↑", width=34, state="disabled" if indice == 0 else "normal",
                          command=lambda codigo=secao["id"]: self.mover(codigo, -1)).pack(side="left", padx=2, pady=7)
            ctk.CTkButton(linha, text="↓", width=34, state="disabled" if indice == len(secoes) - 1 else "normal",
                          command=lambda codigo=secao["id"]: self.mover(codigo, 1)).pack(side="left", padx=2, pady=7)
            ctk.CTkButton(linha, text="Renomear", width=86, command=lambda item=secao: self.renomear(item)).pack(
                side="left", padx=(5, 2), pady=7
            )
            ctk.CTkButton(linha, text="Apagar", width=70, fg_color="#B42318", hover_color="#8E1B12",
                          command=lambda item=secao: self.apagar(item)).pack(side="left", padx=(2, 8), pady=7)

    def criar_secao(self) -> None:
        nome = ctk.CTkInputDialog(text="Qual será o nome da nova seção?", title="Nova seção").get_input()
        if not nome:
            return
        try:
            identificador = self.app.gerenciador.criar_secao(nome)
        except ValueError as erro:
            self.app.mostrar_erro(str(erro))
            return
        self.app.secao_atual = identificador
        self.app.atualizar_painel()
        self.atualizar_lista()

    def renomear(self, secao: dict) -> None:
        nome = ctk.CTkInputDialog(text="Novo nome para a seção:", title="Renomear seção").get_input()
        if not nome:
            return
        try:
            self.app.gerenciador.renomear_secao(secao["id"], nome)
        except ValueError as erro:
            self.app.mostrar_erro(str(erro))
            return
        self.app.atualizar_painel()
        self.atualizar_lista()

    def mover(self, secao: str, direcao: int) -> None:
        self.app.gerenciador.mover_secao(secao, direcao)
        self.app.renderizar_barra_lateral()
        self.atualizar_lista()

    def apagar(self, secao: dict) -> None:
        mensagem = f'Tem certeza que deseja apagar "{secao["nome"]}"?\nOs projetos e históricos desta seção serão apagados.'
        if not self.app.confirmar("Apagar seção", mensagem, "Sim, apagar"):
            return
        try:
            self.app.gerenciador.remover_secao(secao["id"])
        except ValueError as erro:
            self.app.mostrar_erro(str(erro))
            return
        if self.app.secao_atual == secao["id"]:
            self.app.secao_atual = self.app.gerenciador.listar_secoes()[0]["id"]
        self.app.atualizar_painel()
        self.atualizar_lista()


class GestorApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.gerenciador = GerenciadorProjetos()
        self.secao_atual = self.gerenciador.listar_secoes()[0]["id"]
        self.busca = ctk.StringVar()
        self.filtro_status = None
        self.filtro_prazo = None
        self.modo_visualizacao = "projetos"
        self.busca.trace_add("write", lambda *_: self.renderizar_projetos())
        self.title("Gestor de Projetos")
        self.geometry("1080x690")
        self.minsize(880, 570)
        ctk.set_appearance_mode("system")
        ctk.set_default_color_theme("blue")
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.barra_lateral = ctk.CTkFrame(self, width=230, corner_radius=0)
        self.barra_lateral.grid(row=0, column=0, sticky="nsew")
        self.barra_lateral.grid_propagate(False)
        ctk.CTkLabel(self.barra_lateral, text="Gestor de\nProjetos", font=ctk.CTkFont(size=25, weight="bold")).pack(
            padx=25, pady=(38, 26), anchor="w"
        )
        self.area_secoes = ctk.CTkFrame(self.barra_lateral, fg_color="transparent")
        self.area_secoes.pack(fill="both", expand=True)
        ctk.CTkButton(self.barra_lateral, text="Estatísticas gerais", command=self.mostrar_estatisticas_gerais).pack(
            fill="x", padx=16, pady=(10, 0)
        )
        ctk.CTkButton(self.barra_lateral, text="Gerenciar seções", command=self.abrir_gerenciador_secoes).pack(
            fill="x", padx=16, pady=(8, 24)
        )

        self.conteudo = ctk.CTkFrame(self, fg_color="transparent")
        self.conteudo.grid(row=0, column=1, sticky="nsew", padx=38, pady=32)
        self.conteudo.grid_columnconfigure(0, weight=1)
        self.conteudo.grid_rowconfigure(5, weight=1)
        self.titulo = ctk.CTkLabel(self.conteudo, font=ctk.CTkFont(size=28, weight="bold"))
        self.titulo.grid(row=0, column=0, sticky="w")
        self.resumo = ctk.CTkLabel(self.conteudo, text_color=("gray45", "gray70"))
        self.resumo.grid(row=1, column=0, sticky="w", pady=(4, 20))
        self.alertas = ctk.CTkFrame(self.conteudo, fg_color=("#FFF2CC", "#5A4700"))
        self.alertas.grid(row=2, column=0, sticky="ew", pady=(0, 12))
        self.acoes = ctk.CTkFrame(self.conteudo, fg_color="transparent")
        self.acoes.grid(row=3, column=0, sticky="ew", pady=(0, 14))
        self.acoes.grid_columnconfigure(0, weight=1)
        ctk.CTkEntry(self.acoes, textvariable=self.busca, placeholder_text="Buscar projeto...").grid(
            row=0, column=0, sticky="ew", padx=(0, 10)
        )
        ctk.CTkButton(self.acoes, text="+ Adicionar projeto", command=self.abrir_formulario_projeto).grid(row=0, column=1, padx=4)
        ctk.CTkButton(self.acoes, text="Estatísticas", command=self.mostrar_estatisticas_secao).grid(row=0, column=2, padx=4)
        ctk.CTkButton(self.acoes, text="Limpar seção", fg_color="#7A5D00", hover_color="#5D4600",
                      command=self.limpar_secao).grid(row=0, column=3, padx=(4, 0))
        self.indicadores = ctk.CTkFrame(self.conteudo, fg_color="transparent")
        self.indicadores.grid(row=4, column=0, sticky="ew", pady=(0, 12))
        self.lista_projetos = ctk.CTkScrollableFrame(self.conteudo, label_text="Projetos")
        self.lista_projetos.grid(row=5, column=0, sticky="nsew")
        self.atualizar_painel()

    def renderizar_barra_lateral(self) -> None:
        for botao in self.area_secoes.winfo_children():
            botao.destroy()
        for secao in self.gerenciador.listar_secoes():
            ctk.CTkButton(self.area_secoes, text=secao["nome"], anchor="w",
                          command=lambda codigo=secao["id"]: self.selecionar_secao(codigo)).pack(fill="x", padx=16, pady=6)

    def selecionar_secao(self, secao: str) -> None:
        self.secao_atual = secao
        self.modo_visualizacao = "projetos"
        self.filtro_status = None
        self.filtro_prazo = None
        self.busca.set("")
        self.atualizar_painel()

    def atualizar_painel(self) -> None:
        self.renderizar_barra_lateral()
        dados_secao = next(item for item in self.gerenciador.listar_secoes() if item["id"] == self.secao_atual)
        estatisticas = self.gerenciador.estatisticas(self.secao_atual)
        self.acoes.grid()
        self.indicadores.grid()
        self.alertas.grid()
        self.titulo.configure(text=dados_secao["nome"])
        self.resumo.configure(text=f"{estatisticas['total']} projeto(s) nesta seção")
        self.renderizar_filtros(estatisticas)
        self.renderizar_alertas()
        self.renderizar_projetos()

    def renderizar_filtros(self, estatisticas: dict) -> None:
        for item in self.indicadores.winfo_children():
            item.destroy()
        linha_status = ctk.CTkFrame(self.indicadores, fg_color="transparent")
        linha_status.pack(anchor="w", pady=(0, 5))
        for texto, status, quantidade in (
            ("Pendentes", "PENDENTE", estatisticas["pendentes"]),
            ("Em andamento", "EM ANDAMENTO", estatisticas["em_andamento"]),
            ("Concluídos", "CONCLUÍDO", estatisticas["concluidos"]),
        ):
            selecionado = self.filtro_status == status
            ctk.CTkButton(
                linha_status,
                text=f"{texto}: {quantidade}",
                width=160,
                fg_color=("#1F6AA5" if selecionado else "#3A3A3A"),
                command=lambda valor=status: self.alternar_filtro(valor),
            ).pack(side="left", padx=(0, 8))

        linha_prazo = ctk.CTkFrame(self.indicadores, fg_color="transparent")
        linha_prazo.pack(anchor="w")
        for texto, filtro in (
            ("Vencendo hoje", "HOJE"),
            ("Próximos 7 dias", "PROXIMOS_7_DIAS"),
            ("Sem prazo", "SEM_PRAZO"),
            ("Atrasados", "ATRASADO"),
        ):
            selecionado = self.filtro_prazo == filtro
            ctk.CTkButton(
                linha_prazo,
                text=texto,
                width=142,
                fg_color=("#9A6700" if selecionado else "#3A3A3A"),
                command=lambda valor=filtro: self.alternar_filtro_prazo(valor),
            ).pack(side="left", padx=(0, 8))

    def alternar_filtro(self, status: str) -> None:
        self.filtro_status = None if self.filtro_status == status else status
        self.atualizar_painel()

    def alternar_filtro_prazo(self, filtro: str) -> None:
        self.filtro_prazo = None if self.filtro_prazo == filtro else filtro
        self.atualizar_painel()

    def renderizar_alertas(self) -> None:
        for item in self.alertas.winfo_children():
            item.destroy()
        projetos = self.gerenciador.listar(self.secao_atual)
        alertas = [
            item for item in projetos
            if item["status"] != "CONCLUÍDO"
            and item["situacao_prazo"] in ("ATRASADO", "HOJE", "PROXIMOS_7_DIAS")
            and item.get("alerta_dispensado_para") != item["prazo"]
        ]
        if not alertas:
            self.alertas.grid_remove()
            return
        textos = {
            "ATRASADO": "Prazo atrasado",
            "HOJE": "Vence hoje",
            "PROXIMOS_7_DIAS": "Prazo próximo",
        }
        for projeto in alertas:
            linha = ctk.CTkFrame(self.alertas, fg_color="transparent")
            linha.pack(fill="x", padx=10, pady=2)
            ctk.CTkLabel(
                linha, text=f"⚠ {textos[projeto['situacao_prazo']]}: {projeto['nome']}", anchor="w"
            ).pack(side="left", fill="x", expand=True, padx=4, pady=5)
            ctk.CTkButton(linha, text="×", width=28, height=26, fg_color="transparent", hover_color="#806600",
                          command=lambda item=projeto: self.dispensar_alerta(item)).pack(side="right", padx=2)

    def dispensar_alerta(self, projeto: dict) -> None:
        self.gerenciador.dispensar_alerta(self.secao_atual, projeto["nome"])
        self.renderizar_alertas()

    def renderizar_projetos(self) -> None:
        if not hasattr(self, "lista_projetos"):
            return
        for item in self.lista_projetos.winfo_children():
            item.destroy()
        termo = self.busca.get().strip().upper()
        projetos = [
            item for item in self.gerenciador.listar(self.secao_atual)
            if termo in item["nome"]
            and (self.filtro_status is None or item["status"] == self.filtro_status)
            and (self.filtro_prazo is None or item["situacao_prazo"] == self.filtro_prazo)
        ]
        if not projetos:
            texto = "Nenhum projeto encontrado." if termo else "Ainda não há projetos nesta seção."
            ctk.CTkLabel(self.lista_projetos, text=texto, text_color=("gray45", "gray70")).pack(pady=32)
            return
        for projeto in projetos:
            linha = ctk.CTkFrame(self.lista_projetos)
            linha.pack(fill="x", padx=4, pady=5)
            prazo = projeto["prazo"]
            prazo_texto = "Sem prazo" if not prazo else f"Prazo: {'/'.join(reversed(prazo.split('-')))}"
            cores_prazo = {"ATRASADO": "#E05252", "HOJE": "#D98E00", "PROXIMOS_7_DIAS": "#D98E00"}
            cor_nome = "#3FAE5A" if projeto["status"] == "CONCLUÍDO" else cores_prazo.get(
                projeto["situacao_prazo"], ("gray25", "gray85")
            )
            ctk.CTkLabel(
                linha,
                text=f"{projeto['nome']}\n{prazo_texto}",
                anchor="w",
                justify="left",
                text_color=cor_nome,
                font=ctk.CTkFont(size=15, weight="bold"),
            ).pack(
                side="left", fill="x", expand=True, padx=(14, 8), pady=10
            )
            status = ctk.StringVar(value=projeto["status"])
            ctk.CTkOptionMenu(linha, values=list(STATUS_VALIDOS), variable=status, width=140).pack(side="left", padx=5, pady=7)
            ctk.CTkButton(linha, text="Atualizar", width=86,
                          command=lambda nome=projeto["nome"], valor=status: self.atualizar_status(nome, valor.get())).pack(
                side="left", padx=3, pady=7
            )
            ctk.CTkButton(linha, text="Prazo", width=62,
                          command=lambda item=projeto: self.editar_prazo(item)).pack(side="left", padx=3, pady=7)
            ctk.CTkButton(linha, text="Excluir", width=70, fg_color="#B42318", hover_color="#8E1B12",
                          command=lambda nome=projeto["nome"]: self.excluir_projeto(nome)).pack(side="left", padx=(3, 8), pady=7)

    def mostrar_estatisticas_secao(self) -> None:
        nome = next(item["nome"] for item in self.gerenciador.listar_secoes() if item["id"] == self.secao_atual)
        self.modo_visualizacao = "estatisticas_secao"
        self.exibir_estatisticas(f"Estatísticas: {nome}", self.gerenciador.estatisticas(self.secao_atual))

    def mostrar_estatisticas_gerais(self) -> None:
        self.modo_visualizacao = "estatisticas_gerais"
        self.exibir_estatisticas("Estatísticas gerais", self.gerenciador.estatisticas_gerais())

    def exibir_estatisticas(self, titulo: str, estatisticas: dict) -> None:
        self.acoes.grid_remove()
        self.indicadores.grid_remove()
        self.alertas.grid_remove()
        self.titulo.configure(text=titulo)
        self.resumo.configure(text="Resumo de projetos concluídos e status atuais")
        self.lista_projetos.configure(label_text="Resumo")
        for item in self.lista_projetos.winfo_children():
            item.destroy()
        ctk.CTkButton(self.lista_projetos, text="← Voltar aos projetos", command=self.mostrar_projetos).pack(
            anchor="w", padx=6, pady=(6, 18)
        )
        grupos = (
            ("Status atual", (("Total de projetos", estatisticas["total"]), ("Pendentes", estatisticas["pendentes"]),
                               ("Em andamento", estatisticas["em_andamento"]), ("Concluídos", estatisticas["concluidos"]))),
            ("Projetos concluídos", (("Hoje", estatisticas["concluidos_hoje"]), ("Nos últimos 7 dias", estatisticas["concluidos_semana"]),
                                      ("Nos últimos 30 dias", estatisticas["concluidos_mes"]))),
            ("Prazos em aberto", (("Atrasados", estatisticas["atrasados"]), ("Vencem hoje", estatisticas["vencem_hoje"]),
                                   ("Próximos 7 dias", estatisticas["proximos_7_dias"]), ("Sem prazo", estatisticas["sem_prazo"]))),
        )
        for nome_grupo, metricas in grupos:
            ctk.CTkLabel(self.lista_projetos, text=nome_grupo, font=ctk.CTkFont(size=18, weight="bold")).pack(
                anchor="w", padx=8, pady=(4, 8)
            )
            linha = ctk.CTkFrame(self.lista_projetos, fg_color="transparent")
            linha.pack(fill="x", padx=4, pady=(0, 16))
            for rotulo, valor in metricas:
                cartao = ctk.CTkFrame(linha)
                cartao.pack(side="left", fill="both", expand=True, padx=4)
                ctk.CTkLabel(cartao, text=str(valor), font=ctk.CTkFont(size=26, weight="bold")).pack(pady=(16, 2))
                ctk.CTkLabel(cartao, text=rotulo, text_color=("gray45", "gray70"), wraplength=125, justify="center").pack(
                    padx=6, pady=(0, 16)
                )

    def mostrar_projetos(self) -> None:
        self.modo_visualizacao = "projetos"
        self.lista_projetos.configure(label_text="Projetos")
        self.atualizar_painel()

    def abrir_formulario_projeto(self) -> None:
        FormularioProjeto(self)

    def editar_prazo(self, projeto: dict) -> None:
        calendario = SeletorCalendario(self, f"Prazo: {projeto['nome']}", permitir_remover=True)
        self.wait_window(calendario)
        if calendario.data_selecionada is None:
            return
        try:
            self.gerenciador.atualizar_prazo(self.secao_atual, projeto["nome"], calendario.data_selecionada)
        except ValueError as erro:
            self.mostrar_erro(str(erro))
            return
        self.atualizar_painel()

    def atualizar_status(self, nome: str, status: str) -> None:
        try:
            self.gerenciador.atualizar_status(self.secao_atual, nome, status)
        except ValueError as erro:
            self.mostrar_erro(str(erro))
            return
        self.atualizar_painel()

    def excluir_projeto(self, nome: str) -> None:
        if not self.confirmar("Excluir projeto", f'Tem certeza que deseja excluir "{nome}"?', "Sim, excluir"):
            return
        self.gerenciador.remover(self.secao_atual, nome)
        self.atualizar_painel()

    def limpar_secao(self) -> None:
        nome_secao = next(item["nome"] for item in self.gerenciador.listar_secoes() if item["id"] == self.secao_atual)
        mensagem = f'Tem certeza que deseja limpar "{nome_secao}"?\nTodos os projetos desta seção serão apagados.'
        if self.confirmar("Limpar seção", mensagem, "Sim, limpar"):
            self.gerenciador.limpar_secao(self.secao_atual)
            self.atualizar_painel()

    def abrir_gerenciador_secoes(self) -> None:
        GerenciarSecoes(self)

    def confirmar(self, titulo: str, mensagem: str, acao: str) -> bool:
        dialogo = Confirmacao(self, titulo, mensagem, acao)
        self.wait_window(dialogo)
        return dialogo.confirmado

    def mostrar_erro(self, mensagem: str) -> None:
        dialogo = ctk.CTkToplevel(self)
        dialogo.title("Não foi possível concluir")
        dialogo.geometry("380x160")
        dialogo.resizable(False, False)
        dialogo.transient(self)
        ctk.CTkLabel(dialogo, text=mensagem, wraplength=320, justify="center").pack(padx=30, pady=(35, 18))
        ctk.CTkButton(dialogo, text="Entendi", command=dialogo.destroy).pack()


if __name__ == "__main__":
    app = GestorApp()
    app.mainloop()
