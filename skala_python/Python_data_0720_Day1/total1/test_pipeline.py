import pandas as pd
from pipeline import load, transform


def test_카테고리_소문자화():
    valid, _ = transform(
        [{"id": 1, "name": "A", "category": " FOOD ", "price": 10}]
    )
    assert valid[0].category == "food"


def test_음수_가격_거부():
    valid, invalid = transform(
        [{"id": 1, "name": "A", "category": "food", "price": -5}]
    )
    assert len(valid) == 0
    assert len(invalid) == 1


def test_유효_무효_건수_일치():
    rows = [
        {"id": 1, "name": "A", "category": "food", "price": 10},
        {"id": 2, "name": "B", "category": "drink", "price": 20},
        {"id": 3, "name": "C", "category": "food", "price": -5},
    ]
    valid, invalid = transform(rows)
    assert len(valid) + len(invalid) == len(rows)


# [STEP 5] Parquet 라운드트립 테스트 — '저장 후 다시 읽어도 같은가'
def test_parquet_라운드트립(tmp_path):
    # 🌟 대괄호를 쓰지 않고 list(range(1, 3))을 사용하여 1, 2가 담긴 리스트를 동적으로 만듭니다.
    id_list = list(range(1, 3))
    price_list = [10.5, 20.0]
    
    df = pd.DataFrame({"id": id_list, "price": price_list})
    p = tmp_path / "test.parquet"

    df.to_parquet(p, index=False)
    back = pd.read_parquet(p)

    # 완벽히 복원되는지 데이터 무결성 검증
    pd.testing.assert_frame_equal(df, back)


def test_load_함수_데이터프레임_반환():
    valid, _ = transform(
        [{"id": 1, "name": "A", "category": "food", "price": 10}]
    )
    df = load(valid, out_dir="tmp_output")
    assert isinstance(df, pd.DataFrame)


def test_스키마_정규화_공백제거():
    valid, _ = transform(
        [{"id": 1, "name": "A", "category": "  drink  ", "price": 15}]
    )
    assert valid[0].category == "drink"