"""
Castaño Logistics MVP
=====================
Aplicación para supervisores de terreno.
- Mi Ruta: Consulta rutas planificadas (Spanner Graph)
- Rendir Gastos: Ingesta de rendiciones (BigQuery)

Autor: Castaño Team
Fecha: 2026-02
"""

import streamlit as st
import pandas as pd
import uuid
from datetime import date, datetime

# ================================================================
# CONFIGURACIÓN DE PÁGINA
# ================================================================
st.set_page_config(
    page_title="Castaño Logistics",
    page_icon="🚚",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ================================================================
# CONFIGURACIÓN GCP (Modificar según tu proyecto)
# ================================================================
# IMPORTANTE: Cambiar a False cuando tengas GCP configurado
DEMO_MODE = True  # Usar datos demo sin conexión a GCP

GCP_PROJECT = "tu-proyecto-gcp"
SPANNER_INSTANCE = "logistics-instance"
SPANNER_DATABASE = "logistics-db"
BIGQUERY_DATASET = "lakehouse_gold"
BIGQUERY_TABLE = "Fact_Rendicion"

# ================================================================
# SISTEMA DE AUTENTICACIÓN SIMPLE (MVP)
# Usuarios generados desde datos reales de Base de Datos
# ================================================================
USUARIOS_VALIDOS = {
    # Administrador
    'admin': {'password': 'castano2026', 'nombre': 'Administrador', 'id': 'admin001', 'rol': 'admin'},
    
    # Zonales (Jefes de Zona) - Pueden gestionar rutas de su equipo
    'ricardo': {'password': 'zonal123', 'nombre': 'Ricardo Millar', 'id': 'zce0bf2f8', 'rol': 'zonal'},
    'alvaro': {'password': 'zonal123', 'nombre': 'Alvaro Sauterel', 'id': 'z002', 'rol': 'zonal'},
    'jerson': {'password': 'zonal123', 'nombre': 'Jerson Placencia', 'id': 'z003', 'rol': 'zonal'},
    
    # Supervisores - Solo ven su ruta y rinden gastos
    'harry': {'password': 'ruta123', 'nombre': 'Harry Urra', 'id': 's41861921', 'rol': 'supervisor'},
    'rodrigo': {'password': 'ruta123', 'nombre': 'Rodrigo Castro', 'id': 's3048eab6', 'rol': 'supervisor'},
    'daniela': {'password': 'ruta123', 'nombre': 'Daniela Leon', 'id': 's52b7164b', 'rol': 'supervisor'},
    'alejandro': {'password': 'ruta123', 'nombre': 'Alejandro Perez', 'id': 's4e75d6f2', 'rol': 'supervisor'},
    'lisset': {'password': 'ruta123', 'nombre': 'Lisset Medina', 'id': 's0d9492dc', 'rol': 'supervisor'},
    'gema': {'password': 'ruta123', 'nombre': 'Gema Nuñez', 'id': 's1dc69e68', 'rol': 'supervisor'},
    'wladimir': {'password': 'ruta123', 'nombre': 'Wladimir Lara', 'id': 's88ae2d48', 'rol': 'supervisor'},
    'alexander': {'password': 'ruta123', 'nombre': 'Alexander Yañez', 'id': 's0df53ceb', 'rol': 'supervisor'},
    'edgardo': {'password': 'ruta123', 'nombre': 'Edgardo Ordenes', 'id': 'sbe29bbd6', 'rol': 'supervisor'},
    'mauro': {'password': 'ruta123', 'nombre': 'Mauro Saenz', 'id': 's03ff5266', 'rol': 'supervisor'},
}

def inicializar_sesion():
    """Inicializa variables de sesión si no existen."""
    if 'autenticado' not in st.session_state:
        st.session_state.autenticado = False
    if 'usuario' not in st.session_state:
        st.session_state.usuario = None
    if 'pagina' not in st.session_state:
        st.session_state.pagina = 'Mi Ruta'
    if 'supervisor_seleccionado' not in st.session_state:
        st.session_state.supervisor_seleccionado = None

def verificar_credenciales(usuario: str, password: str) -> bool:
    """Verifica las credenciales del usuario."""
    if usuario in USUARIOS_VALIDOS:
        if USUARIOS_VALIDOS[usuario]['password'] == password:
            st.session_state.autenticado = True
            st.session_state.usuario = {
                'username': usuario,
                'nombre': USUARIOS_VALIDOS[usuario]['nombre'],
                'id': USUARIOS_VALIDOS[usuario]['id'],
                'rol': USUARIOS_VALIDOS[usuario].get('rol', 'supervisor')
            }
            # Zonales van directo a gestionar rutas
            if st.session_state.usuario['rol'] == 'zonal':
                st.session_state.pagina = 'Gestionar Rutas'
            return True
    return False

def cerrar_sesion():
    """Cierra la sesión del usuario."""
    st.session_state.autenticado = False
    st.session_state.usuario = None
    st.session_state.pagina = 'Mi Ruta'

def mostrar_exito_castano():
    """Muestra animación de éxito: Checkmark + Croissant giratorio."""
    st.markdown("""
    <style>
    /* Contenedor central */
    .success-container {
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        display: flex;
        justify-content: center;
        align-items: center;
        background: rgba(65, 10, 20, 0.3);
        z-index: 9999;
        animation: fade-out 3s ease-out forwards;
    }
    
    @keyframes fade-out {
        0%, 80% { opacity: 1; }
        100% { opacity: 0; pointer-events: none; }
    }
    
    /* Tarjeta de éxito */
    .success-card {
        background: white;
        border-radius: 24px;
        padding: 40px 60px;
        text-align: center;
        box-shadow: 0 20px 60px rgba(65, 10, 20, 0.3);
        animation: pop-in 0.5s cubic-bezier(0.68, -0.55, 0.265, 1.55);
    }
    
    @keyframes pop-in {
        0% { transform: scale(0.5); opacity: 0; }
        100% { transform: scale(1); opacity: 1; }
    }
    
    /* Croissant giratorio */
    .croissant {
        font-size: 48px;
        animation: spin-croissant 1s ease-out;
        display: inline-block;
    }
    
    @keyframes spin-croissant {
        0% { transform: rotate(0deg) scale(0.5); }
        50% { transform: rotate(360deg) scale(1.2); }
        100% { transform: rotate(360deg) scale(1); }
    }
    
    /* Círculo del checkmark */
    .checkmark-circle {
        width: 80px;
        height: 80px;
        position: relative;
        display: inline-block;
        margin: 20px auto;
    }
    
    .checkmark-circle svg {
        width: 80px;
        height: 80px;
    }
    
    .checkmark-circle .circle {
        stroke: #8DBF2C;
        stroke-width: 4;
        fill: none;
        stroke-dasharray: 251;
        stroke-dashoffset: 251;
        animation: draw-circle 0.6s ease-out 0.2s forwards;
    }
    
    @keyframes draw-circle {
        to { stroke-dashoffset: 0; }
    }
    
    .checkmark-circle .check {
        stroke: #8DBF2C;
        stroke-width: 5;
        fill: none;
        stroke-linecap: round;
        stroke-linejoin: round;
        stroke-dasharray: 50;
        stroke-dashoffset: 50;
        animation: draw-check 0.4s ease-out 0.8s forwards;
    }
    
    @keyframes draw-check {
        to { stroke-dashoffset: 0; }
    }
    
    /* Texto */
    .success-text {
        font-family: 'Poppins', sans-serif;
        color: #410A14;
        font-size: 18px;
        font-weight: 600;
        margin-top: 15px;
        opacity: 0;
        animation: fade-in-text 0.5s ease-out 1s forwards;
    }
    
    @keyframes fade-in-text {
        to { opacity: 1; }
    }
    </style>
    
    <div class="success-container" id="success-animation">
        <div class="success-card">
            <div class="croissant">🥐</div>
            <div class="checkmark-circle">
                <svg viewBox="0 0 80 80">
                    <circle class="circle" cx="40" cy="40" r="38"/>
                    <polyline class="check" points="25,42 35,52 55,32"/>
                </svg>
            </div>
            <div class="success-text">¡Guardado exitosamente!</div>
        </div>
    </div>
    
    <script>
        setTimeout(function() {
            var el = document.getElementById('success-animation');
            if (el) el.remove();
        }, 3500);
    </script>
    """, unsafe_allow_html=True)

def mostrar_login():
    """Muestra el formulario de login con diseño oficial Castaño."""
    
    # CSS Oficial Castaño (basado en castano.cl)
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700&display=swap');
    
    /* ============================================
       PALETA OFICIAL CASTAÑO
       ============================================
       Borgoña Oscuro: #410A14
       Dorado:         #E1B313
       Crema:          #F2ECE1
       Verde Acción:   #8DBF2C
       Texto:          #333333
    */
    
    /* Tema cálido Castaño */
    .stApp {
        background: linear-gradient(180deg, #F2ECE1 0%, #EDE5D8 100%) !important;
    }
    
    /* Ocultar elementos de Streamlit */
    #MainMenu, footer, header {visibility: hidden;}
    
    /* Contenedor principal */
    .main .block-container {
        padding-top: 2rem;
        max-width: 100%;
    }
    
    /* Tarjetas con estilo cálido */
    div[data-testid="stForm"] {
        background: white !important;
        border-radius: 24px !important;
        padding: 40px !important;
        border: none !important;
        box-shadow: 0 4px 20px rgba(65, 10, 20, 0.1) !important;
    }
    
    /* Inputs grandes y claros */
    .stTextInput > div > div > input {
        font-family: 'Poppins', sans-serif !important;
        font-size: 16px !important;
        padding: 16px 20px !important;
        border-radius: 12px !important;
        background: #F8F5F0 !important;
        border: 2px solid #E8E0D5 !important;
        color: #333333 !important;
    }
    
    .stTextInput > div > div > input::placeholder {
        color: #999999 !important;
    }
    
    .stTextInput > div > div > input:focus {
        border-color: #410A14 !important;
        box-shadow: 0 0 0 3px rgba(65, 10, 20, 0.1) !important;
    }
    
    /* Labels */
    .stTextInput > label {
        font-family: 'Poppins', sans-serif !important;
        font-size: 14px !important;
        font-weight: 500 !important;
        color: #410A14 !important;
    }
    
    /* Botón principal - Verde Castaño */
    .stFormSubmitButton > button {
        background: #8DBF2C !important;
        color: white !important;
        font-family: 'Poppins', sans-serif !important;
        font-size: 16px !important;
        font-weight: 600 !important;
        padding: 16px 40px !important;
        border-radius: 12px !important;
        border: none !important;
        transition: all 0.3s ease !important;
        width: 100% !important;
        text-transform: uppercase !important;
        letter-spacing: 1px !important;
    }
    
    .stFormSubmitButton > button:hover {
        background: #7AAD25 !important;
        transform: translateY(-2px) !important;
        box-shadow: 0 8px 25px rgba(141, 191, 44, 0.3) !important;
    }
    
    /* Títulos */
    h1, h2, h3 {
        font-family: 'Poppins', sans-serif !important;
        color: #410A14 !important;
    }
    
    /* Texto general */
    p, span, div, label {
        font-family: 'Poppins', sans-serif !important;
    }
    
    /* Alertas */
    .stAlert {
        border-radius: 12px !important;
        font-size: 14px !important;
    }
    
    /* Success alert */
    div[data-baseweb="notification"] {
        background: #E8F5E9 !important;
        border: 1px solid #8DBF2C !important;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Espaciado superior
    st.markdown("<br><br>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        # Logo y título con estilo Castaño oficial
        st.markdown("""
        <div style="text-align: center; margin-bottom: 30px;">
            <h1 style="
                font-family: 'Poppins', sans-serif;
                font-size: 2.2rem;
                font-weight: 700;
                color: #410A14;
                margin-bottom: 10px;
            ">🥐 Castaño Logistics</h1>
            <p style="color: #666666; font-size: 1rem; font-family: 'Poppins', sans-serif;">Sistema de Planificación de Rutas</p>
        </div>
        """, unsafe_allow_html=True)
        
        with st.form("login_form"):
            st.markdown("<br>", unsafe_allow_html=True)
            
            usuario = st.text_input("👤 Usuario", placeholder="Escribe tu usuario aquí")
            password = st.text_input("🔒 Contraseña", type="password", placeholder="Escribe tu contraseña")
            
            st.markdown("<br>", unsafe_allow_html=True)
            
            submit = st.form_submit_button("🚀 INGRESAR", use_container_width=True, type="primary")
            
            if submit:
                if usuario and password:
                    if verificar_credenciales(usuario, password):
                        st.success(f"✅ ¡Bienvenido, {st.session_state.usuario['nombre']}!")
                        st.rerun()
                    else:
                        st.error("❌ Usuario o contraseña incorrectos. Intenta de nuevo.")
                else:
                    st.warning("⚠️ Por favor completa ambos campos")
        
        # Ayuda visual
        st.markdown("""
        <div style="
            text-align: center; 
            margin-top: 30px;
            padding: 20px;
            background: #FFF8E7;
            border-radius: 12px;
            border: 1px solid #E1B313;
        ">
            <p style="color: #410A14; font-size: 14px; margin: 0; font-family: 'Poppins', sans-serif;">
                💡 <strong>¿Olvidaste tu contraseña?</strong><br>
                <span style="color: #666666;">Contacta a tu administrador</span>
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div style="text-align: center; margin-top: 40px; color: #888888; font-family: 'Poppins', sans-serif;">
            <small>Castaño Chile © 2026 | Versión 1.0</small>
        </div>
        """, unsafe_allow_html=True)

# ================================================================
# CONEXIONES A GCP
# ================================================================

def get_spanner_client():
    """Retorna cliente de Spanner. Requiere autenticación GCP."""
    if DEMO_MODE:
        return None  # Modo demo - no intentar conexión
    try:
        from google.cloud import spanner
        client = spanner.Client(project=GCP_PROJECT)
        instance = client.instance(SPANNER_INSTANCE)
        database = instance.database(SPANNER_DATABASE)
        return database
    except Exception as e:
        st.warning(f"⚠️ No se pudo conectar a Spanner: {e}")
        return None

def get_bigquery_client():
    """Retorna cliente de BigQuery. Requiere autenticación GCP."""
    if DEMO_MODE:
        return None  # Modo demo - no intentar conexión
    try:
        from google.cloud import bigquery
        client = bigquery.Client(project=GCP_PROJECT)
        return client
    except Exception as e:
        st.warning(f"⚠️ No se pudo conectar a BigQuery: {e}")
        return None

# ================================================================
# FUNCIONES DE DATOS - SPANNER (MI RUTA)
# ================================================================

def obtener_rutas_supervisor(supervisor_id: str) -> pd.DataFrame:
    """Obtiene las rutas planificadas del supervisor desde Spanner Graph."""
    database = get_spanner_client()
    
    if database is None:
        # Datos de demostración si no hay conexión
        return pd.DataFrame({
            'dia_semana': ['LUNES', 'LUNES', 'MARTES', 'MIERCOLES', 'JUEVES'],
            'orden': [1, 2, 1, 1, 1],
            'sala_nombre': ['Walmart Maipú', 'Jumbo Kennedy', 'Lider Providencia', 'Unimarc Las Condes', 'Tottus La Florida'],
            'quintil': [3, 5, 4, 4, 3],
            'latitud': [-33.51, -33.42, -33.43, -33.41, -33.52],
            'longitud': [-70.76, -70.58, -70.60, -70.55, -70.59]
        })
    
    # Consulta al grafo de Spanner
    query = """
    SELECT 
        vp.dia_semana,
        vp.orden,
        s.nombre as sala_nombre,
        s.quintil,
        s.latitud,
        s.longitud
    FROM Visita_Planificada vp
    JOIN Sala s ON vp.sala_id = s.id
    WHERE vp.supervisor_id = @supervisor_id
    ORDER BY 
        CASE vp.dia_semana
            WHEN 'LUNES' THEN 1
            WHEN 'MARTES' THEN 2
            WHEN 'MIERCOLES' THEN 3
            WHEN 'JUEVES' THEN 4
            WHEN 'VIERNES' THEN 5
            WHEN 'SABADO' THEN 6
        END,
        vp.orden
    """
    
    with database.snapshot() as snapshot:
        results = snapshot.execute_sql(
            query,
            params={"supervisor_id": supervisor_id},
            param_types={"supervisor_id": spanner.param_types.STRING}
        )
        
        rows = list(results)
        if rows:
            return pd.DataFrame(rows, columns=['dia_semana', 'orden', 'sala_nombre', 'quintil', 'latitud', 'longitud'])
    
    return pd.DataFrame()

def obtener_zonal_supervisor(supervisor_id: str) -> str:
    """Obtiene el nombre del zonal al que reporta el supervisor."""
    database = get_spanner_client()
    
    if database is None:
        return "María González (Demo)"
    
    query = """
    SELECT z.nombre
    FROM Reporta_A ra
    JOIN Zonal z ON ra.zonal_id = z.id
    WHERE ra.supervisor_id = @supervisor_id
    """
    
    with database.snapshot() as snapshot:
        results = snapshot.execute_sql(
            query,
            params={"supervisor_id": supervisor_id},
            param_types={"supervisor_id": spanner.param_types.STRING}
        )
        
        for row in results:
            return row[0]
    
    return "No asignado"

# ================================================================
# FUNCIONES DE DATOS - BIGQUERY (RENDIR GASTOS)
# ================================================================

def insertar_rendicion(supervisor_id: str, fecha: date, monto: int, categoria: str, comentario: str) -> bool:
    """Inserta una rendición usando Streaming Insert en BigQuery."""
    client = get_bigquery_client()
    
    if client is None:
        st.info("💡 Modo demo: La rendición se registraría en BigQuery")
        return True
    
    table_id = f"{GCP_PROJECT}.{BIGQUERY_DATASET}.{BIGQUERY_TABLE}"
    
    row = {
        "id_rendicion": str(uuid.uuid4()),
        "id_supervisor": supervisor_id,
        "fecha": fecha.isoformat(),
        "monto": monto,
        "categoria": categoria,
        "comentario": comentario or "",
    }
    
    errors = client.insert_rows_json(table_id, [row])
    
    if errors:
        st.error(f"Error al insertar: {errors}")
        return False
    
    return True

def obtener_rendiciones_supervisor(supervisor_id: str) -> pd.DataFrame:
    """Obtiene el historial de rendiciones del supervisor."""
    client = get_bigquery_client()
    
    if client is None:
        # Datos de demostración
        return pd.DataFrame({
            'fecha': [date(2026, 2, 1), date(2026, 2, 3), date(2026, 2, 5)],
            'monto': [15000, 8500, 22000],
            'categoria': ['TRANSPORTE', 'ALIMENTACION', 'TRANSPORTE'],
            'comentario': ['Combustible semana', 'Almuerzo reunión', 'Peajes + estacionamiento']
        })
    
    query = f"""
    SELECT fecha, monto, categoria, comentario
    FROM `{GCP_PROJECT}.{BIGQUERY_DATASET}.{BIGQUERY_TABLE}`
    WHERE id_supervisor = @supervisor_id
    ORDER BY fecha DESC
    LIMIT 20
    """
    
    job_config = bigquery.QueryJobConfig(
        query_parameters=[
            bigquery.ScalarQueryParameter("supervisor_id", "STRING", supervisor_id)
        ]
    )
    
    df = client.query(query, job_config=job_config).to_dataframe()
    return df

# ================================================================
# PÁGINAS DE LA APLICACIÓN
# ================================================================

def pagina_mi_ruta():
    """Página principal: Mi Ruta - Consulta al grafo."""
    st.header("🗺️ Mi Ruta")
    
    usuario = st.session_state.usuario
    supervisor_id = usuario['id']
    
    # Información del supervisor
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Supervisor", usuario['nombre'])
    with col2:
        zonal = obtener_zonal_supervisor(supervisor_id)
        st.metric("Reporta a", zonal)
    
    st.markdown("---")
    
    # Obtener rutas
    df_rutas = obtener_rutas_supervisor(supervisor_id)
    
    if df_rutas.empty:
        st.info("No hay rutas planificadas asignadas.")
        return
    
    # Selector de día
    dias_disponibles = df_rutas['dia_semana'].unique().tolist()
    dia_seleccionado = st.selectbox("📅 Seleccionar día:", dias_disponibles)
    
    # Filtrar por día
    df_dia = df_rutas[df_rutas['dia_semana'] == dia_seleccionado].copy()
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader(f"📍 Visitas para {dia_seleccionado}")
        
        # Mostrar tabla de visitas
        df_mostrar = df_dia[['orden', 'sala_nombre', 'quintil']].copy()
        df_mostrar.columns = ['Orden', 'Sala', 'Quintil']
        st.dataframe(df_mostrar, use_container_width=True, hide_index=True)
    
    with col2:
        st.subheader("📊 Resumen")
        st.metric("Total visitas", len(df_dia))
        if 'quintil' in df_dia.columns:
            st.metric("Quintil promedio", f"{df_dia['quintil'].mean():.1f}")
    
    # Mapa de ubicaciones
    st.subheader("🗺️ Mapa de Visitas")
    if 'latitud' in df_dia.columns and df_dia['latitud'].notna().any():
        df_mapa = df_dia[['latitud', 'longitud']].dropna()
        df_mapa.columns = ['lat', 'lon']
        st.map(df_mapa)
    else:
        st.info("No hay coordenadas disponibles para mostrar el mapa.")

def pagina_rendir_gastos():
    """Página: Rendir Gastos - Formulario de ingesta a BigQuery."""
    st.header("💰 Rendir Gastos")
    
    usuario = st.session_state.usuario
    supervisor_id = usuario['id']
    
    # Formulario de rendición
    st.subheader("📝 Nueva Rendición")
    
    with st.form("form_rendicion", clear_on_submit=True):
        col1, col2 = st.columns(2)
        
        with col1:
            fecha = st.date_input("📅 Fecha del gasto", value=date.today())
            monto = st.number_input("💵 Monto (CLP)", min_value=0, step=500, value=0)
        
        with col2:
            categoria = st.selectbox(
                "📁 Categoría",
                options=['TRANSPORTE', 'ALIMENTACION', 'MATERIALES', 'OTROS']
            )
            comentario = st.text_area("💬 Comentario (opcional)", height=100)
        
        submitted = st.form_submit_button("✅ Registrar Rendición", use_container_width=True, type="primary")
        
        if submitted:
            if monto <= 0:
                st.error("❌ El monto debe ser mayor a 0")
            else:
                if insertar_rendicion(supervisor_id, fecha, monto, categoria, comentario):
                    st.success(f"✅ Rendición registrada: ${monto:,} en {categoria}")
                    mostrar_exito_castano()
    
    # Historial de rendiciones
    st.markdown("---")
    st.subheader("📋 Historial de Rendiciones")
    
    df_historial = obtener_rendiciones_supervisor(supervisor_id)
    
    if df_historial.empty:
        st.info("No hay rendiciones registradas.")
    else:
        # Métricas resumen
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total rendido", f"${df_historial['monto'].sum():,}")
        with col2:
            st.metric("Promedio por gasto", f"${df_historial['monto'].mean():,.0f}")
        with col3:
            st.metric("Número de rendiciones", len(df_historial))
        
        # Tabla de historial
        st.dataframe(df_historial, use_container_width=True, hide_index=True)

# ================================================================
# PÁGINA GESTIONAR RUTAS (SOLO ZONALES)
# ================================================================

def obtener_supervisores_del_zonal(zonal_id: str) -> pd.DataFrame:
    """Obtiene los supervisores que reportan a este zonal."""
    database = get_spanner_client()
    
    if database is None:
        # Datos demo para el zonal Ricardo Millar
        return pd.DataFrame({
            'id': ['s41861921', 's3048eab6', 's52b7164b', 's4e75d6f2', 's0d9492dc', 's1dc69e68', 's88ae2d48', 's0df53ceb'],
            'nombre': ['Harry Urra', 'Rodrigo Castro', 'Daniela Leon', 'Alejandro Perez', 'Lisset Medina', 'Gema Nuñez', 'Wladimir Lara', 'Alexander Yañez'],
            'email': ['harry.urra@castano.cl', 'rodrigo.castro@castano.cl', 'daniela.leon@castano.cl', 'alejandro.perez@castano.cl', 'lisset.medina@castano.cl', 'gema.nunez@castano.cl', 'wladimir.lara@castano.cl', 'alexander.yanez@castano.cl'],
            'total_visitas': [24, 18, 22, 20, 15, 19, 21, 17]
        })
    
    query = """
    SELECT s.id, s.nombre, s.email
    FROM Reporta_A ra
    JOIN Supervisor s ON ra.supervisor_id = s.id
    WHERE ra.zonal_id = @zonal_id
    """
    
    with database.snapshot() as snapshot:
        results = snapshot.execute_sql(
            query, params={"zonal_id": zonal_id},
            param_types={"zonal_id": spanner.param_types.STRING}
        )
        rows = list(results)
        if rows:
            return pd.DataFrame(rows, columns=['id', 'nombre', 'email'])
    return pd.DataFrame()

def obtener_rutas_supervisor_editable(supervisor_id: str) -> pd.DataFrame:
    """Obtiene las rutas del supervisor en formato editable."""
    database = get_spanner_client()
    
    if database is None:
        # Datos demo
        return pd.DataFrame({
            'sala_id': ['sala001', 'sala002', 'sala003', 'sala004', 'sala005'],
            'sala_nombre': ['TOT FLO WALKER MARTINEZ / 55', 'S10 ROJAS MAGALLANES / 80', 'UNI FLO ROJAS MAGALLANES / 258', 'JUMBO KENNEDY', 'LIDER EXPRESS MAIPU'],
            'LUNES': [True, True, True, False, True],
            'MARTES': [True, False, True, True, False],
            'MIERCOLES': [True, False, True, False, True],
            'JUEVES': [True, False, True, True, False],
            'VIERNES': [True, True, True, False, True],
            'SABADO': [True, True, True, False, False]
        })
    
    # Consulta real a Spanner - obtener visitas pivotadas por día
    query = """
    SELECT sala_id, sala_nombre, dia_semana
    FROM Visita_Planificada vp
    JOIN Sala s ON vp.sala_id = s.id
    WHERE vp.supervisor_id = @supervisor_id
    """
    # ... (implementar lógica de pivot)
    return pd.DataFrame()

def guardar_cambios_rutas(supervisor_id: str, sala_id: str, dias: dict) -> bool:
    """Guarda los cambios de días de visita en Spanner."""
    database = get_spanner_client()
    
    if database is None:
        st.info("💡 Modo demo: Los cambios se guardarían en Spanner")
        return True
    
    # Implementar INSERT/DELETE de visitas
    # DELETE FROM Visita_Planificada WHERE supervisor_id = X AND sala_id = Y
    # INSERT INTO Visita_Planificada ... para cada día marcado
    return True

def pagina_gestionar_rutas():
    """Página para que Zonales gestionen rutas de su equipo."""
    
    usuario = st.session_state.usuario
    zonal_id = usuario['id']
    
    # Verificar si hay un supervisor seleccionado
    if st.session_state.supervisor_seleccionado:
        mostrar_detalle_supervisor()
        return
    
    # Vista principal: Lista de supervisores
    st.header("📋 Gestionar Rutas de Mi Equipo")
    
    col1, col2 = st.columns([2, 1])
    with col1:
        st.markdown(f"**👤 Zonal:** {usuario['nombre']}")
    
    st.markdown("---")
    
    # Obtener supervisores del zonal
    df_supervisores = obtener_supervisores_del_zonal(zonal_id)
    
    if df_supervisores.empty:
        st.warning("No tienes supervisores asignados.")
        return
    
    st.markdown(f"### 👥 Tu equipo ({len(df_supervisores)} supervisores)")
    st.markdown("")
    
    # Mostrar tarjetas de supervisores
    cols = st.columns(2)
    for idx, row in df_supervisores.iterrows():
        with cols[idx % 2]:
            with st.container():
                st.markdown(f"""
                <div style="
                    background: linear-gradient(135deg, #f5f7fa 0%, #e4e8ec 100%);
                    padding: 20px;
                    border-radius: 15px;
                    margin-bottom: 15px;
                    border-left: 5px solid #667eea;
                ">
                    <h4 style="margin:0; color:#333;">👤 {row['nombre']}</h4>
                    <p style="margin:5px 0; color:#666; font-size:14px;">📧 {row['email']}</p>
                    <p style="margin:5px 0; color:#667eea; font-size:14px;">📍 {row.get('total_visitas', 0)} visitas planificadas</p>
                </div>
                """, unsafe_allow_html=True)
                
                if st.button(f"📝 Ver Rutas", key=f"btn_{row['id']}", use_container_width=True):
                    st.session_state.supervisor_seleccionado = {
                        'id': row['id'],
                        'nombre': row['nombre']
                    }
                    st.rerun()

def mostrar_detalle_supervisor():
    """Muestra el detalle de rutas de un supervisor con checkboxes."""
    
    sup = st.session_state.supervisor_seleccionado
    
    # Botón volver
    col1, col2 = st.columns([1, 4])
    with col1:
        if st.button("⬅️ Volver", use_container_width=True):
            st.session_state.supervisor_seleccionado = None
            st.rerun()
    
    st.header(f"🗺️ Rutas de {sup['nombre']}")
    st.markdown("---")
    
    # Obtener rutas
    df_rutas = obtener_rutas_supervisor_editable(sup['id'])
    
    if df_rutas.empty:
        st.info("Este supervisor no tiene salas asignadas.")
        
        # Opción para agregar sala
        st.markdown("### ➕ Agregar nueva sala")
        with st.form("agregar_sala"):
            nueva_sala = st.text_input("Nombre de la sala")
            if st.form_submit_button("Agregar"):
                st.success(f"Sala '{nueva_sala}' agregada (demo)")
        return
    
    # Instrucciones simples
    st.info("✅ Marca los días en que el supervisor debe visitar cada sala. Los cambios se guardan automáticamente.")
    
    # Días de la semana
    DIAS = ['LUNES', 'MARTES', 'MIERCOLES', 'JUEVES', 'VIERNES', 'SABADO']
    DIAS_CORTOS = ['L', 'M', 'X', 'J', 'V', 'S']
    
    # Encabezado visual
    header_cols = st.columns([3] + [1]*6)
    with header_cols[0]:
        st.markdown("**📍 SALA**")
    for i, dia in enumerate(DIAS_CORTOS):
        with header_cols[i+1]:
            st.markdown(f"**{dia}**")
    
    st.markdown("---")
    
    # Matriz de checkboxes para cada sala
    cambios = {}
    for idx, row in df_rutas.iterrows():
        cols = st.columns([3] + [1]*6)
        
        with cols[0]:
            st.markdown(f"**{row['sala_nombre'][:40]}**")
        
        dias_seleccionados = {}
        for i, dia in enumerate(DIAS):
            with cols[i+1]:
                valor_actual = row.get(dia, False)
                nuevo_valor = st.checkbox(
                    dia, 
                    value=valor_actual, 
                    key=f"chk_{row['sala_id']}_{dia}",
                    label_visibility="collapsed"
                )
                dias_seleccionados[dia] = nuevo_valor
                
                if nuevo_valor != valor_actual:
                    cambios[row['sala_id']] = dias_seleccionados
    
    st.markdown("---")
    
    # Botón guardar grande y visible
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("💾 GUARDAR CAMBIOS", use_container_width=True, type="primary"):
            if cambios:
                for sala_id, dias in cambios.items():
                    guardar_cambios_rutas(sup['id'], sala_id, dias)
                st.success("✅ ¡Cambios guardados exitosamente!")
                mostrar_exito_castano()
            else:
                st.info("No hay cambios para guardar.")
    
    # Agregar nueva sala
    st.markdown("---")
    st.markdown("### ➕ Agregar Sala")
    with st.expander("Agregar nueva sala a la ruta"):
        col1, col2 = st.columns(2)
        with col1:
            nueva_sala = st.selectbox("Seleccionar sala", 
                ["JUMBO PARQUE ARAUCO", "LIDER MAIPU", "UNIMARC PROVIDENCIA", "TOTTUS LA FLORIDA"])
        with col2:
            if st.button("➕ Agregar", use_container_width=True):
                st.success(f"Sala '{nueva_sala}' agregada a la ruta (demo)")

# ================================================================
# SIDEBAR Y NAVEGACIÓN
# ================================================================

def mostrar_sidebar():
    """Muestra el sidebar con navegación oficial Castaño."""
    
    # CSS Sidebar Castaño Oficial
    st.markdown("""
    <style>
    /* ============================================
       SIDEBAR CASTAÑO OFICIAL
       ============================================ */
    
    /* Sidebar borgoña */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #410A14 0%, #5A1520 100%) !important;
    }
    
    [data-testid="stSidebar"] * {
        color: white !important;
        font-family: 'Poppins', sans-serif !important;
    }
    
    /* Botones del sidebar */
    [data-testid="stSidebar"] .stButton > button {
        background: rgba(255, 255, 255, 0.1) !important;
        border: 1px solid rgba(255, 255, 255, 0.2) !important;
        color: white !important;
        font-family: 'Poppins', sans-serif !important;
        font-size: 15px !important;
        font-weight: 500 !important;
        padding: 14px 20px !important;
        border-radius: 12px !important;
        margin-bottom: 8px !important;
        transition: all 0.3s ease !important;
    }
    
    [data-testid="stSidebar"] .stButton > button:hover {
        background: rgba(225, 179, 19, 0.3) !important;
        border-color: #E1B313 !important;
        transform: translateX(5px) !important;
    }
    
    [data-testid="stSidebar"] .stButton > button[kind="primary"] {
        background: #8DBF2C !important;
        border: none !important;
    }
    
    [data-testid="stSidebar"] .stButton > button[kind="primary"]:hover {
        background: #7AAD25 !important;
    }
    
    [data-testid="stSidebar"] .stButton > button[kind="secondary"] {
        background: rgba(255, 255, 255, 0.05) !important;
        border-color: rgba(255, 255, 255, 0.3) !important;
    }
    
    /* Contenido principal tema cálido */
    .stApp {
        background: linear-gradient(180deg, #F2ECE1 0%, #EDE5D8 100%) !important;
    }
    
    /* Headers y texto */
    h1, h2, h3 {
        font-family: 'Poppins', sans-serif !important;
        color: #410A14 !important;
    }
    
    /* Tarjetas métricas */
    [data-testid="stMetric"] {
        background: white !important;
        border-radius: 16px !important;
        padding: 20px !important;
        border: none !important;
        box-shadow: 0 2px 12px rgba(65, 10, 20, 0.08) !important;
    }
    
    [data-testid="stMetricValue"] {
        font-family: 'Poppins', sans-serif !important;
        color: #410A14 !important;
    }
    
    [data-testid="stMetricLabel"] {
        color: #666666 !important;
    }
    
    /* Tablas */
    .stDataFrame {
        background: white !important;
        border-radius: 12px !important;
        box-shadow: 0 2px 8px rgba(65, 10, 20, 0.06) !important;
    }
    
    /* Selectbox */
    .stSelectbox > div > div {
        background: white !important;
        border-radius: 12px !important;
        border: 2px solid #E8E0D5 !important;
        color: #333333 !important;
        font-family: 'Poppins', sans-serif !important;
    }
    
    /* Checkboxes */
    .stCheckbox > label {
        font-family: 'Poppins', sans-serif !important;
    }
    
    /* Info boxes */
    .stAlert {
        background: #FFF8E7 !important;
        border: 1px solid #E1B313 !important;
        border-radius: 12px !important;
        font-family: 'Poppins', sans-serif !important;
    }
    
    /* Expander */
    .streamlit-expanderHeader {
        font-family: 'Poppins', sans-serif !important;
        color: #410A14 !important;
    }
    </style>
    """, unsafe_allow_html=True)
    
    with st.sidebar:
        # Logo con estilo Castaño oficial
        st.markdown("""
        <div style="text-align: center; padding: 20px 0;">
            <h2 style="
                font-family: 'Poppins', sans-serif;
                color: #E1B313;
                font-size: 1.5rem;
                font-weight: 700;
                margin: 0;
            ">🥐 Castaño</h2>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        usuario = st.session_state.usuario
        rol = usuario.get('rol', 'supervisor')
        
        # Tarjeta de usuario con estilo Castaño
        rol_emoji = {'zonal': '👔', 'supervisor': '👷', 'admin': '⚙️'}
        rol_color = {'zonal': '#E1B313', 'supervisor': '#8DBF2C', 'admin': '#410A14'}
        
        st.markdown(f"""
        <div style="
            background: rgba(255, 255, 255, 0.1);
            border-radius: 12px;
            padding: 15px;
            margin-bottom: 20px;
            border-left: 4px solid {rol_color.get(rol, '#E1B313')};
        ">
            <p style="margin: 0; font-size: 16px; font-weight: 600; font-family: 'Poppins', sans-serif;">
                {rol_emoji.get(rol, '👤')} {usuario['nombre']}
            </p>
            <p style="margin: 5px 0 0 0; font-size: 12px; color: rgba(255,255,255,0.7); font-family: 'Poppins', sans-serif;">
                {rol.upper()}
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("### 📍 Menú")
        st.markdown("")
        
        # Navegación según rol con botones grandes
        if rol in ['zonal', 'admin']:
            if st.button("📋 Gestionar Rutas", use_container_width=True, type="primary"):
                st.session_state.pagina = 'Gestionar Rutas'
                st.session_state.supervisor_seleccionado = None
                st.rerun()
        
        if rol in ['supervisor', 'admin']:
            if st.button("🗺️ Ver Mi Ruta", use_container_width=True):
                st.session_state.pagina = 'Mi Ruta'
                st.rerun()
            
            if st.button("💰 Rendir Gastos", use_container_width=True):
                st.session_state.pagina = 'Rendir Gastos'
                st.rerun()
        
        st.markdown("")
        st.markdown("---")
        
        if st.button("🚪 Cerrar Sesión", use_container_width=True, type="secondary"):
            cerrar_sesion()
            st.rerun()
        
        # Footer
        st.markdown("""
        <div style="
            text-align: center;
            margin-top: 40px;
            padding: 15px;
            color: #8892b0;
            font-size: 12px;
        ">
            <p style="margin: 0;">Castaño Logistics v1.0</p>
            <p style="margin: 5px 0 0 0;">© 2026</p>
        </div>
        """, unsafe_allow_html=True)

# ================================================================
# MAIN
# ================================================================

def main():
    """Función principal de la aplicación."""
    inicializar_sesion()
    
    if not st.session_state.autenticado:
        mostrar_login()
    else:
        mostrar_sidebar()
        
        # Renderizar página según selección
        if st.session_state.pagina == 'Mi Ruta':
            pagina_mi_ruta()
        elif st.session_state.pagina == 'Rendir Gastos':
            pagina_rendir_gastos()
        elif st.session_state.pagina == 'Gestionar Rutas':
            pagina_gestionar_rutas()

if __name__ == "__main__":
    main()
