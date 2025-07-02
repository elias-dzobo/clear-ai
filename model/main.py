
#external
import os
import json
import opik
from pydantic import BaseModel, Field
from typing import List
from groq import Groq
import instructor
from dotenv import load_dotenv
from opik import track


#internal
from schema.main import *

load_dotenv()  


groq_api_key = os.environ.get("GROQ_API_KEY")

if not groq_api_key:
    raise RuntimeError('Groq API Key not found')

opik.configure(
    api_key=os.environ.get("OPIK_API_KEY"),
    workspace=os.environ.get("OPIK_WORKSPACE"),
    use_local=False
)
    

@track
def analyze_skin_with_ai(image_urls: List[str], user_info: dict) -> AnalysisResult:
    prompt = f"""You are a board-certified dermatologist. Given multiple facial photos and this patient profile:
    - Name: {user_info['name']}
    - Age: {user_info['age']}
    - Skin Type: {user_info['skin_type']}
    - Main Concerns: {','.join(user_info['skin_condition'])}

    Perform the following and return exactly one JSON object matching the Pydantic schema for {AnalysisResult.model_json_schema}:

    1. **Executive Summary** (2–3 sentences):  
    - Brief, elegant overview of overall skin health and main issues.  
    - A concise “Skin Health Score” (0–100) summarizing global condition.

    2. **Detailed Skin Analysis**  
    For each attribute below, provide:
    - **Detail**: 2–3 sentences explaining what you see.  
    - **Score** (0–100): (“75 = adequate hydration but mild barrier dryness in cheeks”).  
    Attributes:
    - Hydration Levels  
    - Skin Texture  
    - Pigmentation Issues  
    - Acne & Inflammation  
    - Signs of Aging  
    - Sensitivity Indicators  

    3. **Tailored Skincare Routine**  
    Based directly on the analysis above, prescribe:
    - **Morning Routine** (4–5 steps)  
    - **Evening Routine** (4–5 steps)  
    For each step, include:
    - **Instruction**: clear action (e.g., “Apply a pea-sized vitamin C serum evenly to dry skin”).  
    - **Product Type**: specific product category based on user's skin type and concerns (e.g., “anti-oxidant serum,” “gentle chemical exfoliant”).  
    - Rationale: one brief clause linking it to the specific finding (e.g., “to boost collagen after low elasticity score”).

    4. **Output**  
    Serialize everything as JSON per the AnalysisResult schema (no extra keys, no narrative outside the JSON).

    Example of a full JSON key ordering and naming is provided in the Pydantic schema. Ensure each score accurately reflects severity/quality, each detail bridges back to the images and summary, and each routine step explicitly addresses the scored findings.


    Output the result as a JSON object conforming to the following Pydantic schema:
    ```json
    {AnalysisResult.model_json_schema}
    ```
    """

    content = [{"type": "text", "text": prompt}]
    for url in image_urls:
        content.append({"type": "image_url", "image_url": {"url": url, "detail": "auto"}})
    
    client = Groq(api_key=groq_api_key)
    client = instructor.from_groq(client)
    

    response = client.chat.completions.create(
        messages=[{"role": "user", "content": content}],
        model="meta-llama/llama-4-scout-17b-16e-instruct",
        temperature=0.5,
        max_tokens=1024,
        response_model=AnalysisResult
    )

    return response

    
@track
def reanalyze_skin_with_ai(
    image_urls: List[str],
    user_info: dict,
    previous_analysis: dict,
    previous_routine: dict
) -> AnalysisResult:
    """
    Re-analyze skin given new images, comparing against previous_analysis and previous_routine.
    Returns an updated AnalysisResult per the same schema, adjusting scores/details and
    prescribing any routine changes if needed (or retaining the prior routine if unchanged).
    """
    # Serialize previous analysis and routine for inclusion in prompt
    # We assume AnalysisResult has a .json() method producing valid JSON of the previous analysis.
    prev_analysis_json = previous_analysis
    # previous_routine is assumed to be a dict matching the routine portion of the schema.
    prev_routine_json = previous_routine

    prompt = f"""You are a board-certified dermatologist. You have previously performed a skin analysis and prescribed a skincare routine based on that analysis. Now the patient has followed the routine for some time. Given their new facial photos and the same patient profile, re-analyze their skin, compare with the previous findings, and adjust the skincare routine only if needed.

    Patient profile (same as before):
    - Name: {user_info['name']}
    - Age: {user_info['age']} 
    - Skin Type: {user_info['skin_type']}
    - Main Concerns: {','.join(user_info['skin_condition'])}

    Previous analysis (JSON):
    {prev_analysis_json}

    Previous skincare routine (JSON):
    {prev_routine_json}

    Instructions:
    1. **Compare & Contrast**:
    - For each attribute originally analyzed (Hydration Levels, Skin Texture, Pigmentation Issues, Acne & Inflammation, Signs of Aging, Sensitivity Indicators):
        - Review the new images and patient profile.
        - Refer to the previous score and detail for that attribute.
        - Provide a brief note (2–3 sentences) on whether the attribute has improved, worsened, or remained stable, with specifics visible in the new images compared to before.
        - Assign an updated **Score** (0–100) reflecting the current status (e.g., if hydration improved from 60 to 75, mention that).
    
    2. **Executive Summary Update** (2–3 sentences):
    - Summarize overall changes since last analysis.
    - Provide an updated “Skin Health Score” (0–100) summarizing the global condition now.

    3. **Routine Adjustment**:
    - Based on updated analysis:
        - If the patient’s skin has improved or certain concerns have shifted, decide whether to:
        - Keep the previous routine exactly as-is (if all attributes are stable or improved such that no change is needed).
        - Modify existing steps (e.g., change product types, concentrations, frequency).
        - Add or remove steps (e.g., introduce a new treatment if a concern emerged, pause an exfoliant if barrier shows fragility).
        - For each step in **Morning Routine** and **Evening Routine**:
        - If unchanged, you may restate the original step with a note “(unchanged from previous routine)”.
        - If changed, provide:
            - **Instruction**: clear action.
            - **Product Type**: updated category or concentration.
            - **Rationale**: one brief clause linking to the updated finding.
        - Keep the total steps to 4–5 for each routine; if unchanged, simply restate them.

    4. **Output**:
    - Serialize everything as a JSON object conforming exactly to the same Pydantic schema as in `analyze_skin_with_ai` (i.e., the `AnalysisResult` schema).
    - Do not include any extra narrative outside the JSON.
    - Ensure the key ordering and naming matches exactly the schema expectations.

    When constructing the prompt content for the Groq client, include the new images similarly to before.

    """

    content = [{"type": "text", "text": prompt}]
    for url in image_urls:
        content.append({"type": "image_url", "image_url": {"url": url, "detail": "auto"}})

    client = Groq(api_key=groq_api_key)
    client = instructor.from_groq(client)

    response = client.chat.completions.create(
        messages=[{"role": "user", "content": content}],
        model="meta-llama/llama-4-scout-17b-16e-instruct",
        temperature=0.5,
        max_tokens=1024,
        response_model=AnalysisResult
    )

    return response
