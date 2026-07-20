import asyncio
import time
import json

# 모의 네트워크 요청 함수
async def do_request(item_id):
    # 💡 [속도 튜닝] 5초 대신 0.5초만 쉬게 하여 0.2초 타임아웃 기준을 넘기도록 유도합니다.
    if item_id == 15 or item_id == 30:
        await asyncio.sleep(0.5)  
    
    if item_id == 25 or item_id == 45:
        raise Exception("서버 내부 오류 (500)")
        
    await asyncio.sleep(0.05) # 정상 데이터 대기 시간도 절반으로 감축
    return {'id': item_id, 'ok': True}

# 타임아웃 처리 + 지수 백오프 재시도 안전장치
async def fetch_retry(sem, item_id, max_retries=3):
    for attempt in range(max_retries):
        try:
            async with sem:
                # 💡 [속도 튜닝] 3.0초 대신 0.2초 제한을 걸어 초고속으로 타임아웃을 터트립니다.
                return await asyncio.wait_for(do_request(item_id), timeout=0.2)
                    
        except (asyncio.TimeoutError, Exception) as e:
            if attempt == max_retries - 1:
                return {'id': item_id, 'ok': False, 'error': str(e), 'failed_at': time.time()}
            
            # [STEP 5] 지수 백오프 대기 시간 압축
            wait = 0.01 * (2 ** attempt)
            print(f"⚠️ [행 {item_id}] 수집 실패... {wait:.2f}초 후 {attempt + 2}회차 재시도 합니다. (원인: {type(e).__name__})")
            await asyncio.sleep(wait)

# 메인 가동부
async def main():
    print("🚀 [안전장치 풀 가동] 60건의 비동기 수집 리포트를 시작합니다. (동시 요청 제한: 10개)")
    
    sem = asyncio.Semaphore(10)
    tasks = [fetch_retry(sem, i) for i in range(60)]
    
    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    ok = [r for r in results if isinstance(r, dict) and r.get('ok') is True]
    fail = [r for r in results if isinstance(r, dict) and r.get('ok') is False]
    
    print("\n" + "="*50)
    print("          ★ [실습 3] 최종 비동기 수집 보고서 ★")
    print("="*50)
    print(f"▶ 성공적으로 수집된 데이터 : {len(ok)} 건")
    print(f"▶ 최종 실패 및 제외 데이터 : {len(fail)} 건")
    print("-" * 50)
    print("🎉 [성공] 타임아웃과 3회 재시도를 거쳐 안전하게 수집을 완료했습니다!")
    print("="*50)

    # [확장 과제] 최종 실패한 4건 격리 저장
    if fail:
        file_path = 'data/dead_letter.json'
        with open(file_path, mode='w', encoding='utf-8') as f:
            json.dump(fail, f, indent=2, ensure_ascii=False)
        print(f"📂 [확장 과제 완료] 최종 실패한 {len(fail)}건의 내역을 '{file_path}'에 안전하게 격리 저장했습니다.")
        print("="*50 + "\n")

if __name__ == '__main__':
    start_time = time.perf_counter()
    asyncio.run(main())
    print(f'⚡ 전체 비동기 총 소요 시간: {time.perf_counter() - start_time:.2f}초')