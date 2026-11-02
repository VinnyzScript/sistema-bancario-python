
import json
import os
import random
import hashlib
from datetime import datetime

ARQUIVO = "banco_dados.json"


# ==============================
# ARMAZENAMENTO DE DADOS
# ==============================

def carregar_dados():
    if os.path.exists(ARQUIVO):
        try:
            with open(ARQUIVO, "r", encoding="utf-8") as arquivo:
                return json.load(arquivo)
        except (json.JSONDecodeError, OSError):
            print("Erro ao carregar os dados.")
    return {"clientes": {}}


dados = carregar_dados()


def salvar_dados():
    with open(ARQUIVO, "w", encoding="utf-8") as arquivo:
        json.dump(dados, arquivo, indent=4, ensure_ascii=False)


def gerar_hash(senha):
    return hashlib.sha256(senha.encode()).hexdigest()


def registrar_movimentacao(conta, descricao, valor):
    conta["extrato"].append({
        "data": datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
        "descricao": descricao,
        "valor": valor
    })


def ler_valor(mensagem):
    try:
        valor = float(input(mensagem).replace(",", "."))
        if not valor > 0:
            print("Digite um valor maior que zero!")
            return None
        return valor
    except ValueError:
        print("Digite um número válido!")
        return None


# ==============================
# CADASTRO DE CLIENTES
# ==============================

def cadastrar_cliente():
    print("\n===== CADASTRO DE CLIENTE =====")

    nome = input("Nome completo: ").strip()
    cpf = input("CPF (somente números): ").strip()

    if not nome:
        print("Nome inválido!")
        return

    if not cpf.isdigit() or len(cpf) != 11:
        print("CPF deve conter 11 números!")
        return

    if cpf in dados["clientes"]:
        print("Cliente já cadastrado!")
        return

    senha = input("Crie uma senha: ")

    if len(senha) < 6:
        print("A senha precisa ter pelo menos 6 caracteres!")
        return

    numero = gerar_numero_conta()

    dados["clientes"][cpf] = {
        "nome": nome,
        "senha": gerar_hash(senha),
        "contas": {
            numero: {
                "saldo": 0.0,
                "extrato": []
            }
        }
    }

    salvar_dados()

    print("\nCadastro realizado com sucesso!")
    print(f"Cliente: {nome}")
    print(f"Número da conta: {numero}")


def gerar_numero_conta():
    contas_existentes = set()

    for cliente in dados["clientes"].values():
        contas_existentes.update(cliente["contas"].keys())

    while True:
        numero = str(random.randint(10000, 99999))

        if numero not in contas_existentes:
            return numero


# ==============================
# LOGIN
# ==============================

def login():
    print("\n===== LOGIN =====")

    cpf = input("CPF: ").strip()
    senha = input("Senha: ")

    cliente = dados["clientes"].get(cpf)

    if cliente and cliente["senha"] == gerar_hash(senha):
        print(f"\nBem-vindo(a), {cliente['nome']}!")
        return cpf

    print("CPF ou senha incorretos!")
    return None


# ==============================
# CONTAS BANCÁRIAS
# ==============================

def selecionar_conta(cpf):
    contas = dados["clientes"][cpf]["contas"]

    print("\n===== SUAS CONTAS =====")

    for numero, conta in contas.items():
        print(f"Conta: {numero} | Saldo: R$ {conta['saldo']:.2f}")

    numero = input("\nDigite o número da conta: ").strip()

    if numero not in contas:
        print("Conta não encontrada!")
        return None

    return numero


def criar_conta(cpf):
    numero = gerar_numero_conta()

    dados["clientes"][cpf]["contas"][numero] = {
        "saldo": 0.0,
        "extrato": []
    }

    salvar_dados()

    print(f"\nNova conta criada com sucesso!")
    print(f"Número da conta: {numero}")


# ==============================
# OPERAÇÕES BANCÁRIAS
# ==============================

def consultar_saldo(cpf, numero):
    conta = dados["clientes"][cpf]["contas"][numero]

    print(f"\nSaldo disponível: R$ {conta['saldo']:.2f}")


def depositar(cpf, numero):
    valor = ler_valor("Valor do depósito: R$ ")

    if valor is None:
        return

    conta = dados["clientes"][cpf]["contas"][numero]

    conta["saldo"] += valor

    registrar_movimentacao(
        conta, "Depósito", valor
    )

    salvar_dados()

    print("Depósito realizado com sucesso!")


