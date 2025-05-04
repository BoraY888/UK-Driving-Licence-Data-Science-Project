import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np                  #importing all necessary libraries

st.sidebar.title("Page")            #Navigation box
page = st.sidebar.selectbox("Select a Page", options=["Overview", "Charts and Insights", "Interactive Map"])

total_licences = 42_537_111
drivers_with_penalty_points = 3_001_294
average_age_of_drivers = 61.53
gender_ratio_drivers = "1.15:1"

if page == "Overview":              #First introductory page
    st.title("UK Drivers Risk Assessment Interactive Dashboard")
    st.header("Overview")
    st.write("This Interactive Dashboard aims to provide users with insights and tools to assess the risks of certain demographics of UK Drivers, and possible reasons why insurance companies may charge more or less for Motor Vehicle Insurance")
    st.subheader("Key Statistics")          #Key Statistics widget
    st.caption("as of February 2025")
    
    st.metric(label="Total Driving Licences in the UK", value=f"{total_licences:,}")
    st.metric(label="Total Drivers with Penalty Points", value=f"{drivers_with_penalty_points:,}")
    st.metric(label="Average Age of UK Drivers", value=f"{average_age_of_drivers} years")
    st.metric(label="Male to Female Ratio of UK Drivers", value=gender_ratio_drivers)

elif page == "Charts and Insights":
    st.title("Charts and Insights")
    st.write("Distribution of driving licences and penalty points.")

    data1 = pd.read_excel('CW_App/driving-licence-data-feb-2025.xlsx', skiprows=21) #Cleaning first dataset
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


    data6 = pd.read_excel('CW_App/driving-licence-data-feb-2025.xlsx', sheet_name=5, skiprows=25)  #cleaning and importing of the penalty points by age group data
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
    st.write("Initial findings we can deduce from this chart include the fact that policies have changed drastically in the last 30 years, which has previously allowed all drivers to drive a larger variety of vehicles, shown in the Other - Licences category. " \
    "This also provides us with a comparison for newer drivers, as we can determine that younger drivers who have gone out of their way to get other driving qualifications, which is rare for their age group, could show they are skilled as a driver and lead to a smaller insurance premium. " \
    "Looking at the Full and Provisional Licence data, we see the expected pattern of an increase in Full Licence holders and decrease in Provisional Licence holders as people get older, however the fact that lots of UK citizens don't have Full Driving Licences could show interesting patterns, such as finding areas with a small amount of vehicle usage.")

    st.header("Weighted Total of Penalty Points held by Age Group")
    st.caption("Weighted Total has been calculated by multiplying the amount of Penalty Points by the Count of Drivers (e.g 300 drivers hold 3 points on Licence each = 900)")

    data4 = pd.read_excel('CW_App/driving-licence-data-feb-2025.xlsx', sheet_name=3, skiprows=25)      #Cleaning and importing Penalty Points dataset
    data4 = data4.drop(columns=['Gender', 'Current Pts', 'Unnamed: 50', 'Total'])
    data4 = data4.groupby("Age At Refresh", as_index=False).sum()
    weighted_cols = [col for col in data4.columns if col not in ['Age At Refresh']]     #As penalty points is each column, this code isolates those columns

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
    st.write("The Weighted Penalty Points per Age Group follows a normal distribution, which is surprising considering Penalty Points remain on your licence for only 4 years, meaning plenty of experienced drivers are still accumulating Penalty Points. " \
    "This will need researching, as the exact reason for each Penalty Point is not known, but this could imply that a policy or traffic law is causing too many Penalty Points, regardless of driving experience.")

