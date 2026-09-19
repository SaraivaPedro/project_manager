"""Regras de negócio e persistência do gestor de projetos."""

import json
import sys
from datetime import datetime, timedelta
from pathlib import Path
from uuid import uuid4


SECOES_INICIAIS = {
    "projetos_pessoais": "Projetos pessoais",
    "tarefas_academicas": "Tarefas acadêmicas",
    "tarefas_domiciliares": "Tarefas domiciliares",
}
STATUS_VALIDOS = ("PENDENTE", "EM ANDAMENTO", "CONCLUÍDO")
STATUS_INICIAIS = ("PENDENTE", "EM ANDAMENTO")


def caminho_dados() -> Path:
    """Retorna o local do arquivo de dados, inclusive no executável."""
    pasta = Path(sys.executable).parent if getattr(sys, "frozen", False) else Path(__file__).parent
    return pasta / "dados.json"


class GerenciadorProjetos:
    def __init__(self, arquivo: Path | None = None):
        self.arquivo = arquivo or caminho_dados()
        self.dados, foi_migrado = self._carregar()
        if foi_migrado:
            self.salvar()

    @staticmethod
    def _dados_vazios() -> dict:
        return {
            "versao": 2,
            "secoes": {
                identificador: {"nome": nome, "projetos": {}}
                for identificador, nome in SECOES_INICIAIS.items()
            },
        }

    def _carregar(self) -> tuple[dict, bool]:
        try:
            with self.arquivo.open("r", encoding="utf-8") as arquivo:
                dados = json.load(arquivo)
        except (FileNotFoundError, json.JSONDecodeError):
            return self._dados_vazios(), True

        if dados.get("versao") == 2 and isinstance(dados.get("secoes"), dict):
            atualizado = False
            for secao in dados["secoes"].values():
                for projeto in secao.get("projetos", {}).values():
                    if "prazo" not in projeto:
                        projeto["prazo"] = None
                        atualizado = True
                    if "alerta_dispensado_para" not in projeto:
                        projeto["alerta_dispensado_para"] = None
                        atualizado = True
            return dados, atualizado
        return self._migrar_dados_legados(dados), True

    def _migrar_dados_legados(self, dados_legados: dict) -> dict:
        """Converte o formato antigo sem descartar projetos ou eventos."""
        dados_novos = self._dados_vazios()
        historico_antigo = dados_legados.get("historico", {})

        campos_antigos = {
            "projetos_pessoais": "projetosPessoais",
            "tarefas_academicas": "tarefasAcademicas",
            "tarefas_domiciliares": "tarefasDomiciliares",
        }
        for secao, campo_antigo in campos_antigos.items():
            for nome, status in dados_legados.get(campo_antigo, {}).items():
                eventos = []
                for evento in historico_antigo.get(nome, []):
                    eventos.append({
                        "status": evento["status"],
                        "data": evento["data"],
                        "secao": secao,
                        "projeto": nome,
                    })
                dados_novos["secoes"][secao]["projetos"][nome] = {
                    "status": status,
                    "historico": eventos,
                    "prazo": None,
                    "alerta_dispensado_para": None,
                }
        return dados_novos

    def salvar(self) -> None:
        with self.arquivo.open("w", encoding="utf-8") as arquivo:
            json.dump(self.dados, arquivo, indent=4, ensure_ascii=False)

    def _secao(self, identificador: str) -> dict:
        try:
            return self.dados["secoes"][identificador]
        except KeyError as erro:
            raise ValueError("Seção não encontrada.") from erro

    @staticmethod
    def _normalizar_nome(nome: str, descricao: str = "projeto") -> str:
        nome = nome.strip().upper()
        if not nome:
            raise ValueError(f"Informe um nome para o {descricao}.")
        return nome

    @staticmethod
    def _normalizar_status(status: str, permitidos: tuple[str, ...] = STATUS_VALIDOS) -> str:
        status = status.strip().upper()
        status = {"CONCLUIDO": "CONCLUÍDO"}.get(status, status)
        if status not in permitidos:
            opcoes = ", ".join(permitidos).lower()
            raise ValueError(f"Status inválido. Escolha entre: {opcoes}.")
        return status

    @staticmethod
    def _normalizar_prazo(prazo: str | None) -> str | None:
        if not prazo or not prazo.strip():
            return None
        try:
            data = datetime.strptime(prazo.strip(), "%d/%m/%Y").date()
        except ValueError as erro:
            raise ValueError("Use a data no formato DD/MM/AAAA.") from erro
        if data < datetime.now().date():
            raise ValueError("O prazo não pode ser anterior à data de hoje.")
        return data.isoformat()

    def listar_secoes(self) -> list[dict]:
        return [
            {"id": identificador, "nome": secao["nome"], "total": len(secao["projetos"])}
            for identificador, secao in self.dados["secoes"].items()
        ]

    def criar_secao(self, nome: str) -> str:
        nome = self._normalizar_titulo(nome, "seção")
        if any(secao["nome"].casefold() == nome.casefold() for secao in self.dados["secoes"].values()):
            raise ValueError("Já existe uma seção com esse nome.")
        identificador = f"secao_{uuid4().hex[:8]}"
        self.dados["secoes"][identificador] = {"nome": nome, "projetos": {}}
        self.salvar()
        return identificador

    @staticmethod
    def _normalizar_titulo(nome: str, descricao: str) -> str:
        nome = nome.strip()
        if not nome:
            raise ValueError(f"Informe um nome para a {descricao}.")
        return nome

    def renomear_secao(self, secao: str, novo_nome: str) -> None:
        dados_secao = self._secao(secao)
        novo_nome = self._normalizar_titulo(novo_nome, "seção")
        if any(
            identificador != secao and item["nome"].casefold() == novo_nome.casefold()
            for identificador, item in self.dados["secoes"].items()
        ):
            raise ValueError("Já existe uma seção com esse nome.")
        dados_secao["nome"] = novo_nome
        self.salvar()

    def remover_secao(self, secao: str) -> None:
        self._secao(secao)
        if len(self.dados["secoes"]) == 1:
            raise ValueError("Crie outra seção antes de apagar a última seção existente.")
        del self.dados["secoes"][secao]
        self.salvar()

    def mover_secao(self, secao: str, direcao: int) -> None:
        """Move uma seção uma posição. Direção: -1 para cima, 1 para baixo."""
        self._secao(secao)
        identificadores = list(self.dados["secoes"])
        indice = identificadores.index(secao)
        novo_indice = indice + direcao
        if novo_indice < 0 or novo_indice >= len(identificadores):
            return
        identificadores[indice], identificadores[novo_indice] = (
            identificadores[novo_indice],
            identificadores[indice],
        )
        self.dados["secoes"] = {identificador: self.dados["secoes"][identificador] for identificador in identificadores}
        self.salvar()

    def listar(self, secao: str) -> list[dict]:
        projetos = self._secao(secao)["projetos"]
        return [
            {
                "nome": nome,
                "status": projeto["status"],
                "historico": projeto["historico"],
                "prazo": projeto.get("prazo"),
                "alerta_dispensado_para": projeto.get("alerta_dispensado_para"),
                "situacao_prazo": self.situacao_prazo(projeto.get("prazo")),
            }
            for nome, projeto in sorted(projetos.items())
        ]

    def _registrar_evento(self, secao: str, nome: str, status: str) -> dict:
        return {
            "status": status,
            "data": datetime.now().isoformat(),
            "secao": secao,
            "projeto": nome,
        }

    def adicionar(self, secao: str, nome: str, status: str, prazo: str | None = None) -> None:
        projetos = self._secao(secao)["projetos"]
        nome = self._normalizar_nome(nome)
        status = self._normalizar_status(status, STATUS_INICIAIS)
        prazo = self._normalizar_prazo(prazo)
        if nome in projetos:
            raise ValueError("Já existe um projeto com esse nome nesta seção.")
        projetos[nome] = {
            "status": status,
            "historico": [self._registrar_evento(secao, nome, status)],
            "prazo": prazo,
            "alerta_dispensado_para": None,
        }
        self.salvar()

    def atualizar_prazo(self, secao: str, nome: str, prazo: str | None) -> None:
        projetos = self._secao(secao)["projetos"]
        nome = self._normalizar_nome(nome)
        if nome not in projetos:
            raise ValueError("Projeto não encontrado.")
        projetos[nome]["prazo"] = self._normalizar_prazo(prazo)
        projetos[nome]["alerta_dispensado_para"] = None
        self.salvar()

    def dispensar_alerta(self, secao: str, nome: str) -> None:
        projetos = self._secao(secao)["projetos"]
        nome = self._normalizar_nome(nome)
        if nome not in projetos:
            raise ValueError("Projeto não encontrado.")
        projetos[nome]["alerta_dispensado_para"] = projetos[nome].get("prazo")
        self.salvar()

    @staticmethod
    def situacao_prazo(prazo: str | None) -> str:
        if not prazo:
            return "SEM_PRAZO"
        data = datetime.fromisoformat(prazo).date()
        hoje = datetime.now().date()
        if data < hoje:
            return "ATRASADO"
        if data == hoje:
            return "HOJE"
        if data <= hoje + timedelta(days=7):
            return "PROXIMOS_7_DIAS"
        return "FUTURO"

    def atualizar_status(self, secao: str, nome: str, status: str) -> None:
        projetos = self._secao(secao)["projetos"]
        nome = self._normalizar_nome(nome)
        status = self._normalizar_status(status)
        if nome not in projetos:
            raise ValueError("Projeto não encontrado.")
        projetos[nome]["status"] = status
        projetos[nome]["historico"].append(self._registrar_evento(secao, nome, status))
        self.salvar()

    def remover(self, secao: str, nome: str) -> None:
        projetos = self._secao(secao)["projetos"]
        nome = self._normalizar_nome(nome)
        if nome not in projetos:
            raise ValueError("Projeto não encontrado.")
        del projetos[nome]
        self.salvar()

    def limpar_secao(self, secao: str) -> None:
        self._secao(secao)["projetos"].clear()
        self.salvar()

    def estatisticas(self, secao: str) -> dict:
        projetos = self._secao(secao)["projetos"]
        agora = datetime.now()
        concluidos_hoje = set()
        concluidos_semana = set()
        concluidos_mes = set()
        atrasados = 0
        vencem_hoje = 0
        proximos_7_dias = 0
        sem_prazo = 0

        for nome, projeto in projetos.items():
            for evento in projeto["historico"]:
                if evento["status"] != "CONCLUÍDO":
                    continue
                data = datetime.fromisoformat(evento["data"])
                if data.date() == agora.date():
                    concluidos_hoje.add(nome)
                if data >= agora - timedelta(days=7):
                    concluidos_semana.add(nome)
                if data >= agora - timedelta(days=30):
                    concluidos_mes.add(nome)
            if projeto["status"] != "CONCLUÍDO":
                situacao = self.situacao_prazo(projeto.get("prazo"))
                if situacao == "ATRASADO":
                    atrasados += 1
                elif situacao == "HOJE":
                    vencem_hoje += 1
                elif situacao == "PROXIMOS_7_DIAS":
                    proximos_7_dias += 1
                elif situacao == "SEM_PRAZO":
                    sem_prazo += 1

        return {
            "total": len(projetos),
            "pendentes": sum(item["status"] == "PENDENTE" for item in projetos.values()),
            "em_andamento": sum(item["status"] == "EM ANDAMENTO" for item in projetos.values()),
            "concluidos": sum(item["status"] == "CONCLUÍDO" for item in projetos.values()),
            "concluidos_hoje": len(concluidos_hoje),
            "concluidos_semana": len(concluidos_semana),
            "concluidos_mes": len(concluidos_mes),
            "atrasados": atrasados,
            "vencem_hoje": vencem_hoje,
            "proximos_7_dias": proximos_7_dias,
            "sem_prazo": sem_prazo,
        }

    def estatisticas_gerais(self) -> dict:
        """Consolida as estatísticas de todas as seções."""
        totais = {
            "total": 0,
            "pendentes": 0,
            "em_andamento": 0,
            "concluidos": 0,
            "concluidos_hoje": 0,
            "concluidos_semana": 0,
            "concluidos_mes": 0,
            "atrasados": 0,
            "vencem_hoje": 0,
            "proximos_7_dias": 0,
            "sem_prazo": 0,
        }
        for secao in self.dados["secoes"]:
            estatisticas = self.estatisticas(secao)
            for campo in totais:
                totais[campo] += estatisticas[campo]
        return totais