def sacar(cpf, numero):
    valor = ler_valor("Valor do saque: R$ ")

    if valor is None:
        return

    conta = dados["clientes"][cpf]["contas"][numero]

    if valor > conta["saldo"]:
        print("Saldo insuficiente!")
        return

    conta["saldo"] -= valor

    registrar_movimentacao(
        conta, "Saque", -valor
    )

    salvar_dados()

    print("Saque realizado com sucesso!")


def transferir(cpf, numero):
    print("\n===== TRANSFERÊNCIA =====")

    cpf_destino = input("CPF do destinatário: ").strip()

    if cpf_destino not in dados["clientes"]:
        print("Cliente não encontrado!")
        return

    numero_destino = input("Conta de destino: ").strip()

    cliente_destino = dados["clientes"][cpf_destino]

    if numero_destino not in cliente_destino["contas"]:
        print("Conta de destino não encontrada!")
        return

    if cpf == cpf_destino and numero == numero_destino:
        print("Não é possível transferir para a mesma conta!")
        return

    valor = ler_valor("Valor da transferência: R$ ")

    if valor is None:
        return

    origem = dados["clientes"][cpf]["contas"][numero]
    destino = cliente_destino["contas"][numero_destino]

    if valor > origem["saldo"]:
        print("Saldo insuficiente!")
        return

    origem["saldo"] -= valor
    destino["saldo"] += valor

    registrar_movimentacao(
        origem,
        f"Transferência enviada para {cliente_destino['nome']}",
        -valor
    )

    registrar_movimentacao(
        destino,
        f"Transferência recebida de {dados['clientes'][cpf]['nome']}",
        valor
    )

    salvar_dados()

    print("Transferência realizada com sucesso!")


# ==============================
# EXTRATO
# ==============================

def ver_extrato(cpf, numero):
    conta = dados["clientes"][cpf]["contas"][numero]

    print("\n===== EXTRATO BANCÁRIO =====")

    if not conta["extrato"]:
        print("Nenhuma movimentação realizada.")

    for item in conta["extrato"]:
        print(
            f"{item['data']} | "
            f"{item['descricao']} | "
            f"R$ {item['valor']:.2f}"
        )

    print("-" * 35)
    print(f"Saldo atual: R$ {conta['saldo']:.2f}")


# ==============================
# MENU DO BANCO
# ==============================

def menu_bancario(cpf, numero):
    while True:
        print("\n======= BANCO PYTHON =======")
        print(f"Cliente: {dados['clientes'][cpf]['nome']}")
        print(f"Conta atual: {numero}")
        print("----------------------------")
        print("1 - Consultar saldo")
        print("2 - Depositar")
        print("3 - Sacar")
        print("4 - Transferir")
        print("5 - Ver extrato")
        print("6 - Criar outra conta")
        print("7 - Trocar de conta")
        print("0 - Sair da conta")

        opcao = input("\nEscolha uma opção: ")

        if opcao == "1":
            consultar_saldo(cpf, numero)

        elif opcao == "2":
            depositar(cpf, numero)

        elif opcao == "3":
            sacar(cpf, numero)

        elif opcao == "4":
            transferir(cpf, numero)

        elif opcao == "5":
            ver_extrato(cpf, numero)

        elif opcao == "6":
            criar_conta(cpf)

        elif opcao == "7":
            nova_conta = selecionar_conta(cpf)

            if nova_conta:
                numero = nova_conta
                print("Conta alterada com sucesso!")

        elif opcao == "0":
            print("Logout realizado!")
            break

        else:
            print("Opção inválida!")


# ==============================
# INICIALIZAÇÃO
# ==============================

def iniciar():
    while True:
        print("\n======= BANCO PYTHON =======")
        print("1 - Cadastrar cliente")
        print("2 - Fazer login")
        print("0 - Encerrar sistema")

        opcao = input("\nEscolha uma opção: ")

        if opcao == "1":
            cadastrar_cliente()

        elif opcao == "2":
            cpf = login()

            if cpf:
                numero = selecionar_conta(cpf)

                if numero:
                    menu_bancario(cpf, numero)

        elif opcao == "0":
            print("\nObrigado por utilizar o Banco Python!")
            break

        else:
            print("Opção inválida!")


if __name__ == "__main__":
    iniciar()
