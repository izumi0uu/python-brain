"""
WorldQuant Brain simulation 管理工具
"""
from time import sleep
import logging
from datetime import datetime
from typing import List, Dict, Optional
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed
from threading import Lock

from .brainLogin import get_session
from .brainSimulationConfig import get_simulation_data
from .brainSimulationRecord import db, save_simulation_record

# 配置logging
logging.basicConfig(
    filename='simulation.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

class SimulationManager:
    def __init__(self, max_workers=3, max_retries=6, retry_delay=10):
        """
        初始化模拟管理器
        
        Args:
            max_workers: 最大并发数
            max_retries: 单个alpha最大重试次数
            retry_delay: 重试等待时间(秒)
        """
        self.max_workers = max_workers
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self.session_lock = Lock()
        self.session = get_session()
        
    def _get_new_session(self):
        """获取新的会话（线程安全）"""
        with self.session_lock:
            self.session = get_session()
            return self.session
            
    def simulate_single_alpha(self, alpha: Dict) -> bool:
        """
        模拟单个Alpha
        
        Args:
            alpha: Alpha配置
            
        Returns:
            bool: 是否成功
        """
        retries = 0
        while retries < self.max_retries:
            try:
                # 发送模拟请求
                sim_resp = self.session.post(
                    'https://api.worldquantbrain.com/simulations',
                    json=alpha
                )
                
                if sim_resp.status_code != 201:
                    raise Exception(f"Simulation failed with status {sim_resp.status_code}")
                    
                # 获取位置信息
                sim_id = sim_resp.headers.get('Location', '').split('/')[-1]
                
                # 记录成功
                save_simulation_record(
                    alpha_id=sim_id,
                    datafield=alpha['regular'],
                    status='success'
                )
                
                logging.info(f"Simulation success - Alpha: {alpha['regular']}")
                return True
                
            except Exception as e:
                retries += 1
                error_msg = f"Attempt {retries} failed - {str(e)}"
                logging.error(error_msg)
                
                if retries >= self.max_retries:
                    # 记录失败
                    save_simulation_record(
                        alpha_id=None,
                        datafield=alpha['regular'],
                        status='failed',
                        extra_info={'error': str(e), 'attempts': retries}
                    )
                    return False
                    
                # 如果是认证错误，重新获取session
                if "401" in str(e) or "403" in str(e):
                    self.session = self._get_new_session()
                    
                sleep(self.retry_delay)
                
        return False
        
    def run_batch_simulation(self, alpha_list: List[Dict], batch_size: int = 1000):
        """
        批量运行Alpha模拟
        
        Args:
            alpha_list: Alpha配置列表
            batch_size: 每批处理的数量
        """
        total = len(alpha_list)
        processed = 0
        
        # 分批处理
        for i in range(0, total, batch_size):
            batch = alpha_list[i:i + batch_size]
            success_count = 0
            
            # 使用线程池并发处理
            with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
                future_to_alpha = {
                    executor.submit(self.simulate_single_alpha, alpha): alpha 
                    for alpha in batch
                }
                
                for future in as_completed(future_to_alpha):
                    alpha = future_to_alpha[future]
                    try:
                        if future.result():
                            success_count += 1
                    except Exception as e:
                        logging.error(f"Unexpected error for alpha {alpha['regular']}: {str(e)}")
            
            processed += len(batch)
            
            # 打印进度
            progress = (processed / total) * 100
            logging.info(f"Processed {processed}/{total} ({progress:.2f}%) - "
                       f"Batch success rate: {(success_count/len(batch))*100:.2f}%")
            
            # 每批处理完后短暂休息
            sleep(5)

def run_alpha_simulation(alpha_list: List[Dict], batch_id: Optional[str] = None):
    """
    运行Alpha模拟的主函数
    
    Args:
        alpha_list: Alpha配置列表
        batch_id: 批次ID
    """
    # 添加批次信息
    if batch_id is None:
        batch_id = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    # 对于pending状态的alpha，更新它们的batch_id
    regulars = [alpha['regular'] for alpha in alpha_list]
    db.alphas.update_many(
        {
            'regular': {'$in': regulars},
            'status': 'pending'
        },
        {
            '$set': {
                'batch_id': batch_id,
                'updated_at': datetime.now()
            }
        }
    )
    
    # # 将新的alpha添加到数据库
    # inserted = db.add_batch(alpha_list, batch_id)
    # logging.info(f"Added {inserted} alphas to batch {batch_id}")
    
    # 创建模拟管理器并运行
    manager = SimulationManager(max_workers=5)
    manager.run_batch_simulation(alpha_list)
    
    # 打印最终统计信息
    stats = db.get_statistics(batch_id)
    logging.info(f"Batch {batch_id} completed:")
    logging.info(f"Total: {stats['total']}")
    logging.info(f"Success: {stats['success']}")
    logging.info(f"Failed: {stats['failed']}")
    logging.info(f"Pending: {stats['pending']}")

def rerun_alphas(status: str = 'pending'):
    """
    重新运行指定状态的Alpha
    
    Args:
        status: 要处理的Alpha状态 ('pending' 或 'failed')
    """
    # 如果是pending状态，先清理旧的batch_id
    if status == 'pending':
        db.clean_pending_batches()
    
    # 获取需要重跑的alpha
    alphas = db.get_alphas_by_status(status)
    if not alphas:
        print(f"No {status} alphas found")
        return
        
    # 生成新的batch_id
    batch_id = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    # 准备alpha配置
    alpha_list = []
    for alpha in alphas:
        alpha_list.append({
            'type': alpha['type'],
            'settings': alpha['settings'],
            'regular': alpha['regular']
        })
    
    # 使用原有的run_alpha_simulation函数
    run_alpha_simulation(alpha_list, batch_id)

__all__ = ['run_alpha_simulation', 'rerun_alphas']