from entity_extraction.src.extractors.company_extractor import ChineseCompanyExtractor
from entity_extraction.src.preprocess.extraction_cleaner import TextCleaner
from entity_extraction.src.postprocess.llm_cleaner import LLMCompanyCleaner
from entity_extraction.src.config.suffix import COMPANY_SUFFIXES

MIN_COMPANY_NAME_LENGTH = 4
COMPANY_SUFFIX_TUPLE = tuple(COMPANY_SUFFIXES)

class CompanyExtractionPipeline:
    def __init__(
        self,
        cleaner: TextCleaner | None = None,
        extractor: ChineseCompanyExtractor | None = None,
        llm_cleaner: LLMCompanyCleaner | None = None,
    ) -> None:
        '''
        Initialize the company name extraction pipeline, which includes three steps: 
        text cleaning, company name extraction, and LLM cleaning
        '''
        self.cleaner = cleaner or TextCleaner()
        self.extractor = extractor or ChineseCompanyExtractor()
        self.llm_cleaner = llm_cleaner or LLMCompanyCleaner()

    def run(self, title: str = "", summary: str = "", content: str = "") -> list[str]:
        '''
        Run the entire sample extraction process — text merging → regular selection candidate 
        → rule filtering and deduplication → LLM secondary cleaning
        '''
        text = self.cleaner.merge(title=title, summary=summary, content=content)
        seen: set[str] = set()
        companies: list[str] = []
        
        for raw_candidate in self.extractor.extract(text):
            candidate = raw_candidate.strip()
            if candidate in seen or not self._is_normal_company(candidate):
                continue
            seen.add(candidate)
            companies.append(candidate)
        
        try:
            print(f"[pipeline] company fro LLM clean: {companies}")
            companies = self.llm_cleaner.clean(companies) 
        except Exception as e:
            print(f"[pipeline] LLM cleaner request fail: {e}")

        return companies
        

    def _is_normal_company(self, candidate: str) -> bool:
        '''
        Rule checks whether candidate strings match the format of "legal company name" 
        (length, non-pure numbers, no English letters, ending with a valid suffix)
        '''
        return (
            len(candidate) >= MIN_COMPANY_NAME_LENGTH
            and not candidate.isdigit()
            and all(not (char.isascii() and char.isalpha()) for char in candidate)
            and candidate.endswith(COMPANY_SUFFIX_TUPLE)
        )


