from typing import List, Optional
from pydantic import BaseModel, Field

class SourceItem(BaseModel):
    link: Optional[str] = None
    content: Optional[str] = None

    @property
    def is_valid(self) -> bool:
        return bool(self.content and self.content.strip())


class CompanyInput(BaseModel):
    '''Request Body'''
    company: str
    web_data_list: List[SourceItem] = Field(default_factory=list)
    baike_data: Optional[SourceItem] = None
    yuqing_data_list: List[SourceItem] = Field(default_factory=list)
    patent_data_list: List[SourceItem] = Field(default_factory=list)
    project_data_list: List[SourceItem] = Field(default_factory=list)


class PathResult(BaseModel):
    path: List[str]
    reasoning_chain: List[str]
    score: float

class ClassificationResult(BaseModel):
    '''Response Body'''
    paths: List[PathResult]


# ---------------------------------------------------------------------------
# Structured Returns for LLM Layer-by-Layer Selection (for use with `hierarchical_reasoner`)
# Indicates the applicable child node selected by the LLM from its direct child nodes under a given parent node
# ---------------------------------------------------------------------------
class LayerSelection(BaseModel):
    parent_path: List[str]
    selected_children: List[str]
    reasoning: Optional[str] = None