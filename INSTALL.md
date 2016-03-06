# 安装 Python #

=下载 python= [python ftp](http://www.python.org/ftp/python/)

## windows下安装 ##
从 http://www.python.org/ftp/python/ 选择最新的 Python Windows 安装程序，下载 .exe 安装文件。

双击安装程序 Python-x.x.x.exe。文件名依赖于您所下载的 Python 安装程序文件。

按照安装程序的提示信息一步步地执行。

在安装完成之后，关闭安装程序，打开 开始->程序->Python 2.6->IDLE (Python GUI)。您将看到类似如下的信息：
```
Python 2.6.5 (r254:67916, Dec 23 2008, 15:10:54) [MSC v.1310 32 bit (Intel)] on win32
Type "copyright", "credits" or "license()" for more information.

    ****************************************************************
    Personal firewall software may warn about the connection IDLE
    makes to its subprocess using this computer's internal loopback
    interface.  This connection is not visible on any external
    interface and no data is sent to or received from the Internet.
    ****************************************************************
    
IDLE 1.2.4   
```
<p />
## linux 下安装 ##
```
wget http://www.python.org/ftp/python/2.6/Python-2.6.5.tgz
tar xfz Python-2.6.5.tgz
cd python-2.6.5
./configure
make && make install
```

# 安装django #
从django 官方 下载最新的django 1.2.3.tar.gz [django](http://www.djangoproject.com/download/)<br />
然后 执行
```
tar xzvf Django-1.2.3.tar.gz
cd Django-1.2.3
sudo python setup.py install
```
django 也提供了Svn 地址
```
svn co http://code.djangoproject.com/svn/django/trunk/
```

# 安装youflog #
从svn 中检出 youflog
```
svn checkout http://youflog.googlecode.com/svn/trunk/ youflog-read-only
```
切换到youflog目录下面建立youflog需要的数据库表<p />
执行 python manage.py syncdb<p />

完成上一步之后 就可以执行 python manage.py runserver 启动了<p />

youflog博客系统默认使用的是sqlite数据库如果想更换成mysql或其它的数据库<br />
请编辑settings.py中的这些项<br />
```
DATABASE_ENGINE = 'mysql'  # 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
DATABASE_NAME = 'youflog'         # Or path to database file if using sqlite3.
DATABASE_USER = 'root'             # Not used with sqlite3.
DATABASE_PASSWORD = 'root'         # Not used with sqlite3.
DATABASE_HOST = '127.0.0.1'     # Set to empty string for localhost. Not used with sqlite3.
DATABASE_PORT = '3306' 
```