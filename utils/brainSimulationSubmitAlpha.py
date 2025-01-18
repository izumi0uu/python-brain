def submit_alpha(alpha_id, session=None):
    """
    提交 Alpha 到 WorldQuant Brain
    
    Args:
        alpha_id (str): Alpha 的 ID，例如 'o6mqEXn'
        session: 已登录的 session 对象
        
    Returns:
        dict: API 响应的 JSON 数据
    """
    # 如果没有提供 session，则自动获取
    if session is None:
        from utils.brainLogin import get_session
        session = get_session()
    
    url = f"https://api.worldquantbrain.com/alphas/{alpha_id}/submit"

    try:
        response = session.get(url)
        return response.json()
    except Exception as e:
        print(f"提交失败: {str(e)}")
        return None
