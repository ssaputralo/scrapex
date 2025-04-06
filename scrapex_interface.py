import streamlit as st
from scrapex_class import Scrapex
import pandas as pd
import os
import plotly.express as px

st.set_page_config(page_title="ScrapeX - AI-Powered Scraper", layout="wide")
st.image("ScrapeX Logo.png", width=150)
st.title("ScrapeX: AI-Powered Scraper")

st.markdown("""
    <style>
        /* Default button styling */
        .stButton > button {
            background-color: #007bff;
            color: white;
            border-radius: 8px;
            border: none;
            padding: 8px 16px;
        }
        .stButton > button:hover {
            background-color: #0056b3;
        }
        /* Download button styling */
        .stDownloadButton > button {
            background-color: #28a745 !important;
            color: white !important;
            border-radius: 8px;
            border: none;
            padding: 8px 16px;
        }
        .stDownloadButton > button:hover {
            background-color: #218838 !important;
        }
        /* Update button styling */
        #update-button-container button {
            background-color: #f1c40f;
            color: white;
            border-radius: 8px;
            border: none;
            padding: 8px 16px;
        }
        #update-button-container button:hover {
            background-color: #d4ac0d;
        }
    </style>
""", unsafe_allow_html=True)

scraper = Scrapex()

if "company_data" not in st.session_state:
    st.session_state.company_data = None
if "df_result" not in st.session_state:
    st.session_state.df_result = None
if "error_message" not in st.session_state:
    st.session_state.error_message = None
if "company_name" not in st.session_state:
    st.session_state.company_name = ""

def scrape_callback():
    company = st.session_state.input_company.strip()
    if not company:
        st.warning("Please enter a company name.")
        return

    with st.spinner("Scraping in progress... this may take a few minutes"):
        try:
            df_result, error_message = scraper.search_company_info(company)
            st.session_state.company_name = company
            st.session_state.df_result = df_result
            st.session_state.error_message = error_message

            if error_message:
                st.error(f"An error occurred: {error_message}")
            else:
                st.success(f"Scraping complete for '{company}'!")
        except Exception as e:
            st.error(f"Unexpected error: {e}")

def update_data_callback():
    if st.session_state.company_data is None:
        st.warning("No data to update. Please scrape a company first.")
        return

    try:
        scraper.company_data = st.session_state.company_data
        if scraper.save():
            st.success("Data updated and saved successfully!")
        else:
            st.error("Data was not saved. Please check the logs.")
    except Exception as e:
        st.error(f"Failed to update data: {e}")

def search_and_analyze():
    company = st.session_state.input_company.strip()
    if not company:
        st.warning("Please enter a company name.")
        return

    with st.spinner("Searching company details"):
        df_result, error_message = scraper.search_company_info(company)

        if error_message:
            st.error(f"{error_message}")
        else:
            st.success(f"Found details for '{company}'!")
            st.session_state.company_data = df_result

            with st.spinner("Analyzing lead quality..."):
                analysis_result, analysis_error = scraper.analyze_lead(df_result.to_dict())
                
                if analysis_error:
                    st.error(f"{analysis_error}")
                else:
                    df = st.session_state.company_data.copy()
                    for key, value in analysis_result.items():
                        df[key] = value
                    st.session_state.company_data = df

def score_lead_saved_data_callback():
    csv_file_path = os.path.join("results", "data.csv")
    if not os.path.exists(csv_file_path):
        st.warning("No saved data found. Please run scraping and update saved data first.")
        return
    try:
        lead_scores = []
        scoring_reasons = []

        for index, row in saved_df.iterrows():
            company_dict = row.to_dict()
            scoring = scraper.score_lead(company_dict)
            lead_scores.append(scoring.get("Real-Time Lead Score", "N/A"))
            scoring_reasons.append(scoring.get("Scoring Reason", ""))

        saved_df["Real-Time Lead Score"] = lead_scores
        saved_df["Scoring Reason"] = scoring_reasons

        saved_df.to_csv(csv_file_path, index=False)
        excel_file_path = os.path.join("results", "data.xlsx")
        saved_df.to_excel(excel_file_path, index=False)

        st.success("Real-Time Lead Scoring updated for saved data!")
    except Exception as e:
        st.error(f"Error updating saved data: {e}")

# Input field for company name.
st.text_input("Enter a company name:", key="input_company")
st.button("Analyze", on_click=search_and_analyze)

if st.session_state.company_data is not None:
    company_name = st.session_state.company_data.iloc[0].get("Company Name", "Data")
    st.subheader("Company Information")
    st.dataframe(st.session_state.company_data)

    csv = st.session_state.company_data.to_csv(index=False).encode()
    st.download_button(
        label="Download CSV",
        data=csv,
        file_name=f"{company_name}_data.csv",
        mime="text/csv"
    )
    
    st.markdown('<div id="update-button-container">', unsafe_allow_html=True)
    st.button("Update Data", on_click=update_data_callback)
    st.markdown('</div>', unsafe_allow_html=True)

# Optionally display saved data from data.csv.
st.markdown("### Content of Saved Data (data.csv)")
csv_file_path = os.path.join("results", "data.csv")
if os.path.exists(csv_file_path):
    saved_df = pd.read_csv(csv_file_path)
    st.dataframe(saved_df)
else:
    st.info("No saved data.csv file found in the 'results' folder.")
    
st.button("Update Score Lead", on_click=score_lead_saved_data_callback)
