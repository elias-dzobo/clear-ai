""" API Endpoint """

#internal 
from model.main import analyze_skin_with_ai, reanalyze_skin_with_ai
from schema.main import AnalysisResult
from schema.api_schema import Request, ReanalysisRequest

#external 
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

app = FastAPI(
    title="Clear AI Endpoint"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Allows all origins
    allow_credentials=True,
    allow_methods=["*"], # Allows all methods (GET, POST, etc.)
    allow_headers=["*"],
)

@app.get('/health')
async def health_check():
    return JSONResponse(content={"status": "ok"}, status_code=200)


@app.post('/analyze', response_model=AnalysisResult)
async def get_ai_analysis(patient: Request):
    user_images = patient.image_urls
    user_info = patient.user_info.dict()

    try:
        response = analyze_skin_with_ai(user_images, user_info).dict()

        return JSONResponse(content = response, status_code=200)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f'Encountered error {e} when analysing user skin data')
    

@app.post('/reanalyze', response_model=AnalysisResult)
async def reanalyze_skin(patient: ReanalysisRequest):
    from pprint import pprint
    pprint(patient)
    user_images = patient.image_urls
    user_info = patient.user_info.dict()
    previous_analysis = patient.previous_analysis.dict()["skin_analysis"]
    previous_routine = patient.previous_analysis.dict()["skincare_routine"]

    try:
        response = reanalyze_skin_with_ai(user_images, user_info, previous_analysis, previous_routine).dict()

        return JSONResponse(content = response, status_code=200)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f'Encountered error {e} when re-analysing user skin data')