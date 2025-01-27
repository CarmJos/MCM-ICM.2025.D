# ------------------ Helper Functions ------------------
from typing import Optional, Callable, Union, List, Any, Dict

import pandas as pd
import geopandas as gpd
from pandas import DataFrame
from geopandas import GeoDataFrame
from tqdm import tqdm


def read_geo(
        file_path: str, index_columns: Union[str, List[str]] = None,
        value_filter: Callable[[pd.DataFrame], bool] = None,
        converter: Callable[[pd.DataFrame], Any] = None
) -> GeoDataFrame:
    index_columns = index_columns if isinstance(index_columns, list) else [index_columns]
    df = pd.read_csv(file_path, index_col=index_columns, low_memory=False)
    if value_filter is not None:
        df = df[value_filter(df)]
    return gpd.GeoDataFrame(df, geometry=converter(df))


def load(
        desc: str, df: DataFrame,
        converter: Callable[[pd.Series], Any]
) -> Dict[Any, Any]:
    table: Dict[Any, Any] = {}
    for idx, row in tqdm(df.iterrows(), total=df.shape[0], desc=desc):
        table[idx] = converter(row)
    return table


def safe_int(value) -> Optional[int]:
    try:
        return int(float(value)) if pd.notna(value) else None
    except ValueError:
        return None


def safe_float(value) -> Optional[float]:
    try:
        return float(value) if pd.notna(value) else None
    except ValueError:
        return None
