python_crawler_booksearch
=========================

search various categories of books' information in amazon 

说明：
    本系统用于爬取亚马逊网站，不同类别下前50名的书本信息，将获取的信息按照一定的格式存到EXCEL中

安装：
	1、安装python2.7版本（2.6版本请安装支持OrderedDict包）
	
	2、配置python运行的环境变量
	
	3、下载并安装xlwt模块
	
运行：
	windows下直接运行start.bat,其他环境下通过命令行需要通过运行python bookinfo.python

输出:
	由于亚马逊网站的书本信息并不是完全结构化的数据，因此输出会包含一些系统不能处理的脚本，以便用户手工编辑
    输出的主要内容包括：
	1、output/outpub.xls（注意是03版本的EXCEL文件）
	
	2、loss.txt （系统未能识别的书本信息的链接，请用户手工补齐,由于网络原因导致的页面无法打开）
	
	3、log.txt （记录搜索的过程和结果）

注意：由于字符串的复杂性，搜索结果并不能完全满足需求，比如书名是网页上搜索得到的全称（附加许多说明信息），用户需要进行二次编辑
