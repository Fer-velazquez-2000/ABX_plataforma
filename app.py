import streamlit as st

##################################################### ESTILOS #####################################################

st.set_page_config(
    page_title="ABX Solutions",
    page_icon="static/logo.png",
    layout="centered",
    initial_sidebar_state="collapsed"
)

st.markdown("""
<style>
    [data-testid="stMain"] > div {
        padding-top: 1w;
    }
            
    [data-testid="stBaseButton-headerNoPadding"] {
        display: None;
    }
            
    [data-testid="stHeader"] { display: none !important; }
            
    button[kind="primary"] { 
        height: 50px; 
        width: 40%;
        border: solid .05em rgba(0,0,0,0);  
        background-color: #ea0a2a;
        color: #white;
        border-radius: 30px;
        display: block;
        margin: 0 auto;
        justify-content: center;
    }

    button[kind="primary"]:hover { 
        background-color: white;
        border: solid 0.3em #3f5364;
        color: #3f5364;
    }
            
    [data-testid="stTextInputRootElement"] input {
        color: white; 
    }
</style>
""", unsafe_allow_html=True)


c1,c2,c3 = st.columns([1,2,1])
with c2:
    st.image("static/logo.png", use_container_width =True)



##################################################### INICIO DE SESIÓN #####################################################

# Se pide usuario y contraseña para iniciar sesión, si es correcto se redirecciona a la página de dashboard

c1,c2,c3 = st.columns([1,4,1])
with c2:
    usuario = st.text_input("Usuario", placeholder="Usuario", label_visibility="hidden")
    password = st.text_input("Contraseña", type="password", placeholder="Contraseña", label_visibility="hidden")
    st.markdown("<br>", unsafe_allow_html=True)

if st.button("**Iniciar Sesión**", type="primary"):
    if usuario == "admin" and password == "user1928":
        st.switch_page("pages/dashboard.py")
    else:
        st.error("Usuario o contraseña incorrectos")




