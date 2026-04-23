# -*- coding: utf-8 -*-
import sys
sys.path.insert(0, '.')
from generate_almanac import get_ganzhi

result, day_gz, data = get_ganzhi('2026-04-13')
print('干支：', result)
print('月柱：', data['month'])
print('日柱：', data['day'])
