import pandas as pd
import numpy as np
from sklearn.ensemble import IsolationForest
import joblib

# 1. 가상의 데이터 생성
# 정상 데이터 (USL/LSL 이내의 평이한 값들)
data = {
    'RESULT_1': np.random.normal(100, 5, 500), # 평균 100, 표준편차 5
    'RESULT_2': np.random.normal(50, 2, 500),  # 평균 50, 표준편차 2
    'RESULT_3': np.random.normal(200, 10, 500) # 평균 200, 표준편차 10
}
df_train = pd.DataFrame(data)

# 2. Isolation Forest 모델 설정
# contamination: 전체 데이터 중 이상치 비율 (모르면 'auto' 혹은 0.05 정도)
model = IsolationForest(n_estimators=100, contamination=0.05, random_state=42)

# 3. 모델 학습 (정상 데이터의 분포를 배웁니다)
model.fit(df_train)

# 4. 학습된 모델 저장 (서버 배포용)
joblib.dump(model, 'inspection_anomaly_model.pkl')
print("모델 학습 및 저장 완료!")

# 5. 테스트 (새로운 데이터가 들어왔을 때)
test_data = pd.DataFrame([[102, 51, 205],  # 정상 범위 데이터
                          [150, 80, 300]], # 아주 이상한 데이터
                         columns=['RESULT_1', 'RESULT_2', 'RESULT_3'])

# 예측 (-1: 이상, 1: 정상)
predictions = model.predict(test_data)
# 점수 (낮을수록 이상함)
scores = model.decision_function(test_data)

for i, pred in enumerate(predictions):
    status = "이상 발생!" if pred == -1 else "정상"
    print(f"데이터 {i+1}: 결과 = {status}, 이상 점수 = {scores[i]:.4f}")