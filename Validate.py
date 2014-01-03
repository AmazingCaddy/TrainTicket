#!/usr/bin/env python
#coding: utf-8

import re
import Stations

def validate_station(station_name):
	if Stations.stations_dict.has_key(station_name):
		return Stations.stations_dict[station_name]
	return False

def is_leap_year(year):
	return (year % 400 == 0) if (year % 100 == 0) else (year % 4 == 0)

def validate_date(date):
	prog = re.compile('\d\d\d\d-\d\d-\d\d')
	result = prog.match(date)
	if result == None:
		return False
	dates = date.split('-')
	yy = int(dates[0])
	mm = int(dates[1])
	dd = int(dates[2])
	if mm not in range(1, 13):
		return False
	monthes = [0, 31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
	d = monthes[mm] + int(is_leap_year(yy))
	return 1 <= dd and dd <= d
