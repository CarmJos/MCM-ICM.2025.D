import math
from collections import defaultdict
from typing import List, Union, Dict, Callable

import pandas as pd
from tqdm import tqdm

from _references import TRAFFIC_DATA_FILE


class TrafficData:
    def __init__(self, data_row: pd.Series):
        """使用DataFrame的单个行数据初始化"""
        self._data = data_row

    # 基础属性
    @property
    def global_id(self) -> str:
        return self._data['GlobalID']

    @property
    def gis_object_id(self) -> int:
        return int(self._data['GIS Object ID'])

    # 节点信息
    @property
    def node_start(self) -> List[int]:
        return self._parse_nodes(self._data['node start'])

    @property
    def nodes_end(self) -> List[int]:
        return self._parse_nodes(self._data['node(s) end'])

    # 动态年份数据处理
    def _get_year_data(self, prefix: str, year: Union[int, str]) -> float:
        """通用年份数据获取方法"""
        if isinstance(year, int) and 2014 <= year <= 2022:
            col_name = f"{prefix} {year}"
        elif year == 'current':
            col_name = f"{prefix} (Current)"
        else:
            raise ValueError("Invalid year parameter")

        return float(self._data.get(col_name, 0.0))

    def aadt(self, year: Union[int, str] = 'current') -> float:
        """获取格式化AADT数据"""
        return self._get_year_data('AADT', year)

    def aawdt(self, year: Union[int, str] = 'current') -> float:
        """获取格式化AAWDT数据"""
        return self._get_year_data('AAWDT', year)

    @property
    def get_related_nodes(self) -> List[int]:
        """获取与当前记录相关的所有节点ID（自动类型转换）"""
        return [
            node_id
            for node_id in self.node_start + self.nodes_end
        ]

    # 私有方法
    def _parse_nodes(self, node_str: str) -> List[int]:
        """解析节点字符串为整数列表"""
        return [
            int(n.strip())
            for n in node_str.strip('{}').split(',')
            if n.strip().isdigit()
        ]


def _load_traffic_data() -> pd.DataFrame:
    """加载并预处理数据"""
    df = pd.read_csv(TRAFFIC_DATA_FILE, index_col='GlobalID', low_memory=False)
    df['node start'] = df['node start'].fillna('{}')
    df['node(s) end'] = df['node(s) end'].fillna('{}')
    return df


class TrafficSet:
    def __init__(self):
        self.data = _load_traffic_data()
        self._data = [TrafficData(row) for _, row in
                      tqdm(self.data.iterrows(), total=self.data.shape[0], desc="|TRAFFIC")]

    @property
    def records(self) -> List[TrafficData]:
        """获取所有记录"""
        return self._data

    def get_by_station(self, station_id: str) -> Union[TrafficData, None]:
        """按站点ID查询"""
        matches = self.data[self.data['Station ID'] == station_id]
        if not matches.empty:
            return TrafficData(matches.iloc[0])
        return None

    def build_node_traffic_dict(
            self, traffic_extractor: Callable[[TrafficData], float]
    ) -> Dict[int, float]:
        """
        构建节点流量对照字典
        :param traffic_extractor: 流量数据提取函数
        :return: {node_id: aggregated_traffic}
        """
        # 初始化临时存储结构
        node_traffic = defaultdict(list)

        # 遍历所有数据记录
        for record in tqdm(self.records, desc="EXTRACTING TRAFFICS"):
            # 获取当前记录的流量值
            traffic_value = traffic_extractor(record)
            if not traffic_value:
                continue

            # 获取相关节点并分配流量
            for node_id in record.get_related_nodes:
                node_traffic[node_id].append(traffic_value)

        # 应用合并策略（求和） 排除无效流量
        return {
            node_id: sum(traffic_values)
            for node_id, traffic_values in node_traffic.items()
            if any(traffic_values)
        }
