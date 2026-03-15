import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

data = pd.read_csv("data/production_data.csv")

# 1. 페이지 설정
st.set_page_config(layout="centered")
st.title("🏭 MES AI 제조 분석 시스템")

# 2. 사이드바 - C#의 조회 조건 영역과 유사
st.sidebar.header("조회 조건")
selected_line = st.sidebar.multiselect("생산 라인 선택", ["LINE1", "LINE2"], default=["LINE1", "LINE2"])
temp_range = st.sidebar.slider("온도 범위 설정", 20, 35, (25, 30))

# 3. 데이터 로드 및 필터링
data = pd.read_csv("data/production_data.csv")
filtered_data = data[(data['line'].isin(selected_line)) & 
                     (data['temperature'].between(temp_range[0], temp_range[1]))]

# 4. 통계 카드 (C#의 Summary Label 역할)
col1, col2, col3 = st.columns(3)
col1.metric("조회 건수", f"{len(filtered_data)} 건")
col2.metric("평균 온도", f"{filtered_data['temperature'].mean():.2f} °C")
col3.metric("최대 생산량", f"{filtered_data['output'].max()} 개")

# 5. 그리드 출력 (C#의 GridControl)
st.subheader("📊 생산 데이터 상세 내역")
st.dataframe(filtered_data, use_container_width=True) # 필터링된 결과가 실시간 반영됩니다.

# 6. 차트 출력
st.subheader("📈 상관관계 분석")
fig, ax = plt.subplots()
sns.scatterplot(data=filtered_data, x="temperature", y="defect", hue="line", ax=ax)
st.pyplot(fig)