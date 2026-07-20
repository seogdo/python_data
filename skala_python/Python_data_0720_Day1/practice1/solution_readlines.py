import csv
import tracemalloc
from collections import Counter
from functools import reduce

FILE_PATH = 'data/web_logs.csv'

def fold(acc, row):
    acc['total'] += 1
    acc['status'][row['status']] += 1
    acc['path'][row['path']] += 1
    acc['ip'][row['ip']] += 1
    return acc

def main():
    # 1. 메모리 측정 시작
    tracemalloc.start()
    
    # ⚠️ [문제의 구간] readlines()로 파일 20만 줄을 메모리에 몽땅 적재
    with open(FILE_PATH, newline='', encoding='utf-8') as f:
        lines = f.readlines()
        
    reader = csv.DictReader(lines)
    init = {'total': 0, 'status': Counter(), 'path': Counter(), 'ip': Counter()}
    
    # 집계 수행
    reduce(fold, reader, init)
    
    # 2. 메모리 측정 종료 및 출력
    _, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    
    print('=' * 45)
    print(f'▶ [readlines 버전] 최대 메모리 사용량: {peak / 1024 / 1024:.2f} MB')
    print('=' * 45)

if __name__ == '__main__':
    main()