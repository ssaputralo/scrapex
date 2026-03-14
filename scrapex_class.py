import google.generativeai as genai
import os
import pandas as pd
import json

class Scrapex:
    def __init__(self):
        """Initialize Google Gemini API Key."""
        api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
        if not api_key:
            raise ValueError(
                "Missing Gemini API key. Set GEMINI_API_KEY (recommended) "
                "or GOOGLE_API_KEY in your environment."
            )

        genai.configure(api_key=api_key)
        self._preferred_models = [
            "gemini-2.0-flash",
            "gemini-1.5-flash-latest",
            "gemini-1.5-flash",
            "gemini-1.5-pro-latest"
        ]

    def _resolve_model_candidates(self):
        """
        Build model candidates from available API models that support generateContent.
        Returns preferred models first if they exist, then other compatible Gemini models.
        """
        available = []
        for model in genai.list_models():
            methods = getattr(model, "supported_generation_methods", []) or []
            if "generateContent" not in methods:
                continue

            model_name = getattr(model, "name", "")
            # API may return names like "models/gemini-1.5-flash".
            if model_name.startswith("models/"):
                model_name = model_name.split("/", 1)[1]

            if model_name.startswith("gemini"):
                available.append(model_name)

        if not available:
            return self._preferred_models

        prioritized = [name for name in self._preferred_models if name in available]
        others = [name for name in available if name not in prioritized]
        return prioritized + others

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
            model_candidates = self._resolve_model_candidates()
            last_error = None
            for model_name in model_candidates:
                try:
                    model = genai.GenerativeModel(model_name)
                    response = model.generate_content(prompt)
                    ai_text = response.text.strip()
                    parsed_data = self._extract_json(ai_text)

                    if parsed_data:
                        return pd.DataFrame([parsed_data]), None
                    return None, "Search Error: Failed to extract valid JSON."
                except Exception as model_error:
                    last_error = model_error
                    continue

            return None, (
                "Search Error: No compatible Gemini model was available. "
                f"Tried: {', '.join(model_candidates)}. "
                f"Last error: {last_error}"
            )
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
