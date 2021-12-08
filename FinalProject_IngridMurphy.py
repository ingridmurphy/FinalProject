"""
Class: CS230--Section 1
Name: Ingrid Murphy
Description: (Give a brief description for Exercise name--See below)
I pledge that I have completed the programming assignment independently. 
I have not copied the code from a student or any source.
I have not given my code to any student. 
"""

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import streamlit as st
import pydeck as pdk


# Welcome Page
st.title('Crime Data in Boston,MA')
st.markdown("_By: Ingrid Murphy_")
st.write('Welcome to the Visualization of the Boston Crime Data! The sidebar to the left will be your guide.\n'
         '\n============================================================================================')
st.sidebar.title("Select a Visual:")
st.sidebar.markdown("_Choose the visual that you want to analyze._")


# read in data and exclude the 2 columns that are blank
def read_data():
    crime_data = pd.read_csv("FinalProject/bostoncrime2021_7000_sample.csv", usecols= ['INCIDENT_NUMBER','OFFENSE_CODE','OFFENSE_DESCRIPTION','DISTRICT','REPORTING_AREA',
                                                                'SHOOTING','OCCURRED_ON_DATE','YEAR','MONTH','DAY_OF_WEEK','HOUR','STREET','Lat','Long','Location']).set_index("INCIDENT_NUMBER")
    return crime_data

# rename data set for the purpose of making it easier to refer to
crime_data = read_data()


# Pass through each visual and shows the explanation text at the bottom of the page
def show_text(explanation):
    st.write("=============================================================================================\n"
             "\nExplanation:", explanation)
    pass


# color selections for visuals
colors = ['#ff9999','#66b3ff','#99ff99','#ffcc99']

# View Data by Day of the Week & Time with a Data Table
if st.sidebar.checkbox('Table: Crime Data based on Day & Time'):
    st.markdown("__Data Table on for the selected day and hour:__ \n"
                "\n-_Crimes Committed_\n"
                "\n-_Number of Times They Were Committed_\n")
    st.markdown("__Color Key:__\n"
                "\n_Darker_ = highest occurring crime\n"
                "\n_Lighter_ = lowest occurring crime\n")
    day_selection = st.sidebar.selectbox("Select a day of the week: ", crime_data['DAY_OF_WEEK'].unique())
    time_selection = st.sidebar.slider('Select an Hour of The Day [0 = 12 am / 23 = 11 pm]',0,23)


    def tableMaker(hour, day):
        table = (crime_data[(crime_data['DAY_OF_WEEK'] == day) & (crime_data['HOUR'] == hour)].groupby('OFFENSE_DESCRIPTION')
            ['OFFENSE_DESCRIPTION'].agg(['count']).style.set_properties(**{'border':'1.0px solid grey', 'color':'black'}).background_gradient('pink'))

        return table


    summary_table = tableMaker(time_selection,day_selection)
    if st.sidebar.button('Generate Summary Table'):
        st.header("Crime By Time & Day:")
        st.table(summary_table)
        table_explanation = """This chart allows users to search a specific date and time of day
        and be able to view which kind of offenses occurred and how many of each specific offense there were."""
        show_text(table_explanation)

# Loop / Functions for Displaying the Frequency of Each Crime
if st.sidebar.checkbox("Pie Chart: Compare Crimes"):
    crime_select = st.sidebar.multiselect("Select at least 2 Crimes: ",crime_data['OFFENSE_DESCRIPTION'].unique())


    def count_offenses(offenses,df):
        return [crime_data.loc[crime_data['OFFENSE_DESCRIPTION'].isin([offense])].shape[0] for offense in offenses]


    # Formatting the Pie Chart
    def pie_chart(counts, selected_offenses):
        plt.figure()
        plt.legend()
        explodes = [0 for i in range(len(counts))]
        max = counts.index(np.max(counts))
        explodes[max] = 0.10
        plt.pie(counts,explode=explodes,colors=colors,
                autopct="%1.1f%%")
        # format it as a hollow circle - this is a unique way of doing a Pie Chart & I am proud of this!
        plt.title(f"Frequency of the Select Offenses")
        centre_circle = plt.Circle((0,0),0.70,fc='white')
        fig = plt.gcf()
        fig.gca().add_artist(centre_circle)
        plt.legend(title = "Legend", labels = crime_select, loc = "lower left",fontsize = 6)

        
        return plt

    # calling the Pie Chart
    count1 = count_offenses(crime_select,crime_data)
    if st.sidebar.button('Generate Pie Chart'):
        st.pyplot(pie_chart(count1,crime_select))
        pie_explanation = """This pie chart allows users to select as many offenses
        as they wish. The selected offenses are then put into a pie chart where it gives
        the percentage of how many times those offenses happen compared to the others.
        This is helpful if one wishes to see which crime are the mosdt common in the Boston area. """
        show_text(pie_explanation)



