import json

from entity_extraction.src.client.extraction_client import chat
from entity_extraction.src.core.extraction_prompt import PROMPT_TEMPLATE 

class LLMCompanyCleaner:
    def clean(self, companies: list[str]) -> list[str]:
        '''
        Call the company's internal LLM (OpenAI-compatible) to perform a secondary cleanup 
        on the list of candidate company names, and return the cleaned list of company names.
        '''
        if not companies:
            return []
        prompt = self._build_prompt(companies)
        response = chat(prompt)
        return self._parse_response(response)


    def _build_prompt(self, companies: list[str]) -> str:
        '''
        Construct a prompt for the LLM to process the cleansing request, including a 
        list of candidate company names and cleansing rules
        '''
        payload = {"companies": companies}
        input_json = json.dumps(payload, ensure_ascii=False, indent=2)
        return PROMPT_TEMPLATE.replace("{input_json}", input_json)

    
    def _parse_response(self, response: str) -> list[str]:
        response = response.strip()
        if response.startswith("```"):
            lines = response.splitlines()
            response = "\n".join(lines[1:-1]).strip()

        try:
            data = json.loads(response)
            companies = data.get("companies", [])

            if isinstance(companies, list):
                return [str(company).strip() for company in companies if str(company).strip()]

        except Exception:
            pass

        return []