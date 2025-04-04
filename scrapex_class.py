import google.generativeai as genai
import os
import pandas as pd
import json
import re  # For cleaning AI responses

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
            # Find the first occurrence of "{" and the last occurrence of "}"
            start = text.find('{')
            end = text.rfind('}') + 1  # Include the closing brace.
            if start != -1 and end != -1:
                json_str = text[start:end]
                # Optionally, perform additional cleaning here if needed.
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

        Provide the result in a structured JSON format like:
        {{
            "Company Name": "Example Corp",
            "Website": "https://example.com",
            "Email": "contact@example.com",
            "LinkedIn": "https://linkedin.com/company/example"
        }}
        """

        try:
            model = genai.GenerativeModel("gemini-1.5-flash")  # ✅ Ensure correct model name
            response = model.generate_content(prompt)
            ai_text = response.text.strip()  # Extract and clean response

            parsed_data = self._extract_json(ai_text)  # Try to extract JSON

            if parsed_data:
                return pd.DataFrame([parsed_data]), None  # Return tuple: (result, None)
            else:
                return None, "Search Error: Failed to extract valid JSON."

        except Exception as e:
            return None, f"Search Error: {str(e)}"

    def analyze_lead(self, company_data):
        """
        Uses Gemini AI to analyze the company's lead quality.
        
        Returns:
            tuple: (analysis dictionary or None, error message or None)
        """
        prompt = f"""
        Based on the following company data:
        {json.dumps(company_data, indent=2)}

        Rate the company's potential as a business lead.
        Provide insights in a structured JSON format like:
        {{
            "Lead Score": "High",
            "Reasoning": "Strong online presence and multiple contact options."
        }}
        """

        try:
            model = genai.GenerativeModel("gemini-1.5-flash")  # ✅ Ensure correct model name
            response = model.generate_content(prompt)
            ai_text = response.text.strip()  # Extract and clean response

            parsed_analysis = self._extract_json(ai_text)  # Try to extract JSON

            if parsed_analysis:
                return parsed_analysis, None  # Return tuple: (result, None)
            else:
                return None, "Analysis Error: Failed to extract valid JSON."

        except Exception as e:
            return None, f"Analysis Error: {str(e)}"
