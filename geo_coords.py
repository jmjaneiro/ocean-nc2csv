"""
Módulo de Conversão de Coordenadas Geográficas e Integração CMEMS (Copernicus Marine).
Apoio a Oceanografia Física e Biologia Marinha.
"""

import math
import re


def dd_to_dms(val: float, is_lat: bool = True):
    """Converte Graus Decimais (DD) para Graus, Minutos e Segundos (DMS)."""
    hemi = ("N" if val >= 0 else "S") if is_lat else ("E" if val >= 0 else "W")
    abs_v = abs(val)
    d = int(abs_v)
    m_full = (abs_v - d) * 60
    m = int(m_full)
    s = (m_full - m) * 60
    # Evitar arredondamento que leve a 60 segundos
    if round(s, 2) >= 60.0:
        s = 0.0
        m += 1
    if m >= 60:
        m = 0
        d += 1
    formatted = f"{d}° {m:02d}' {s:05.2f}\" {hemi}"
    return d, m, s, hemi, formatted


def dd_to_dmm(val: float, is_lat: bool = True):
    """Converte Graus Decimais (DD) para Graus e Minutos Decimais (DMM - GPS Náutico)."""
    hemi = ("N" if val >= 0 else "S") if is_lat else ("E" if val >= 0 else "W")
    abs_v = abs(val)
    d = int(abs_v)
    m = (abs_v - d) * 60
    if round(m, 4) >= 60.0:
        m = 0.0
        d += 1
    formatted = f"{d}° {m:06.3f}' {hemi}"
    return d, m, hemi, formatted


def dd_to_cardinal(val: float, is_lat: bool = True, decimals: int = 6):
    """Devolve a representação cardinal (ex: 37.015000° N ou 7.935000° W)."""
    hemi = ("N" if val >= 0 else "S") if is_lat else ("E" if val >= 0 else "W")
    return f"{abs(val):.{decimals}f}° {hemi}"


def dms_to_dd(d: int, m: int, s: float, hemi: str) -> float:
    """Converte DMS para Graus Decimais (DD com sinal)."""
    dd = float(d) + float(m) / 60.0 + float(s) / 3600.0
    return -dd if hemi.upper() in ["S", "W"] else dd


def dmm_to_dd(d: int, m: float, hemi: str) -> float:
    """Converte DMM para Graus Decimais (DD com sinal)."""
    dd = float(d) + float(m) / 60.0
    return -dd if hemi.upper() in ["S", "W"] else dd


def lon_to_360(lon: float) -> float:
    """Converte longitude [-180, 180] para grelha global [0, 360]."""
    return (lon + 360.0) % 360.0


