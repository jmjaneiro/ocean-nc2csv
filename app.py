"""
OceanNC to CSV Converter
Ferramenta interativa para aulas de Oceanografia Física e Biologia Marinha.
Converte ficheiros NetCDF (.nc) para CSV com assistente pedagógico de dimensões.
"""

import io
import os
import tempfile
import numpy as np
import pandas as pd
import streamlit as st
import xarray as xr

# Configuração da Página
st.set_page_config(
    page_title="OceanNC -> CSV Converter",
    page_icon="🌊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Estilo personalizado com CSS
st.markdown(
    """
    <style>
    .main-header {
        color: #0077b6;
        font-size: 2.2rem;
        font-weight: 700;
        margin-bottom: 0.2rem;
    }
    .sub-header {
        color: #4a5568;
        font-size: 1.05rem;
        margin-bottom: 1.5rem;
    }
    .card {
        background-color: #f8fafc;
        border-radius: 8px;
        padding: 18px;
        border-left: 5px solid #0077b6;
        margin-bottom: 15px;
    }
    .metric-box {
        background-color: #e0f2fe;
        border-radius: 6px;
        padding: 10px;
        text-align: center;
    }
    </style>
""",
    unsafe_allow_html=True,
)


def find_dimension(ds, candidates):
    """Procura por um nome de dimensão na lista de candidatos."""
    for cand in candidates:
        for dim in ds.dims:
            if cand.lower() == dim.lower():
                return dim
        for coord in ds.coords:
            if cand.lower() == coord.lower():
                return coord
    return None


def get_dataset_summary(ds):
    """Calcula estatísticas de dimensões e número teórico de pontos."""
    dim_sizes = {str(k): int(v) for k, v in ds.dims.items()}
    total_points = 1
    for size in dim_sizes.values():
        total_points *= size
    return dim_sizes, total_points


# Cabeçalho
st.markdown(
    '<div class="main-header">🌊 OceanNC to CSV Converter</div>',
    unsafe_allow_html=True,
)
st.markdown(
    '<div class="sub-header">Ferramenta pedagógica para Biologia Marinha & Oceanografia Física • Conversão inteligente de grelhas NetCDF para dados tabulares (CSV, Excel, R, QGIS)</div>',
    unsafe_allow_html=True,
)

# Barra lateral com guia e metadados
with st.sidebar:
    st.image(
        "https://images.unsplash.com/photo-1518837695005-2083093ee35b?auto=format&fit=crop&w=600&q=80",
        use_container_width=True,
    )
    st.markdown("### 🧭 Guia Rápido")
    st.info(
        """
    **1. Carregue o ficheiro `.nc`** (Copernicus, NOAA, etc.) ou use o exemplo.
    
    **2. Responda às perguntas**:
    * Que variáveis pretende (SST, Salinidade, etc.)?
    * Como tratar a profundidade (4D -> 2D)?
    * Deseja recortar o período ou coordenadas?
    
    **3. Pré-visualize e Descarregue** o CSV pronto para Excel ou R!
    """
    )

    st.markdown("---")
    st.markdown("#### 💡 Dica Oceanográfica")
    st.caption(
        "O Microsoft Excel tem um limite estrito de **1.048.576 linhas**. "
        "Ficheiros 4D com várias profundidades ultrapassam este limite com facilidade. "
        "Selecione **Superfície** ou recorte a área para manter o ficheiro leve e utilizável."
    )


# Área de Carregamento de Ficheiros
col_upload, col_demo = st.columns([3, 1])

with col_upload:
    uploaded_file = st.file_uploader(
        "📂 Arraste o ficheiro NetCDF (.nc / .nc4) ou clique para procurar:",
        type=["nc", "nc4", "netcdf"],
        help="Suporta formatos NetCDF-3 e NetCDF-4 comuns em oceanografia e satélites.",
    )

with col_demo:
    st.markdown("<div style='height: 28px;'></div>", unsafe_allow_html=True)
    use_sample = st.button(
        "🧪 Testar com Dados de Exemplo (Algarve)",
        use_container_width=True,
        help="Carrega um conjunto de dados 4D realista com Temperatura, Salinidade e Clorofila-a.",
    )

# Determinar qual ficheiro carregar
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
        st.info(
            "Tente verificar se o ficheiro está corrompido ou se requer bibliotecas HDF5 específicas."
        )
    finally:
        try:
            os.remove(tmp_path)
        except Exception:
            pass

elif use_sample or "sample_loaded" in st.session_state:
    st.session_state["sample_loaded"] = True
    sample_file = "exemplo_oceanografia_algarve.nc"
    if not os.path.exists(sample_file):
        # Se ainda não existir no disco, gera na hora
        from generate_sample_nc import generate_sample_dataset

        ds_sample = generate_sample_dataset()
        ds_sample.to_netcdf(sample_file)
    filename = "exemplo_oceanografia_algarve.nc (Costa Sul de Portugal)"
    ds = xr.open_dataset(sample_file)


# Se temos um dataset carregado, inicia o assistente inteligente
if ds is not None:
    st.success(f"Ficheiro carregado com sucesso: **{filename}**")

    # Inspecionar Dimensões
    dim_sizes, total_raw_points = get_dataset_summary(ds)

    # Identificar ecrã das dimensões
    time_dim = find_dimension(
        ds, ["time", "time_counter", "valid_time", "t", "date"]
    )
    depth_dim = find_dimension(
        ds, ["depth", "deptht", "lev", "level", "z", "elevation"]
    )
    lat_dim = find_dimension(ds, ["latitude", "lat", "nav_lat", "y"])
    lon_dim = find_dimension(ds, ["longitude", "lon", "nav_lon", "x"])

    # Separar variáveis de dados de coordenadas
    data_vars = list(ds.data_vars.keys())
    if not data_vars:
        # Caso especial: tudo são coordenadas
        data_vars = list(ds.variables.keys())

    # Painel de Diagnóstico do Ficheiro
    st.markdown("### 📊 1. Diagnóstico do Ficheiro Oceanográfico")

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total de Dimensões", f"{len(ds.dims)}D")
    with col2:
        st.metric("Variáveis Científicas", len(data_vars))
    with col3:
        st.metric("Pontos na Grelha Bruta", f"{total_raw_points:,}")
    with col4:
        if total_raw_points > 1_048_576:
            st.error("⚠️ Excede limite do Excel")
        else:
            st.success("✅ Tamanho Seguro para Excel")

    with st.expander("🔍 Inspecionar Dimensões e Metadados do NetCDF"):
        dim_info = []
        for dim, length in dim_sizes.items():
            dim_type = "Outra"
            if dim == time_dim:
                dim_type = "Temporal (Tempo)"
            elif dim == depth_dim:
                dim_type = "Vertical (Profundidade)"
            elif dim == lat_dim:
                dim_type = "Espacial (Latitude)"
            elif dim == lon_dim:
                dim_type = "Espacial (Longitude)"

            dim_info.append(
                {
                    "Dimensão": dim,
                    "Tipo": dim_type,
                    "N.º de Pontos": length,
                }
            )
        st.table(pd.DataFrame(dim_info))

        if ds.attrs:
            st.markdown("**Atributos Globais (Metadados):**")
            st.json(dict(list(ds.attrs.items())[:8]))

    # --- Assistente de Configuração da Conversão ---
    st.markdown("---")
    st.markdown("### ⚙️ 2. Assistente Guiado de Filtragem e Conversão")
    st.markdown(
        "Responda às questões abaixo para ajustar a tabela às suas necessidades:"
    )

    col_q1, col_q2 = st.columns(2)

    with col_q1:
        st.markdown("#### 🧪 Variáveis a Incluir")
        # Mostrar variáveis com os seus nomes longos e unidades se disponíveis
        var_labels = {}
        for v in data_vars:
            long_name = ds[v].attrs.get("long_name", v)
            units = ds[v].attrs.get("units", "")
            unit_str = f" [{units}]" if units else ""
            var_labels[v] = f"{v} - {long_name}{unit_str}"

        selected_vars = st.multiselect(
            "Selecione as variáveis oceanográficas que pretende no CSV:",
            options=data_vars,
            default=data_vars,
            format_func=lambda x: var_labels.get(x, x),
            help="Pode remover variáveis que não sejam relevantes para a sua análise para reduzir o tamanho.",
        )

        if not selected_vars:
            st.warning("⚠️ Selecione pelo menos uma variável para exportar.")
            st.stop()

    with col_q2:
        st.markdown("#### 🌊 Tratamento da Profundidade")
        if depth_dim and depth_dim in ds.dims:
            depth_values = ds[depth_dim].values
            depth_units = ds[depth_dim].attrs.get("units", "m")

            depth_choice = st.radio(
                f"O ficheiro contém {len(depth_values)} níveis de profundidade ({depth_dim}). O que pretende fazer?",
                [
                    "🟢 Apenas Superfície (0 m / primeiro nível) [Recomendado]",
                    "🔵 Escolher uma profundidade específica",
                    "🟡 Todas as profundidades (Atenção: multiplica o n.º de linhas)",
                ],
                index=0,
            )

            chosen_depth_idx = 0
            if "Superfície" in depth_choice:
                chosen_depth_idx = 0
            elif "específica" in depth_choice:
                depth_options = [
                    f"{float(val):.1f} {depth_units} (índice {i})"
                    for i, val in enumerate(depth_values)
                ]
                chosen_option = st.selectbox(
                    "Selecione o nível de profundidade desejado:",
                    options=depth_options,
                    index=0,
                )
                chosen_depth_idx = depth_options.index(chosen_option)
            else:
                chosen_depth_idx = None  # Todas
        else:
            st.info(
                "ℹ️ Este ficheiro não tem dimensão vertical (dados de superfície ou 2D)."
            )
            depth_choice = None
            chosen_depth_idx = None

    col_q3, col_q4 = st.columns(2)

    with col_q3:
        st.markdown("#### ⏱️ Tratamento do Tempo")
        if time_dim and time_dim in ds.dims:
            time_values = ds[time_dim].values
            n_times = len(time_values)

            time_choice = st.radio(
                f"O ficheiro tem {n_times} passo(s) temporal(is).",
                [
                    "📅 Todos os passos de tempo",
                    "🎯 Apenas uma data / passo de tempo específico",
                ],
                index=0 if n_times <= 365 else 1,
            )

            chosen_time_idx = None
            if "Apenas uma data" in time_choice:
                time_str_list = [str(t)[:19] for t in time_values]
                chosen_time_str = st.selectbox(
                    "Selecione a data/hora:", options=time_str_list, index=0
                )
                chosen_time_idx = time_str_list.index(chosen_time_str)
        else:
            st.info("ℹ️ Este ficheiro não possui dimensão temporal.")
            time_choice = None
            chosen_time_idx = None

    with col_q4:
        st.markdown("#### 🗺️ Recorte Geográfico (Opcional)")
        enable_spatial_crop = st.checkbox(
            "Recortar coordenadas (Bounding Box)",
            value=False,
            help="Permite selecionar apenas uma sub-região geográfica.",
        )

        min_lat_val, max_lat_val = None, None
        min_lon_val, max_lon_val = None, None

        if enable_spatial_crop and lat_dim and lon_dim:
            lats = ds[lat_dim].values
            lons = ds[lon_dim].values

            c_lat1, c_lat2 = st.columns(2)
            with c_lat1:
                min_lat_val = st.number_input(
                    "Lat Mínima (ºN)",
                    value=float(np.min(lats)),
                    step=0.1,
                    format="%.2f",
                )
            with c_lat2:
                max_lat_val = st.number_input(
                    "Lat Máxima (ºN)",
                    value=float(np.max(lats)),
                    step=0.1,
                    format="%.2f",
                )

            c_lon1, c_lon2 = st.columns(2)
            with c_lon1:
                min_lon_val = st.number_input(
                    "Lon Mínima (ºE/ºW)",
                    value=float(np.min(lons)),
                    step=0.1,
                    format="%.2f",
                )
            with c_lon2:
                max_lon_val = st.number_input(
                    "Lon Máxima (ºE/ºW)",
                    value=float(np.max(lons)),
                    step=0.1,
                    format="%.2f",
                )
        elif enable_spatial_crop:
            st.warning("Coordenadas de latitude/longitude não detetadas.")

    # Opções de Limpeza e Formato do Ficheiro
    st.markdown("---")
    st.markdown("#### 🧹 Opções de Limpeza e Formatação")
    col_opt1, col_opt2, col_opt3 = st.columns(3)

    with col_opt1:
        drop_na = st.checkbox(
            "Excluir pontos em terra / NaNs",
            value=True,
            help="Remove linhas onde as variáveis têm valor nulo (terra ou sem dados de satélite), reduzindo drasticamente o ficheiro.",
        )

    with col_opt2:
        csv_sep = st.selectbox(
            "Separador de Colunas do CSV:",
            options=[", (Vírgula - Padrão R / Python / QGIS)", "; (Ponto e Vírgula - Padrão Excel PT)"],
            index=0,
            help="No Excel em português de Portugal, o separador padrão é ponto e vírgula (;).",
        )
        sep_char = ";" if ";" in csv_sep else ","

    with col_opt3:
        decimal_char = st.selectbox(
            "Separador Decimal:",
            options=[". (Ponto - 36.5)", ", (Vírgula - 36,5 - Excel PT)"],
            index=0 if sep_char == "," else 1,
            help="Escolha vírgula decimal se quiser que o Excel em português formate automaticamente os números.",
        )
        dec_char = "," if "," in decimal_char else "."

    # --- Aplicação dos Filtros no xarray ---
    filtered_ds = ds[selected_vars]

    # Filtro de Profundidade
    if depth_dim and depth_dim in filtered_ds.dims:
        if chosen_depth_idx is not None:
            filtered_ds = filtered_ds.isel({depth_dim: chosen_depth_idx})

    # Filtro de Tempo
    if time_dim and time_dim in filtered_ds.dims:
        if chosen_time_idx is not None:
            filtered_ds = filtered_ds.isel({time_dim: chosen_time_idx})

    # Filtro Geográfico
    if enable_spatial_crop and lat_dim and lon_dim:
        try:
            # Ordenar coordenadas se necessário
            lat_slice = (
                slice(min_lat_val, max_lat_val)
                if min_lat_val < max_lat_val
                else slice(max_lat_val, min_lat_val)
            )
            lon_slice = (
                slice(min_lon_val, max_lon_val)
                if min_lon_val < max_lon_val
                else slice(max_lon_val, min_lon_val)
            )
            filtered_ds = filtered_ds.sel(
                {lat_dim: lat_slice, lon_dim: lon_slice}
            )
        except Exception as e:
            st.warning(f"Não foi possível aplicar o recorte espacial: {e}")

    # Estimativa de linhas pós-filtros
    _, estimated_filtered_points = get_dataset_summary(filtered_ds)

    st.markdown("---")
    st.markdown("### 🚀 3. Processamento & Pré-visualização")

    col_res1, col_res2 = st.columns([2, 1])
    with col_res1:
        st.write(
            f"**Tamanho estimado após filtros:** ~`{estimated_filtered_points:,}` linhas potenciais na grelha."
        )
        if estimated_filtered_points > 1_048_576:
            st.error(
                f"⚠️ Atenção: A grelha filtrada ainda tem {estimated_filtered_points:,} pontos. "
                "Ultrapassa o limite de 1.048.576 linhas do Excel! "
                "Selecione um passo de tempo específico ou recorte a área para diminuir."
            )
        else:
            st.success("✅ Tamanho totalmente seguro para Excel e R!")

    # Botão de Conversão
    if st.button("⚡ Converter e Pré-visualizar Tabela", type="primary", use_container_width=True):
        with st.spinner("A converter NetCDF para DataFrame e a formatar dados..."):
            try:
                # Conversão para pandas DataFrame
                df = filtered_ds.to_dataframe()

                # Se houver índice multi-nível (lat, lon, time, etc.), torná-los colunas normais
                df = df.reset_index()

                # Descartar NaNs / pontos de terra se solicitado
                if drop_na:
                    original_len = len(df)
                    df = df.dropna(subset=selected_vars, how="all")
                    final_len = len(df)
                    st.info(
                        f"🧹 Limpeza concluída: Foram removidas {original_len - final_len:,} linhas com valores nulos (ex: terra)."
                    )

                # Guardar no estado da sessão para download
                st.session_state["converted_df"] = df
                st.session_state["df_ready"] = True

            except Exception as e:
                st.error(f"Erro ao processar dados: {e}")

    # Exibição do resultado se pronto
    if st.session_state.get("df_ready", False) and "converted_df" in st.session_state:
        df = st.session_state["converted_df"]

        st.markdown(f"#### 📋 Tabela Gerada: `{len(df):,}` linhas × `{len(df.columns)}` colunas")
        st.dataframe(df.head(15), use_container_width=True)

        with st.expander("📈 Estatísticas Resumidas (Mín, Méd, Máx)"):
            st.dataframe(df.describe())

        # Gerar o ficheiro CSV em memória
        csv_buffer = io.StringIO()
        df.to_csv(csv_buffer, sep=sep_char, decimal=dec_char, index=False)
        csv_bytes = csv_buffer.getvalue().encode("utf-8-sig")  # utf-8-sig para abrir com acentos corretos no Excel

        clean_filename = filename.replace(".nc", "").replace(".nc4", "").replace(" ", "_")
        output_filename = f"{clean_filename}_convertido.csv"

        st.download_button(
            label=f"📥 Descarregar CSV para Excel / R ({len(csv_bytes)/1024:.1f} KB)",
            data=csv_bytes,
            file_name=output_filename,
            mime="text/csv",
            type="primary",
            use_container_width=True,
        )

# Rodapé pedagógico
st.markdown("---")
st.caption(
    "OceanNC to CSV Converter • Desenvolvido para apoio às aulas de Oceanografia Física e Biologia Marinha. "
    "Compatível com grelhas de modelos hidrodinâmicos (ROMS, NEMO, Copernicus Marine) e dados de satélite (MODIS, Sentinel)."
)