elif page == "Interactive Map":
    st.title("Interactive UK Maps")
    st.write("(excl. Northern Ireland), Ceremonial County Boundaries used")
    st.write("Adjusting the filters to regions such as England, will compare the risk of an English County to exclusively English Counties")
    import geopandas as gpd
    import matplotlib.colors as mcolors

    st.header("Gender Distribution of Driving Licences by County")

    import os
    import requests
    url = "https://drive.google.com/uc?export=download&id=1ZK_5NzrwGQUUasTs26zMfcjVEosCxOG3"
    local_file = "bdline_gb.gpkg"
    if not os.path.exists(local_file):
        response = requests.get(url)
        with open(local_file, "wb") as f:
            f.write(response.content)
    
    @st.cache                   #importing the county map geoPKG file with cache, as file is very large and any change to the maps crashed the app before the caching
    def load_data(file_path):
        return gpd.read_file(file_path)
    gdf = load_data("bdline_gb.gpkg")

    data2 = pd.read_excel("CW_App/driving-licence-data-feb-2025.xlsx", sheet_name=1, skiprows=11)
    data2 = data2[data2["County"] != "Unknown"]
    data2 = data2.iloc[:-1]

    # Group by County and totalling the full licences
    grouped3 = data2.groupby('County')[['Full Licences - Male', 'Full Licences - Female']].sum().fillna(0)
    grouped3['Total'] = grouped3['Full Licences - Male'] + grouped3['Full Licences - Female']
    grouped3['Ratio'] = (grouped3['Full Licences - Female'] - grouped3['Full Licences - Male']) / grouped3['Total']

    # Merge ratio data with the GeoDataFrame
    gdf['County'] = gdf['Name']  # Matching column names for proper merge
    gdf = gdf.merge(grouped3[['Ratio']], on='County', how='left')

    #Creating the sidebar filter that includes individual counties, and which countries they belong to
    st.sidebar.title("Filter by Region")
    region = st.sidebar.selectbox("Select a region", ["All", "England", "Scotland", "Wales"])
    all_counties = gdf['County'].unique()
    england_counties = ['Bedfordshire', 'Berkshire', 'Buckinghamshire', 'Cambridgeshire', 'Cheshire', 'Derbyshire', 'Greater Manchester', 'Hertfordshire', 'Leicestershire', 'Northamptonshire', 'Rutland', 'Nottinghamshire', 'Oxfordshire', 'Shropshire', 'South Yorkshire', 'Staffordshire', 'Surrey', 'Warwickshire', 'West Midlands', 'West Yorkshire', 'Wiltshire', 'Worcestershire', 'Herefordshire', 'Cumbria', 'Bristol', 'City and County of the City of London', 'Cornwall', 'Devon', 'Dorset', 'Durham', 'East Riding of Yorkshire', 'East Sussex', 'Essex', 'Gloucestershire', 'Greater London', 'Hampshire', 'Isle of Wight', 'Kent', 'Lancashire', 'Lincolnshire', 'Merseyside', 'Norfolk', 'North Yorkshire', 'Northumberland', 'Somerset', 'Suffolk', 'Tyne & Wear', 'West Sussex']
    scotland_counties = ['City of Edinburgh', 'East Lothian', 'West Lothian', 'Angus', 'Perth and Kinross', 'City of Dundee', 'Ayrshire and Arran', 'Renfrewshire', 'Dunbartonshire', 'City of Aberdeen', 'Kincardineshire', 'Aberdeenshire', 'Banffshire', 'Moray', 'Dumfries', 'Argyll and Bute', 'Berwickshire', 'Caithness', 'City of Glasgow', 'Clackmannan', 'Fife', 'Inverness', 'Lanarkshire', 'Midlothian', 'Nairn', 'Orkney', 'Ross and Cromarty', 'Roxburgh, Ettrick and Lauderdale', 'Shetland', 'Stirling and Falkirk', 'Sutherland', 'The Stewartry of Kirkcudbright', 'Tweeddale', 'Western Isles', 'Wigtown']
    wales_counties = ['South Glamorgan', 'West Glamorgan', 'Mid Glamorgan', 'Gwynedd', 'Clwyd', 'Dyfed', 'Gwent', 'Powys']
    if region == "England":
        filtered_counties = england_counties
    elif region == "Scotland":
        filtered_counties = scotland_counties
    elif region == "Wales":
        filtered_counties = wales_counties
    else:
        filtered_counties = all_counties

    county_selection = st.sidebar.multiselect("Select counties", options=filtered_counties, default=filtered_counties)
    gdf_filtered = gdf[gdf['County'].isin(county_selection)]

    # Pink to Blue colour map (Pink = more females, Blue = more males)
    cmap = mcolors.LinearSegmentedColormap.from_list("gender_ratio", ["blue", "white", "pink"])

    fig2, ax2 = plt.subplots(figsize=(10, 12))

    gdf_filtered[gdf_filtered['Ratio'].isna()].plot(          #Counties with no data in grey
        ax=ax2,
        color='lightgrey',
        edgecolor='black',
        linewidth=0.4,
        zorder=1    # behind the coloured counties
    )

    gdf_filtered[gdf_filtered['Ratio'].notna()].plot(         #Ratio colour map applied to counties with data
        ax=ax2,
        column='Ratio',
        cmap=cmap,
        edgecolor='black',
        linewidth=0.5,
        legend=True,
        legend_kwds={'label': "Gender Ratio\n(Pink = More Females, Blue = More Males)"},
        zorder=2    #in front
    )

    ax2.set_title("Gender Ratio of Full Driving Licences by County", fontsize=16)
    ax2.set_axis_off()
    plt.tight_layout()

    st.pyplot(fig2)

    st.header("Risk Assessment of accumulating Penalty Points per County")
    #Loading and cleaning data
    data5 = pd.read_excel('CW_App/driving-licence-data-feb-2025.xlsx', sheet_name=4, skiprows=25)
    data5 = data5.drop(columns=['Current Pts', 'Unnamed: 49'])
    penalty_cols1 = [col for col in data5.columns if col not in ['Total', 'County', 'District']]
    data5['Weighted Points'] = data5[penalty_cols1].mul([int(c) for c in penalty_cols1], axis=1).sum(axis=1)
    county_weighted = data5.groupby('County').agg({     #Creating another variable with the needed columns for map
        'Weighted Points': 'sum',
        'Total': 'sum'
    }).reset_index()
    county_weighted['Adjusted Weighted Total'] = county_weighted['Weighted Points'] / county_weighted['Total'] #Getting a proportionate value for comparison

    gdf1 = load_data("bdline_gb.gpkg")
    gdf1['County'] = gdf1['Name']
    gdf1 = gdf1.merge(county_weighted[['County', 'Adjusted Weighted Total', 'Weighted Points']], on='County', how='left')

    gdf1_filtered = gdf1[gdf1['County'].isin(county_selection)]

    # Green-to-Red colormap (lower risk = green, higher risk = red)
    cmap1 = mcolors.LinearSegmentedColormap.from_list("Risk Level", ["green", "white", "red"])

    fig3, ax3 = plt.subplots(figsize=(10, 12))

    gdf1_filtered[gdf1_filtered['Adjusted Weighted Total'].isna()].plot(      #Missing data for counties made grey but kept in map
        ax=ax3,
        color='lightgrey',
        edgecolor='black',
        linewidth=0.4,
        zorder=1  # behind the coloured counties
    )

    gdf1_filtered[gdf1_filtered['Adjusted Weighted Total'].notna()].plot(     #Weighted Total data coloured for counties with available data
        ax=ax3,
        column='Adjusted Weighted Total',
        cmap=cmap1,
        edgecolor='black',
        linewidth=0.5,
        legend=True,
        legend_kwds={'label': "Adjusted Weighted Total\n(Green = Lower, Red = Higher)"},
        zorder=2  # in front 
    )

    ax3.set_title("Adjusted Weighted Total of Penalty Points by County", fontsize=16)
    ax3.set_axis_off()
    plt.tight_layout()

    st.pyplot(fig3)