def parse_coordinate_string(text: str):
    """
    Parser inteligente e flexível de coordenadas de texto.
    Suporta:
    - '37.015, -7.935'
    - '37.015 N, 7.935 W' ou '37.015N 7.935W'
    - '37° 00' 54" N, 7° 56' 06" W'
    - '37 00.900 N, 7 56.100 W'
    """
    if not text:
        return None

    cleaned = text.strip().replace(";", ",").replace("\t", " ")

    # 1. Padrão DMS: 37° 00' 54" N, 7° 56' 06" W
    m_dms = re.search(
        r"(\d+)\s*°?\s*(\d+)\s*[\'′]?\s*(\d+(?:\.\d+)?)\s*[\"″]?\s*([NSns])"
        r"[\s,;]*"
        r"(\d+)\s*°?\s*(\d+)\s*[\'′]?\s*(\d+(?:\.\d+)?)\s*[\"″]?\s*([EWew])",
        cleaned,
    )
    if m_dms:
        lat = dms_to_dd(
            int(m_dms.group(1)),
            int(m_dms.group(2)),
            float(m_dms.group(3)),
            m_dms.group(4),
        )
        lon = dms_to_dd(
            int(m_dms.group(5)),
            int(m_dms.group(6)),
            float(m_dms.group(7)),
            m_dms.group(8),
        )
        return lat, lon

    # 2. Padrão DMM (GPS): 37° 00.900' N, 7° 56.100' W
    m_dmm = re.search(
        r"(\d+)\s*°?\s*(\d+(?:\.\d+)?)\s*[\'′]?\s*([NSns])"
        r"[\s,;]*"
        r"(\d+)\s*°?\s*(\d+(?:\.\d+)?)\s*[\'′]?\s*([EWew])",
        cleaned,
    )
    if m_dmm:
        lat = dmm_to_dd(
            int(m_dmm.group(1)), float(m_dmm.group(2)), m_dmm.group(3)
        )
        lon = dmm_to_dd(
            int(m_dmm.group(4)), float(m_dmm.group(5)), m_dmm.group(6)
        )
        return lat, lon

    # 3. Padrão DD com cardinais: 37.015 N, 7.935 W
    m_dd_card = re.search(
        r"(\d+(?:\.\d+)?)\s*°?\s*([NSns])[\s,;]*(\d+(?:\.\d+)?)\s*°?\s*([EWew])",
        cleaned,
    )
    if m_dd_card:
        lat = float(m_dd_card.group(1)) * (
            -1 if m_dd_card.group(2).upper() == "S" else 1
        )
        lon = float(m_dd_card.group(3)) * (
            -1 if m_dd_card.group(4).upper() == "W" else 1
        )
        return lat, lon

    # 4. Padrão numérico simples: 37.015, -7.935
    m_num = re.search(
        r"([+-]?\d+(?:\.\d+)?)\s*[\s,;]\s*([+-]?\d+(?:\.\d+)?)", cleaned
    )
    if m_num:
        lat = float(m_num.group(1))
        lon = float(m_num.group(2))
        if -90.0 <= lat <= 90.0 and -180.0 <= lon <= 180.0:
            return lat, lon

    return None


PRESET_LOCATIONS = {
    "Personalizado": None,
    "⚓ Ria Formosa (Estação Costeira / Faro)": (36.9850, -7.9250),
    "🌊 Costa do Algarve (Plataforma Continental Sul)": (36.8500, -8.1500),
    "🏄 Canhão da Nazaré (Bóia Oceanográfica)": (39.5500, -9.2000),
    "🐋 Banco de Gorringe (Monte Submarino de Gettysburg)": (36.5000, -11.5500),
    "🏝️ Canal Faial-Pico (Açores - Observatório Pelágico)": (38.5200, -28.5800),
    "🐬 Cabo Girão (Madeira - Estação Pelágica Sul)": (32.6200, -17.0100),
    "🚢 Foz do Tejo / Estuário de Lisboa": (38.6800, -9.3200),
}


def get_cmems_box(lat: float, lon: float, buffer_deg: float = 0.1):
    """Calcula Bounding Box com buffer e gera snippets para Copernicus Marine."""
    min_lat = round(max(-90.0, lat - buffer_deg), 4)
    max_lat = round(min(90.0, lat + buffer_deg), 4)
    min_lon = round(max(-180.0, lon - buffer_deg), 4)
    max_lon = round(min(180.0, lon + buffer_deg), 4)

    cli_cmd = (
        f"copernicusmarine subset -i <DATASET_ID> \\\n"
        f"  --minimum-longitude {min_lon:.4f} \\\n"
        f"  --maximum-longitude {max_lon:.4f} \\\n"
        f"  --minimum-latitude {min_lat:.4f} \\\n"
        f"  --maximum-latitude {max_lat:.4f}"
    )

    python_snippet = f"""import copernicusmarine

# Descarregar dados Copernicus Marine para esta estação / vizinhança
ds = copernicusmarine.subset(
    dataset_id="cmems_mod_glo_phy-cur_anfc_0.083deg_P1D-m",
    variables=["uo", "vo", "thetao", "so"],
    minimum_longitude={min_lon:.4f},
    maximum_longitude={max_lon:.4f},
    minimum_latitude={min_lat:.4f},
    maximum_latitude={max_lat:.4f},
    output_directory="./dados_cmems"
)"""

    return {
        "min_lat": min_lat,
        "max_lat": max_lat,
        "min_lon": min_lon,
        "max_lon": max_lon,
        "cli_cmd": cli_cmd,
        "python_snippet": python_snippet,
    }
