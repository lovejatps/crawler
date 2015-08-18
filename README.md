# crawler
该项目完成对喜马拉雅内容的获取
项目用python编码
python 安装：
 sudo apt-get install Python-bs4
 sudo apt-get install Python-lxml
#使用插件
1、BeautifulSoup   官网：https://pypi.python.org/pypi/beautifulsoup4/4.3.2  最新的版本提4.3.2

  安装方法：
  1、下载安装包，
  2、解压安装包，运行：sudo python setup.py install

2、MongoDB
.安装Python依赖包
按照官方的说法，推荐使用pip来安装MongoDb的Python驱动，但是pip首先依赖于setuptools，所以你得先检查有没有安装它，
如果没有，可以下载安装setuptools或者：
$apt-get install python-setuptools
注意：如果你使用的是python3.0或以上版本，请使用对应版本的setuptools。
另外，在安装pip的过程中，你可能需要顺带安装python-dev：
$apt-get install python-dev
2.安装pip
首先下载：
$wget http://pypi.python.org/packages/source/p/pip/pip-1.0.2.tar.gz#md5=47ec6ff3f6d962696fe08d4c8264ad49
然后解压：
$tar -xvf pip-1.0.2.tar.gz
然后安装：
$cd pip-1.0.2
$python setup.py install
安装好pip之后，就可以用命令来安装pymongo了：
3.安装Python for Mongo的驱动
很简单：
$pip install pymongo
注意，以后可以直接通过pip来更新pymongo，命令是
$pip --upgrade pymongo

3、安装ES
    pip install elasticsearch    另外还有一种：  pip install pyes
