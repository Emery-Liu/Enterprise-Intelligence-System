import re


_STOCK_CODE_RE = re.compile(r"[（(]\s*(?:\d{6}|[A-Z]{1,5}|\d{6}\.[A-Z]{2})\s*[）)]")
_SPACE_RE = re.compile(r"\s+")


class TextCleaner:
    def clean_field(self, value: str | None) -> str:
        '''
        Clean a single text field, remove stock symbols and consecutive spaces, and return the cleaned string
        '''
        if not value:
            return ""
        text = str(value).strip()
        text = _STOCK_CODE_RE.sub("", text)
        text = _SPACE_RE.sub(" ", text)
        return text.strip()

    def merge(self, title: str, summary: str, content: str) -> str:
        '''
        After cleaning the three fields separately, concatenate them in the order of content → summary → title 
        (skipping empty fields), and join them into a single text string using line breaks.
        '''
        fields = [self.clean_field(content), self.clean_field(summary), self.clean_field(title)]
        return "\n".join(field for field in fields if field)
