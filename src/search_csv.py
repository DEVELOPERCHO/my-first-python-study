import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# 데이터 로드
data = pd.read_csv("data/production_data.csv")

print("\n[데이터 정보]")
print(data.info())

print("\n[기초 통계]")
print(data.describe())

print("\n[라인별 불량률]")
line_defect = data.groupby("line")["defect"].mean()
print(line_defect)

#sns.barplot(x=line_defect.index, y=line_defect.values)
sns.scatterplot(x="temperature", y="defect", hue="line", data=data)

# 2. 이미지 파일로 저장 (파일 이름과 확장자 지정)
plt.savefig("defect_analysis_result.png")

# 3. (선택사항) 화면에도 띄우기
plt.show()