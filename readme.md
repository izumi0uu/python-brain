## WORLDQUANT BRAIN FACTOR PROJECT RUN IN THE SERVER

### UTILS

- brainSaveSimulationRecord.py: 保存模拟记录到 mongo 数据库
- brainGetDataFields.py: 获取数据字段
- brainSimulationConfig.py: 获取模拟数据
- brainLogin.py: 登录
- brainDatafieldsSearchScopeConfig.py: 数据字段搜索范围配置
- brainSimulation.py: 模拟操作

### CONFIG INFO

system Alibaba Cloud Linux 3.2104 LTS 64 位

### INSTALL PYTHON ENVIRONMENT

更新包管理器
sudo yum update # CentOS

安装 Python 和 pip
sudo yum install python3 python3-pip # CentOS

安装虚拟环境
python3 -m pip install virtualenv

### INSTALL MONGODB

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

#### check and create necessary directories and permissions

确认当前目录内容
ls -l

使用正确的目录名移动
sudo mv mongodb-linux-x86_64-rhel88-8.0.4 /usr/local/mongodb

验证移动是否成功
ls -l /usr/local/mongodb

添加到环境变量
echo 'export PATH=/usr/local/mongodb/bin:$PATH' >> ~/.bashrc
source ~/.bashrc

创建 mongod 用户和用户组（如果不存在）
sudo groupadd mongod
sudo useradd -r -g mongod -s /sbin/nologin mongod

创建必要的目录
sudo mkdir -p /data/db
sudo mkdir -p /var/log/mongodb
sudo mkdir -p /var/run/mongodb

设置正确的权限
sudo chown -R mongod:mongod /data/db
sudo chown -R mongod:mongod /var/log/mongodb
sudo chown -R mongod:mongod /var/run/mongodb
sudo chmod 755 /data/db /var/log/mongodb /var/run/mongodb

恢复数据
mongorestore /data/dump

#### create config file

创建配置文件目录
sudo mkdir -p /etc/mongodb

创建配置文件
sudo vi /etc/mongodb/mongod.conf

添加以下内容
systemLog:
destination: file
path: /var/log/mongodb/mongod.log
logAppend: true
storage:
dbPath: /data/db
net:
bindIp: 127.0.0.1,::1
port: 27017
processManagement:
fork: true
pidFilePath: /var/run/mongodb/mongod.pid

### CREATE PROJECT DIRECTORY

mkdir /home/project/python
cd /home/project/python

创建并激活虚拟环境
python3 -m virtualenv venv
source venv/bin/activate

sudo mongod --dbpath /data/db

#### create systemd service file

创建服务文件
sudo vi /etc/systemd/system/mongod.service

添加以下内容
[Unit]
Description=MongoDB Database Server
Documentation=https://docs.mongodb.org/manual
After=network.target

[Service]
User=mongod
Group=mongod
Environment="OPTIONS=-f /etc/mongodb/mongod.conf"
ExecStart=/usr/local/mongodb/bin/mongod $OPTIONS
ExecStartPre=/usr/bin/mkdir -p /var/run/mongodb
ExecStartPre=/usr/bin/chown mongod:mongod /var/run/mongodb
ExecStartPre=/usr/bin/chmod 0755 /var/run/mongodb
PermissionsStartOnly=true
PIDFile=/var/run/mongodb/mongod.pid
Type=forking
\# file size
LimitFSIZE=infinity
\# cpu time
LimitCPU=infinity
\# virtual memory size
LimitAS=infinity
\# open files
LimitNOFILE=64000
\# processes/threads
LimitNPROC=64000
\# locked memory
LimitMEMLOCK=infinity
\# total threads (user+kernel)
TasksMax=infinity
TasksAccounting=false
\# Recommended limits for mongod as specified in
\# https://docs.mongodb.com/manual/reference/ulimit/#recommended-ulimit-settings

[Install]
WantedBy=multi-user.target

#### start service

重新加载 systemd
sudo systemctl daemon-reload

启动 MongoDB
sudo systemctl start mongod

检查状态
sudo systemctl status mongod

设置开机自启
sudo systemctl enable mongod

### INSTALL PROJECT DEPENDENCY

创建 requirements.txt
pip freeze > requirements.txt

安装依赖
pip install -r requirements.txt

MongoDB 驱动
pip install pymongo

### INSTALL JUPYTER NOTEBOOK

安装虚拟环境工具
pip3.8 install virtualenv

创建新的虚拟环境
python3.8 -m venv jupyter_env

激活虚拟环境
source jupyter_env/bin/activate

升级 pip
pip install --upgrade pip

安装必要的依赖
pip install wheel
pip install setuptools --upgrade

安装 Jupyter
pip install jupyter

启动 Jupyter Notebook
jupyter notebook --ip=0.0.0.0 --port=8888 --allow-root --no-browser (服务器安全组需要开放 8888 端口)

浏览器访问
http://服务器主网 ip:8888

检查进程
ps aux | grep jupyter

检查端口
netstat -tulpn | grep 8888

查看日志
cat -f jupyter.log

### INSTALL OTHER PACKAGE

pandas
numpy
requests
tqdm

### PERSONAL CONFIG

/opt/Python-3.8.12/ # 这是实际的 Python 3.8.12 安装
└── bin/
└── python3.8 # 主要的 Python 解释器

/home/project/python/venv/ # 这不是新的 Python 安装，而是一个虚拟环境
└── bin/
└── python -> /opt/Python-3.8.12/bin/python3.8 # 链接到主 Python

/opt/Python-3.8.12 提供基础 Python 解释器
/home/project/python/venv 是一个独立的虚拟环境，但使用的是 opt 下的 Python
虚拟环境有自己独立的包管理，不会影响或使用 opt 下安装的包
