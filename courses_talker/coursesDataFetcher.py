# -*- coding: utf-8 -*-
from urllib2 import urlopen
from bs4 import BeautifulSoup
import codecs
import json
import sys

class DataFetcher:
    def __init__(self):
	self.root_url = "https://zapisy.ii.uni.wroc.pl"
	self.course_desc = {}
	self.fetch_courses_list()
	for course in self.courses:
	    print("Fething and parsing " + course['url'])
	    self.fetch_course_description(course)



    def get_link_content(self, link):
	return urlopen(link).read()


    def fetch_courses_list(self):
	raw_content = self.get_link_content(self.root_url + '/courses/')
	parsed = BeautifulSoup(raw_content, 'html.parser')
	unparsed_json = parsed.find(id='courses_list_json').contents[0]
	self.courses = json.loads(unparsed_json)['courseList']


    def fetch_course_description(self, course_entry):
	raw_content = self.get_link_content(self.root_url + course_entry['url'])
	parsed = BeautifulSoup(raw_content, 'html.parser')
	title = parsed.find('h2').text
	desc = parsed.find(class_="description").find("p").text
	self.course_desc[title] = desc