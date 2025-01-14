"""
WorldQuant Brain 数据字段搜索范围配置
    - instrumentType: 工具类型
    - region: 地区
    - delay: 延迟
    - universe: 股票池
"""

DEFAULT_SEARCH_SCOPE = {
    'region': 'USA',
    'delay': 1,
    'universe': 'TOP3000',
    'instrumentType': 'EQUITY'
}

def get_search_scope(config=None):
    """
    获取搜索范围配置
    
    Args:
        config: 自定义配置(可选)，会覆盖默认配置
        
    Returns:
        dict: 完整的搜索范围配置
    """
    search_scope = DEFAULT_SEARCH_SCOPE.copy()
    
    if config:
        search_scope.update(config)
    
    return search_scope