"""
WorldQuant Brain simulation 记录工具
使用MongoDB存储记录
"""
import logging
from datetime import datetime
from typing import Optional, Dict, List
from pymongo import MongoClient, ASCENDING
from pymongo.errors import DuplicateKeyError

# 配置logging
logging.basicConfig(
    filename='simulation.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

class SimulationDB:
    def __init__(self, db_url='mongodb://localhost:27017/'):
        """初始化数据库连接"""
        self.client = MongoClient(db_url)
        self.db = self.client['brain_simulation']
        self.alphas = self.db['alphas']
        self._init_db()
    
    def _init_db(self):
        """初始化数据库索引"""
        # 创建索引
        self.alphas.create_index([('regular', ASCENDING)], unique=True)
        self.alphas.create_index([('status', ASCENDING)])
        self.alphas.create_index([('batch_id', ASCENDING)])
        self.alphas.create_index([('created_at', ASCENDING)])
        
    def add_batch(self, alpha_list: List[Dict], batch_id: str) -> int:
        """批量添加Alpha任务"""
        now = datetime.now()
        documents = []
        
        for alpha in alpha_list:
            doc = {
                'type': alpha['type'],
                'settings': alpha['settings'],
                'regular': alpha['regular'],
                'status': 'pending',
                'attempt_count': 0,
                'batch_id': batch_id,
                'created_at': now,
                'updated_at': now
            }
            documents.append(doc)
            
        try:
            result = self.alphas.insert_many(documents, ordered=False)
            return len(result.inserted_ids)
        except Exception as e:
            logging.error(f"Batch insert error: {str(e)}")
            return 0
            
    def update_status(self, regular: str, status: str, 
                     alpha_id: Optional[str] = None,
                     error_message: Optional[str] = None):
        """更新Alpha状态"""
        update = {
            '$set': {
                'status': status,
                'updated_at': datetime.now()
            },
            '$inc': {'attempt_count': 1}
        }
        
        if alpha_id:
            update['$set']['alpha_id'] = alpha_id
        if error_message:
            update['$set']['error_message'] = error_message
            
        self.alphas.update_one(
            {'regular': regular},
            update
        )
        
    def get_pending_alphas(self, batch_size: int = 100) -> List[Dict]:
        """获取待处理的Alpha"""
        return list(self.alphas.find(
            {'status': 'pending'},
            sort=[('created_at', 1)],
            limit=batch_size
        ))
        
    def get_statistics(self, batch_id: Optional[str] = None) -> Dict:
        """获取统计信息"""
        match = {'batch_id': batch_id} if batch_id else {}
        
        pipeline = [
            {'$match': match},
            {
                '$group': {
                    '_id': '$status',
                    'count': {'$sum': 1}
                }
            }
        ]
        
        stats = {item['_id']: item['count'] 
                for item in self.alphas.aggregate(pipeline)}
        
        return {
            'total': sum(stats.values()),
            'pending': stats.get('pending', 0),
            'success': stats.get('success', 0),
            'failed': stats.get('failed', 0)
        }

# 创建全局数据库实例
db = SimulationDB()

def save_simulation_record(alpha_id: Optional[str], datafield: str, 
                         status: str, extra_info: Optional[Dict] = None):
    """记录模拟结果"""
    if status == 'success':
        logging.info(f"Simulation success - Alpha ID: {alpha_id}, Expression: {datafield}")
        db.update_status(datafield, 'success', alpha_id)
    else:
        error_msg = str(extra_info) if extra_info else 'Unknown error'
        logging.error(f"Simulation failed - Expression: {datafield}, Error: {error_msg}")
        db.update_status(datafield, 'failed', error_message=error_msg)

def check_progress(batch_id: Optional[str] = None):
    """检查处理进度"""
    stats = db.get_statistics(batch_id)
    print(f"Total tasks: {stats['total']}")
    print(f"Successful: {stats['success']}")
    print(f"Failed: {stats['failed']}")
    print(f"Pending: {stats['pending']}")
    
    if stats['total'] > 0:
        success_rate = (stats['success'] / stats['total']) * 100
        print(f"Success rate: {success_rate:.2f}%")