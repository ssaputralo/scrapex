import streamlit as st
from scrapex_class import Scrapex
import pandas as pd
import os

# Set page configuration, display logo and title
st.set_page_config(page_title="ScrapeX - AI-Powered Scraper", layout="wide")
st.image("ScrapeX Logo.png", width=150)
st.title("ScrapeX: AI-Powered Scraper")

# Inject custom CSS for button styling
st.markdown("""
    <style>
        /* Default button styling (if any st.button is not overridden) */
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
        /* Download button styling: target st.download_button wrapper */
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
        /* Update button styling: wrap the update button in a container with an ID */
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

# Initialize session state variables to avoid key errors
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
                    # Integrate the analysis result into the company data DataFrame.
                    df = st.session_state.company_data.copy()
                    # For each key from the analysis, add a new column with that value.
                    for key, value in analysis_result.items():
                        df[key] = value
                    st.session_state.company_data = df

# Main input and action buttons
st.text_input("Enter a company name:", key="input_company")
st.button("Analyze", on_click=search_and_analyze)

if st.session_state.company_data is not None:
    company_name = st.session_state.company_data.iloc[0]["Company Name"]
    st.subheader("Company Information")
    st.dataframe(st.session_state.company_data)

    # Convert DataFrame to CSV bytes
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
    
    st.subheader("Company Financial Data")
    # code for displaying financial data from yahoo finance
    st.subheader("Company Recent News")
    # code for displaying recent news from Yahoo Finance
    

st.markdown("### Content of Saved Data (data.csv)")
csv_file_path = os.path.join("results", "data.csv")
if os.path.exists(csv_file_path):
    saved_df = pd.read_csv(csv_file_path)
    st.dataframe(saved_df)
else:
    st.info("No saved data.csv file found in the 'results' folder.")
