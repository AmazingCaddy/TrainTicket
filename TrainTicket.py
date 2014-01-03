#!/usr/bin/env python
#coding: utf-8

import urllib2, urllib, httplib, socket
import json
import platform
import re
import time

import DetectCode, Stations, Validate

def get_all_tickets(params):
	'''
	params:
	train_date:
	from_station:
	to_station:
	purpose_codes:
	'''
	url_params = {
		'leftTicketDTO.train_date':		params['train_date'],
		'leftTicketDTO.from_station': params['from_station'],
		'leftTicketDTO.to_station': params['to_station'],
		'purpose_codes': params['purpose_codes']
	}
	#urllib.urlencode(url_params)
	url_list = [
		'https://kyfw.12306.cn/otn/leftTicket/query?', 
		'leftTicketDTO.train_date=',
		'%(train_date)s',
		'&leftTicketDTO.from_station=',
		'%(from_station)s',
		'&leftTicketDTO.to_station=',
		'%(to_station)s',
		'&purpose_codes=',
		'%(purpose_codes)s'
	]
	
	request_url = ''.join(url_list) % params
	print request_url

	''' for debug log '''
	#httpHandler = urllib2.HTTPHandler(debuglevel=1)
	#httpsHandler = urllib2.HTTPSHandler(debuglevel=1)
	#opener = urllib2.build_opener(httpHandler, httpsHandler)
	#urllib2.install_opener(opener)

	request = urllib2.Request(request_url)
	
	try:
		response = urllib2.urlopen(request, timeout = 10)
		#print time.time()
		json_string = response.read()
		#print time.time()
	except urllib2.HTTPError, e:
		if isinstance(e.reason, socket.timeout):
			print 'Time Out'
			return list()
	except urllib2.URLError, e:
		print 'URL Error'
		return list()

	json_data = json.loads(json_string)
	results = json_data['data']

	tickets = list()
	if results and isinstance(results, list):
		for res in results:
			ticket = res['queryLeftNewDTO']
			tickets.append(ticket)
	return tickets

def get_all_canbuy_tickets(tickets):
	canbuy_tickets = list()
	for ticket in tickets:
		if ticket['canWebBuy'] == 'Y':
			canbuy_tickets.append(ticket)
	return canbuy_tickets

def print_tickets(tickets):
	'''
		e.g.
		"train_no": "1100000K7500",
		"station_train_code": "K75",
		"start_station_telecode": "CCT",
		"start_station_name": "长春",
		"end_station_telecode": "NGH",
		"end_station_name": "宁波",
		"from_station_telecode": "SNH",
		"from_station_name": "上海南",
		"to_station_telecode": "NGH",
		"to_station_name": "宁波",
		"start_time": "05:18",
		"arrive_time": "09:43",
		"day_difference": "0",
		"train_class_name": "",
		"lishi": "04:25",
		"canWebBuy": "Y",
		"lishiValue": "265",
		"yp_info": "1005053219401525000810050500653010150098",
		"control_train_day": "20300303",
		"start_train_date": "20140110",
		"seat_feature": "W3431333",
		"yp_ex": "10401030",
		"train_seat_feature": "3",
		"seat_types": "1413",
		"location_code": "T2",
		"from_station_no": "35",
		"to_station_no": "41",
		"control_day": 67,
		"sale_time": "0800",
		"is_support_card": "0",
		"gg_num": "--",		
		"gr_num": "--",		高级软卧
		"qt_num": "--",		其他
		"rw_num": "8",		软卧
		"rz_num": "--",		软座
		"tz_num": "--",		特等座
		"wz_num": "有",		无座
		"yb_num": "--",		
		"yw_num": "有",		硬卧
		"yz_num": "有",		硬座
		"ze_num": "--",		二等座
		"zy_num": "--",		一等座
		"swz_num": "--"		商务座
	'''
	no_tickets = u"没有符合要求的火车票"
	platform_encoding = DetectCode.get_platform_encoding()

	if (len(tickets) == 0):
		print no_tickets.encode(platform_encoding)
		return

	from_station_max_len = 0
	to_station_max_len = 0

	for ticket in tickets:
		from_station_len = len(ticket['from_station_name'])
		to_station_len = len(ticket['to_station_name'])
		from_station_max_len = from_station_max_len if from_station_max_len > from_station_len else from_station_len
		to_station_max_len = to_station_max_len if to_station_max_len > to_station_len else to_station_len

	multi = 2 if platform_encoding == 'utf-8' else 1

	from_station_basewidth = 7 + from_station_max_len * multi
	to_station_basewidth = 7 + to_station_max_len * multi

	number = 0
	for ticket in tickets:
		number += 1

		out = list()
		out.append('%-4d' % number)
		out.append(ticket['station_train_code'].encode(platform_encoding))
		tmp_str = '%s(%s)' % (ticket['from_station_name'].encode(platform_encoding), ticket['start_time'].encode(platform_encoding))
		out.append(tmp_str)
		tmp_str = '%s(%s)' % (ticket['to_station_name'].encode(platform_encoding), ticket['arrive_time'].encode(platform_encoding))
		out.append(tmp_str)
		out.append(u'全程:(%s)'.encode(platform_encoding) % ticket['lishi'].encode(platform_encoding))

		from_station_name_len = len(ticket['from_station_name']) + from_station_basewidth
		to_station_name_len = len(ticket['to_station_name']) + to_station_basewidth
		format_str = '%%s%%-6s%%%ds -> %%%ds  %%s' % (from_station_name_len, to_station_name_len)

		print format_str % tuple(out)


