import google.generativeai as genai
import os
import pandas as pd
import json

class Scrapex:
    def __init__(self):
        """Initialize Google Gemini API Key."""
        genai.configure(api_key="AIzaSyDl-XgHR91v7Q_8o5DwqmKemRqDWiZDJX8")  # 🔹 Replace with your actual API key

    def _extract_json(self, text):
        """
        Extract JSON from AI response.
        This method locates the substring between the first "{" and the last "}"
        so that any extraneous text outside the JSON block is removed.
        """
        try:
            start = text.find('{')
            end = text.rfind('}') + 1  # Include the closing brace.
            if start != -1 and end != -1:
                json_str = text[start:end]
                return json.loads(json_str)
        except json.JSONDecodeError as e:
            print(f"JSON decode error: {e}")
        return None

    def search_company_info(self, company_name):
        """
        Uses Gemini AI to find company details like email, LinkedIn, website, etc.
        
        Returns:
            tuple: (pd.DataFrame with company info or None, error message or None)
        """
        prompt = f"""
        Given the company name '{company_name}', find its:
        - Official company name
        - Official website
        - Contact email
        - LinkedIn profile URL
        - Headquarters location

        Provide the result in a structured JSON format like:
        {{
            "Company Name": "Example Corp",
            "Website": "https://example.com",
            "Email": "contact@example.com",
            "LinkedIn": "https://linkedin.com/company/example",
            "Headquarters": "123 Example St, City, Country",
            "Yahoo Finance": "https://finance.yahoo.com/quote/EXAMPLE",
            "Company Description": "Example Corp is a leading company in..."
        }}
        """

        try:
            model = genai.GenerativeModel("gemini-1.5-flash")
            response = model.generate_content(prompt)
            ai_text = response.text.strip()
            parsed_data = self._extract_json(ai_text)
            
            if parsed_data:
                return pd.DataFrame([parsed_data]), None
            else:
                return None, "Search Error: Failed to extract valid JSON."
        except Exception as e:
            return None, f"Search Error: {str(e)}"

    def analyze_lead(self, company_data):
        """
        Performs real-time lead scoring and prioritization using simple heuristics.
        (Fungsi ini menggunakan pendekatan heuristik dan mengembalikan "Lead Score" dan "Scoring Reason".)
        
        Parameters:
            company_data (dict): Company details as a dictionary.
            
        Returns:
            dict: A dictionary containing "Lead Score" and "Scoring Reason".
        """
        score = 0
        reasons = []
        
        email = company_data.get("Email", "")
        if email and "@" in email:
            score += 1
            reasons.append("Valid Email provided")
        else:
            reasons.append("Missing or invalid Email")
        
        website = company_data.get("Website", "")
        if website and website.startswith("http"):
            score += 1
            reasons.append("Valid Website provided")
        else:
            reasons.append("Missing or invalid Website")
        
        linkedin = company_data.get("LinkedIn", "")
        if linkedin and "linkedin" in linkedin.lower():
            score += 1
            reasons.append("LinkedIn profile provided")
        else:
            reasons.append("Missing LinkedIn profile")
        
        if score >= 3:
            lead_score = "High"
        elif score == 2:
            lead_score = "Medium"
        else:
            lead_score = "Low"
        
        return {"Lead Score": lead_score, "Scoring Reason": "; ".join(reasons)}

    def save(self, folder='results'):
        """
        Saves the scraped company data into CSV and Excel formats.
        Expects the instance to have a 'company_data' attribute set externally.
        """
        try:
            os.makedirs(folder, exist_ok=True)
            csv_path = os.path.join(folder, 'data.csv')

            if not hasattr(self, 'company_data') or self.company_data is None:
                print("Error in save(): 'company_data' attribute is not set.")
                return False

            if os.path.exists(csv_path):
                try:
                    existing_data = pd.read_csv(csv_path)
                except Exception as read_err:
                    print("Error reading existing CSV file:", read_err)
                    existing_data = None

                if existing_data is not None and not existing_data.empty:
                    new_data = pd.concat([existing_data, self.company_data], ignore_index=True)
                else:
                    new_data = self.company_data.copy()
                new_data.to_csv(csv_path, index=False)
                print(f"Data successfully updated in {folder}/")
            else:
                self.company_data.to_csv(csv_path, index=False)
                print(f"Data saved for the first time in {folder}/")
            return True
        except Exception as e:
            print("Failed to save data:", e)
            return False
