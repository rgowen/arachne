import http.client
import sys
import math
import concurrent.futures
import threading
import time
import re
import urllib.request
import argparse

ip_targets = list() #List containing all IP targets
responsive_ips = list() #Global list of IPs with HTTP responses
lock = threading.Lock() #Lock for the global IP list


def get_title(ip):
	''''Use regex to get the title from the html document at the given IP address'''
	open = urllib.request.urlopen('http://' + ip)
	html = str(open.read())
	title_compile = re.compile("<title>(.+?)</title>")
	match = title_compile.match(html)
	if(match):
		return match.group(1)
	else:
		return('[No title]')
		
def add_to_responsive_ips(ip):
	'''Add IP to the global list of responsive addresses.'''
	global responsive_ips
	with lock:
		responsive_ips.append(ip)
		
def get_http_status_code(host, path="/"):
	'''Attempt HTTP connection and return the result.'''
	try:
		conn = http.client.HTTPConnection(host, timeout=1)
		conn.request("HEAD", path)
		return conn.getresponse().status
	except:
		return 'No HTTP response.'
		
def get_ip_range(start_ip, end_ip):
	'''Create a range of IP addresses from given start and end addresses.'''
	start = list(map(int, start_ip.split(".")))
	end = list(map(int, end_ip.split(".")))
	temp = start
	ip_range = []
	ip_range.append(start_ip)
	while temp != end:
		start[3] += 1
		for i in (3, 2, 1):
			if temp[i] == 256:
				temp[i] = 0
				temp[i-1] += 1
		ip_range.append(".".join(map(str, temp)))    
	return ip_range
	
def divide_ip_range(ip_range, thread_count): # Deprecated
	'''Divide the given list of IP addresses by the number of threads.'''
	avg = len(ip_range) / float(thread_count)
	out = []
	last = 0.0
	while(last < len(ip_range)):
		out.append(ip_range[int(last):int(last + avg)])
		last += avg
	return out
	
def scan():
	'''Pop an IP off the global list and scan it'''
	ip = ip_targets.pop()
	response = get_http_status_code(ip)
	print('Response from ' + ip + ': ' + str(response))
	if(response == 200):
		add_to_responsive_ips(ip)

def sort_ips(ips):
	'''Sort the given list of IPs from lowest to highest.'''
	for i in range(len(ips)):
		ips[i] = "%3s.%3s.%3s.%3s" % tuple(ips[i].split("."))
	ips.sort()
	for i in range(len(ips)):
		ips[i] = ips[i].replace(" ", "")
	return ips

'''Handle all command line arguments'''
parser = argparse.ArgumentParser()
parser.add_argument('-b', nargs='?', type=str, help="IP range beginning.", required=True)
parser.add_argument('-e', nargs='?', type=str, help="IP range end.", required=True)
parser.add_argument('-n', nargs='?', type=int, help="Number of threads to use.", default=1)
parser.add_argument("-t", action="store_true", help="Add HTML titles of pages with an HTTP response to output file.")
args = parser.parse_args()
add_titles = False
if(args.t):
	add_titles = True
ip_begin = args.b
ip_end = args.e
threads = args.n

'''Main script'''
ip_targets = get_ip_range(ip_begin, ip_end)
# chunked_ranges = (divide_ip_range(ip_range, threads))
executor = concurrent.futures.ThreadPoolExecutor(int(threads))
futures = [executor.submit(scan) for ip in ip_targets]
concurrent.futures.wait(futures)
if(responsive_ips): 
	print('These IPs returned HTTP 200 response:')
	for ip in responsive_ips:
		print(ip)
	sorted_ips = sort_ips(responsive_ips)
	filename = ('responsive_ips_' + time.strftime("%Y%m%d-%H%M%S") + '.txt')
	file = open(filename, 'w')
	for ip in sorted_ips:
		if(add_titles == True):
			file.write(ip + ' ' + get_title(ip) + '\n')
		else:
			file.write(ip + '\n')
	file.close()
	print('Responsive IPs written to ' + filename)
else:
	print('No responsive IPs in given range.')

	



