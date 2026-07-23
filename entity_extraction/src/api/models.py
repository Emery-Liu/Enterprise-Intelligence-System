from pydantic import BaseModel

class ExtractCompaniesRequest(BaseModel):
    '''request body'''
    title: str = ""
    summary: str = ""
    content: str = ""

class ExtractCompaniesResponse(BaseModel):
    '''response body'''
    companies: list[str]