# 3rd checkbox in sidebar - View Bar Charts of Data
# make a list of all the offenses and their total
offenses = [row['OFFENSE_DESCRIPTION'] for ind, row in crime_data.iterrows()]
unique_offense = []
for offense in offenses:
    if offense not in unique_offense:
        unique_offense.append(offense)
        unique_offense.sort()

if st.sidebar.checkbox("Bar Graph: Number of Times Each Crime was Reported"):
    selection_crime = st.sidebar.multiselect("Select at least two of the offenses: ", unique_offense)
    st.markdown("Number of Reports for the Selected Crimes:")

    if st.sidebar.button('Generate Bar Graph'):
        offense_dict = {}
        for offense in selection_crime:
            offense_dict[offense] = 0

        for key in offense_dict.keys():
            count = 0
            for offense in offenses:
                if key == offense:
                    count +=1
            offense_dict[key] = count

        if(len(offense_dict.keys()) > 1):
            plt.bar(offense_dict.keys(), offense_dict.values(), color = colors)
            plt.xticks(fontsize = 6)
            plt.xlabel("Offenses Chosen",fontsize =9)
            plt.ylabel("Total Number of Occurrences",fontsize=9)
            plt.title("Comparison of Total Number of Crime Occurrences")
            st.pyplot(plt)
            bar_explanation = """This bar chart feature allows users to select at least 
            two offenses and the bar chart will display each offense next to each other
            along with the actual number of times that offense occurred within the datasets 
            time frame. This is useful if the user wishes to see a comparison like the pie chart,
            but wishes to view the actual number of happenings."""
            show_text(bar_explanation)


# 4th checkbox - View Map

if st.sidebar.checkbox("Map: Crimes Reported in Boston"):
    st.header("Crimes in the Boston Area")

    def map(df):
        map_df = df.filter(['OFFENSE_DESCRIPTION','OCCURRED_ON_DATE','Lat','Long'])
        view_state = pdk.ViewState(latitude=42.360031,
                               longitude=-71.054749,
                               zoom=11)
        layer = pdk.Layer('ScatterplotLayer',
                      data=map_df,
                      get_position='[Long,Lat]',
                      get_radius = 50,
                      get_color = [220,20,100],
                      pickable=True)
        tool_tip = {'html': '<b>Offense Description:<b><br/>{OFFENSE_DESCRIPTION}<br/><b>Time of Report:<b><br/>{OCCURRED_ON_DATE}', 'style':{'backgroundColor':'lightpink','color':'black'}}
        map = pdk.Deck(map_style='mapbox://styles/mapbox/light-v9',
                   initial_view_state=view_state,
                   layers = [layer],
                   tooltip=tool_tip)

        return map

    if st.sidebar.button('Display the Map'):
        st.markdown(f"Map of Boston Crime.\n"
                    f"Zoom in or hover over a crime to find out more!\n"
                    f"\n*_Description of Offense_\n"
                    f"\n*_Date & Time of Offense_\n")
        st.pydeck_chart(map(crime_data))
        map_explanation = """This map feature allows users to browse at a map of the Boston area
        where all dots on the map represent a crime. The user can hover over that crime and 
        receive further data on what type of crime occurred and when it occurred. This
        is helpful for users because they can check on their living area and get data on 
        what kind of illegal activity they should look out for in their radius."""
        show_text(map_explanation)


# 5th CheckBox for references used in this code
if st.sidebar.checkbox("Sources"):
    st.header("SOURCES:")
    st.write("Below is the list of the sources I used to help with this project!")
    st.markdown(" \nhttps://pandas.pydata.org/Pandas_Cheat_Sheet.pdf \n"
                "\nhttps://pythonwife.com/plotly-with-streamlit/ \n"
                "\nhttps://pythonwife.com/matplotlib-with-streamlit/\n"
                "\nhttps://medium.com/@kvnamipara/a-better-visualisation-of-pie-charts-by-matplotlib-935b7667d77f\n"
                "\nhttps://codingfordata.com/8-simple-and-useful-streamlit-tricks-you-should-know/\n"
                "\nhttps://www.analyticsvidhya.com/blog/2021/06/style-your-pandas-dataframe-and-make-it-stunning/\n")
    source_explanation = """This sources tab contains all of the helpful sites I used in order to 
    complete this final project. I used several others for small tidbits, however, the sources 
     above are the ones that helped with a good amount of my code. """
    show_text(source_explanation)
    st.markdown("_THANK YOU!_")


