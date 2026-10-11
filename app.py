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
import folium
from streamlit_folium import st_folium

import geo_coords as gc

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

# Injeção de CSS Premium Estático
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
        <div class="hero-badge">🌊 Simplificando a vida aos meus alunos</div>
        <h1 class="hero-title">BlueData • OceanNC Studio</h1>
        <p class="hero-subtitle">
            Plataforma científica para inspeção, amostragem e conversão de dados oceânicos multidimensionais (NetCDF 3D/4D)
            e calculadora de coordenadas para Copernicus Marine (CMEMS).
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
        Modelos numéricos (*Copernicus Marine*, *ROMS*, *NEMO*) e satélites (*Sentinel*, *MODIS*) geram matrizes 4D:
        
        $$f(\\text{tempo}, \\text{profundidade}, \\text{lat}, \\text{lon})$$
        
        **O Desafio:** O Excel suporta no máximo **1.048.576 linhas**.
        Esta ferramenta permite isolar a superfície ou a sua área de amostragem.
        """
    )

    st.markdown("---")
    st.markdown("### ⚙️ Atalhos de Análise (Presets)")
    st.caption("Atalhos rápidos para filtros da aula.")

    preset_surface = st.button("🌊 Preset: Biologia de Superfície", use_container_width=True)
    preset_all = st.button("📦 Preset: Exportar Grelha Plena", use_container_width=True)


# ---------------------------------------------------------
# 5. MÓDULO 1: Conversor NetCDF → CSV
# ---------------------------------------------------------
def render_netcdf_tab(preset_all_flag):
    st.markdown('<div class="step-pill">1. Importação & Fonte de Dados</div>', unsafe_allow_html=True)

    col_up, col_sample = st.columns([3, 1])

    with col_up:
        uploaded_file = st.file_uploader(
            "Arraste ou selecione o ficheiro NetCDF (.nc, .nc4):",
            help="Compatível com iPad, Mac e Windows. Suporta ficheiros Copernicus Marine Service, NOAA, NASA OBPG e modelos locais.",
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
        suffix = ".nc4" if ".nc4" in filename.lower() else ".nc"
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp_file:
            tmp_file.write(uploaded_file.getvalue())
            tmp_path = tmp_file.name
        try:
            ds = xr.open_dataset(tmp_path)
        except Exception as e:
            st.error(f"⚠️ Não foi possível ler o ficheiro como NetCDF válido (**{filename}**).")
            st.info("Certifique-se de que selecionou um ficheiro oceanográfico NetCDF (.nc ou .nc4) completo.")
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

    if ds is not None:
        st.markdown("---")
        st.markdown(f'<div class="step-pill">2. Diagnóstico Estrutural • {filename}</div>', unsafe_allow_html=True)

        time_dim = find_dimension(ds, ["time", "time_counter", "valid_time", "t", "date"])
        depth_dim = find_dimension(ds, ["depth", "deptht", "lev", "level", "z", "elevation"])
        lat_dim = find_dimension(ds, ["latitude", "lat", "nav_lat", "y"])
        lon_dim = find_dimension(ds, ["longitude", "lon", "nav_lon", "x"])

        dim_sizes, total_raw_points = get_dataset_summary(ds)
        data_vars = list(ds.data_vars.keys()) or list(ds.variables.keys())

        # KPIs
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

        st.markdown("---")
        st.markdown('<div class="step-pill">3. Filtros & Reshape Tabular</div>', unsafe_allow_html=True)

        f_col1, f_col2 = st.columns(2)

        with f_col1:
            st.markdown("##### 🧪 1. Parâmetros a Extrair")
            var_dropdown_options = [
                f"🌟 Todas as variáveis ({len(data_vars)} parâmetros)",
                "✏️ Seleção personalizada (escolher múltiplas)",
            ] + data_vars

            param_choice = st.selectbox(
                "Selecione o que pretende extrair no menu:",
                options=var_dropdown_options,
                format_func=lambda x: (
                    x if (x.startswith("🌟") or x.startswith("✏️"))
                    else f"{x} — {ds[x].attrs.get('long_name', x)}" + (f" ({ds[x].attrs.get('units', '')})" if ds[x].attrs.get("units") else "")
                ),
                index=0,
                help="Escolha todas as variáveis ou selecione um parâmetro específico.",
            )

            if param_choice.startswith("🌟"):
                selected_vars = data_vars
                st.caption(f"✓ Serão extraídas todas as colunas: `{', '.join(data_vars)}`")
            elif param_choice.startswith("✏️"):
                selected_vars = []
                cols_chk = st.columns(2)
                for idx, v in enumerate(data_vars):
                    with cols_chk[idx % 2]:
                        chk = st.checkbox(f"{v}", value=True, key=f"chk_var_{v}", help=ds[v].attrs.get('long_name', v))
                        if chk:
                            selected_vars.append(v)
                if not selected_vars:
                    st.warning("⚠️ Selecione pelo menos uma variável.")
                    st.stop()
            else:
                selected_vars = [param_choice]
                unit_info = f" ({ds[param_choice].attrs.get('units', '')})" if ds[param_choice].attrs.get("units") else ""
                st.caption(f"✓ Extrair apenas: **{param_choice}**{unit_info}")

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
                    index=0 if not preset_all_flag else 2,
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
                    crop_lat_min = st.number_input("Lat Mín (ºN)", value=float(np.min(all_lats)), step=0.1, format="%.2f", key="inp_c_lat_min")
                with c_l2:
                    crop_lat_max = st.number_input("Lat Máx (ºN)", value=float(np.max(all_lats)), step=0.1, format="%.2f", key="inp_c_lat_max")

                c_lo1, c_lo2 = st.columns(2)
                with c_lo1:
                    crop_lon_min = st.number_input("Lon Mín (ºE/W)", value=float(np.min(all_lons)), step=0.1, format="%.2f", key="inp_c_lon_min")
                with c_lo2:
                    crop_lon_max = st.number_input("Lon Máx (ºE/W)", value=float(np.max(all_lons)), step=0.1, format="%.2f", key="inp_c_lon_max")
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

        # Aplicação dos Filtros
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

        st.markdown("---")
        st.markdown('<div class="step-pill">4. Visualização Oceanográfica & Exportação</div>', unsafe_allow_html=True)

        with st.expander("🗺️ Pré-visualização Oceanográfica Interativa (Mapas & Perfis CTD)", expanded=True):
            viz_tab_map, viz_tab_profile = st.tabs(["Mapa de Superfície (Campo 2D)", "Perfil Vertical (CTD / Profundidade)"])

            with viz_tab_map:
                if lat_dim and lon_dim and len(selected_vars) > 0:
                    first_var = selected_vars[0]
                    slice_2d = filtered_ds[first_var]
                    for d in slice_2d.dims:
                        if d not in [lat_dim, lon_dim]:
                            slice_2d = slice_2d.isel({d: 0})

                    lats = slice_2d[lat_dim].values
                    lons = slice_2d[lon_dim].values
                    vals = slice_2d.values

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
                if depth_dim and depth_dim in ds.dims and len(selected_vars) > 0:
                    first_var = selected_vars[0]
                    var_data = ds[first_var]
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
                        yaxis=dict(autorange="reversed"),
                        margin=dict(l=40, r=40, t=50, b=40),
                        height=380,
                    )
                    st.plotly_chart(fig_prof, use_container_width=True)
                else:
                    st.caption("Ficheiro sem dimensão de profundidade para perfil CTD.")

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

                with st.expander("📊 Estatísticas Descritivas dos Dados (Média, Desvio Padrão, Quartis)"):
                    st.dataframe(df.describe(), use_container_width=True)

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


# ---------------------------------------------------------
# 6. MÓDULO 2: Calculadora de Coordenadas & CMEMS
# ---------------------------------------------------------
def render_coords_tab():
    st.markdown('<div class="step-pill">🧭 Conversor de Coordenadas Geográficas</div>', unsafe_allow_html=True)
    st.markdown(
        "Selecione um ponto diretamente no **mapa batimétrico com isolinhas de profundidade** para converter instantaneamente entre "
        "**Graus Decimais (DD)**, **GPS Náutico (DMM)** e **Cartas Náuticas (DMS)** com indicação direta das componentes **N, S, E, W**."
    )

    # Inicializar coordenadas na sessão
    if "coord_lat" not in st.session_state:
        st.session_state["coord_lat"] = 37.0150
    if "coord_lon" not in st.session_state:
        st.session_state["coord_lon"] = -7.9350

    # Barra de presets rápidos e indicador
    col_pre, col_stat = st.columns([2, 1])
    with col_pre:
        preset_choice = st.selectbox(
            "⚓ Carregar Estação Oceanográfica Didática (Portugal & Regiões):",
            options=list(gc.PRESET_LOCATIONS.keys()),
            index=0,
            help="Carrega coordenadas de estações conhecidas da costa portuguesa, ilhas e montes submarinos.",
        )
        if preset_choice != "Personalizado" and gc.PRESET_LOCATIONS.get(preset_choice) is not None:
            p_lat, p_lon = gc.PRESET_LOCATIONS[preset_choice]
            if abs(st.session_state["coord_lat"] - p_lat) > 1e-4 or abs(st.session_state["coord_lon"] - p_lon) > 1e-4:
                st.session_state["coord_lat"] = p_lat
                st.session_state["coord_lon"] = p_lon
                st.rerun()

    curr_lat = float(st.session_state["coord_lat"])
    curr_lon = float(st.session_state["coord_lon"])

    # Representações calculadas para rótulos
    _, _, _, _, dms_lat_str = gc.dd_to_dms(curr_lat, True)
    _, _, _, _, dms_lon_str = gc.dd_to_dms(curr_lon, False)
    _, _, _, dmm_lat_str = gc.dd_to_dmm(curr_lat, True)
    _, _, _, dmm_lon_str = gc.dd_to_dmm(curr_lon, False)
    card_lat_str = gc.dd_to_cardinal(curr_lat, True)
    card_lon_str = gc.dd_to_cardinal(curr_lon, False)

    with col_stat:
        st.markdown(
            f"""
            <div style="background: rgba(14, 165, 233, 0.1); border: 1px solid rgba(56, 189, 248, 0.3); border-radius: 10px; padding: 10px 14px; text-align: center; margin-top: 4px;">
                <div style="font-size: 0.72rem; color: #94a3b8; text-transform: uppercase; font-weight: 700;">Ponto Selecionado</div>
                <div style="font-size: 0.98rem; color: #38bdf8; font-weight: 700; margin-top: 2px;">{card_lat_str}, {card_lon_str}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    # ---------------------------------------------------------
    # 1. MAPA BATIMÉTRICO GLOBAL INTERATIVO (POR CIMA DA CONVERSÃO)
    # ---------------------------------------------------------
    st.markdown("---")
    st.markdown("#### 🌊 Mapa Batimétrico Global (Clique no mapa para escolher o ponto)")
    st.caption(
        "Cartografia batimétrica de alta resolução (GEBCO / NOAA / ESRI Ocean Basemap) com relevo submarino sombreado, plataformas continentais, "
        "fossas e **isolinhas de profundidade (isóbatas em metros)**. **Clique em qualquer zona do oceano para atualizar instantaneamente as coordenadas e conversões.**"
    )

    # Criar mapa Folium com camadas batimétricas
    m = folium.Map(
        location=[curr_lat, curr_lon],
        zoom_start=7,
        tiles=None,
        control_scale=True,
    )

    # 1. Camada Base: Relevo Batimétrico Shaded Relief
    folium.TileLayer(
        tiles="https://server.arcgisonline.com/ArcGIS/rest/services/Ocean/World_Ocean_Base/MapServer/tile/{z}/{y}/{x}",
        attr="ESRI, GEBCO, NOAA",
        name="Relevo Batimétrico Oceânico",
        control=False,
    ).add_to(m)

    # 2. Camada de Sobreposição: Isolinhas de Profundidade e Toponímia
    folium.TileLayer(
        tiles="https://server.arcgisonline.com/ArcGIS/rest/services/Ocean/World_Ocean_Reference/MapServer/tile/{z}/{y}/{x}",
        attr="ESRI Ocean Reference",
        name="Isolinhas de Profundidade e Toponímia",
        overlay=True,
        control=False,
    ).add_to(m)

    # 3. Marcador da Estação Selecionada
    folium.Marker(
        [curr_lat, curr_lon],
        tooltip=f"Ponto Selecionado: {card_lat_str}, {card_lon_str}",
        popup=f"<b>Estação Oceanográfica:</b><br>{card_lat_str}, {card_lon_str}<br>DD: {curr_lat:.6f}, {curr_lon:.6f}",
        icon=folium.Icon(color="red", icon="crosshairs", prefix="fa"),
    ).add_to(m)

    # Renderizar mapa interativo e capturar clique
    map_data = st_folium(
        m,
        height=460,
        width="100%",
        returned_objects=["last_clicked"],
        key=f"bathy_map_picker_{curr_lat:.4f}_{curr_lon:.4f}",
    )

    if map_data and map_data.get("last_clicked"):
        clicked_lat = round(map_data["last_clicked"]["lat"], 6)
        clicked_lon = round(map_data["last_clicked"]["lng"], 6)
        if abs(clicked_lat - st.session_state["coord_lat"]) > 1e-4 or abs(clicked_lon - st.session_state["coord_lon"]) > 1e-4:
            st.session_state["coord_lat"] = clicked_lat
            st.session_state["coord_lon"] = clicked_lon
            st.rerun()

    # ---------------------------------------------------------
    # 2. TABELA DE CONVERSÃO MULTI-FORMATO (POR BAIXO DO MAPA)
    # ---------------------------------------------------------
    st.markdown("---")
    st.markdown("#### 📊 Tabela de Conversão Multi-Formato do Ponto Selecionado")

    c_c1, c_c2 = st.columns(2)
    with c_c1:
        st.markdown(
            f"""
            <div class="kpi-card">
                <div class="kpi-label">Componentes Cardinais (N S E W)</div>
                <div class="kpi-value" style="font-size: 1.22rem; color: #38bdf8;">{card_lat_str}<br>{card_lon_str}</div>
                <div class="kpi-desc">Notação formal de oceanografia (direto para estações CMEMS, bóias e cruzeiros)</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with c_c2:
        st.markdown(
            f"""
            <div class="kpi-card">
                <div class="kpi-label">Graus Decimais (DD com sinal)</div>
                <div class="kpi-value" style="font-size: 1.22rem; color: #34d399;">Lat: {curr_lat:.6f}<br>Lon: {curr_lon:.6f}</div>
                <div class="kpi-desc">Padrão numérico computacional (Python, R, QGIS, Excel e GIS)</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    c_c3, c_c4 = st.columns(2)
    with c_c3:
        st.markdown(
            f"""
            <div class="kpi-card">
                <div class="kpi-label">GPS Náutico / Diário de Bordo (DMM)</div>
                <div class="kpi-value" style="font-size: 1.2rem; color: #f59e0b;">{dmm_lat_str}<br>{dmm_lon_str}</div>
                <div class="kpi-desc">Graus e minutos decimais habitual a bordo e em rosetas CTD</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with c_c4:
        st.markdown(
            f"""
            <div class="kpi-card">
                <div class="kpi-label">Cartas Náuticas (DMS)</div>
                <div class="kpi-value" style="font-size: 1.2rem; color: #a78bfa;">{dms_lat_str}<br>{dms_lon_str}</div>
                <div class="kpi-desc">Graus, minutos e segundos (cartografia náutica impressa)</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    # ---------------------------------------------------------
    # 3. OPÇÃO: AJUSTE MANUAL POR TECLADO
    # ---------------------------------------------------------
    with st.expander("✏️ Ajustar ou Inserir Coordenadas Manualmente (Teclado)"):
        st.caption("Se tiver coordenadas exatas de um diário de bordo, artigo ou GPS, pode introduzi-las aqui:")
        mode_choice = st.radio(
            "Formato de Entrada Manual:",
            [
                "1️⃣ Graus Decimais (DD com sinal)",
                "2️⃣ Componentes Cardinais (N/S e E/W)",
                "3️⃣ GPS Náutico (DMM)",
                "4️⃣ Cartas Náuticas (DMS)",
                "📋 Colar Texto Livre (Smart Parser)",
            ],
            horizontal=True,
        )

        new_lat = curr_lat
        new_lon = curr_lon

        if "1️⃣" in mode_choice:
            m1, m2 = st.columns(2)
            with m1:
                new_lat = st.number_input("Latitude (DD):", value=float(curr_lat), step=0.001, format="%.6f", min_value=-90.0, max_value=90.0, key="man_dd_lat")
            with m2:
                new_lon = st.number_input("Longitude (DD):", value=float(curr_lon), step=0.001, format="%.6f", min_value=-180.0, max_value=180.0, key="man_dd_lon")

        elif "2️⃣" in mode_choice:
            m1, m2, m3, m4 = st.columns([3, 1, 3, 1])
            with m1:
                lat_abs = st.number_input("Latitude:", value=float(abs(curr_lat)), step=0.001, format="%.6f", min_value=0.0, max_value=90.0, key="man_card_lat")
            with m2:
                lat_h = st.selectbox("Hemi:", ["N", "S"], index=0 if curr_lat >= 0 else 1, key="man_lh")
            with m3:
                lon_abs = st.number_input("Longitude:", value=float(abs(curr_lon)), step=0.001, format="%.6f", min_value=0.0, max_value=180.0, key="man_card_lon")
            with m4:
                lon_h = st.selectbox("Hemi:", ["W", "E"], index=0 if curr_lon <= 0 else 1, key="man_loh")
            new_lat = lat_abs if lat_h == "N" else -lat_abs
            new_lon = lon_abs if lon_h == "E" else -lon_abs

        elif "3️⃣" in mode_choice:
            d_l, m_l, h_l, _ = gc.dd_to_dmm(curr_lat, True)
            d_lo, m_lo, h_lo, _ = gc.dd_to_dmm(curr_lon, False)
            m1, m2, m3 = st.columns([2, 3, 1])
            with m1:
                dmm_l_d = st.number_input("Lat Graus:", value=int(d_l), min_value=0, max_value=90, step=1, key="man_dmm_ld")
            with m2:
                dmm_l_m = st.number_input("Lat Minutos:", value=float(m_l), min_value=0.0, max_value=59.9999, step=0.1, format="%.4f", key="man_dmm_lm")
            with m3:
                dmm_l_h = st.selectbox("Hemi:", ["N", "S"], index=0 if h_l == "N" else 1, key="man_dmm_lh")
            m4, m5, m6 = st.columns([2, 3, 1])
            with m4:
                dmm_lo_d = st.number_input("Lon Graus:", value=int(d_lo), min_value=0, max_value=180, step=1, key="man_dmm_lod")
            with m5:
                dmm_lo_m = st.number_input("Lon Minutos:", value=float(m_lo), min_value=0.0, max_value=59.9999, step=0.1, format="%.4f", key="man_dmm_lom")
            with m6:
                dmm_lo_h = st.selectbox("Hemi:", ["W", "E"], index=0 if h_lo == "W" else 1, key="man_dmm_loh")
            new_lat = gc.dmm_to_dd(dmm_l_d, dmm_l_m, dmm_l_h)
            new_lon = gc.dmm_to_dd(dmm_lo_d, dmm_lo_m, dmm_lo_h)

        elif "4️⃣" in mode_choice:
            d_l, m_l, s_l, h_l, _ = gc.dd_to_dms(curr_lat, True)
            d_lo, m_lo, s_lo, h_lo, _ = gc.dd_to_dms(curr_lon, False)
            m1, m2, m3, m4 = st.columns([2, 2, 2, 1])
            with m1:
                dms_l_d = st.number_input("Lat º:", value=int(d_l), min_value=0, max_value=90, step=1, key="man_dms_ld")
            with m2:
                dms_l_m = st.number_input("Lat ':", value=int(m_l), min_value=0, max_value=59, step=1, key="man_dms_lm")
            with m3:
                dms_l_s = st.number_input('Lat ":', value=float(s_l), min_value=0.0, max_value=59.99, step=0.1, format="%.2f", key="man_dms_ls")
            with m4:
                dms_l_h = st.selectbox("Hemi:", ["N", "S"], index=0 if h_l == "N" else 1, key="man_dms_lh")
            m5, m6, m7, m8 = st.columns([2, 2, 2, 1])
            with m5:
                dms_lo_d = st.number_input("Lon º:", value=int(d_lo), min_value=0, max_value=180, step=1, key="man_dms_lod")
            with m6:
                dms_lo_m = st.number_input("Lon ':", value=int(m_lo), min_value=0, max_value=59, step=1, key="man_dms_lom")
            with m7:
                dms_lo_s = st.number_input('Lon ":', value=float(s_lo), min_value=0.0, max_value=59.99, step=0.1, format="%.2f", key="man_dms_los")
            with m8:
                dms_lo_h = st.selectbox("Hemi:", ["W", "E"], index=0 if h_lo == "W" else 1, key="man_dms_loh")
            new_lat = gc.dms_to_dd(dms_l_d, dms_l_m, dms_l_s, dms_l_h)
            new_lon = gc.dms_to_dd(dms_lo_d, dms_lo_m, dms_lo_s, dms_lo_h)

        elif "📋" in mode_choice:
            raw_val = st.text_input("Cole aqui o texto com coordenadas:", value=f"{curr_lat:.4f}, {curr_lon:.4f}", key="man_paste_str")
            parsed_val = gc.parse_coordinate_string(raw_val)
            if parsed_val:
                new_lat, new_lon = parsed_val
                st.success(f"✓ Identificado: {new_lat:.6f}, {new_lon:.6f}")

        if st.button("📍 Atualizar Ponto no Mapa", use_container_width=True):
            st.session_state["coord_lat"] = round(new_lat, 6)
            st.session_state["coord_lon"] = round(new_lon, 6)
            st.rerun()


# ---------------------------------------------------------
# 7. Renderização com Separadores Principais
# ---------------------------------------------------------
tab_converter, tab_coords = st.tabs([
    "🌊 Conversor NetCDF → CSV",
    "🧭 Conversor de Coordenadas",
])

with tab_converter:
    render_netcdf_tab(preset_all)

with tab_coords:
    render_coords_tab()


# ---------------------------------------------------------
# 8. Rodapé com Branding e "Powered by"
# ---------------------------------------------------------
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
