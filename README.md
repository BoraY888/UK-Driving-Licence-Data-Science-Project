# UK-Driving-Licence-Data-Science-Project
Creation of an interactive dashboard on Streamlit to analyse UK Driving Licence data

## UK Drivers Age Visualisation
**Plan**

For the first visualisation in the dashboard I want to create simple bar charts that display the age of drivers, and how many of the types of licences each age groups holds, as well as how many penalty points each age group has accumulated. 

**Design**

A sketch was created using Draw.io and uploaded to the repository as an XML file. Two bar charts will be created with age groups starting with 16-17, then 18-20 and 3 year intervals till 27-29, and 5 year intervals after. The interactive elements will include changing which types of driving licences the user wants to see, and which number of penalty points the user would like to see on the bar chart. Also, appropriate colours must be chosen to account for colourblind users.
To view the diagram:
Go to https://app.diagrams.net
Click "File" > "Open from URL" (or open from device if downloaded)
Paste this link: https://raw.githubusercontent.com/BoraY888/UK-Driving-Licence-Data-Science-Project/main/Driver Age Visualisation.drawio

**Development**

The current version of the App will be uploaded to the repository with comments explaining choices I made during the development of the first two visualisations.

**Testing**

The dashboard has been tested and passed each test case that was relevant to the charts. The test log will be available in the final report for this project, which will also be uploaded to this repository.

## UK Drivers Risk Analysis Interactive Map
**Plan**

For this part of the dashboard I will create a regional map of the UK that firstly shows the Gender distribution of Penalty Points accumulated by County, and then a fully interactive map that allows users to input an Age and Gender and will be able to see the risk of UK Drivers in that same demographic

**Design**

Using a UK County Map I sketched a general idea for how the interactive map will work. The Gender distribution map will have a gradient scale to give users insights on which regions in the UK have a larger amount of Male or Female drivers with Penalty Points. The interactive elements will be hovering over each region will show an exact ratio of Male:Female drivers with Penalty Points, which can be used to compare regions in the next interactive map. The second map will encompass all important variables, asking the user to input a Gender and Age and then highlighting each region by whether the inputted demographic would be considered high (red) or low (green) risk, which will also be a gradient scale.
To view the diagram:
Go to https://app.diagrams.net
Click "File" > "Open from URL" (or open from device if downloaded)
Paste this link: https://raw.githubusercontent.com/BoraY888/UK-Driving-Licence-Data-Science-Project/main/UK Interactive Maps.drawio

**Development**
Many issues occurred while I was creating the interactive map, such as mapping issues with the Ceremonial Counties, as well as my first chosen GeoJSON file missing many values where coordinates and county boundaries were present, but no county was assigned to it. After switching to the ONS Boundary-Line Map, the GeoPKG file was very large but contained structure as it only included 91 Ceremonial Counties. When I created the Gender distribution map in relation to Penalty Points accumulated by each gender, every county was very similar with the entire map being coloured slightly blue to show that males accumulated more penalty points than females. The uniform distribution didn't seem very insightful, so I changed the map to Full Driving Licences held by each Gender per County. I then tried to create a map with the inputs for Gender and Age, however I misunderstood my datasets and had to normalise data on one excel sheet with Age and Gender, and then normalise data for Penalty Points per County, causing many issues. Due to the minimal changes between each region after all group weights had been applied, I spent hours going back and forth between normalising, logarithmic scaling, and min-max scaling, none of which adjusted my map whatsoever. This lead me to settling for creating a map that shows Weighted Penalty Points accumulated per County, and a nice filter system that allows users to compare, for example, a Counties Risk to their respetive country (England, Scotland, or Wales), as well as comparing a selected county to the whole of the UK, excluding Northern Ireland.

**Testing**
The dashboard has been tested and passed each test case that was relevant to the charts. The test log will be available in the final report for this project, which will also be uploaded to this repository.
