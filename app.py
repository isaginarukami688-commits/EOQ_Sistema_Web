import math

import streamlit as st
from scipy.optimize import linprog

# Los colores base del tema viven en .streamlit/config.toml (se leen al arrancar).
# Este archivo agrega el diseño: fondo, efectos y detalles en rojo.
# Ejecuta siempre desde la carpeta del proyecto:  streamlit run app.py

st.set_page_config(page_title="Investigación de operaciones", layout="wide")

ESTILOS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Bodoni+Moda:opsz,wght@6..96,400..600&family=IBM+Plex+Sans:wght@400;500;600&display=swap');

:root {
  --text: #FFF4F0;
  --muted: #F2CEC8;
  --line: rgba(255, 255, 255, .16);
  --glow: rgba(255, 64, 64, .55);
  --red-hi: #FF4D4D;
  --display: 'Bodoni Moda', 'Didot', 'Times New Roman', serif;
  --body: 'IBM Plex Sans', system-ui, -apple-system, 'Segoe UI', sans-serif;
}

/* Tipografía base (no se toca <span> para no romper los íconos de Streamlit) */
.stApp, .stApp p, .stApp label, .stApp li, .stApp input, .stApp button,
[data-testid="stSidebar"] {
  font-family: var(--body);
}

/* Fondo: rojo en degradado con dos focos de luz */
.stApp {
  background:
    radial-gradient(1100px 620px at 12% -8%, rgba(255, 80, 80, .50), transparent 62%),
    radial-gradient(900px 520px at 100% 105%, rgba(255, 45, 45, .30), transparent 58%),
    linear-gradient(160deg, #961B1B 0%, #5C0F10 48%, #2B0707 100%);
  background-attachment: fixed;
}
[data-testid="stAppViewContainer"], [data-testid="stMain"], [data-testid="stHeader"] {
  background: transparent !important;
}
.block-container { max-width: 1040px; padding: 3.5rem 2rem 5rem; }
footer, [data-testid="stDeployButton"] { visibility: hidden; }

/* Barra lateral: rojo con textura de metal cepillado */
[data-testid="stSidebar"] {
  background:
    repeating-linear-gradient(90deg, rgba(255, 255, 255, .05) 0 1px, rgba(0, 0, 0, .05) 1px 3px),
    linear-gradient(180deg, #CC2A2A 0%, #901717 55%, #680F10 100%);
  border-right: 1px solid rgba(255, 255, 255, .25);
  box-shadow: 8px 0 40px rgba(0, 0, 0, .38);
}
[data-testid="stSidebarContent"], [data-testid="stSidebar"] > div:first-child {
  background: transparent;
}
[data-testid="stSidebar"] [data-testid="stWidgetLabel"] p { color: var(--text); }

.brand { padding: .5rem 0 1.5rem; border-bottom: 1px solid rgba(255, 255, 255, .25); margin-bottom: 1.5rem; }
.mark {
  display: grid; place-items: center;
  width: 64px; height: 64px; margin-bottom: 1rem;
  border-radius: 50%;
  font-family: var(--display); font-size: 1.6rem; font-weight: 500; color: #fff;
  background: radial-gradient(circle at 30% 25%, #FF7A7A, #8F1414 72%);
  box-shadow: 0 0 0 1px rgba(255, 255, 255, .4), 0 8px 24px rgba(0, 0, 0, .4), 0 0 30px var(--glow);
}
.brand-name { display: block; font-family: var(--display); font-size: 1.4rem; line-height: 1.2; color: var(--text); }
.brand-sub { display: block; margin-top: .45rem; font-size: .8rem; line-height: 1.45; color: var(--muted); }

/* Encabezado de página */
.stApp .page-head h1 {
  font-family: var(--display);
  font-weight: 500;
  font-size: clamp(2rem, 4.5vw, 3rem);
  line-height: 1.1;
  letter-spacing: -0.01em;
  color: var(--text);
  text-shadow: 0 2px 24px rgba(0, 0, 0, .45);
  margin: 0;
  padding: 0;
}
.page-head .rule {
  width: 64px; height: 3px; margin: 1.1rem 0 1rem; border-radius: 2px;
  background: linear-gradient(90deg, #FF8A8A, #FF2D2D);
  box-shadow: 0 0 14px rgba(255, 70, 70, .9);
}
.page-head p { max-width: 58ch; margin: 0 0 1.5rem; font-size: 1rem; line-height: 1.6; color: var(--muted); }

/* Secciones: una línea fina separa cada bloque */
.sec { margin: 2.25rem 0 .5rem; padding-top: 1.5rem; border-top: 1px solid var(--line); font-size: .95rem; font-weight: 600; color: var(--text); }
.sec.first { margin-top: 0; padding-top: 0; border-top: 0; }

/* Campos con borde luminoso */
[data-testid="stWidgetLabel"] p { font-size: .88rem; font-weight: 400; color: var(--muted); }
[data-baseweb="base-input"] { background: transparent !important; }
[data-baseweb="input"], [data-baseweb="select"] > div {
  background: rgba(25, 0, 0, .55) !important;
  border: 1px solid rgba(255, 96, 96, .85) !important;
  border-radius: 8px !important;
  box-shadow: 0 0 14px rgba(255, 60, 60, .35), inset 0 0 10px rgba(0, 0, 0, .35);
  transition: box-shadow .18s ease, border-color .18s ease;
}
[data-baseweb="input"]:hover, [data-baseweb="select"] > div:hover,
[data-baseweb="input"]:focus-within, [data-baseweb="select"] > div:focus-within {
  border-color: #FFB3B3 !important;
  box-shadow: 0 0 0 1px rgba(255, 179, 179, .6), 0 0 24px rgba(255, 70, 70, .7), inset 0 0 10px rgba(0, 0, 0, .35);
}
[data-testid="stNumberInput"] input { color: var(--text); font-variant-numeric: tabular-nums; }
[data-testid="stNumberInputStepUp"], [data-testid="stNumberInputStepDown"] {
  background: rgba(0, 0, 0, .28) !important; color: #fff !important;
}
[data-baseweb="select"] * { color: var(--text); }

/* Botón principal con brillo */
.stButton > button { padding: .75rem 2rem; border-radius: 10px; font-weight: 600; transition: transform .15s ease, box-shadow .15s ease; }
.stButton > button[kind="primary"],
.stButton > button[data-testid="stBaseButton-primary"] {
  color: #fff;
  background: linear-gradient(180deg, #FF5A52 0%, #D32F2F 55%, #A51818 100%);
  border: 1px solid rgba(255, 255, 255, .45);
  box-shadow: 0 0 22px rgba(255, 60, 60, .55), 0 8px 20px rgba(0, 0, 0, .35), inset 0 1px 0 rgba(255, 255, 255, .35);
  animation: respira 3.6s ease-in-out infinite;
}
.stButton > button[kind="primary"]:hover,
.stButton > button[data-testid="stBaseButton-primary"]:hover {
  color: #fff;
  transform: translateY(-2px);
  animation: none;
  box-shadow: 0 0 34px rgba(255, 90, 90, .85), 0 12px 26px rgba(0, 0, 0, .4), inset 0 1px 0 rgba(255, 255, 255, .45);
}
.stButton > button[kind="primary"]:active,
.stButton > button[data-testid="stBaseButton-primary"]:active { transform: translateY(0); }
.stButton > button:focus-visible { outline: 2px solid #fff; outline-offset: 3px; }
@keyframes respira {
  0%, 100% { box-shadow: 0 0 18px rgba(255, 60, 60, .45), 0 8px 20px rgba(0, 0, 0, .35), inset 0 1px 0 rgba(255, 255, 255, .35); }
  50%      { box-shadow: 0 0 32px rgba(255, 80, 80, .80), 0 8px 20px rgba(0, 0, 0, .35), inset 0 1px 0 rgba(255, 255, 255, .35); }
}

/* Resultado: panel de cristal, la pieza grande de la página */
.readout {
  margin-top: 2.5rem; padding: 2rem 2rem 1.75rem;
  border: 1px solid rgba(255, 130, 130, .55);
  border-radius: 16px;
  background: linear-gradient(160deg, rgba(40, 0, 0, .62), rgba(20, 0, 0, .45));
  backdrop-filter: blur(8px);
  box-shadow: 0 16px 48px rgba(0, 0, 0, .40), 0 0 34px rgba(255, 60, 60, .22);
  animation: aparece .45s ease both;
}
@keyframes aparece { from { opacity: 0; transform: translateY(10px); } to { opacity: 1; transform: none; } }
.readout .k { display: block; font-size: .85rem; color: var(--muted); }
.readout .fig {
  margin: .35rem 0 .15rem;
  font-family: var(--display);
  font-weight: 500;
  font-size: clamp(3.2rem, 9vw, 6rem);
  line-height: 1.05;
  letter-spacing: -0.02em;
  color: #fff;
  text-shadow: 0 0 28px rgba(255, 90, 90, .65);
  font-variant-numeric: lining-nums tabular-nums;
}
.readout .u { font-size: 1rem; color: var(--muted); }
.readout-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(170px, 1fr)); gap: 1.5rem; margin-top: 1.75rem; padding-top: 1.25rem; border-top: 1px solid var(--line); }
.readout-grid .v { display: block; margin-top: .2rem; font-size: 1.6rem; font-weight: 500; color: var(--text); font-variant-numeric: tabular-nums; }

/* Tabla comparativa (descuentos por cantidad) */
.tbl { width: 100%; border-collapse: collapse; margin: .5rem 0 1rem; font-variant-numeric: tabular-nums; }
.tbl th { text-align: left; padding: .6rem .75rem; font-size: .8rem; font-weight: 600; color: var(--muted); border-bottom: 1px solid var(--line); }
.tbl td { padding: .65rem .75rem; font-size: .95rem; color: var(--text); border-bottom: 1px solid var(--line); }
.tbl tr.best td { background: rgba(255, 90, 90, .18); font-weight: 600; }
.tbl tr.off td { opacity: .55; }

/* Avisos */
[data-testid="stAlert"] {
  border: 1px solid rgba(255, 160, 150, .5); border-left: 3px solid #FFB4A8;
  border-radius: 10px; background: rgba(25, 0, 0, .55);
}

@media (prefers-reduced-motion: reduce) {
  .stButton > button, [data-baseweb="input"], [data-baseweb="select"] > div { transition: none; }
  .stButton > button[kind="primary"], .stButton > button[data-testid="stBaseButton-primary"], .readout { animation: none; }
}
</style>
"""

st.markdown(ESTILOS, unsafe_allow_html=True)


# ---------------------------------------------------------------------------
# Piezas de interfaz
# ---------------------------------------------------------------------------
def encabezado(titulo, descripcion):
    st.markdown(
        f'<div class="page-head"><h1>{titulo}</h1><div class="rule"></div>'
        f"<p>{descripcion}</p></div>",
        unsafe_allow_html=True,
    )


def seccion(texto, primera=False):
    clase = "sec first" if primera else "sec"
    st.markdown(f'<div class="{clase}">{texto}</div>', unsafe_allow_html=True)


def lectura(etiqueta, valor, unidad, datos):
    """Resultado principal en grande y los datos secundarios en una fila."""
    unidad_html = f'<span class="u">{unidad}</span>' if unidad else ""
    celdas = "".join(
        f'<div><span class="k">{k}</span><span class="v">{v}</span></div>'
        for k, v in datos
    )
    st.markdown(
        f'<div class="readout"><span class="k">{etiqueta}</span>'
        f'<div class="fig">{valor}</div>{unidad_html}'
        f'<div class="readout-grid">{celdas}</div></div>',
        unsafe_allow_html=True,
    )


def tabla(encabezados, filas, destacada=None, apagadas=()):
    """Tabla HTML simple; resalta una fila y atenúa las que no aplican."""
    th = "".join(f"<th>{h}</th>" for h in encabezados)
    trs = ""
    for i, fila in enumerate(filas):
        clase = "best" if i == destacada else ("off" if i in apagadas else "")
        celdas = "".join(f"<td>{c}</td>" for c in fila)
        trs += f'<tr class="{clase}">{celdas}</tr>'
    st.markdown(
        f'<table class="tbl"><thead><tr>{th}</tr></thead><tbody>{trs}</tbody></table>',
        unsafe_allow_html=True,
    )


def formulas(*ecuaciones):
    """Fórmulas del modelo en un panel que se despliega."""
    with st.expander("Ver fórmulas"):
        for ecuacion in ecuaciones:
            st.latex(ecuacion)


def expresion(a1, a2):
    """Escribe a1*x1 + a2*x2 en LaTeX, omitiendo ceros y cuidando los signos."""
    partes = []
    for coef, var in ((a1, "x_1"), (a2, "x_2")):
        if coef == 0:
            continue
        magnitud = abs(coef)
        cuerpo = var if magnitud == 1 else f"{magnitud:g}{var}"
        partes.append(("-" if coef < 0 else "+", cuerpo))
    if not partes:
        return "0"
    signo, cuerpo = partes[0]
    texto = ("-" if signo == "-" else "") + cuerpo
    for signo, cuerpo in partes[1:]:
        texto += f" {signo} {cuerpo}"
    return texto


# ---------------------------------------------------------------------------
# Navegación
# ---------------------------------------------------------------------------
MODULO_EOQ = "EOQ básico"
MODULO_DESC = "EOQ con descuentos"
MODULO_FALT = "EOQ con faltantes"
MODULO_PROD = "EOQ producción sin déficit"
MODULO_PROD_DEF = "EOQ producción con déficit"
MODULO_LP = "Programación lineal (Simplex)"

st.sidebar.markdown(
    '<div class="brand"><div class="mark">IO</div>'
    '<span class="brand-name">Investigación de operaciones</span>'
    '<span class="brand-sub">Planeación de operaciones empresariales</span></div>',
    unsafe_allow_html=True,
)
modulo = st.sidebar.selectbox(
    "Selecciona un módulo",
    [MODULO_EOQ, MODULO_DESC, MODULO_FALT, MODULO_PROD, MODULO_PROD_DEF, MODULO_LP],
)

# ---------------------------------------------------------------------------
# Módulo 1: EOQ básico
# ---------------------------------------------------------------------------
if modulo == MODULO_EOQ:
    encabezado(
        "Cantidad económica de pedido",
        "Calcula el tamaño de lote que minimiza el costo anual de ordenar y mantener inventario.",
    )
    formulas(
        r"Q^* = \sqrt{\dfrac{2DS}{H}}",
        r"CT = D\,C + \dfrac{D}{Q^*}\,S + \dfrac{Q^*}{2}\,H",
    )

    seccion("Datos del producto", primera=True)
    col1, col2 = st.columns(2, gap="large")
    with col1:
        D = st.number_input("Demanda anual (unidades)", min_value=1.0, value=1000.0)
        S = st.number_input("Costo de ordenar por pedido ($)", min_value=0.1, value=10.0)
    with col2:
        H = st.number_input("Costo de mantener por unidad al año ($)", min_value=0.1, value=2.5)
        C = st.number_input("Costo unitario del producto ($)", min_value=0.1, value=50.0)
        dias_habiles = st.number_input("Días hábiles por año", min_value=1, value=250)

    st.write("")
    if st.button("Calcular política de inventario", type="primary"):
        Q_optimo = math.sqrt((2 * D * S) / H)
        numero_pedidos = D / Q_optimo
        tiempo_entre_pedidos = dias_habiles / numero_pedidos
        costo_total = (D * C) + ((D / Q_optimo) * S) + ((Q_optimo / 2) * H)

        lectura(
            "Lote óptimo",
            f"{Q_optimo:,.2f}",
            "unidades por pedido",
            [
                ("Pedidos al año", f"{numero_pedidos:,.2f}"),
                ("Tiempo entre pedidos", f"{tiempo_entre_pedidos:,.2f} días"),
                ("Costo total mínimo", f"${costo_total:,.2f}"),
            ],
        )

# ---------------------------------------------------------------------------
# Módulo 2: EOQ con descuentos por cantidad
# ---------------------------------------------------------------------------
elif modulo == MODULO_DESC:
    encabezado(
        "EOQ con descuentos por cantidad",
        "El proveedor baja el precio al comprar más. Se evalúa cada rango y se elige el lote de menor costo total anual.",
    )
    formulas(
        r"Q_i = \sqrt{\dfrac{2DS}{H_i}} \qquad H_i = I \cdot C_i",
        r"CT_i = D\,C_i + \dfrac{D}{Q_i}\,S + \dfrac{Q_i}{2}\,H_i",
    )
    st.caption(
        "Si el EOQ de un rango queda por debajo de su mínimo, se compra justo el mínimo del rango. "
        "Si queda por encima de su límite superior, ese rango no es factible."
    )

    seccion("Datos del producto", primera=True)
    col1, col2 = st.columns(2, gap="large")
    with col1:
        D = st.number_input("Demanda anual (unidades)", min_value=1.0, value=5000.0)
        S = st.number_input("Costo de ordenar por pedido ($)", min_value=0.1, value=49.0)
    with col2:
        tipo_h = st.radio(
            "El costo de mantener se expresa como",
            ["% del precio unitario", "Monto fijo por unidad"],
            horizontal=True,
        )
        if tipo_h == "% del precio unitario":
            pct = st.number_input(
                "Costo de mantener (% del precio al año)",
                min_value=0.1, max_value=100.0, value=20.0,
            )
            h_fijo = None
        else:
            h_fijo = st.number_input("Costo de mantener por unidad al año ($)", min_value=0.1, value=1.0)
            pct = None

    seccion("Rangos de precio")
    n_rangos = st.number_input("Número de rangos", min_value=2, max_value=6, value=3, step=1)

    # Por defecto: 0 → $5.00 ; 1,000 → $4.80 ; 2,000 → $4.75
    defaults = [(0.0, 5.00), (1000.0, 4.80), (2000.0, 4.75)]
    rangos = []
    for i in range(int(n_rangos)):
        dq, dp = defaults[i] if i < len(defaults) else (3000.0 + 1000.0 * (i - 3), 4.75)
        cq, cp = st.columns(2, gap="large")
        if i == 0:
            qmin = cq.number_input("Cantidad mínima (R1)", value=0.0, disabled=True, key="qmin_0")
        else:
            qmin = cq.number_input(f"Cantidad mínima (R{i + 1})", min_value=0.0, value=dq, key=f"qmin_{i}")
        precio = cp.number_input(f"Precio unitario (R{i + 1}) ($)", min_value=0.01, value=dp, key=f"precio_{i}")
        rangos.append((qmin, precio))

    st.write("")
    if st.button("Calcular lote con descuentos", type="primary"):
        minimos = [r[0] for r in rangos]
        if any(b_ <= a_ for a_, b_ in zip(minimos, minimos[1:])):
            st.error("Las cantidades mínimas deben ir en orden creciente.")
        else:
            filas = []
            for i, (qmin, precio) in enumerate(rangos):
                qmax = rangos[i + 1][0] if i + 1 < len(rangos) else math.inf
                h = (pct / 100) * precio if pct is not None else h_fijo
                q_eoq = math.sqrt(2 * D * S / h)
                q = max(q_eoq, qmin)
                factible = q < qmax
                costo = D * precio + (D / q) * S + (q / 2) * h if factible else None

                if i == 0:
                    etiqueta = f"Menos de {qmax:,.0f}"
                elif qmax == math.inf:
                    etiqueta = f"{qmin:,.0f} o más"
                else:
                    etiqueta = f"{qmin:,.0f} a menos de {qmax:,.0f}"
                filas.append(
                    dict(etiqueta=etiqueta, precio=precio, h=h, q_eoq=q_eoq,
                         q=q, factible=factible, costo=costo, qmin=qmin)
                )

            candidatos = [i for i, f in enumerate(filas) if f["factible"]]
            mejor = min(candidatos, key=lambda i: filas[i]["costo"])
            g = filas[mejor]

            lectura(
                "Lote óptimo",
                f"{g['q']:,.2f}",
                "unidades por pedido",
                [
                    ("Rango aplicado", g["etiqueta"]),
                    ("Precio unitario", f"${g['precio']:,.2f}"),
                    ("Pedidos al año", f"{D / g['q']:,.2f}"),
                    ("Costo total mínimo", f"${g['costo']:,.2f}"),
                ],
            )

            seccion("Comparación por rango")
            tabla(
                ["Rango", "Precio", "EOQ calculado", "Lote a evaluar", "Costo total anual", "Estado"],
                [
                    [
                        f["etiqueta"],
                        f"${f['precio']:,.2f}",
                        f"{f['q_eoq']:,.2f}",
                        f"{f['q']:,.2f}" if f["factible"] else "—",
                        f"${f['costo']:,.2f}" if f["factible"] else "—",
                        "Óptimo" if i == mejor else ("Factible" if f["factible"] else "No factible"),
                    ]
                    for i, f in enumerate(filas)
                ],
                destacada=mejor,
                apagadas=[i for i, f in enumerate(filas) if not f["factible"]],
            )

# ---------------------------------------------------------------------------
# Módulo 3: EOQ con faltantes
# ---------------------------------------------------------------------------
elif modulo == MODULO_FALT:
    encabezado(
        "EOQ con faltantes",
        "Permite quedarse sin inventario y surtir después los pedidos pendientes, a cambio de un costo por faltante.",
    )
    formulas(
        r"Q^* = \sqrt{\dfrac{2DS}{H}}\,\sqrt{\dfrac{H+P}{P}}",
        r"I_{max} = Q^*\,\dfrac{P}{H+P} \qquad B_{max} = Q^*\,\dfrac{H}{H+P}",
        r"CT = D\,C + \dfrac{D}{Q}\,S + \dfrac{I_{max}^2}{2Q}\,H + \dfrac{B_{max}^2}{2Q}\,P",
    )
    st.caption("P es el costo de tener una unidad en faltante (pedido pendiente) durante un año.")

    seccion("Datos del producto", primera=True)
    col1, col2 = st.columns(2, gap="large")
    with col1:
        D = st.number_input("Demanda anual (unidades)", min_value=1.0, value=1000.0)
        S = st.number_input("Costo de ordenar por pedido ($)", min_value=0.1, value=10.0)
        H = st.number_input("Costo de mantener por unidad al año ($)", min_value=0.1, value=2.5)
    with col2:
        P = st.number_input("Costo de faltante por unidad al año ($)", min_value=0.1, value=5.0)
        C = st.number_input("Costo unitario del producto ($)", min_value=0.1, value=50.0)
        dias_habiles = st.number_input("Días hábiles por año", min_value=1, value=250)

    st.write("")
    if st.button("Calcular política con faltantes", type="primary"):
        Q = math.sqrt(2 * D * S / H) * math.sqrt((H + P) / P)
        inv_max = Q * P / (H + P)
        faltante_max = Q - inv_max
        pedidos = D / Q
        ciclo = dias_habiles * Q / D
        dias_con_inv = dias_habiles * inv_max / D
        dias_faltante = dias_habiles * faltante_max / D
        costo_total = (
            D * C
            + (D / Q) * S
            + (inv_max ** 2 / (2 * Q)) * H
            + (faltante_max ** 2 / (2 * Q)) * P
        )

        lectura(
            "Lote óptimo",
            f"{Q:,.2f}",
            "unidades por pedido",
            [
                ("Inventario máximo", f"{inv_max:,.2f}"),
                ("Faltante máximo", f"{faltante_max:,.2f}"),
                ("Pedidos al año", f"{pedidos:,.2f}"),
                ("Tiempo entre pedidos", f"{ciclo:,.2f} días"),
                ("Días con inventario", f"{dias_con_inv:,.2f}"),
                ("Días con faltante", f"{dias_faltante:,.2f}"),
                ("Costo total mínimo", f"${costo_total:,.2f}"),
            ],
        )

# ---------------------------------------------------------------------------
# Módulo 4: EOQ de producción sin déficit
# ---------------------------------------------------------------------------
elif modulo == MODULO_PROD:
    encabezado(
        "EOQ de producción sin déficit",
        "Calcula el lote de producción cuando el inventario se forma poco a poco mientras se produce y no se permiten faltantes.",
    )
    formulas(
        r"Q^* = \sqrt{\dfrac{2DS}{H\left(1-\dfrac{D}{p}\right)}}",
        r"I_{max} = Q^*\left(1-\dfrac{D}{p}\right) \qquad t_p = \dfrac{Q^*}{p}",
        r"CT = D\,C + \dfrac{D}{Q}\,S + \dfrac{I_{max}}{2}\,H",
    )
    st.caption("La tasa de producción anual (p) debe ser mayor que la demanda anual (D).")

    seccion("Datos del producto", primera=True)
    col1, col2 = st.columns(2, gap="large")
    with col1:
        D = st.number_input("Demanda anual (unidades)", min_value=1.0, value=1000.0)
        p = st.number_input("Tasa de producción anual (unidades)", min_value=1.0, value=4000.0)
        S = st.number_input("Costo de preparación por corrida ($)", min_value=0.1, value=10.0)
    with col2:
        H = st.number_input("Costo de mantener por unidad al año ($)", min_value=0.1, value=2.5)
        C = st.number_input("Costo unitario de producción ($)", min_value=0.1, value=50.0)
        dias_habiles = st.number_input("Días hábiles por año", min_value=1, value=250)

    st.write("")
    if st.button("Calcular lote de producción", type="primary"):
        if p <= D:
            st.error(
                "La tasa de producción debe ser mayor que la demanda; "
                "de lo contrario nunca se acumula inventario."
            )
        else:
            factor = 1 - D / p
            Q = math.sqrt(2 * D * S / (H * factor))
            inv_max = Q * factor
            corridas = D / Q
            ciclo = dias_habiles * Q / D
            dias_prod = dias_habiles * Q / p
            costo_total = D * C + (D / Q) * S + (inv_max / 2) * H

            lectura(
                "Lote óptimo de producción",
                f"{Q:,.2f}",
                "unidades por corrida",
                [
                    ("Inventario máximo", f"{inv_max:,.2f}"),
                    ("Corridas al año", f"{corridas:,.2f}"),
                    ("Tiempo entre corridas", f"{ciclo:,.2f} días"),
                    ("Días de producción", f"{dias_prod:,.2f}"),
                    ("Costo total mínimo", f"${costo_total:,.2f}"),
                ],
            )

# ---------------------------------------------------------------------------
# Módulo 5: EOQ de producción con déficit
# ---------------------------------------------------------------------------
elif modulo == MODULO_PROD_DEF:
    encabezado(
        "EOQ de producción con déficit",
        "Combina producción gradual y faltantes permitidos: se acumulan pedidos pendientes que se surten al reanudar la producción.",
    )
    formulas(
        r"Q^* = \sqrt{\dfrac{2DS}{H}}\,\sqrt{\dfrac{p}{p-D}}\,\sqrt{\dfrac{H+P}{P}}",
        r"I_{max} = Q^*\left(1-\dfrac{D}{p}\right)\dfrac{P}{H+P} \qquad B_{max} = Q^*\left(1-\dfrac{D}{p}\right)\dfrac{H}{H+P}",
        r"CT = D\,C + \dfrac{D}{Q}\,S + \dfrac{H\,I_{max}^2 + P\,B_{max}^2}{2Q\left(1-\dfrac{D}{p}\right)}",
    )
    st.caption(
        "p es la tasa de producción anual (mayor que D) y P es el costo de tener una unidad "
        "en faltante durante un año."
    )

    seccion("Datos del producto", primera=True)
    col1, col2 = st.columns(2, gap="large")
    with col1:
        D = st.number_input("Demanda anual (unidades)", min_value=1.0, value=1000.0)
        p = st.number_input("Tasa de producción anual (unidades)", min_value=1.0, value=4000.0)
        S = st.number_input("Costo de preparación por corrida ($)", min_value=0.1, value=10.0)
        H = st.number_input("Costo de mantener por unidad al año ($)", min_value=0.1, value=2.5)
    with col2:
        P = st.number_input("Costo de faltante por unidad al año ($)", min_value=0.1, value=5.0)
        C = st.number_input("Costo unitario de producción ($)", min_value=0.1, value=50.0)
        dias_habiles = st.number_input("Días hábiles por año", min_value=1, value=250)

    st.write("")
    if st.button("Calcular lote de producción", type="primary"):
        if p <= D:
            st.error(
                "La tasa de producción debe ser mayor que la demanda; "
                "de lo contrario nunca se acumula inventario."
            )
        else:
            factor = 1 - D / p
            Q = math.sqrt(2 * D * S / H) * math.sqrt(p / (p - D)) * math.sqrt((H + P) / P)
            inv_max = Q * factor * P / (H + P)
            faltante_max = Q * factor * H / (H + P)
            corridas = D / Q
            ciclo = dias_habiles * Q / D
            dias_prod = dias_habiles * Q / p
            costo_total = (
                D * C
                + (D / Q) * S
                + (H * inv_max ** 2 + P * faltante_max ** 2) / (2 * Q * factor)
            )

            lectura(
                "Lote óptimo de producción",
                f"{Q:,.2f}",
                "unidades por corrida",
                [
                    ("Inventario máximo", f"{inv_max:,.2f}"),
                    ("Faltante máximo", f"{faltante_max:,.2f}"),
                    ("Corridas al año", f"{corridas:,.2f}"),
                    ("Tiempo entre corridas", f"{ciclo:,.2f} días"),
                    ("Días de producción", f"{dias_prod:,.2f}"),
                    ("Costo total mínimo", f"${costo_total:,.2f}"),
                ],
            )

# ---------------------------------------------------------------------------
# Módulo 6: Programación lineal
# ---------------------------------------------------------------------------
else:
    encabezado(
        "Programación lineal",
        "Encuentra los valores de X1 y X2 que maximizan la utilidad respetando tus restricciones.",
    )

    seccion("Función objetivo", primera=True)
    oc1, oc2 = st.columns(2, gap="large")
    c1 = oc1.number_input("Utilidad por unidad de X1 (c1)", value=3.0)
    c2 = oc2.number_input("Utilidad por unidad de X2 (c2)", value=5.0)

    seccion("Restricciones: a1·X1 + a2·X2 ≤ b")
    n_restr = st.number_input(
        "Número de restricciones", min_value=1, max_value=6, value=3, step=1
    )

    # Valores por defecto: problema clásico  max 3X1 + 5X2
    #   X1 <= 4 ;  2·X2 <= 12 ;  3·X1 + 2·X2 <= 18
    defaults = [(1.0, 0.0, 4.0), (0.0, 2.0, 12.0), (3.0, 2.0, 18.0)]

    A, b = [], []
    for i in range(int(n_restr)):
        d1, d2, db = defaults[i] if i < len(defaults) else (1.0, 1.0, 10.0)
        col1, col2, col3 = st.columns(3, gap="large")
        a1 = col1.number_input(f"X1 (R{i + 1})", value=d1, key=f"a1_{i}")
        a2 = col2.number_input(f"X2 (R{i + 1})", value=d2, key=f"a2_{i}")
        bi = col3.number_input(f"Límite b (R{i + 1})", value=db, key=f"b_{i}")
        A.append([a1, a2])
        b.append(bi)

    seccion("Modelo")
    lineas = (
        [rf"\max\; Z = {expresion(c1, c2)}", r"\text{sujeto a:}"]
        + [rf"{expresion(fila[0], fila[1])} \leq {limite:g}" for fila, limite in zip(A, b)]
        + [r"x_1,\, x_2 \geq 0"]
    )
    st.latex(r"\begin{array}{l}" + r" \\ ".join(lineas) + r"\end{array}")

    st.write("")
    if st.button("Resolver con método Simplex", type="primary"):
        # linprog minimiza, por eso se niegan los coeficientes para maximizar
        res = linprog(
            [-c1, -c2],
            A_ub=A,
            b_ub=b,
            bounds=[(0, None), (0, None)],
            method="highs",
        )

        if res.success:
            lectura(
                "Utilidad máxima (Z)",
                f"{-res.fun:,.2f}",
                "",
                [
                    ("Valor de X1", f"{res.x[0]:,.2f}"),
                    ("Valor de X2", f"{res.x[1]:,.2f}"),
                ],
            )
        elif res.status == 3:
            st.error(
                "El problema no está acotado: alguna variable puede crecer sin límite. "
                "Agrega una restricción que limite X1 y X2."
            )
        elif res.status == 2:
            st.error(
                "El problema es infactible: las restricciones se contradicen. "
                "Revisa los límites b."
            )
        else:
            st.error(f"No se encontró solución: {res.message}")