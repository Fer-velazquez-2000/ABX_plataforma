import streamlit as st
import pandas as pd
import plotly.express as px
from st_aggrid import AgGrid, GridOptionsBuilder, JsCode
from st_aggrid.shared import GridUpdateMode
import random


##################################################### ESTILOS #####################################################

# Configurar el formato de la página, el logo, título, etc

st.set_page_config(
    page_title="Inventario",
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

    [data-testid="stExpander"] summary div[data-testid="stMarkdownContainer"] {
        font-size: 1.7rem !important;
        font-weight: bold;
    }

    [data-testid="stExpander"] {
        box-shadow: 0 4px 12px rgba(0,0,0,0.1);
        border: 0px solid #ffffff;
    }
</style>
""", unsafe_allow_html=True)

st.logo("static/logo.png")

st.title("📋 Inventario")


##################################################### Barra Lateral #####################################################

# Botones de navegación
botones = [
    {"label": "General", "img": "static/general.png", "page": "Dashboard"},
    {"label": "Embarques", "img": "static/embarques.png", "page": "Embarques"},
]


for b in botones:
    st.sidebar.image(b["img"], use_container_width=True)

    if st.sidebar.button(b["label"]):
        st.switch_page("pages/" + b["page"] + ".py")


##################################################### Datos ##############################################################

# Cargar datos
if 'df' not in st.session_state:
    st.session_state['df'] = pd.read_excel(
        "EMBARQUES 2025.xlsx",
        sheet_name="MAYO 2025",
    )

# Seleccionar columnas necesarias
df = st.session_state['df']
df = (
    df[[
        "FOLIO",
        "CLIENTE",
        "DESTINO",
        "INICIO DE CARGA",
        "UNIDAD",
        "TIEMPO DE CARGA"
    ]]
    .dropna(subset=["TIEMPO DE CARGA"])
    .copy()
)



###### Datos Simulados de Productos ######
pedidos = pd.DataFrame({
    "Producto": [
        "POLIN PINT. 8X2.5", "POLIN PINT. 4X2", "POLIN PINT. 6X2",
        "PTR 4X4 C-11", "TUBO RED. 1.90x105x252", "PTR 3x2 C-14",
        "POLIN PINT. 5X1.5", "VIGA IPN 200"
    ],
    "Pedido (T)": [3.82, 1.24, 4.31, 3.28, 2.15, 1.86, 2.50, 3.75],
    "Disponible (T)": [2.00, 1.24, 4.50, 5.00, 2.50, 1.20, 2.00, 4.00],
    "Apartado (T)": [1, 0, 1.2, 0, 2, 0, 0, 3]
})

# Calcular nivel de inventario
def evaluar_estado(pedido, stock):
    if stock < pedido:
        return "🟥 Sin Inventario"
    elif stock == pedido:
        return "🟨 Bajo Stock"
    else:
        return "🟩 Suficiente"

pedidos["Estado"] = pedidos.apply(lambda row: evaluar_estado(row["Pedido (T)"], row["Disponible (T)"]), axis=1)

# Datos Simulados de Etapas
etapas = pd.DataFrame({
    "Etapa": ["En preparación", "Corriendo", "Listo para embarcar", "En camino", "Entregado"],
    "Pedidos": [12, 8, 15, 9, 6]
})



########### Datos Simulados de Pedidos Por Clientes ###########
clientes = [
    {"id_cliente": 101, "nombre": "Aceros Monterrey"},
    {"id_cliente": 102, "nombre": "Constructora del Norte"},
    {"id_cliente": 103, "nombre": "Grupo Industrial Alfa"},
]

productos = [
    "POLIN PINT. 8X2.5", "PTR 3x2 C-14", "TUBO RED. 1.90x105x252",
    "VIGA IPN 200", "POLIN PINT. 6X2"
]

estados = ["Pendiente", "Facturado", "Completo"]



##################################################### Gráficos ##############################################################

# Tarjetas de métricas
col1, col2, col3 = st.columns(3)
col1.metric("🚨 Productos Sin Inventario", str((pedidos["Estado"] == "🟥 Sin Inventario").sum()))
col2.metric("⚠️ Productos Bajo Stock", str((pedidos["Estado"] == "🟨 Bajo Stock").sum()))
col3.metric("📄 Productos Mal Registrados", "0")


c1, c2 = st.columns([2,2])
with c1:
    #####  Gráfica de etapas  #####
    fig = px.bar(
        etapas,
    x="Etapa",
    y="Pedidos",
    orientation="v",
    text="Pedidos",
    title="<b>📌 Status de Pedidos</b>",
    color_discrete_sequence=["#3f5364"] 
)

    fig.update_layout(
        title_font=dict(size=26, color="#3f5364", family="Arial"),
        xaxis=dict(
            title=None,
            color="#3f5364",
            showgrid=False,
            tickfont=dict(
                color="#3f5364",
                size=10,
                family="Arial",
                weight="bold")
    ),
    yaxis=dict(
        title=None,
    ),
    plot_bgcolor="white",
    paper_bgcolor="white",
)

    fig.update_traces(
        textposition="outside",
        textfont=dict(color="#3f5364", size=12, family="Arial")
    )

    st.plotly_chart(fig, use_container_width=True)

with c2:
    ############ Tabla Semaforizada de Inventario ############
    st.subheader("📝 Productos con Pedido vs Inventario")
    pedidos["Seleccionado"] = False
    gb = GridOptionsBuilder.from_dataframe(pedidos)
    gb.configure_column(
        "Producto",
        header_name="Producto",
        editable=False,
        cellStyle=JsCode("""
        function(params) {
            if (params.data.Seleccionado) {
            return {backgroundColor:'#FF6B6B', color:'white', fontWeight:'bold'};
            }
            return {};
        }
        """)
    )

    # Checkbox para marcar productos incorrectos
    gb.configure_column(
        "Seleccionado",
        header_name="Marcar",
        editable=True,
        cellEditor="agCheckboxCellEditor",
        cellRenderer="agCheckboxCellRenderer"
    )
    gb.configure_grid_options(getRowStyle=JsCode("""
    function(params) {
        if (params.data.Seleccionado) {
        return {backgroundColor:'#FF6B6B', color:'white'};
        }
    }
    """))

    gridOptions = gb.build()
    grid_response = AgGrid(
        pedidos,
        gridOptions=gridOptions,
        update_mode=GridUpdateMode.VALUE_CHANGED,
        allow_unsafe_jscode=True,
        height=350,
        fit_columns_on_grid_load=True
    )

    df_actualizado = grid_response["data"]
    seleccionados = df_actualizado[df_actualizado["Seleccionado"] == True]


####### Tarjetas Expandibles de Pedidos por cliente #######
for cliente in clientes:
    pedidos_clientes = []
    for i in range(random.randint(2, 5)):
        pedidos_clientes.append({
            "Folio": f"{cliente['id_cliente']}-{i+1}",
            "Producto": random.choice(productos),
            "Cantidad (t)": round(random.uniform(1, 5), 2),
            "Status": random.choice(estados)
        })

    df_pedidos = pd.DataFrame(pedidos_clientes)
    with st.expander(f"###### 📦 Pedidos de {cliente['nombre']}"):
        st.dataframe(df_pedidos, use_container_width=True)