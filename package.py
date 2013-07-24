import os
import zipfile

NAME = 'webapi'

if not os.path.exists('./scripts'):
    os.makedirs('./scripts')
f = zipfile.PyZipFile('./scripts/%s.zip' % NAME, mode='w')
os.chdir('src')
try:
    f.writepy(NAME)
finally:
    f.close()
for name in f.namelist():
    print name
