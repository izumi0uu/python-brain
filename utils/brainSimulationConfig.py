"""
WorldQuant Brain simulation 配置文件
"""

DEFAULT_SIMULATION_CONFIG = {
    'type': 'REGULAR',
    'settings': {
        'instrumentType': 'EQUITY',
        'region': 'USA',
        'universe': 'TOP3000',
        'delay': 1,
        'decay': 0,
        'neutralization': 'SUBINDUSTRY',
        'truncation': 0.01,
        'pasteurization': 'ON',
        'unitHandling': 'VERIFY',
        'nanHandling': 'ON',
        'language': 'FASTEXPR',
        'visualization': False,
    }
}

def get_simulation_data(datafield, config=None):
    """
    获取模拟配置数据
    
    Args:
        datafield: 数据字段
        config: 自定义配置(可选)，会覆盖默认配置
        
    Returns:
        dict: 完整的模拟配置
    """
    simulation_data = DEFAULT_SIMULATION_CONFIG.copy()
    
    if config:
        simulation_data['settings'].update(config)
    
    simulation_data['regular'] = datafield
    return simulation_data