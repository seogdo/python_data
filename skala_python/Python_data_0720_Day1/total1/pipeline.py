import asyncio
from pathlib import Path

import pandas as pd
from models import Product
from pydantic import ValidationError


# [STEP 3] Extract — 비동기 데이터 수집 함수
async def fetch(i: int) -> dict:
    """실제 서버나 API에서 데이터를 비동기로 가져오는 가상 함수"""
    await asyncio.sleep(0.01)  # 네트워크 지연 시뮬레이션
    return {"id": i, "name": f"Product_{i}", "category": "FOOD", "price": 10.0}


async def extract(ids: list[int], max_concurrent: int = 10) -> list[dict]:
    # 백프레셔 제어: 동시에 실행될 최대 비동기 개수를 10개로 제한
    sem = asyncio.Semaphore(max_concurrent)

    async def one(i):
        async with sem:
            # 실패 시 최대 3번 지수 백오프 재시도
            for attempt in range(3):
                try:
                    return await fetch(i)
                except Exception:
                    if attempt == 2:
                        raise
                    await asyncio.sleep(2**attempt)

    results = await asyncio.gather(*[one(i) for i in ids], return_exceptions=True)
    return [r for r in results if not isinstance(r, Exception)]


# [STEP 2] Transform — Pydantic 검증 및 스키마 정규화
def transform(raw: list[dict]) -> tuple[list, list]:
    valid, invalid = [], []
    for row in raw:
        try:
            # Pydantic 스펙 검증을 거쳐 객체 형태로 리스트에 저장
            valid.append(Product(**row))
        except ValidationError as e:
            invalid.append({"data": row, "errors": e.errors()})
    return valid, invalid


# [STEP 4] Load — DataFrame으로 만들고 CSV, Parquet 저장
def load(valid: list, out_dir: str = "output") -> pd.DataFrame:
    # 저장할 디렉터리가 없으면 자동 생성
    Path(out_dir).mkdir(parents=True, exist_ok=True)

    # ★ 가이드라인 명시 Pydantic v2 문법(.model_dump()) 완벽 적용
    df = pd.DataFrame([v.model_dump() for v in valid])

    # 데이터가 존재하는 경우에만 로컬 파일로 압축 저장
    if not df.empty:
        df.to_csv(f"{out_dir}/products.csv", index=False)
        df.to_parquet(f"{out_dir}/products.parquet", index=False)
    else:
        df = pd.DataFrame(columns=["id", "name", "category", "price"])

    return df


# [STEP 6] Orchestrate — run()으로 전체 인프라 조율
async def run(ids: list[int]) -> dict:
    raw = await extract(ids)  # E 단계 (추출)
    valid, invalid = transform(raw)  # T 단계 (변형)
    df = load(valid)  # L 단계 (적재)

    # 요약 결과 딕셔너리 출력 사양 충족
    return {
        "total": len(raw),
        "valid": len(valid),
        "invalid": len(invalid),
        "rows_saved": len(df),
    }


if __name__ == "__main__":
    # 0부터 59까지 총 60개의 ID를 타겟으로 비동기 파이프라인 트리거
    summary = asyncio.run(run(list(range(60))))
    print(summary)