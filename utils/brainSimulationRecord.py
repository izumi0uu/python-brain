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

    def clean_pending_batches(self):
        """清理所有pending状态alpha的batch_id"""
        result = self.alphas.update_many(
            {'status': 'pending'},
            {
                '$set': {
                    'batch_id': None,
                    'attempt_count': 0,
                    'updated_at': datetime.now()
                }
            }
        )
        logging.info(f"Cleaned batch_id for {result.modified_count} pending alphas")
        return result.modified_count
        
    def get_alphas_by_status(self, status: str = 'pending') -> List[Dict]:
        """获取指定状态的Alpha"""
        return list(self.alphas.find(
            {
                'status': status,
                'batch_id': None  # 只获取未分配批次的
            },
            sort=[('created_at', 1)]
        ))
        
    def get_statistics(self, batch_id: Optional[str] = None) -> Dict:
        """获取统计信息"""
        match = {'batch_id': batch_id} if batch_id else {}
        
        pipeline = [
            {'$match': match},
            {
                '$group': {
                    '_id': {
                        'batch': '$batch_id',
                        'status': '$status'
                    },
                    'count': {'$sum': 1}
                }
            },
            {
                '$group': {
                    '_id': '$_id.batch',
                    'details': {
                        '$push': {
                            'status': '$_id.status',
                            'count': '$count'
                        }
                    }
                }
            }
        ]
        
        results = list(self.alphas.aggregate(pipeline))
        
        if batch_id:
            # 单个批次的统计
            batch_stats = next((r for r in results if r['_id'] == batch_id), None)
            if not batch_stats:
                return {'total': 0, 'pending': 0, 'success': 0, 'failed': 0}
                
            stats = {'total': 0, 'pending': 0, 'success': 0, 'failed': 0}
            for detail in batch_stats['details']:
                status = detail['status'] or 'pending'  # 处理 None 值
                count = detail['count']
                stats[status] = count
                stats['total'] += count
            return stats
        else:
            # 所有批次的统计
            all_stats = {}
            for batch in results:
                batch_id = batch['_id']
                stats = {'total': 0, 'pending': 0, 'success': 0, 'failed': 0}
                for detail in batch['details']:
                    status = detail['status'] or 'pending'
                    count = detail['count']
                    stats[status] = count
                    stats['total'] += count
                all_stats[batch_id] = stats
            return all_stats

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

    if batch_id:
        # 单个批次的统计
        print(f"\n批次 {batch_id} 的统计信息:")
        print(f"总任务数: {stats['total']}")
        print(f"已成功: {stats['success']}")
        print(f"已失败: {stats['failed']}")
        print(f"待处理: {stats['pending']}")
        
        if stats['total'] > 0:
            success_rate = (stats['success'] / stats['total']) * 100
            print(f"成功率: {success_rate:.2f}%")
    else:
        # 所有批次的统计
        print("\n所有批次的统计信息:")
        for batch_id, batch_stats in stats.items():
            print(f"\n批次 {batch_id}:")
            print(f"总任务数: {batch_stats['total']}")
            print(f"已成功: {batch_stats['success']}")
            print(f"已失败: {batch_stats['failed']}")
            print(f"待处理: {batch_stats['pending']}")
            
            if batch_stats['total'] > 0:
                success_rate = (batch_stats['success'] / batch_stats['total']) * 100
                print(f"成功率: {success_rate:.2f}%")