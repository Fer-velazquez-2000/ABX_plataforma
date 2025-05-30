import streamlit as st
import pandas as pd
import plotly.express as px
import datetime

##################################################### ESTILOS #####################################################
# Configurar el formato de la página, el logo, título, etc


st.set_page_config(
    page_title="Dashboard",
    page_icon="static/logo.png",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
    [data-testid="stSidebarNavLink"] {
        display: none;
    }
    
    [data-testid="stMetric"] {
        background-color: white;
        border-radius: 10px;
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
        transition: box-shadow 0.3s ease;
    }


    [data-testid="stMetricLabel"] > div > div > p {
        font-size: 1.5vm; 
        font-weight: bold; 
        margin: 0; 
        padding: 0;
        padding-left: 15px;
        margin-top: 10px;
    }

    [data-testid="stMetricValue"] {
        padding-left: 15px; 
    }

    [data-testid="stMetricDelta"] {
        position: absolute;
        top: 15px;
        right: 10px;
        font-size: 1em;
        font-weight: bold;
    }
            
    [data-testid="stImage"] {
        width: 80% !important;
        height: 5vw !important;
    }
            

    button[kind="secondary"] { 
        height: 50px; 
        width: 80%;
        border: solid .05em rgba(0,0,0,0);  
        background-color: #ea0a2a;
        color: #white;
        border-radius: 0 0 10px 10px;
        display: block;
        margin: 0 auto;
        justify-content: center;
    }

    button[kind="secondary"]:hover { 
        background-color: white;
        background-color: #3f5364;
        border: solid .05em rgba(0,0,0,0);
        color: white;
        scale: 1.05;
    }
            
    [data-testid="stElementToolbarButtonIcon"] {
        display: none;
    }
            
    [data-testid="stBaseButton-headerNoPadding"] {
        display: None;
    }

    
    [data-testid="stDataFrameResizable"] .stDataFrameGlideDataEditor {
    --gdg-bg-header: black !important;  /* Azul oscuro */
    --gdg-text-header: #ffffff !important;  /* Texto blanco */
    --gdg-border-color: black !important;  /* Borde entre celdas */
    }
    
    [data-testid="stHeader"] { display: none !important; }        

    [data-testid="stMain"] > div {
        padding-top: 1rem;
        padding-left: 3rem;
        padding-right: 3rem;
    }
            
    [data-testid="stLogo"] {
        width: 10vw !important;
        height: 5vw;
        margin-top:1vw;
        margin-left: 2.5vw;
    }
            
    [data-testid="stSelectbox"] div[data-baseweb="select"] {
        background-color: #1c1c1c;
        color: white;
        width: 80%;
        justify-content: center !important;
    }
    
    /* Cambia el color de fondo cuando una opción está seleccionada */
    [data-testid="stSelectbox"] div[data-baseweb="select"] > div {
        background-color: #1c1c1c;
        color: white;
        justify-content: center !important;
    }
    
    /* Cambia el color de las opciones en el desplegable */
    [data-testid="stSelectbox"] input {
        background-color: #1c1c1c;
        color: white;
    }
            
    [data-testid="stSelectboxVirtualDropdown"] {
        background-color: #1c1c1c;
        color: white;
    }
</style>
""", unsafe_allow_html=True)

st.logo("static/logo.png")

st.title("📦 Embarques")




##################################################### DATOS #####################################################

# Cargar Datos
if 'df' not in st.session_state:
    st.session_state['df'] = pd.read_excel(
        "EMBARQUES 2025.xlsx",
        sheet_name="MAYO 2025",
    )

# Filtrar datos vacíos en columna Partidas Cargadas
df = st.session_state['df']
df = df[df["PARTIDAS CARGADAS"].notna()]

# Seleccionar columnas necesarias
df = (
    df[[
        "FOLIO",
        "CLIENTE",
        "DESTINO",
        "INICIO DE CARGA",
        "UNIDAD",
        "TIEMPO DE CARGA",
        "PARTIDAS CARGADAS",
        "NUMERO DE NAVES"
    ]]
    .dropna(subset=["TIEMPO DE CARGA"])
    .copy()
)

# Convertir valores de fecha a timedelta para calcular el promedio
def convertir_a_timedelta(valor):
    if isinstance(valor, datetime.datetime):
        return datetime.timedelta(hours=valor.hour, minutes=valor.minute, seconds=valor.second)
    elif isinstance(valor, datetime.time):
        return datetime.timedelta(hours=valor.hour, minutes=valor.minute, seconds=valor.second)
    elif isinstance(valor, str):
        try:
            return pd.to_timedelta(valor)
        except:
            return pd.NaT
    elif isinstance(valor, pd.Timedelta):
        return valor
    else:
        return pd.NaT
df["TIEMPO DE CARGA"] = df["TIEMPO DE CARGA"].apply(convertir_a_timedelta)


##################################################### BARRA LATERAL #####################################################

# Filtro por Partidas Cargadas
partidas = ["Todas"] + sorted(df["PARTIDAS CARGADAS"].astype(str).unique())
seleccion = st.sidebar.selectbox("**Filtro por Partidas Cargadas**", partidas)
if seleccion != "Todas":
    df_ship = df[df["PARTIDAS CARGADAS"].astype(str) == seleccion].copy()
else:
    df_ship = df.copy()


# Filtro de Número de Nave
num_nave = ["Todas"] + sorted(df_ship["NUMERO DE NAVES"].unique())
seleccion_nave = st.sidebar.selectbox("**Filtro por Naves**", num_nave)
if seleccion_nave != "Todas":
    df_ship = df_ship[df_ship["NUMERO DE NAVES"] == seleccion_nave].copy()
else:
    df_ship = df_ship.copy()

# Botones de Navegación
botones = [
    {"label": "General", "img": "static/general.png", "page": "Dashboard"},
    {"label": "Inventarios", "img": "static/inventarios.png", "page": "Inventario"},
]


for b in botones:
    st.sidebar.image(b["img"], use_container_width=True)

    if st.sidebar.button(b["label"]):
        st.switch_page("pages/" + b["page"].lower() + ".py")


####################################   Cálculos   #####################################

# Calcular métricas de tiempos
mean_td    = df_ship["TIEMPO DE CARGA"].mean()
count_exceed = (df_ship["TIEMPO DE CARGA"] > mean_td).sum()
pct_exceed   = (count_exceed / len(df_ship) * 100) if len(df_ship) else 0

# Formato HH:MM:SS
if pd.isna(mean_td):
    prom_str = "00:00:00"
else:
    secs = int(mean_td.total_seconds())
    h, m = divmod(secs, 3600)
    m, s = divmod(m, 60)
    prom_str = f"{h:02d}:{m:02d}:{s:02d}"



##############################################  GRÁFICOS  ##############################################################

# Tarjetas de métricas
c1, c2, c3 = st.columns(3)
c1.metric("⏱️ Tiempo promedio", prom_str)
c2.metric("⚠️ Exceden tiempo", f"{count_exceed}")
c3.metric("📉 % de retrasos", f"{pct_exceed:.1f}%")

#### Tabla semaforizada de Embarques ####
tabla = df_ship[[
    "UNIDAD",
    "FOLIO",
    "CLIENTE",
    "DESTINO",
    "INICIO DE CARGA",
    "TIEMPO DE CARGA"
]].copy()

# Función que pintará en rojo o verde la celda según el tiempo de carga
def highlight_delay(val):
    return (
        'background-color: #FF6B6B; color: white;'
        if val > mean_td
        else 'background-color: #51CF66; color: white;'
    )
tabla_styled = (
    tabla
    .style
    .applymap(highlight_delay, subset=["TIEMPO DE CARGA"])
    .format({
        "TIEMPO DE CARGA": lambda td: (
            f"{int(td.total_seconds()//3600):02d}:"
            f"{int((td.total_seconds()%3600)//60):02d}:"
            f"{int(td.total_seconds()%60):02d}"
        )
    })
)

# Tabla semaforizada de Embarques
st.write("#### 📋 Detalle de Embarques")
st.dataframe(
    tabla_styled,
    hide_index=True,
    use_container_width=True,
    height=400
)