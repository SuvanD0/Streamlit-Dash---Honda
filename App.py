import pandas as pd
import streamlit as st
import streamlit.components.v1 as components
import numpy as np
import time
import plotly.express as px
import pydeck as pdk

st.set_page_config(layout="wide")
# set margins for left and right columns
left_margin = "10%"
right_margin = "10%"

@st.cache
def load_data():
    trip_summary_df = pd.read_csv("data/trip_summary.csv")
    df_vehicle = pd.read_csv("data/vehicle.csv")
    df_tripReq = pd.read_csv("data/trip_request.csv")
    route_df = pd.read_csv("data/route.csv")
    vehicle_match = pd.read_csv("data/vehicleMatch.csv")
    merged_df = pd.read_csv("data/Final_Data.csv")
    return trip_summary_df, df_vehicle, df_tripReq, route_df, vehicle_match, merged_df

trip_summary_df, df_vehicle, df_tripReq, route_df, vehicle_match, merged_df = load_data()
merged_df = merged_df.rename(columns={'carbon emissions grams per mile\xa0': 'carbon emissions grams per mile'})

# Define list of valid organization IDs
valid_org_ids = [96, 245, 221, 195, 45, 37, 2, 1, 117, 187]

# Prompt the user to enter an organization ID with a unique key
org_id = st.text_input('Enter Organization ID', key="org_id_input")

if org_id.strip() == '':
    st.write('Please enter an organization ID')
elif int(org_id) not in valid_org_ids:
    st.write('Invalid organization ID. Please enter a valid ID')
