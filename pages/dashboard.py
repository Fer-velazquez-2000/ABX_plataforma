import streamlit as st
import pandas as pd
import plotly.express as px
import base64

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
</style>
""", unsafe_allow_html=True)

st.logo("static/logo.png")

st.title("Dashboard")

##################################################### BARRA LATERAL #####################################################

# Botones de Navegación
botones = [
    {"label": "Inventarios", "img": "static/inventarios.png", "page": "Inventario"},
    {"label": "Embarques", "img": "static/embarques.png", "page": "Embarques"},
]

for b in botones:
    st.sidebar.image(b["img"], use_container_width=True)

    if st.sidebar.button(b["label"]):
        st.switch_page("pages/" + b["page"].lower() + ".py")



##################################################### DATOS #####################################################

# Cargar datos
if 'df' not in st.session_state:
    st.session_state['df'] = pd.read_excel(
        "EMBARQUES 2025.xlsx",
        sheet_name="MAYO 2025",
    )
df = st.session_state['df']

# Eliminar filas con valores vacíos en la columna TOTAL TON
df["TOTAL TON"] = pd.to_numeric(df["TOTAL TON"], errors="coerce")
df = df[df["TOTAL TON"].notna()]

# Cálculos de Métricas
total_embarques = len(df) / 30
total_toneladas = df["TOTAL TON"].sum() / 30
eficiencia_embarque = 52 # Dato Simulado de Posible Indicador
max_toneladas = df["TOTAL TON"].max()

# Datos simulados de pedidos
pedidos = pd.DataFrame({
"Producto": [
    "POLIN PINT. 8X2.5", "POLIN PINT. 4X2", "POLIN PINT. 6X2", "PTR 4X4 C-11",
    "TUBO RED. 1.90x105x252", "PTR 3x2 C-14", "POLIN PINT. 5X1.5", "VIGA IPN 200"
],
"Pedido (toneladas)": [3.82, 1.24, 4.31, 3.28, 2.15, 1.86, 2.50, 3.75],
"Existencia (toneladas)": [2.00, 1.24, 4.50, 5.00, 2.50, 1.20, 2.00, 4.00]
})


# Cálculos para la tabla de inventario
def evaluar_estado(row):
    if row["Existencia (toneladas)"] < row["Pedido (toneladas)"]:
        return "🟥 Sin Inventario"
    else:
        return "🟩 Suficiente"

pedidos["Estado"] = pedidos.apply(evaluar_estado, axis=1)
tabla = pedidos[["Producto", "Existencia (toneladas)", "Estado"]]
pct_bajo_stock = (tabla["Estado"] == "🟥 Sin Inventario").mean() * 100


##################################################### GRÁFICOS #####################################################


# Tarjetas de métricas
col1, col2, col3, col4 = st.columns(4)
col1.metric("Total de Embarques Diarios", f"{total_embarques:,.0f}")
col2.metric("Total Toneladas Diarias", f"{total_toneladas:,.0f}")
col3.metric("Eficiencia de Embarque", f"{eficiencia_embarque:,.0f}%")
col4.metric("% de Productos con Bajo Stock", f"{pct_bajo_stock:.1f}%")



c1, c2 = st.columns(2)
with c1:
    ###### Gráfico de Top de Clientes ######
    df_top = df.groupby("CLIENTE")["TOTAL TON"].sum().sort_values(ascending=True).head(5).reset_index()
    df_top["TOTAL TON"] = df_top["TOTAL TON"] / 30
    df_top["TOTAL TON"] = df_top["TOTAL TON"].round(2)
    fig = px.bar(df_top, y="CLIENTE", x="TOTAL TON", title="Top Clientes por Promedio Diario de Toneladas Embarcadas",
                labels={"CLIENTE": "Cliente", "TOTAL TON": "Toneladas"})
    fig.update_layout(xaxis_tickangle=0)

    fig.update_layout(
        title_font=dict(size=18, color="#3f5364", family="Arial"),
        yaxis=dict(
            title=None,
            color="#3f5364",
            showgrid=False,
            tickfont=dict(
                color="#3f5364",
                size=10,
                family="Arial",
                weight="bold")
        ),
        xaxis=dict(
            title=None,
        ),
        plot_bgcolor="white",
        paper_bgcolor="white",
    )

    st.plotly_chart(fig)

with c2:
    # Tabla de Inventario Sin Stock
    st.markdown("<br>", unsafe_allow_html=True)
    st.write("##### Productos con Bajo Stock")
    tabla = pedidos[pedidos["Estado"] == "🟥 Sin Inventario"][["Producto", "Existencia (toneladas)", "Estado"]]
    st.dataframe(tabla, use_container_width=True)
    





