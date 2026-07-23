from pydantic import BaseModel


class EnterpriseRelevanceRequest(BaseModel):
    '''request body'''
    enterprise_name: str
    title: str = ""
    summary: str = ""
    content: str = ""


class EnterpriseRelevanceResponse(BaseModel):
    '''response body'''
    related: bool