def get_all_stations(params):
	'''
		train_no:
		from_station_telecode:
		to_station_telecode:
		depart_date:
	'''
	url_list = [
		'https://kyfw.12306.cn/otn/czxx/queryByTrainNo?',
		'train_no=',
		'%(train_no)s',
		#'5l000D320171',
		'&from_station_telecode=',
		'%(from_station_telecode)s',
		#'AOH',
		'&to_station_telecode=',
		'%(to_station_telecode)s'
		#'NGH',
		'&depart_date=',
		'%(depart_date)s'
		#'2014-01-04'
	]
	request = ''.join(url_list) % params

def main():
	today = time.strftime('%Y-%m-%d',time.localtime(time.time()))
	platform_encoding = DetectCode.get_platform_encoding()
	from_station_str = u'出发火车站名: '.encode(platform_encoding)
	to_station_str = u'到达火车站名: '.encode(platform_encoding)
	train_date_str = (u'出发日期(YYYY-MM-DD, e.g., ' + unicode(today) + u'): ').encode(platform_encoding)
	purpose_codes_str = u'是否学生票(Y/N): '.encode(platform_encoding)
	con_message = u'是否继续查询(Y/N) '.encode(platform_encoding)
	error_message = {
		'station_not_exist': u'该火车站不存在，请输入正确的'.encode(platform_encoding),
		'date_format': u'日期格式错误，请重新输入'.encode(platform_encoding)
	}
	input_tip =  u'请输入'.encode(platform_encoding)

	while True:
		message = input_tip
		while True:
			from_station = raw_input(message + from_station_str)
			from_station = from_station.decode(platform_encoding)
			from_station_info = Validate.validate_station(from_station)
			if from_station_info:
				break
			message = error_message['station_not_exist']

		message = input_tip
		while True:
			to_station = raw_input(message + to_station_str)
			to_station = to_station.decode(platform_encoding)
			to_station_info = Validate.validate_station(to_station)
			if to_station_info:
				break
			message = error_message['station_not_exist']

		message = input_tip
		while True:
			train_date = raw_input(message + train_date_str)
			train_date = train_date.decode(platform_encoding)
			if (Validate.validate_date(train_date)):
				break
			message = error_message['date_format']
		
		while True:
			purpose_codes = raw_input(purpose_codes_str)
			purpose_codes = purpose_codes.decode(platform_encoding)
			if purpose_codes in ['Y', 'y', 'N', 'n']:
				break

		if purpose_codes in ['y', 'Y']:
			purpose_codes = '0X00'
		else:
			purpose_codes = 'ADULT'

		params = {
			'train_date': train_date,
			'from_station': from_station_info['station_code'],
			'to_station': to_station_info['station_code'],
			'purpose_codes': purpose_codes		#ADULT
		}
		#print params
		tickets = get_all_tickets(params)
		#print_tickets(tickets)
		
		canbuy_tickets = get_all_canbuy_tickets(tickets)
		print_tickets(canbuy_tickets)

		con_message = raw_input(con_message)
		if con_message not in['Y', 'y']:
			break

if __name__ == '__main__':
	main()
	#get_url('')