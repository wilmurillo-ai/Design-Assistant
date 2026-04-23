import os, openpyxl

desktop = os.path.expanduser('~/Desktop')
out_path = os.path.join(desktop, 'test_run.xlsx')

wb = openpyxl.Workbook()
ws = wb.active
ws.append(['文件名', '公司名'])
ws.append(['test.pdf', '测试公司'])

wb.save(out_path)
print(f'Saved to {out_path}')
print(f'File exists: {os.path.exists(out_path)}')