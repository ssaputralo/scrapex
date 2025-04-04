import streamlit as st
from scrapex_class import Scrapex

st.set_page_config(page_title="ScrapeX", layout="wide")
st.title("🚀 ScrapeX - Scraper with AI-Powered")

scraper = Scrapex()

if "company_data" not in st.session_state:
    st.session_state.company_data = None

def search_and_analyze():
    company = st.session_state.input_company.strip()
    if not company:
        st.warning("Please enter a company name.")
        return

    with st.spinner("Searching company details ⏳"):
        df_result, error_message = scraper.search_company_info(company)

        if error_message:
            st.error(f"⚠️ {error_message}")
        else:
            st.success(f"✅ Found details for '{company}'!")
            st.session_state.company_data = df_result

            with st.spinner("Analyzing lead quality... 🤖"):
                ai_analysis = scraper.analyze_lead(df_result.to_dict())
                st.subheader("📊 Lead Analysis")
                st.write(ai_analysis)

st.text_input("Enter a company name:", key="input_company")
st.button("🔍 Analyze", on_click=search_and_analyze)

if st.session_state.company_data is not None:
    st.subheader("📄 Company Info")
    st.dataframe(st.session_state.company_data)
