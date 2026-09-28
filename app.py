"""
BlueData Studio • OceanNC to CSV
Plataforma profissional de processamento e conversão de dados oceanográficos NetCDF.
Desenvolvida para investigação e ensino em Oceanografia Física & Biologia Marinha.
"""

import base64
import io
import os
import tempfile
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
import xarray as xr

# ---------------------------------------------------------
# 1. Configuração da Página e Tema Visual
# ---------------------------------------------------------
st.set_page_config(
    page_title="BlueData • OceanNC Studio",
    page_icon="🌊",
    layout="wide",
    initial_sidebar_state="expanded",
)

def get_base64_image(image_path):
    """Carrega uma imagem local e devolve a string Base64."""
    if os.path.exists(image_path):
        with open(image_path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode()
    return None

bg_base64 = get_base64_image("assets/background_wave.jpg")
logo_base64 = get_base64_image("assets/logo.png") or get_base64_image("logo.png")
bg_css = ""
if bg_base64:
    bg_css = f"""
    <style>
    [data-testid="stAppViewContainer"] {{
        background: linear-gradient(rgba(11, 19, 41, 0.85), rgba(11, 19, 41, 0.92)), url("data:image/jpeg;base64,{bg_base64}");
        background-size: cover;
        background-position: center bottom;
        background-repeat: no-repeat;
        background-attachment: fixed;
    }}
    [data-testid="stHeader"] {{
        background: rgba(11, 19, 41, 0.4);
        backdrop-filter: blur(8px);
    }}
    [data-testid="stSidebar"] {{
        background: rgba(15, 23, 42, 0.88);
        backdrop-filter: blur(16px);
        border-right: 1px solid rgba(255, 255, 255, 0.08);
    }}
    </style>
    """
    st.markdown(bg_css, unsafe_allow_html=True)

# Injeção de CSS Premium Estático (sem f-string para evitar conflitos com chavetas de CSS)
static_css = """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;500&display=swap');

    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', sans-serif;
    }

    /* Hero Banner Premium */
    .hero-container {
        background: linear-gradient(135deg, #091a30 0%, #0d2847 45%, #024b75 100%);
        border: 1px solid rgba(14, 165, 233, 0.25);
        border-radius: 16px;
        padding: 32px 36px;
        margin-bottom: 24px;
        box-shadow: 0 10px 30px -10px rgba(2, 75, 117, 0.4);
        position: relative;
        overflow: hidden;
    }
    .hero-container::after {
        content: "";
        position: absolute;
        top: -50%;
        right: -10%;
        width: 350px;
        height: 350px;
        background: radial-gradient(circle, rgba(14, 165, 233, 0.15) 0%, transparent 70%);
        pointer-events: none;
    }
    .hero-badge {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        background: rgba(14, 165, 233, 0.15);
        color: #38bdf8;
        border: 1px solid rgba(56, 189, 248, 0.3);
        padding: 4px 12px;
        border-radius: 9999px;
        font-size: 0.78rem;
        font-weight: 600;
        letter-spacing: 0.05em;
        text-transform: uppercase;
        margin-bottom: 12px;
    }
    .hero-title {
        font-size: 2.2rem;
        font-weight: 800;
        color: #ffffff;
        letter-spacing: -0.02em;
        margin: 0 0 8px 0;
        line-height: 1.2;
    }
    .hero-subtitle {
        font-size: 1.02rem;
        color: #94a3b8;
        max-width: 820px;
        margin: 0;
        line-height: 1.55;
    }

    /* Cards de Estatística / KPI */
    .kpi-card {
        background: rgba(19, 31, 55, 0.7);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 14px;
        padding: 18px 20px;
        backdrop-filter: blur(10px);
        transition: transform 0.2s ease, border-color 0.2s ease;
    }
    .kpi-card:hover {
        border-color: rgba(56, 189, 248, 0.4);
        transform: translateY(-2px);
    }
    .kpi-label {
        font-size: 0.8rem;
        text-transform: uppercase;
        color: #94a3b8;
        font-weight: 600;
        letter-spacing: 0.04em;
        margin-bottom: 6px;
    }
    .kpi-value {
        font-size: 1.7rem;
        font-weight: 800;
        color: #f8fafc;
        line-height: 1.1;
    }
    .kpi-desc {
        font-size: 0.78rem;
        color: #64748b;
        margin-top: 6px;
    }

    /* Stepper / Indicador de Passos */
    .step-pill {
        display: inline-flex;
        align-items: center;
        gap: 8px;
        font-size: 0.82rem;
        font-weight: 700;
        color: #38bdf8;
        background: rgba(14, 165, 233, 0.1);
        border: 1px solid rgba(56, 189, 248, 0.25);
        padding: 6px 14px;
        border-radius: 8px;
        margin-bottom: 14px;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }

    /* Barra de Capacidade Excel */
    .capacity-container {
        background: rgba(255, 255, 255, 0.05);
        border-radius: 8px;
        height: 10px;
        width: 100%;
        overflow: hidden;
        margin: 8px 0;
    }
    .capacity-fill-safe {
        background: linear-gradient(90deg, #10b981, #06b6d4);
        height: 100%;
        border-radius: 8px;
    }
    .capacity-fill-warn {
        background: linear-gradient(90deg, #f59e0b, #ef4444);
        height: 100%;
        border-radius: 8px;
    }

    /* Monospace para metadados */
    .code-font {
        font-family: 'JetBrains Mono', monospace;
    }
    </style>
    """
st.markdown(static_css, unsafe_allow_html=True)


# ---------------------------------------------------------
# 2. Funções Utilitárias Oceanográficas
# ---------------------------------------------------------
def find_dimension(ds, candidates):
    """Localiza o nome canónico da dimensão no xarray Dataset."""
    for cand in candidates:
        for dim in ds.dims:
            if cand.lower() == str(dim).lower():
                return dim
        for coord in ds.coords:
            if cand.lower() == str(coord).lower():
                return coord
    return None


def get_dataset_summary(ds):
    """Calcula estatísticas de dimensões e número teórico de pontos."""
    dim_sizes = {str(k): int(v) for k, v in ds.dims.items()}
    total_points = 1
    for size in dim_sizes.values():
        total_points *= size
    return dim_sizes, total_points


# ---------------------------------------------------------
# 3. Cabeçalho Hero
# ---------------------------------------------------------
st.markdown(
    """
    <div class="hero-container">
        <div class="hero-badge">🌊 Oceanografia Física & Biologia Marinha</div>
        <h1 class="hero-title">BlueData • OceanNC Studio</h1>
        <p class="hero-subtitle">
            Plataforma científica para inspeção, amostragem e conversão de dados oceânicos multidimensionais (NetCDF 3D/4D).
            Gere tabelas prontas para Microsoft Excel, R, Python e QGIS com controlo dimensional inteligente.
        </p>
    </div>
""",
    unsafe_allow_html=True,
)

# ---------------------------------------------------------
# 4. Barra Lateral (Sidebar) com Ajuda e Guia
# ---------------------------------------------------------
with st.sidebar:
    if os.path.exists("assets/background_wave.jpg"):
        st.image("assets/background_wave.jpg", caption="TP Oceanografia Física", use_container_width=True)
    st.markdown("### 🎓 Contexto Pedagógico")
    st.info(
        """
        **Porque é que o NetCDF é o padrão?**
        Modelos numéricos (ex: *Copernicus Marine*, *ROMS*, *NEMO*) e satélites (*Sentinel*, *MODIS*) geram matrizes 4D:
        
        $$f(\\text{tempo}, \\text{profundidade}, \\text{lat}, \\text{lon})$$
        
        **O Desafio:** O Excel tem um limite de **1.048.576 linhas**. Esta ferramenta permite fatiar a grelha para isolar a superfície ou a sua área de amostragem.
        """
    )

    st.markdown("---")
    st.markdown("### ⚙️ Atalhos de Análise (Presets)")
    st.caption("Pode utilizar estes atalhos para configurar os filtros habituais da aula.")

    preset_surface = st.button("🌊 Preset: Biologia de Superfície", use_container_width=True)
    preset_all = st.button("📦 Preset: Exportar Grelha Plena", use_container_width=True)


# ---------------------------------------------------------
# 5. PASSO 1: Importação de Dados
# ---------------------------------------------------------
st.markdown('<div class="step-pill">1. Importação & Fonte de Dados</div>', unsafe_allow_html=True)

col_up, col_sample = st.columns([3, 1])

with col_up:
    uploaded_file = st.file_uploader(
        "Arraste ou selecione o ficheiro NetCDF (.nc, .nc4):",
        type=["nc", "nc4", "netcdf"],
        help="Suporta ficheiros Copernicus Marine Service, NOAA, NASA OBPG e modelos oceanográficos locais.",
    )

with col_sample:
    st.markdown("<div style='height: 28px;'></div>", unsafe_allow_html=True)
    load_sample = st.button(
        "🧪 Carregar Dados Algarve (Demo)",
        use_container_width=True,
        help="Carrega um conjunto de dados 4D realista da Costa Sul de Portugal (SST, Salinidade, Clorofila-a).",
    )

ds = None
filename = ""

if uploaded_file is not None:
    filename = uploaded_file.name
    with tempfile.NamedTemporaryFile(delete=False, suffix=".nc") as tmp_file:
        tmp_file.write(uploaded_file.getvalue())
        tmp_path = tmp_file.name
    try:
        ds = xr.open_dataset(tmp_path)
    except Exception as e:
        st.error(f"Erro ao abrir o ficheiro NetCDF: {e}")
    finally:
        try:
            os.remove(tmp_path)
        except Exception:
            pass

elif load_sample or "sample_loaded" in st.session_state:
    st.session_state["sample_loaded"] = True
    sample_file = "exemplo_oceanografia_algarve.nc"
    if not os.path.exists(sample_file):
        from generate_sample_nc import generate_sample_dataset

        ds_sample = generate_sample_dataset()
        ds_sample.to_netcdf(sample_file)
    filename = "exemplo_oceanografia_algarve.nc (Costa de Portugal)"
    ds = xr.open_dataset(sample_file)


# ---------------------------------------------------------
# 6. PASSO 2: Diagnóstico e Metadados Estruturais
# ---------------------------------------------------------
if ds is not None:
    st.markdown("---")
    st.markdown(f'<div class="step-pill">2. Diagnóstico Estrutural • {filename}</div>', unsafe_allow_html=True)

    # Identificar Dimensões
    time_dim = find_dimension(ds, ["time", "time_counter", "valid_time", "t", "date"])
    depth_dim = find_dimension(ds, ["depth", "deptht", "lev", "level", "z", "elevation"])
    lat_dim = find_dimension(ds, ["latitude", "lat", "nav_lat", "y"])
    lon_dim = find_dimension(ds, ["longitude", "lon", "nav_lon", "x"])

    dim_sizes, total_raw_points = get_dataset_summary(ds)
    data_vars = list(ds.data_vars.keys()) or list(ds.variables.keys())

    # Indicadores KPI Modernos
    kpi_col1, kpi_col2, kpi_col3, kpi_col4 = st.columns(4)

    with kpi_col1:
        st.markdown(
            f"""
            <div class="kpi-card">
                <div class="kpi-label">Dimensionalidade</div>
                <div class="kpi-value">{len(ds.dims)}D</div>
                <div class="kpi-desc">{'4D (T, Z, Y, X)' if (time_dim and depth_dim) else 'Grelha Espaço-Temporal'}</div>
            </div>
        """,
            unsafe_allow_html=True,
        )

    with kpi_col2:
        st.markdown(
            f"""
            <div class="kpi-card">
                <div class="kpi-label">Variáveis de Dados</div>
                <div class="kpi-value">{len(data_vars)}</div>
                <div class="kpi-desc">Parâmetros físico-químicos</div>
            </div>
        """,
            unsafe_allow_html=True,
        )

    with kpi_col3:
        st.markdown(
            f"""
            <div class="kpi-card">
                <div class="kpi-label">Pontos da Grelha Bruta</div>
                <div class="kpi-value">{total_raw_points:,}</div>
                <div class="kpi-desc">Produto das dimensões</div>
            </div>
        """,
            unsafe_allow_html=True,
        )

    with kpi_col4:
        pct_excel = min(100.0, (total_raw_points / 1_048_576) * 100)
        status_color = "#10b981" if total_raw_points <= 1_048_576 else "#ef4444"
        status_text = "Seguro p/ Excel" if total_raw_points <= 1_048_576 else "Excede Excel!"
        st.markdown(
            f"""
            <div class="kpi-card">
                <div class="kpi-label">Capacidade Excel</div>
                <div class="kpi-value" style="color: {status_color};">{status_text}</div>
                <div class="kpi-desc">{pct_excel:.1f}% do teto de 1M linhas</div>
            </div>
        """,
            unsafe_allow_html=True,
        )

    # Tabs de Exploração e Metadados
    with st.expander("🔬 Inspecionar Dimensões Detalhadas & Atributos Globais"):
        tab_dims, tab_attrs = st.tabs(["Dimensões e Coordenadas", "Metadados Globais (CF / NetCDF)"])

        with tab_dims:
            dim_records = []
            for d, sz in dim_sizes.items():
                kind = "Outra"
                detail = "-"
                if d == time_dim:
                    kind = "Tempo (Time)"
                    t_vals = ds[d].values
                    detail = f"{str(t_vals[0])[:10]} até {str(t_vals[-1])[:10]}"
                elif d == depth_dim:
                    kind = "Profundidade (Depth)"
                    z_vals = ds[d].values
                    unit = ds[d].attrs.get("units", "m")
                    detail = f"{float(z_vals[0]):.1f} a {float(z_vals[-1]):.1f} {unit}"
                elif d == lat_dim:
                    kind = "Latitude"
                    l_vals = ds[d].values
                    detail = f"{float(np.min(l_vals)):.2f}º a {float(np.max(l_vals)):.2f}º N"
                elif d == lon_dim:
                    kind = "Longitude"
                    lo_vals = ds[d].values
                    detail = f"{float(np.min(lo_vals)):.2f}º a {float(np.max(lo_vals)):.2f}º E/W"

                dim_records.append({"Dimensão": d, "Classificação": kind, "Pontos": sz, "Intervalo": detail})
            st.dataframe(pd.DataFrame(dim_records), use_container_width=True)

        with tab_attrs:
            if ds.attrs:
                st.json(dict(ds.attrs))
            else:
                st.caption("Sem atributos globais no ficheiro.")

    # ---------------------------------------------------------
    # 7. PASSO 3: Filtros e Configuração Dimensional
    # ---------------------------------------------------------
    st.markdown("---")
    st.markdown('<div class="step-pill">3. Filtros & Reshape Tabular</div>', unsafe_allow_html=True)

    # 1. Seleção de Variáveis
    var_labels = {}
    for v in data_vars:
        long_name = ds[v].attrs.get("long_name", v)
        units = ds[v].attrs.get("units", "")
        var_labels[v] = f"{v} — {long_name} ({units})" if units else f"{v} — {long_name}"

    f_col1, f_col2 = st.columns(2)

    with f_col1:
        st.markdown("##### 🧪 1. Parâmetros a Extrair")
        selected_vars = st.multiselect(
            "Selecione as variáveis para a tabela:",
            options=data_vars,
            default=data_vars,
            format_func=lambda x: var_labels.get(x, x),
        )
        if not selected_vars:
            st.warning("⚠️ Selecione pelo menos uma variável.")
            st.stop()

    with f_col2:
        st.markdown("##### 🌊 2. Dimensão Vertical (Profundidade)")
        if depth_dim and depth_dim in ds.dims:
            z_vals = ds[depth_dim].values
            z_unit = ds[depth_dim].attrs.get("units", "m")

            depth_mode = st.radio(
                f"Níveis de profundidade detetados ({len(z_vals)} níveis em `{depth_dim}`):",
                [
                    "🟢 Apenas Superfície (0 m / nível 0) [Padrão de Biologia]",
                    "🔵 Escolher Nível Específico",
                    "🟡 Toda a Coluna de Água (Todas as profundidades)",
                ],
                index=0 if not preset_all else 2,
            )

            chosen_z_idx = 0
            if "Superfície" in depth_mode:
                chosen_z_idx = 0
            elif "Específico" in depth_mode:
                z_options = [f"{float(val):.1f} {z_unit} (nível {i})" for i, val in enumerate(z_vals)]
                chosen_z_str = st.selectbox("Selecione o nível vertical:", options=z_options)
                chosen_z_idx = z_options.index(chosen_z_str)
            else:
                chosen_z_idx = None
        else:
            st.caption("ℹ️ Ficheiro sem dimensão vertical (dados de superfície ou camada única).")
            chosen_z_idx = None

    f_col3, f_col4 = st.columns(2)

    with f_col3:
        st.markdown("##### ⏱️ 3. Dimensão Temporal")
        if time_dim and time_dim in ds.dims:
            t_vals = ds[time_dim].values
            n_t = len(t_vals)

            time_mode = st.radio(
                f"Passos temporais detetados ({n_t} registos em `{time_dim}`):",
                ["📅 Todos os passos temporais", "🎯 Selecionar uma data específica"],
                index=0,
            )

            chosen_t_idx = None
            if "específica" in time_mode:
                t_str_list = [str(t)[:19] for t in t_vals]
                chosen_t_str = st.selectbox("Data/Hora da amostragem:", options=t_str_list)
                chosen_t_idx = t_str_list.index(chosen_t_str)
        else:
            st.caption("ℹ️ Ficheiro sem dimensão temporal.")
            chosen_t_idx = None

    with f_col4:
        st.markdown("##### 🗺️ 4. Recorte Espacial (Bounding Box)")
        enable_crop = st.checkbox("Ativar recorte de coordenadas geográficas", value=False)
        crop_lat_min, crop_lat_max = None, None
        crop_lon_min, crop_lon_max = None, None

        if enable_crop and lat_dim and lon_dim:
            all_lats = ds[lat_dim].values
            all_lons = ds[lon_dim].values

            c_l1, c_l2 = st.columns(2)
            with c_l1:
                crop_lat_min = st.number_input("Lat Mín (ºN)", value=float(np.min(all_lats)), step=0.1, format="%.2f")
            with c_l2:
                crop_lat_max = st.number_input("Lat Máx (ºN)", value=float(np.max(all_lats)), step=0.1, format="%.2f")

            c_lo1, c_lo2 = st.columns(2)
            with c_lo1:
                crop_lon_min = st.number_input("Lon Mín (ºE/W)", value=float(np.min(all_lons)), step=0.1, format="%.2f")
            with c_lo2:
                crop_lon_max = st.number_input("Lon Máx (ºE/W)", value=float(np.max(all_lons)), step=0.1, format="%.2f")
        elif enable_crop:
            st.caption("Coordenadas espaciais não identificadas para recorte.")

    # Opções de Limpeza e Exportação
    st.markdown("##### 🧹 5. Parâmetros de Formatação & Limpeza")
    opt1, opt2, opt3 = st.columns(3)

    with opt1:
        clean_nans = st.checkbox(
            "Descartar pontos de terra (NaNs)",
            value=True,
            help="Remove linhas sem dados oceanográficos válidos (continente ou falhas de sensor).",
        )

    with opt2:
        csv_sep_choice = st.selectbox(
            "Separador de Colunas:",
            [", (Vírgula — Padrão Internacional / R / QGIS)", "; (Ponto e Vírgula — Padrão Excel PT)"],
            index=0,
        )
        csv_sep = ";" if ";" in csv_sep_choice else ","

    with opt3:
        decimal_choice = st.selectbox(
            "Separador Decimal:",
            [". (Ponto — 36.5)", ", (Vírgula — 36,5 — Excel PT)"],
            index=0 if csv_sep == "," else 1,
        )
        decimal_sep = "," if "," in decimal_choice else "."

    # Aplicação dos Filtros no Dataset
    filtered_ds = ds[selected_vars]

    if depth_dim and depth_dim in filtered_ds.dims and chosen_z_idx is not None:
        filtered_ds = filtered_ds.isel({depth_dim: chosen_z_idx})

    if time_dim and time_dim in filtered_ds.dims and chosen_t_idx is not None:
        filtered_ds = filtered_ds.isel({time_dim: chosen_t_idx})

    if enable_crop and lat_dim and lon_dim and crop_lat_min is not None:
        try:
            lat_slice = slice(min(crop_lat_min, crop_lat_max), max(crop_lat_min, crop_lat_max))
            lon_slice = slice(min(crop_lon_min, crop_lon_max), max(crop_lon_min, crop_lon_max))
            filtered_ds = filtered_ds.sel({lat_dim: lat_slice, lon_dim: lon_slice})
        except Exception as e:
            st.warning(f"Aviso no recorte espacial: {e}")

    _, estimated_rows = get_dataset_summary(filtered_ds)

    # Barra Visual de Capacidade
    st.markdown("---")
    st.markdown("##### 📈 Estimativa de Volume Pós-Filtros")

    usage_ratio = estimated_rows / 1_048_576
    usage_pct = min(100.0, usage_ratio * 100)
    fill_class = "capacity-fill-safe" if usage_ratio <= 1.0 else "capacity-fill-warn"

    st.markdown(
        f"""
        <div style="display: flex; justify-content: space-between; font-size: 0.85rem; color: #94a3b8;">
            <span>Linhas estimadas: <strong>{estimated_rows:,}</strong></span>
            <span>Teto do Excel: <strong>1.048.576</strong></span>
        </div>
        <div class="capacity-container">
            <div class="{fill_class}" style="width: {usage_pct:.1f}%;"></div>
        </div>
    """,
        unsafe_allow_html=True,
    )

    if estimated_rows > 1_048_576:
        st.error(
            f"⚠️ **Atenção pedagógica:** Esta configuração gerará ~{estimated_rows:,} linhas, "
            "o que excede o limite do Microsoft Excel. Filtre por profundidade ou recorte as coordenadas para conseguir abrir no Excel."
        )
    else:
        st.success(f"✅ **Tamanho ideal:** A grelha filtrada ({estimated_rows:,} pontos) é 100% compatível com Excel, R e QGIS.")

    # ---------------------------------------------------------
    # 8. PASSO 4: Visualização Interativa & Exportação
    # ---------------------------------------------------------
    st.markdown("---")
    st.markdown('<div class="step-pill">4. Visualização Oceanográfica & Exportação</div>', unsafe_allow_html=True)

    # Painel com Visualizações Gráficas Científicas
    with st.expander("🗺️ Pré-visualização Oceanográfica Interativa (Mapas & Perfis CTD)", expanded=True):
        viz_tab_map, viz_tab_profile = st.tabs(["Mapa de Superfície (Campo 2D)", "Perfil Vertical (CTD / Profundidade)"])

        with viz_tab_map:
            # Gráfico de Campo 2D se tivermos Lat e Lon
            if lat_dim and lon_dim and len(selected_vars) > 0:
                first_var = selected_vars[0]
                slice_2d = filtered_ds[first_var]

                # Reduzir dimensões restantes se necessário (ex: pegar primeiro passo de tempo e prof)
                for d in slice_2d.dims:
                    if d not in [lat_dim, lon_dim]:
                        slice_2d = slice_2d.isel({d: 0})

                lats = slice_2d[lat_dim].values
                lons = slice_2d[lon_dim].values
                vals = slice_2d.values

                # Plotly Heatmap
                fig_map = px.imshow(
                    vals,
                    x=lons,
                    y=lats,
                    labels={"x": "Longitude (º)", "y": "Latitude (º)", "color": first_var},
                    color_continuous_scale="Viridis",
                    origin="lower",
                    title=f"Distribuição Espacial de <b>{first_var}</b> ({ds[first_var].attrs.get('units', '')})",
                )
                fig_map.update_layout(
                    template="plotly_dark",
                    margin=dict(l=40, r=40, t=50, b=40),
                    height=380,
                )
                st.plotly_chart(fig_map, use_container_width=True)
            else:
                st.caption("Coordenadas geográficas insuficientes para mapa 2D.")

        with viz_tab_profile:
            # Perfil vertical CTD se existir dimensão depth
            if depth_dim and depth_dim in ds.dims and len(selected_vars) > 0:
                first_var = selected_vars[0]
                var_data = ds[first_var]

                # Média espacial para obter o perfil vertical
                mean_dims = [d for d in var_data.dims if d != depth_dim and d != time_dim]
                if mean_dims:
                    profile_series = var_data.mean(dim=mean_dims)
                else:
                    profile_series = var_data

                if time_dim in profile_series.dims:
                    profile_series = profile_series.isel({time_dim: 0})

                z_coords = ds[depth_dim].values
                p_vals = profile_series.values

                fig_prof = go.Figure()
                fig_prof.add_trace(
                    go.Scatter(
                        x=p_vals,
                        y=z_coords,
                        mode="lines+markers",
                        line=dict(color="#38bdf8", width=3),
                        marker=dict(size=8, color="#0284c7"),
                        name=first_var,
                    )
                )
                fig_prof.update_layout(
                    template="plotly_dark",
                    title=f"Perfil Vertical de <b>{first_var}</b> (Média da Grelha)",
                    xaxis_title=f"{first_var} ({ds[first_var].attrs.get('units', '')})",
                    yaxis_title=f"Profundidade ({ds[depth_dim].attrs.get('units', 'm')})",
                    yaxis=dict(autorange="reversed"),  # Superfície no topo
                    margin=dict(l=40, r=40, t=50, b=40),
                    height=380,
                )
                st.plotly_chart(fig_prof, use_container_width=True)
            else:
                st.caption("Ficheiro sem dimensão de profundidade para perfil CTD.")

    # Processamento Final para CSV
    col_btn, _ = st.columns([2, 1])
    with col_btn:
        generate_table = st.button("⚡ Processar Tabela e Gerar CSV", type="primary", use_container_width=True)

    if generate_table or "processed_df" in st.session_state:
        if generate_table:
            with st.spinner("A converter grelha oceanográfica para formato tabular..."):
                try:
                    df = filtered_ds.to_dataframe().reset_index()

                    if clean_nans:
                        len_before = len(df)
                        df = df.dropna(subset=selected_vars, how="all")
                        len_after = len(df)
                        st.info(f"🧹 **Limpeza Efetuada**: Removidos {len_before - len_after:,} pontos com valores nulos (ex: terra).")

                    st.session_state["processed_df"] = df
                    st.session_state["processed_ready"] = True
                except Exception as e:
                    st.error(f"Erro na conversão: {e}")

        if st.session_state.get("processed_ready", False):
            df = st.session_state["processed_df"]

            st.markdown(f"#### 📋 Tabela Final: `{len(df):,}` linhas × `{len(df.columns)}` colunas")
            st.dataframe(df.head(20), use_container_width=True)

            # Métricas estatísticas de apoio aos alunos
            with st.expander("📊 Estatísticas Descritivas dos Dados (Média, Desvio Padrão, Quartis)"):
                st.dataframe(df.describe(), use_container_width=True)

            # Exportação de Ficheiro
            csv_buf = io.StringIO()
            df.to_csv(csv_buf, sep=csv_sep, decimal=decimal_sep, index=False)
            csv_bytes = csv_buf.getvalue().encode("utf-8-sig")

            clean_base = filename.replace(".nc", "").replace(".nc4", "").replace(" ", "_")
            out_name = f"{clean_base}_ocean_data.csv"

            st.download_button(
                label=f"📥 Descarregar Ficheiro CSV ({len(csv_bytes)/1024:.1f} KB)",
                data=csv_bytes,
                file_name=out_name,
                mime="text/csv",
                type="primary",
                use_container_width=True,
            )

# Rodapé com branding e "Powered by" encostado à direita
logo_html = ""
if logo_base64:
    logo_html = f"""
    <div style="display: flex; align-items: center; gap: 12px; margin-left: auto;">
        <span style="color: #94a3b8; font-size: 0.82rem; font-weight: 600; letter-spacing: 0.04em;">Powered by</span>
        <img src="data:image/png;base64,{logo_base64}" alt="Powered by" style="height: 38px; width: auto; object-fit: contain; filter: drop-shadow(0 2px 5px rgba(0,0,0,0.35));" />
    </div>
    """

st.markdown(
    f"""
    <div style="display: flex; justify-content: space-between; align-items: center; padding: 22px 0 10px 0; border-top: 1px solid rgba(255, 255, 255, 0.1); margin-top: 40px; flex-wrap: wrap; gap: 16px;">
        <div style="color: #64748b; font-size: 0.82rem; line-height: 1.5;">
            <strong style="color: #94a3b8;">BlueData • OceanNC Studio</strong> • Concebido para Ensino e Investigação em Oceanografia Física & Biologia Marinha.<br>
            Compatível com grelhas de modelos hidrodinâmicos e dados de satélite da União Europeia (Copernicus Marine).
        </div>
        {logo_html}
    </div>
""",
    unsafe_allow_html=True,
)
