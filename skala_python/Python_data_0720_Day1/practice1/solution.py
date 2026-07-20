import csv
import tracemalloc  # [확장 과제] 메모리 측정을 위한 라이브러리
from functools import reduce
from collections import Counter

# [STEP 1] 제너레이터 함수
def read_logs(path):
    with open(path, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            yield row

# [STEP 5] fold 패턴
def fold(acc, row):
    acc['total'] += 1
    acc['status'][row['status']] += 1
    acc['path'][row['path']] += 1
    acc['ip'][row['ip']] += 1
    return acc

def main():
    # [확장 과제] 메모리 측정 시작!
    tracemalloc.start()
    
    init = {
        'total': 0, 
        'status': Counter(),
        'path': Counter(),
        'ip': Counter()
    }
    
    # 집계 코드 실행
    result = reduce(fold, read_logs('data/web_logs.csv'), init)
    
    total = result['total']
    by_status = result['status']
    by_path = result['path']
    by_ip = result['ip']

    err_5xx = sum(c for s, c in by_status.items() if str(s).startswith('5'))
    ratio = err_5xx / total * 100

    # [확장 과제] 사용된 최대 메모리 계산
    current, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()

    # 리포트 출력
    print('=' * 40)
    print(f'총 요청 수 : {total:,}')
    print(f'5xx 오류율 : {ratio:.1f}%')
    
    print('-- 인기 경로 TOP 5 --')
    for path, cnt in by_path.most_common(5):
        print(f'{path:<20} {cnt:>7,}')
        
    print('-- 접속 상위 IP TOP 5 --')
    for ip, cnt in by_ip.most_common(5):
        print(f'{ip:<20} {cnt:>7,}')
    print('=' * 40)
    
    # [확장 과제 결과 출력]
    print(f'▶ [메모리 점검] 최대 메모리 사용량: {peak / 1024 / 1024:.2f} MB')
    print('=' * 40)

if __name__ == '__main__':
    main()