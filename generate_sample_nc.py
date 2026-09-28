"""
Script utilitário para gerar um ficheiro NetCDF (.nc) de exemplo para a aula.
Gera dados oceanográficos sintéticos 4D (tempo, profundidade, latitude, longitude)
para a costa de Portugal/Algarve com Temperatura, Salinidade e Clorofila-a.
"""

import numpy as np
import pandas as pd
import xarray as xr


def generate_sample_dataset():
    # Coordenadas
    times = pd.date_range("2024-01-01", periods=12, freq="1MS")
    depths = np.array([0.0, 5.0, 10.0, 20.0, 50.0, 100.0])  # metros
    lats = np.linspace(36.0, 37.5, 16)  # Costa Sul de Portugal / Algarve
    lons = np.linspace(-9.0, -7.0, 21)

    shape = (len(times), len(depths), len(lats), len(lons))

    # Grelhas de coordenadas
    t_idx = np.arange(len(times))[:, None, None, None]
    z_idx = depths[None, :, None, None]
    lat_grid = lats[None, None, :, None]
    lon_grid = lons[None, None, None, :]

    # Temperatura potencial (thetao, ºC): diminui com a profundidade, ciclo sazonal
    sst_seasonal = 15.0 + 5.0 * np.sin((t_idx - 3) * np.pi / 6)
    temp = sst_seasonal - (z_idx / 100.0) * 4.0 + 0.3 * np.random.randn(*shape)

    # Salinidade (so, PSU): ~36.0 PSU
    salinity = (
        36.2
        + 0.2 * (lat_grid - 36.0)
        + 0.1 * (z_idx / 100.0)
        + 0.05 * np.random.randn(*shape)
    )

    # Clorofila-a (chl, mg/m3): pico na primavera e à superfície
    chl = (
        (0.8 + 0.7 * np.exp(-((t_idx - 4) ** 2) / 2))
        * np.exp(-z_idx / 30.0)
        * (1.0 + 0.1 * np.random.randn(*shape))
    )
    chl = np.clip(chl, 0.05, 5.0)

    # Máscara de "terra" simplificada (norte/este do Algarve)
    land_mask = (lat_grid > 37.1) & (lon_grid > -8.0)
    temp = np.where(land_mask, np.nan, temp)
    salinity = np.where(land_mask, np.nan, salinity)
    chl = np.where(land_mask, np.nan, chl)

    ds = xr.Dataset(
        data_vars={
            "thetao": (
                ["time", "depth", "latitude", "longitude"],
                temp.astype(np.float32),
                {
                    "standard_name": "sea_water_potential_temperature",
                    "long_name": "Temperatura da Água do Mar",
                    "units": "degrees_C",
                },
            ),
            "so": (
                ["time", "depth", "latitude", "longitude"],
                salinity.astype(np.float32),
                {
                    "standard_name": "sea_water_salinity",
                    "long_name": "Salinidade Prática",
                    "units": "PSU",
                },
            ),
            "chl": (
                ["time", "depth", "latitude", "longitude"],
                chl.astype(np.float32),
                {
                    "standard_name": "mass_concentration_of_chlorophyll_a_in_sea_water",
                    "long_name": "Concentração de Clorofila-a",
                    "units": "mg m-3",
                },
            ),
        },
        coords={
            "time": ("time", times),
            "depth": (
                "depth",
                depths,
                {"long_name": "Profundidade", "units": "m", "positive": "down"},
            ),
            "latitude": (
                "latitude",
                lats,
                {"long_name": "Latitude", "units": "degrees_north"},
            ),
            "longitude": (
                "longitude",
                lons,
                {"long_name": "Longitude", "units": "degrees_east"},
            ),
        },
        attrs={
            "title": "Dados Oceanográficos Sintéticos - Algarve / Costa Sul PT",
            "institution": "Aula Teórico-Prática de Oceanografia Física",
            "source": "Modelo Didático Sintético",
        },
    )
    return ds


if __name__ == "__main__":
    ds = generate_sample_dataset()
    output_path = "exemplo_oceanografia_algarve.nc"
    ds.to_netcdf(output_path)
    print(f"Ficheiro de exemplo gerado com sucesso: {output_path}")
    print(ds)
