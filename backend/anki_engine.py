from datetime import date, timedelta

def calculate_sm2_schedule(
    repetitions: int, 
    interval: int, 
    ease_factor: float, 
    quality: int
) -> tuple[int, int, float]:
    """
    SuperMemo-2 (SM-2) 알고리즘을 기반으로 다음 복습 스케줄을 계산합니다.
    quality: 0-5 (0: 완벽히 틀림, 5: 완벽히 맞음)
    """
    if quality >= 3:
        if repetitions == 0:
            interval = 6 # 첫 복습 성공 시 6일
        elif repetitions == 1:
            interval = round(interval * ease_factor) # 두 번째부터 계수 적용
        else:
            interval = round(interval * ease_factor)
        repetitions += 1
    else:
        repetitions = 0
        interval = 1

    ease_factor += (0.1 - (5 - quality) * (0.08 + (5 - quality) * 0.02))
    if ease_factor < 1.3: # 최소 난이도 계수
        ease_factor = 1.3

    return repetitions, interval, ease_factor

def get_initial_anki_schedule(today: date = date.today()) -> tuple[date, int, float, int]:
    """
    새로운 Anki 카드의 초기 스케줄을 반환합니다.
    """
    return today + timedelta(days=1), 1, 2.5, 0 # 다음날, 1일 간격, 난이도 2.5, 반복 0회
