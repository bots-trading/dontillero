from flask import Flask, request, redirect, session, send_from_directory
import sqlite3

app = Flask(__name__)
app.secret_key = "secret123"

conn = sqlite3.connect('database.db', check_same_thread=False)
c = conn.cursor()

# CLIENTES
c.execute('''CREATE TABLE IF NOT EXISTS clientes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT,
    email TEXT UNIQUE,
    senha TEXT,
    plano TEXT,
    etapa INTEGER DEFAULT 1
)''')

# AGENDAMENTOS
c.execute('''CREATE TABLE IF NOT EXISTS agendamentos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    cliente_id INTEGER,
    data TEXT,
    hora TEXT,
    servico TEXT,
    status TEXT,
    valor REAL
)''')

conn.commit()

# ======================
# LANDING
# ======================
@app.route("/vendas")
def vendas():
    return send_from_directory("pages", "landing.html")

# ======================
# CHECKOUT
# ======================
@app.route("/checkout")
def checkout():
    plano = request.args.get("plano")

    precos = {
        "basico": "R$ 97",
        "avancado": "R$ 197",
        "premium": "R$ 497"
    }

    return f"""
    <link rel="stylesheet" href="/static/style.css">

    <div class='container'>
        <div class='card'>
            <h2>Plano {plano.upper()}</h2>
            <h3>{precos.get(plano)}</h3>

            <a href="/pagar/mp?plano={plano}" class="btn">PIX</a><br><br>
            <a href="/pagar/paypal?plano={plano}" class="btn">PayPal</a><br><br>
            <a href="/pagar/crypto?plano={plano}" class="btn">Cripto</a>
        </div>
    </div>
    """

# ======================
# PAGAMENTOS
# ======================
@app.route("/pagar/mp")
def mp():
    return redirect("https://mpago.li/2Ue4gsG")

@app.route("/pagar/paypal")
def paypal():
    return redirect("https://paypal.me/SEULINK")

@app.route("/pagar/crypto")
def crypto():
    return """
    <link rel="stylesheet" href="/static/style.css">
    <div class='container'>
        <div class='card'>
            <h2>Pagamento Cripto</h2>
            <p>USDT (TRC20)</p>
            <p>SUA WALLET</p>
        </div>
    </div>
    """

# ======================
# LOGIN
# ======================
@app.route("/", methods=["GET","POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        senha = request.form["senha"]

        c.execute("SELECT * FROM clientes WHERE email=? AND senha=?", (email, senha))
        user = c.fetchone()

        if user:
            session["user_id"] = user[0]
            return redirect("/dashboard")

    return """
    <link rel="stylesheet" href="/static/style.css">
    <div class='container'>
        <div class='card'>
            <h2>Login</h2>
            <form method='post'>
                <input name='email'>
                <input name='senha' type='password'>
                <button class='btn'>Entrar</button>
            </form>
            <a href='/vendas'>Comprar plano</a>
        </div>
    </div>
    """

# ======================
# DASHBOARD
# ======================
@app.route("/dashboard")
def dashboard():
    if "user_id" not in session:
        return redirect("/")

    c.execute("SELECT * FROM agendamentos WHERE cliente_id=?", (session["user_id"],))
    ags = c.fetchall()

    lista = ""
    for ag in ags:
        lista += f"<p>{ag[3]} - {ag[4]} ({ag[5]})</p>"

    return f"""
    <link rel="stylesheet" href="/static/style.css">
    <div class='container'>
        <div class='card'>
            <h2>Dashboard</h2>
            {lista}
            <br>
            <a href='/agendar' class='btn'>Agendar</a>
        </div>
    </div>
    """

# ======================
# AGENDAR
# ======================
@app.route("/agendar", methods=["GET","POST"])
def agendar():
    if "user_id" not in session:
        return redirect("/")

    if request.method == "POST":
        data = request.form["data"]
        hora = request.form["hora"]
        servico = request.form["servico"]

        c.execute("""
        INSERT INTO agendamentos (cliente_id,data,hora,servico,status,valor)
        VALUES (?,?,?,?,?,?)
        """, (session["user_id"], data, hora, servico, "Agendado", 100))

        conn.commit()
        return redirect("/dashboard")

    return """
    <link rel="stylesheet" href="/static/style.css">
    <div class='container'>
        <div class='card'>
            <h2>Agendar</h2>
            <form method='post'>
                <input type='date' name='data'><br>
                <input type='time' name='hora'><br>

                <select name='servico'>
                    <option>Consulta</option>
                    <option>Suporte</option>
                </select><br>

                <button class='btn'>Salvar</button>
            </form>
        </div>
    </div>
    """

# ======================
# ADMIN
# ======================
@app.route("/admin")
def admin():
    c.execute("SELECT * FROM agendamentos")
    ags = c.fetchall()

    total = sum([ag[6] for ag in ags])

    lista = ""
    for ag in ags:
        lista += f"<p>{ag[3]} - {ag[4]} - {ag[5]}</p>"

    return f"""
    <link rel="stylesheet" href="/static/style.css">
    <div class='container'>
        <div class='card'>
            <h2>Admin</h2>
            <p>Faturamento: R${total}</p>
            {lista}
        </div>
    </div>
    """
# CLIENTES
c.execute('''
CREATE TABLE IF NOT EXISTS clientes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT,
    email TEXT,
    telefone TEXT
)
''')

# SERVIÇOS
c.execute('''
CREATE TABLE IF NOT EXISTS servicos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT,
    preco REAL,
    duracao INTEGER
)
''')

# AGENDAMENTOS
c.execute('''
CREATE TABLE IF NOT EXISTS agendamentos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    cliente_id INTEGER,
    data TEXT,
    hora TEXT,
    servico TEXT,
    status TEXT,
    valor REAL
)
''')
@app.route("/agenda", methods=["GET", "POST"])
def agenda():
    if request.method == "POST":
        cliente_id = request.form.get("cliente_id")
        data = request.form.get("data")
        hora = request.form.get("hora")
        servico = request.form.get("servico")

        c.execute("""
        INSERT INTO agendamentos (cliente_id, data, hora, servico, status, valor)
        VALUES (?, ?, ?, ?, 'Agendado', 0)
        """, (cliente_id, data, hora, servico))
        conn.commit()

    c.execute("SELECT * FROM agendamentos")
    agendamentos = c.fetchall()

    return render_template("agenda.html", agendamentos=agendamentos)
@app.route("/clientes", methods=["GET", "POST"])
def clientes():
    if request.method == "POST":
        nome = request.form.get("nome")
        email = request.form.get("email")
        telefone = request.form.get("telefone")

        c.execute("""
        INSERT INTO clientes (nome, email, telefone)
        VALUES (?, ?, ?)
        """, (nome, email, telefone))
        conn.commit()

    c.execute("SELECT * FROM clientes")
    clientes = c.fetchall()

    return render_template("clientes.html", clientes=clientes)
@app.route("/dashboard")
def dashboard():
    c.execute("SELECT SUM(valor) FROM agendamentos WHERE status='Finalizado'")
    faturamento = c.fetchone()[0] or 0

    c.execute("SELECT COUNT(*) FROM agendamentos")
    total = c.fetchone()[0]

    return render_template("dashboard.html", faturamento=faturamento, total=total)

if __name__ == "__main__":
    app.run(debug=True)