""" A schema for our API """

#internal 
from schema.main import AnalysisResult

#external 
from pydantic import BaseModel, Field
from typing import List

class UserInfo(BaseModel):
    name: str
    age: int 
    skin_type: str
    skin_condition: List[str]

class Request(BaseModel):
    image_urls: List[str]
    user_info: UserInfo

class ReanalysisRequest(BaseModel):
    image_urls: List[str]
    user_info: UserInfo
    previous_analysis: AnalysisResult 


    