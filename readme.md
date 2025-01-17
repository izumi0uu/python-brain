### worldquant brain factor project

### utils

- brainSaveSimulationRecord.py: 保存模拟记录到 mongo 数据库
- brainGetDataFields.py: 获取数据字段
- brainSimulationConfig.py: 获取模拟数据
- brainLogin.py: 登录
- brainDatafieldsSearchScopeConfig.py: 数据字段搜索范围配置
- brainSimulation.py: 模拟操作

### run in the server

#### CONFIG INFO system Alibaba Cloud Linux 3.2104 LTS 64 位

#### PYTHON environment install

更新包管理器
sudo yum update # CentOS

安装 Python 和 pip
sudo yum install python3 python3-pip # CentOS

安装虚拟环境
python3 -m pip install virtualenv

#### MongoDB install

CentOS
创建配置文件
sudo vi /etc/yum.repos.d/mongodb-org.repo
添加以下内容：
[mongodb-org-6.0]
name=MongoDB Repository
baseurl=https://repo.mongodb.org/yum/redhat/9/mongodb-org/6.0/x86_64/
gpgcheck=1
enabled=1
gpgkey=https://pgp.mongodb.com/server-6.0.asc

sudo yum install -y mongodb-org

### create project directory

mkdir /home/project/python
cd /home/project/python

创建并激活虚拟环境
python3 -m virtualenv venv
source venv/bin/activate

sudo mongod --dbpath /data/db

### install projetc independcy

创建 requirements.txt
pip freeze > requirements.txt

安装依赖
pip install -r requirements.txt

MongoDB 驱动
pip install pymongo
