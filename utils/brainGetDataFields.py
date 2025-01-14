"""
WorldQuant Brain 数据字段获取工具
"""
import pandas as pd
from urllib.parse import urlencode

def get_datafields(session, search_scope, dataset_id='', search='', field_type=None):
    """
    获取数据字段，支持类型过滤
    
    Args:
        session: Brain会话对象
        search_scope: 搜索范围配置
        dataset_id: 数据集ID
        search: 搜索关键词
        field_type: 字段类型过滤(如'MATRIX')
        
    Returns:
        pd.DataFrame: 数据字段DataFrame
    """
    # 构建参数字典
    params = {
        'instrumentType': search_scope['instrumentType'],
        'region': search_scope['region'],
        'delay': str(search_scope['delay']),
        'universe': search_scope['universe'],
        'limit': 50
    }
    
    # 添加可选参数
    if dataset_id:
        params['dataset.id'] = dataset_id
    if search:
        params['search'] = search
        
    # 构建基础URL
    base_url = "https://api.worldquantbrain.com/data-fields"
    
    # 获取总数
    first_url = f"{base_url}?{urlencode(params)}&offset=0"
    response = session.get(first_url)
    if response.status_code != 200:
        raise Exception(f"API请求失败: {response.json()}")
        
    count = response.json()['count']
    
    # 收集数据
    datafields_list = []
    for x in range(0, count, 50):
        url = f"{base_url}?{urlencode(params)}&offset={x}"
        response = session.get(url)
        datafields_list.extend(response.json()['results'])
    
    # 转换为DataFrame
    df = pd.DataFrame(datafields_list)
    
    # 类型过滤
    if field_type and not df.empty:
        df = df[df['type'] == field_type]
    
    return df