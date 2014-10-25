#!/usr/bin/env python
# -*- coding: utf-8 -*-
import json
import re
import urllib
import xlwt
from collections import OrderedDict
import time,datetime

class Config(object):

	""" read configuration information from config file 
		to be appended books data and prepared for insert into excel"""
	config_data = {}

	def __init__(self):	
		self.get_config()

	def get_config(self):
		if self.config_data:
			pass
		else:
			file_obj = open('config.json')
			try:
				self.config_data = json.load(file_obj,object_pairs_hook=OrderedDict)
			finally:
				file_obj.close()

	def get_baseurl(self):
		return self.config_data['base_url']

	def get_endurl(self):
		return self.config_data['end_url']

	def get_total(self):
		return self.config_data['total']

	def get_pagesize(self):
		return self.config_data['page_size']

	def get_pagesymbol(self):
		return self.config_data['paging_symbol']

	def get_types(self):
		return self.config_data['type']

	def get_fields(self):
		return self.config_data['fields']

	def append_type_item(self,model_title,model_data):
		types = self.get_types()
		for type_item in types:
			if(type_item['title'] == model_title):
				type_item['books'].append(model_data)
				break

class TypeModel(object):
	""" type model """
	def __init__(self,typeitem):
		self.title = typeitem['title']
		self.id = typeitem['id']
		self.books = typeitem['books']

	def get_title(self):
		return self.title

	def get_id(self):
		return self.id

	def get_books(self):
		return self.books

class BookModel(object):
	""" child model from config applied to coposite,match,get information in Html """
	def __init__(self,id,name,author,publisher,time,brand):
		self.id = id
		self.name = name
		self.author = author
		self.publisher = publisher
		self.time = time
		self.brand = brand

	def get_modeljson(self):

		result_dict = OrderedDict([('id',self.id),('name',self.name),('author',self.author),
						('publisher',self.publisher),('time',self.time),('brand',self.brand)])
		return result_dict

class Html(object):

	""" composite url get books information and convert it to config """
	def get_pagenum_str(self,pagenum,symbol):	
		return symbol + str(pagenum+1)

	def composite_typeurl(self,base,end,typeid,pagenum):
		return base + '/' + str(typeid) + '/' + end + pagenum

	# result format like [('1','http://www.amazon.cn/..../dp/BOONOQNHP','bookname'),()...()] 
	def get_pagebooks(self,type_url):
		reg = re.compile(r'<span class="zg_rankNumber">(\d+)\.</span><span class="zg_rankMeta">'+
		'</span></div><div class="zg_title"><a  href="\s*(http://.*)\s*">(.*?)</a></div>'+
		'<div class="zg_byline">\s*~(.*?)\([插图作编者][\s\S]*?<strong class="price">(.*)</strong>')
		page = urllib.urlopen(type_url)
		html = page.read()
		lis = re.findall(reg,html)
		for i in range(len(lis)-1,-1,-1):
			price = lis[i][4].strip()
			if price == u'免费' or  u'￥' not in price:
				del lis[i]
		if(len(lis) > 20):
			print (u'在该页面上存在免费的书籍需要剔除,否则会导致搜索错误url:'+type_url).encode('GBK', 'ignore')
			print u'请联系开发人员'
			return None
		elif(len(lis) < 20):
			print (u'该页面上的书籍少于20本，请确认是否正确url: ' + type_url).encode('GBK', 'ignore')
		return lis 


	# result format like ('author','publisher','time','brand')
	def get_bookdetail(self,book_url,error_counter):
		page = urllib.urlopen(book_url)
		html = page.read()

		# only support Chinese publisher
		#regpub = re.compile(r'<li><b>出版社:</b> ([\x80-\xff]+).*?(\(\d+年\d+月\d+日\)|\s)</li>.*<li><b>品牌:</b>(.*?)</li>',re.DOTALL)
		#support Chinese publisher or English publisher not mix
		regpub = re.compile(r'<li><b>出版社:</b> ([\w\s]+;|[\x80-\xff]+).*?(\(\d+年\d+月\d+日\)|\s)</li>.*<li><b>品牌:</b>(.*?)</li>',re.DOTALL)
		pub_group = re.search(regpub,html)
		if pub_group == None:
			#http open error
			refail = re.compile(r'<h2>意外错误</h2></div>');
			error_group = re.search(refail,html)
			if error_group:
				error_counter = error_counter + 1
				if error_counter > 10:
					file_path = 'loss.txt'
					file_obj = open(file_path,'a')
					try:
						time.strftime('%Y-%m-%d %H:%M:%S')
						datetime.datetime.strftime(datetime.datetime.now(), '%Y-%m-%d %H:%M:%S')
						file_obj.write(u'\n网络连接出错或者亚马逊网站错误，请尝试手工连接网址:' + book_url+'\n')
						file_obj.write(str(datetime.datetime.now())[:19] + '\n')
					finally:
						file_obj.close()
					print (u'网络连接出错或者亚马逊网站错误，请尝试手工连接网址：' + '\n' + book_url).encode('GBK', 'ignore')
					return ('','','');
				return self.get_bookdetail(book_url,error_counter)
			else:
				file_path = 'loss.txt'
				file_obj = open(file_path,'a')
				try:
					time.strftime('%Y-%m-%d %H:%M:%S')
					datetime.datetime.strftime(datetime.datetime.now(), '%Y-%m-%d %H:%M:%S')
					file_obj.write(u'\n书本【出版社】或【品牌】搜索不到,请手工编辑，链接:' + book_url+'\n')
					file_obj.write(str(datetime.datetime.now())[:19] + '\n')
				finally:
					file_obj.close()
				print (u'书本【出版社】或【品牌】搜索不到,请手工编辑，链接:' + book_url + ' \n').encode('GBK', 'ignore')
				print ' '
				return (u' ',u' ',u' ')
		else:
			publisher = pub_group.group(1)
			thetime = pub_group.group(2)
			brand = pub_group.group(3)
			return (publisher,thetime,brand)



