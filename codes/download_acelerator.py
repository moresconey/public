import os
import time
import shutil
import threading
import requests
from urllib import parse

url = 'http://200.152.38.155/CNPJ/Simples.zip'
conns = 8
tmp_dir = 'C:/Users/neymo/OneDrive/Git/public/codes/tmp/'
dl_dir = 'C:/Users/neymo/OneDrive/Git/public/codes/'

def get_filename_from_url(url):
	return parse.urlsplit(url).path.split('/')[-1]

def download(url, start, this_chunk_size, part):
	r = requests.get(url, headers={'Range':'bytes=%d-%d' % (start, start + this_chunk_size-1)}, stream=True)
	filename = get_filename_from_url(url) + '_%d' % part
	filepath = os.path.join(tmp_dir, filename)
	print('Downloading %s' % filepath)
	with open(filepath, 'wb') as f:
		for chunk in r.iter_content(chunk_size=1024):
			if chunk:
				f.write(chunk)
	print('Downloaded %s' % filepath)

# check if URL accept ranges
r = requests.head(url)
accept_ranges = 'accept-ranges' in r.headers and 'bytes' in r.headers['accept-ranges']
if not accept_ranges:
	print('URL does not accept byte ranges.')
	quit()

# download chunks
size = int(r.headers['content-length'])
chunk_size = int((size / conns))
remainder = 0 if size - (chunk_size * conns) <= 0 else size - (chunk_size * conns)
threads = []
for start in range(0, size, chunk_size):
	part = len(threads)
	this_chunk_size = chunk_size if part != conns-1 else chunk_size + remainder
	t = threading.Thread(target=download, args=(url, start, this_chunk_size, part))
	threads.append(t)
	t.daemon = True
	t.start()

# merge into a single file
while threading.active_count() > 1:
	time.sleep(0.1)

print('All parts downloaded. Joining files...')

filename = get_filename_from_url(url)
filepath = os.path.join(dl_dir, filename)
with open(filepath, 'wb') as f:
	for i in range(conns):
		tmp_filename = filename + '_%d' % i
		tmp_filepath = os.path.join(tmp_dir, tmp_filename)
		shutil.copyfileobj(open(tmp_filepath, 'rb'), f)
		os.remove(tmp_filepath)

print('Joining complete. File saved in %s' % filepath)
