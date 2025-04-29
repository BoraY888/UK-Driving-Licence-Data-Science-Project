import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np                  #importing all necessary libraries

data1 = pd.read_excel('driving-licence-data-feb-2025.xlsx', skiprows=21) #Cleaning first dataset
data1.reset_index(drop=True, inplace=True)
data1["Age"] = pd.to_numeric(data1["Age"], errors="coerce")
bins = [14, 17, 20, 23, 26, 29, 34, 39, 44, 49, 60, 70, 80, 110]
age_groups = ["15-17", "18-20", "21-23", "24-26", "27-29", "30-34", "35-39", "40-44", "45-49", "50-60", "61-70", "71-80", "81+"]
data1['Age_Group'] = pd.cut(data1['Age'], bins=bins, labels=age_groups)
grouped = data1.sort_values("Age").groupby("Age_Group")

def get_group_value(group, label):      #Due to cumulative nature of driving licence data, last value taken for each age group, and max for 81+ as there are very few people who are over 100 and skew the bars
    if label == "81+":
        return group["Full - Total"].max()
    else:
        return group["Full - Total"].iloc[-1]

full_licences_by_group = grouped.apply(lambda g: get_group_value(g, g.name))

def get_group_value(group, label):
    if label == "81+":
        return group["Provisional - Total"].max()
    else:
        return group["Provisional - Total"].iloc[-1]

provisional_licences_by_group = grouped.apply(lambda g: get_group_value(g, g.name))


data6 = pd.read_excel('driving-licence-data-feb-2025.xlsx', sheet_name=5, skiprows=25)  #cleaning and importing of the penalty points by age group data
data6 = data6.drop(index=range(43))  #Removing driving licence types that already come with having a full driving licence   
data6 = data6.rename(columns={"Unnamed: 0": "Licence Type"})
data6 = data6.set_index("Licence Type")
data6 = data6.T             #Ages were the columns, so transposed for consistency
data6 = data6.iloc[1:]
data6 = data6.reset_index().rename(columns={"index": "Age"})
data6 = data6.drop(columns=["M(prov)", "N(prov)", "C1E(auto)", "C1E(prov)", "C1(auto)", "C1(prov)", "C(auto)", "C(prov)", "CE(auto)", 
                            "CE(db)", "CE(auto,db)", "CE(auto)", "CE(prov)", "D1(auto)", "D1(prov)", "D1E(auto)", "D1E(prov)", "D(auto)", 
                            "D(prov)", "DE(auto)", "DE(prov)"])        #These are extra licence types that show people are in the process of receiving these licence types so removed
data6 = data6.drop(index=182)   #Total row at the bottom of dataset
data6["Age"] = pd.to_numeric(data6["Age"], errors="coerce")
data6['Age_Group'] = pd.cut(data6["Age"], bins=bins, labels=age_groups)
cols_to_sum = ["M", "N", "C1E", "C1", "C", "CE", "D1", "D1E", "D", "DE"]
data6["Other - Total"] = data6[cols_to_sum].sum(axis=1)     #Creating a total column of all the driving licence types I want to keep
grouped1 = data6.sort_values("Age").groupby("Age_Group")

def get_group_value(group, label):
    if label == "81+":
        return group["Other - Total"].max()
    else:
        return group["Other - Total"].iloc[-1]

other_licences_by_group = grouped1.apply(lambda g: get_group_value(g, g.name))

st.header("Type of Driving Licence held by Age Group")
st.caption("1e6 means million, so 0.5 is 500,000")

selected_age_groups = st.sidebar.multiselect(           #Sidebar so age groups can be selected for both charts at the same time
    "Select Age Groups:",
    options=age_groups,
    default=age_groups
)
selected_age_groups = [group for group in age_groups if group in selected_age_groups]
provisional_licences_by_group = provisional_licences_by_group.loc[selected_age_groups]
full_licences_by_group = full_licences_by_group[selected_age_groups]
other_licences_by_group = other_licences_by_group[selected_age_groups]

chart_options = {
    "Provisional Licences": provisional_licences_by_group,
    "Full Licences": full_licences_by_group,
    "Other Licences": other_licences_by_group
}

selected_charts = st.multiselect(               #Multiselect for the driving licence chart to add interactivity
    "Choose the Type of Licence:",
    options=list(chart_options.keys()),
    default=list(chart_options.keys())
)
color_mapping = {                           #Unique colours used for simplicity and accessibility
    "Provisional Licences": "green",
    "Full Licences": "blue",
    "Other Licences": "orange"
}

fig, ax = plt.subplots(figsize=(12, 6))

n_charts = len(selected_charts)
bar_width = 0.8 / n_charts 
x = np.arange(len(other_licences_by_group))         #Bar chart created with all three licence types included on the same chart

for idx, chart_name in enumerate(selected_charts):
    offset = (idx - n_charts/2) * bar_width + bar_width/2
    ax.bar(
        x + offset,
        chart_options[chart_name].values,
        width=bar_width,
        label=chart_name,
        color=color_mapping.get(chart_name, "grey")
    )
ax.set_xlabel("Age Group")
ax.set_ylabel("Number of Licences")
ax.set_title("Licence Types by Age Group")
ax.set_xticks(x)
ax.set_xticklabels(other_licences_by_group.index, rotation=45)
ax.legend()
plt.tight_layout()

st.pyplot(fig)

st.header("Weighted Total of Penalty Points held by Age Group")
st.caption("Weighted Total has been calculated by multiplying the amount of Penalty Points by the Count of Drivers (e.g 300 drivers hold 3 points on Licence each = 900)")

data4 = pd.read_excel('driving-licence-data-feb-2025.xlsx', sheet_name=3, skiprows=25)      #Cleaning and importing Penalty Points dataset
data4 = data4.drop(columns=['Gender', 'Current Pts', 'Unnamed: 50', 'Total'])
data4 = data4.groupby("Age At Refresh", as_index=False).sum()
weighted_cols = [col for col in data4.columns if col not in ['Age At Refresh']]

data4["Weighted Total"] = data4[weighted_cols].mul([int(c) for c in weighted_cols], axis=1).sum(axis=1)
data4 = data4.rename(columns={'Age At Refresh': 'Age'})
data4["Age"] = pd.to_numeric(data4["Age"], errors="coerce")
data4['Age_Group'] = pd.cut(data4["Age"], bins=bins, labels=age_groups)
grouped2 = data4.sort_values("Age").groupby("Age_Group")

def get_group_value(group, label):
    if label == "81+":
        return group["Weighted Total"].max()
    else:
        return group["Weighted Total"].iloc[-1]

penalty_points_by_group = grouped2.apply(lambda g: get_group_value(g, g.name))

penalty_points_by_group = penalty_points_by_group[selected_age_groups]

fig1, ax1 = plt.subplots(figsize=(12, 6))
x1 = np.arange(len(penalty_points_by_group))        #Only one variable so color made black
ax1.bar(
    x=x1,
    height=penalty_points_by_group.values,
    color="black",
    width=0.6
)
ax1.set_xlabel("Age Group")
ax1.set_ylabel("Weighted Total of Penalty Points")
ax1.set_title("Penalty Points by Age Group")
ax1.set_xticks(x1)
ax1.set_xticklabels(penalty_points_by_group.index, rotation=45)
ax1.legend(["Penalty Points"])
plt.tight_layout()

st.pyplot(fig1)