else:
    st.write(f'You entered the organization ID: {org_id}')

    # Wait for 2 seconds before displaying the information
    time.sleep(5)

    # Filter merged_df to show only data for the inputted organization ID
    merged_df_filtered = merged_df[merged_df['organization_id'] == int(org_id)]
    title = f'Welcome Organization {org_id}'
    style = """
        <style>
            h1, h3 {
                margin: 0;
                padding: 0;
            }
        </style>
        """

    st.markdown(f"<h1 style='text-align: center; color: white;'>{title}</h1>", unsafe_allow_html=True)
    st.markdown(f"<h3 style='text-align: center; color: white;'>Here is your current summary</h3>", unsafe_allow_html=True)
    st.markdown(style, unsafe_allow_html=True) # Apply the style to remove the gaps
    

    st.write('\n')
    st.write('\n')

     # this will contain all the information regarding vehicle emissions
    with st.container():
        st.markdown("<h4 style='text-align: center; color: white;'>Here is an overlook of all trips made by your organization</h4>", unsafe_allow_html=True)
        
        

        st.pydeck_chart(pdk.Deck(
        map_style='mapbox://styles/mapbox/streets-v12',
        initial_view_state=pdk.ViewState(
            latitude=merged_df_filtered['trip_end_lat'].mean(),
            longitude=merged_df_filtered['trip_end_lon'].mean(),
            zoom=11,
            pitch=50,
        ),
        layers=[
            pdk.Layer(
                'ScatterplotLayer',
                data=merged_df_filtered[['trip_end_lat', 'trip_end_lon']],
                get_position='[trip_end_lon, trip_end_lat]',
                get_color='[200, 30, 0, 160]',
                get_radius=100,
            ),
        ],
    ))

    # Set width ratios
    left_column_width = 2
    right_column_width = 1

    # Create columns
    left_column, right_column = st.columns((left_column_width, right_column_width))

    # left column will be distance traveled
    with left_column:
        st.write('\n')
        st.write('\n')
        st.markdown(f"<h5 style='text-align: center; color: white;'>Total Distance Travled by Cars per day</h5>", unsafe_allow_html=True)
        dist_data = merged_df_filtered.groupby(['weekday']).sum()['trip_distance_miles'].reset_index()
        weekday_order = {'Monday': 1, 'Tuesday': 2, 'Wednesday': 3, 'Thursday': 4, 'Friday': 5, 'Saturday': 6, 'Sunday': 7}
        dist_data['weekday_num'] = dist_data['weekday'].map(weekday_order)
        dist_data = dist_data.sort_values('weekday_num').reset_index(drop=True)
        dist_data['weekday'] = pd.Categorical(dist_data['weekday'], categories=['Monday','Tuesday','Wednesday','Thursday','Friday','Saturday','Sunday'], ordered=True)
        dist_data['trip_distance_km'] = dist_data['trip_distance_miles']*1.60934
        fig = px.bar(dist_data, x='weekday', y='trip_distance_km', labels={'trip_distance_km':'Distance Traveled (km)'})
        fig.update_layout(
            width=500,
            height=300,
        )
        st.plotly_chart(fig)


    # right column will be average trip data
    with right_column:
        st.write('\n')
        st.write('\n')
        st.write('\n')
        st.write('\n')
        st.markdown(f"<h5 style='text-align: center; color: white;'>Average Trip in Kilometers</h5>", unsafe_allow_html=True)
        st.markdown(
            """
        <style>
        [data-testid="stMetricValue"] {
            font-size: 200px;
        }
        </style>
        """,
            unsafe_allow_html=True,
        )

        # Convert miles to kilometers
        merged_df_filtered['trip_distance_km'] = merged_df_filtered['trip_distance_miles'] * 1.60934
        merged_df['trip_distance_km'] = merged_df['trip_distance_miles'] * 1.60934

        # Get the average distance traveled per trip for the given company
        company_avg_distance = merged_df_filtered['trip_distance_km'].mean()

        # Get the total average distance traveled per trip for all companies
        total_avg_distance = merged_df['trip_distance_km'].mean()

        # Calculate the difference between the two averages
        delta_distance = company_avg_distance - total_avg_distance

        # Display the metrics using st.metric
        metric_name = f"avg_distance_{org_id}"
        st.metric(label  = "" , value=f"{company_avg_distance:.2f} ", delta=f"{delta_distance:.2f} ")

        st.write('\n')

        with st.expander("See Value Explanations"):   
            st.write("Value explanations:")
            st.write("* **Average Trip**: The average distance traveled per trip, measured in kilometers.")
            st.write("* **Delta**: The difference between the average distance traveled per trip for the selected organization and the total average distance traveled per trip for all organizations, measured in kilometers.")



    st.write('\n')
    st.write('\n')
    st.write('\n')
     # Calculate the average and total carbon emissions per vehicle
    avg_carbon_emissions_per_trip = merged_df_filtered.groupby('vehicle id')['carbon emissions grams per mile'].mean()
    total_carbon_emissions = merged_df_filtered.groupby('vehicle id')['carbon emissions grams per mile'].sum()



    # Filter the DataFrame to include only vehicles with non-zero emissions
    merged_df_filtered = merged_df_filtered[merged_df_filtered['carbon emissions grams per mile'] > 0]

    # Calculate the average and total carbon emissions per vehicle
    avg_carbon_emissions_per_vehicle = merged_df_filtered.groupby('vehicle id')['carbon emissions grams per mile'].mean()
    total_carbon_emissions_per_vehicle = merged_df_filtered.groupby('vehicle id')['carbon emissions grams per mile'].sum()

    # Filter the DataFrames to include only vehicles that have emissions data
    vehicles_with_emissions = merged_df_filtered['vehicle id'].unique()
    avg_carbon_emissions_per_vehicle = avg_carbon_emissions_per_vehicle[avg_carbon_emissions_per_vehicle.index.isin(vehicles_with_emissions)]
    total_carbon_emissions_per_vehicle = total_carbon_emissions_per_vehicle[total_carbon_emissions_per_vehicle.index.isin(vehicles_with_emissions)]

    # Create a dropdown menu to select the chart type
    chart_type_selection = st.selectbox('Select Chart Type:', ['Average Emissions', 'Total Emissions'])

    if chart_type_selection == 'Average Emissions':
        # Create a bar chart for the average carbon emissions per vehicle
        fig = px.bar(avg_carbon_emissions_per_vehicle, x=avg_carbon_emissions_per_vehicle.index, y='carbon emissions grams per mile')
        fig.update_layout(xaxis_title='Vehicle ID', yaxis_title='Carbon Emissions (grams per mile)')
        st.plotly_chart(fig)

    else:
        # Create a bar chart for the total carbon emissions per vehicle
        fig = px.bar(total_carbon_emissions_per_vehicle, x=total_carbon_emissions_per_vehicle.index, y='carbon emissions grams per mile')
        fig.update_layout(xaxis_title='Vehicle ID', yaxis_title='Total Carbon Emissions (grams per mile)')
        st.plotly_chart(fig)

    st.write('\n')
    st.write('\n')
    st.write('\n')

    st.write('Now that we have a clear understanding of the impact that the current fleet is having on the environment, I\'d like to discuss potential solutions for reducing these emissions. One potential solution is transitioning to all-electric vehicles, which have numerous benefits, including lower emissions, reduced maintenance costs, and greater energy efficiency')

    # this will contain our prediction data and recommendations
    with st.container():
        
        left_column_width = 1
        right_column_width = 1

        # Create columns
        left_column, right_column = st.columns((left_column_width, right_column_width))

        with left_column:
            vehicle_ids = merged_df_filtered['Vehicle ID'].unique()
            vehicle_match_filtered = vehicle_match[vehicle_match['Vehicle ID'].isin(vehicle_ids)]

            st.write('\n\n')
            st.markdown(f"<h4 style='text-align: center; color: white;'>Here are the best matches for your vehicles</h4>", unsafe_allow_html=True)

            purchase_recommendations = []
            for index, row in vehicle_match_filtered.iterrows():
                vehicle_id = row['Vehicle ID']
                best_match = row['Best Match']
                recommendation = f"We recommend you replace vehicle number {vehicle_id} with {best_match}"
                is_selected = st.checkbox(recommendation)
                if is_selected:
                    purchase_recommendations.append(best_match)

        with right_column:
            if len(purchase_recommendations) > 0:
                st.write('\n\n')
                st.markdown(f"<h4 style='text-align: center; color: white;'>You have selected the following recommendations for purchase:</h4>", unsafe_allow_html=True)
                for recommendation in purchase_recommendations:
                    st.write(f"You want to purchase {recommendation}")
            else:
                st.write('')


    

   