class Excel(object):
	""" read rules in excel file and write infomation from config into it"""
	def write_txt(self,array):
		file_path = 'book.txt'
		file_obj = open(file_path,'w')
		try:
			for i in range(len(array)):
				type_item = array[i]
				typemodel = TypeModel(type_item)
				books = typemodel.get_books()
				file_obj.write(type_item.get_title())
				file_obj.write('\n')
				for j in range(len(books)):
					book = books[j]
					for k in book:
						file_obj.write(str(book[k]) + '\t')
					file_obj.write('\n')
		finally:
			file_obj.close()
	def create_xls(self,type_list,fields,total):
		table_list = []
		xls_file = xlwt.Workbook()
		fields_keys = fields.keys()
		for i in range(len(type_list)):
			type_item = type_list[i]
			typemodel = TypeModel(type_item)
			title = typemodel.get_title()
			table = xls_file.add_sheet(title)
			
			# init first row
			for j in range(len(fields_keys)):
				table.write(0,j,fields_keys[j])

			table_list.append(table)
		return (xls_file,table_list)
	def write_xls_row(self,table_list,list_num,row_num,book):
		table = table_list[list_num]
		values = book.values()
		for i in range(len(values)):
			table.write(row_num,i,values[i].decode('utf-8'))

	def write_xls_table(self,table_list,title):
		pass
	def write_xls(self,table_list):
		pass

def main():
	config = Config()

	base_url = config.get_baseurl()
	end_url = config.get_endurl()
	total = config.get_total()
	page_size = config.get_pagesize()
	paging_symbol = config.get_pagesymbol()
	types = config.get_types()
	page_num = total/page_size + 1
	fields = config.get_fields()

	html_obj = Html()

	log = open('log.txt','a')
	log.write('\n')


	excel = Excel()
	file_and_tables = excel.create_xls(types,fields,total)
	xls_file = file_and_tables[0]
	table_list = file_and_tables[1]

	# search all types(10)
	try:
		for i in range(len(types)):
			typeitem = types[i]
			typemodel = TypeModel(typeitem)
			title = typemodel.get_title()
			type_id = typemodel.get_id()
			books = typemodel.get_books()

			#search all books(50)
			for j in range(page_num):
				pagenum_str = html_obj.get_pagenum_str(j,paging_symbol)
				type_url = html_obj.composite_typeurl(base_url,end_url,type_id,pagenum_str)
				page_books = html_obj.get_pagebooks(type_url)

				# page_books as standard
				if len(page_books) != page_size:

					print u'搜索结果存在偏差，搜索出书本数为' + str(len(page_books)) + u'，理论上该页面有20本收费书籍'
					print (u'url 为' + type_url).encode('GBK', 'ignore')
					print u'搜索将继续进行，请手工编辑缺失书本'
				# need_size = (j < 2 and page_size or 10)
				if j < 2:
					need_size = len(page_books)
				else:
					need_size = (10 < len(page_books) and 10 or len(page_books))
				for k in range(need_size):
					bookid = page_size * j + k + 1
					bookid_search = page_books[k][0]
					bookurl = page_books[k][1]
					bookname = page_books[k][2]
					bookauthor = page_books[k][3]

					#bookid_search as standard
					if bookid != int(bookid_search):
						print (u'书本:'+bookname+'排名与计算不一致搜索排名为'+bookid_search+u'计算排名为'+str(bookid)).encode('GBK', 'ignore')
						print (u'分页符号:' + pagenum_str).encode('GBK', 'ignore')
						print (u'类别url:' + type_url).encode('GBK', 'ignore') 
						print u'系统将以搜索排名为准，请手工检查该书排名'
					bookdetail = html_obj.get_bookdetail(bookurl,0)
					bookmodel = BookModel(bookid_search,bookname,bookauthor,bookdetail[0],bookdetail[1],bookdetail[2])
					bookdict = bookmodel.get_modeljson()
					config.append_type_item(title,bookdict)
					print (title + u'下的书本：' + bookname + u' 搜索完成').encode('GBK', 'ignore');
					log.write(title + u'下的书本：' + bookname + u' 搜索完成' + '     ' )
					time.strftime('%Y-%m-%d %H:%M:%S')
					datetime.datetime.strftime(datetime.datetime.now(),'%Y-%m-%d %H:%M:%S')
					log.write(str(datetime.datetime.now())[:19] + '\n')

					#write excel
					excel.write_xls_row(table_list,i,int(bookid_search),bookdict)
				# end interior loop
			# end mid loop
			print (title + u'下的所有书本搜索完成').encode('GBK', 'ignore')
		# end external for loop
	finally:
		log.close()
		xls_file.save('output\\output.xls')
if __name__ == '__main__':
	import sys
	reload(sys)
	sys.setdefaultencoding('utf-8')
	main()	
