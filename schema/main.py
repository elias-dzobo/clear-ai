""" A schema for our model result """

#external 
from pydantic import BaseModel, Field
from typing import List

class Hydration(BaseModel):
    detail: str = Field(..., description="Detailed analysis of hydration levels.")
    score: int = Field(..., description="Score out of 100 of users hydration")

class SkinTexture(BaseModel):
    detail: str = Field(..., description="Detailed analysis of skin texture")
    score: int = Field(..., description="Score out of 100 of users skin texture")

class Pigmentation(BaseModel):
    detail: str = Field(..., description="Detailed analysis of pigmentation issues")
    score: int = Field(..., description="Score out of 100 of users pigmentation issues")

class Acne(BaseModel):
    detail: str = Field(..., description="Detailed analysis of acne and inflammation")
    score: int = Field(..., description="Score out of 100 of acne and inflammation")

class Aging(BaseModel):
    detail: str = Field(..., description="Detailed analysis of signs of aging")
    score: int = Field(..., description="Score out of 100 of signs of aging")

class Sensitivity(BaseModel):
    detail: str = Field(..., description="Detailed analysis of sensitivity indicators")
    score: int = Field(..., description="Score out of 100 of users hydration")

class SkinAnalysis(BaseModel):
    summary: str = Field(..., description="Summary of the users skin analysis")
    skin_score: int = Field(..., description="A score of how good the users skin is")
    hydration_levels: Hydration
    skin_texture: SkinTexture
    pigmentation_issues: Pigmentation
    acne_inflammation: Acne
    signs_of_aging: Aging
    sensitivity_indicators: Sensitivity

class RoutineStep(BaseModel):
    step: str = Field(..., description="An instructional step in patients routine. example; gently apply a cleanser evenly over face and wait for 2 minutes.")
    product_type: str = Field(..., description="Recommended product type for this step.")

class SkincareRoutine(BaseModel):
    morning_routine: List[RoutineStep] = Field(..., description="Personalized morning skincare routine.")
    evening_routine: List[RoutineStep] = Field(..., description="Personalized evening skincare routine.")

class AnalysisResult(BaseModel):
    skin_analysis: SkinAnalysis = Field(..., description="Detailed analysis of the patient's skin.")
    skincare_routine: SkincareRoutine = Field(..., description="Personalized skincare routine.")