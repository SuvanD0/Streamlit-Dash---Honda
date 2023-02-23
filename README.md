
# Hackathon Project ReadMe

This project utilizes Python libraries such as pandas, streamlit, numpy, time, plotly, and pydeck to create an interactive dashboard that displays summary information for organizations regarding their trips.

## How to Run

To run this project, you will need to have Python 3 installed along with the required libraries. You can download the required libraries using pip by running the following command:


pip install pandas streamlit numpy plotly pydeck

Once you have installed the required libraries, you can run the project by executing the following command:

streamlit run app.py


This will launch the application in your default web browser.

## Functionality

The dashboard prompts the user to enter an organization ID, and then displays summary information for that organization based on data stored in CSV files. If an invalid organization ID is entered, an error message is displayed.

The summary information displayed includes:

- A map showing the locations where trips were taken by the organization
- A bar chart showing the total distance traveled per day of the week
- An average trip data in kilometers

The application is designed to be visually appealing and easy to use. The user can enter an organization ID and view summary information in just a few clicks. The dashboard provides an efficient and effective way for organizations to view and analyze their trip data.

