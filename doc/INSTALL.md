# 安装手册

安装演示所使用的操作系统为 Ubuntu 16.04

## 获取项目源码

```bash
git clone git@github.com:jeffzh3ng/InsectsAwake.git
```

## 安装 Python 及 pip

```bash
sudo apt update
sudo apt install python python-pip
```

## 安装 MongoDB

```bash
sudo apt-key adv --keyserver hkp://keyserver.ubuntu.com:80 --recv 2930ADAE8CAF5059EE73BB4B58712A2291FA4AD5
echo "deb [ arch=amd64,arm64,ppc64el,s390x ] http://repo.mongodb.com/apt/ubuntu xenial/mongodb-enterprise/3.6 multiverse" | sudo tee /etc/apt/sources.list.d/mongodb-enterprise.listecho "deb http://repo.mongodb.com/apt/ubuntu "$(lsb_release -sc)"/mongodb-enterprise/3.4 multiverse" | sudo tee /etc/apt/sources.list.d/mongodb-enterprise-3.4.list
echo "deb http://repo.mongodb.com/apt/ubuntu "$(lsb_release -sc)"/mongodb-enterprise/3.4 multiverse" | sudo tee /etc/apt/sources.list.d/mongodb-enterprise-3.4.list
sudo apt-get update
sudo apt-get install -y mongodb-enterprise
```

其他系统安装参考官方手册：

[https://docs.mongodb.com/manual/installation/](https://docs.mongodb.com/manual/installation/)

## 安装 Python 依赖包

```bash
cd InsectsAwake
sudo pip install pip -U
sudo pip install -r requirements.txt
```

## 安装 Nmap

```bash
sudo apt install nmap
```

或者[源码安装](https://github.com/nmap/nmap)

## 配置数据库

启动数据库

```bash
sudo service mongod start
mongo --host 127.0.0.1:27017
```

添加用户

```
use InsectsAwake
db.createUser({user:'you username',pwd:'you password',roles:[{role:'dbOwner',db:'InsectsAwake'}]})
exit
```

## 修改扫描器配置

扫描器配置文件路径：
InsectsAwake-Project/instance/config.py

```
class Config():
    WEB_USER = 'admin'          // 扫描器登录用户
    WEB_PASSWORD = 'whoami'     // 扫描器登录密码
    WEB_HOST = '127.0.0.1'      // 本地访问
    WEB_PORT = 5000             // Web服务端口
    POCSUITE_PATH = basedir + '/../InsectsAwake/views/modules/scanner/pocsuite_plugin/'
    
class ProductionConfig(Config):
    DB_HOST = '127.0.0.1'       // 数据库地址
    DB_PORT = 27017             // 数据库端口
    DB_USERNAME = 'testuser'    // 数据库用户
    DB_PASSWORD = 'testpwd'     // 数据库密码
    DB_NAME = 'test'            // 数据库名
    
    // 数据库集合名
    PLUGIN_DB = 'test_plugin_info'
    TASKS_DB = 'test_tasks'
    VULNERABILITY_DB = 'test_vuldb'
    ASSET_DB = 'test_asset'
    CONFIG_DB = 'test_config'
    SERVER_DB = 'test_server'
    SUBDOMAIN_DB = 'test_subdomain'
    DOMAIN_DB = 'test_domain'
    WEEKPASSWD_DB = 'test_weekpasswd'
```

## 初始化数据库

```bash
cd /InsectsAwake/migration
python start.py
```

## 运行系统

完成依赖安装、数据库配置及修改扫描器配置后

```bash
sudo ./run.sh restart
```

项目默认运行在127.0.0.1:5000 （可以 修改 默认的 WEB_HOST 及 WEB_PORT），无法外网访问，建议配置 Nginx 或者 Caddy 等Web服务代理访问，这里简单介绍下 Caddy 使用

## Caddy 配置

Caddy 是一个能自动创建 HTTPS 功能的 HTTP/2 网站服务器

### 安装

Linux 64-bit 一键安装脚本：

```bash
curl https://getcaddy.com | bash -s personal
```

其他版本操作系统安装参考[Caddy 官网](https://caddyserver.com/download)

安装 Golang 的通过 go get 获取

```bash
go get github.com/mholt/caddy/caddy
```

### 配置

创建配置文件
```bash
sudo mkdir /etc/caddy
sudo touch /etc/caddy/caddy.config
sudo chown -R root:www-data /etc/caddy
sudo vi /etc/caddy/caddy.config
```

配置文件示例：
```config
www.example.com {
    log /var/log/caddy_insectsawake.log
    proxy / 127.0.0.1:5000 {
        transparent 
    }
}
```

修改 <www.example.com> 为你的域名，127.0.0.1:5000 为你配置的服务端口

创建 SSL 证书路径
```bash
sudo mkdir /etc/ssl/caddy
sudo chown -R www-data:root /etc/ssl/caddy
sudo chmod 0770 /etc/ssl/caddy
```

### 运行

测试

```bash
sudo caddy -conf /etc/caddy/caddy.config
```

后台运行

```bash
sudo nohup caddy -conf /etc/caddy/caddy.config > /var/log/caddy_log.log &
```
