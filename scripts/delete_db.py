import os
p = r'c:\Users\yeshw\Desktop\VS code\app\students.db'
try:
    if os.path.exists(p):
        os.remove(p)
        print('deleted')
    else:
        print('not found')
except Exception as e:
    print('error', e)
