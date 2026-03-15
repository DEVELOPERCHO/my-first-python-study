import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

data = pd.read_csv("data/production_data.csv")

st.title("MES Production Dashboard")

st.subheader("Production Data")
st.dataframe(data)

line_output = data.groupby("line")["output"].sum()

st.subheader("Production by Line")

fig, ax = plt.subplots()
line_output.plot(kind="bar", ax=ax)
st.pyplot(fig)

defect_rate = data["defect"].mean()

st.metric("Defect Rate", defect_rate)

fig2, ax2 = plt.subplots()
sns.scatterplot(x="temperature", y="defect", data=data, ax=ax2)

st.subheader("Temperature vs Defect")

st.pyplot(fig2)