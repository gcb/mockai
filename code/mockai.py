from fastapi import FastAPI, Request, HTTPException
from fastapi_mock import MockUtilities
from dataclasses import dataclass
import os
import uvicorn

try:
    port = int(os.getenv('MOCKAI_PORT'))
except ValueError:
    port = 8080


app = FastAPI( title="dummy opensplop api server", version="0.1.0",)

if __name__ == "__main__":
    uvicorn.run(
        app=app,
        host="0.0.0.0",
        #host="127.0.0.1", # in docker, you must listen to the to-be-external-to-container-ip
        port=port
        #reload=True,
    )


# just create an instance of MockUtilities and pass FastAPI app as argument to it. It will add exception handlers to
# the app automatically.
MockUtilities(app, return_example_instead_of_500=True)

@dataclass
class ResponseModel():
    message: str


# TODO: use a data file, like https://github.com/polly3d/mockai does. maybe even the same format?
@app.get("/v1/responses", status_code=200)
async def mock(request: Request) -> ResponseModel:
    """
    Mocks the /v1/responses end point. For the purpose of this project, it should receive a single input, and reply a fixed fake string.
    This endpoint will be called with the following  client code:
        from openai import OpenAI
        from pydantic import BaseModel
        client = OpenAI()
        class ExamMetricData(BaseModel):
            metricName: str
            metricValueUnit: str
            metricValue: number
            metricReferenceValueMin: number
            metricReferenceValueMax: number
            metricMethodology: str
        class ExamData(BaseModel):
            examType: str
            date: str
            patientName: str
            requestinDoctorName: str
            metrics: list[ExamData]
        response = client.responses.parse(
            model="gpt-4o-2024-08-06",
            input=[
                {
                    "role": "user",
                    "content": [
                        {"type": "input_text", "text": "Extract all text from this image."},
                        {
                            "type": "input_image",
                            "image_base64": image_base64
                        }
                    ]
                }
            ],
            text_format=ExamData,
        )
        event = response.output_parsed
    This code should not try to understand or even parse the contents of the request’s input,
    just make sure if the input for the request is valid and have all the above expected keys.
    Then it must reply with a fixed string that mimics the original openai api response for a similar request,
    again, not parsing the contents, only the types, and replying with very boring sample data.
    """
    try:
        body = await request.json()
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid request payload")

    if not isinstance(body, dict):
        raise HTTPException(status_code=400, detail="Invalid request payload")

    if "model" not in body or "input" not in body:
        raise HTTPException(status_code=400, detail="Invalid request payload")

    inputs = body["input"]
    if not isinstance(inputs, list):
        raise HTTPException(status_code=400, detail="Invalid request payload")

    for item in inputs:
        if not isinstance(item, dict):
            raise HTTPException(status_code=400, detail="Invalid request payload")
        if "role" not in item or "content" not in item:
            raise HTTPException(status_code=400, detail="Invalid request payload")
        content = item["content"]
        if not isinstance(content, list):
            raise HTTPException(status_code=400, detail="Invalid request payload")
        for sub_item in content:
            if not isinstance(sub_item, dict):
                raise HTTPException(status_code=400, detail="Invalid request payload")
            if "type" not in sub_item:
                raise HTTPException(status_code=400, detail="Invalid request payload")
            if sub_item["type"] == "input_text":
                if "text" not in sub_item:
                    raise HTTPException(status_code=400, detail="Invalid request payload")
            elif sub_item["type"] == "input_image":
                if "image_base64" not in sub_item:
                    raise HTTPException(status_code=400, detail="Invalid request payload")
            else:
                raise HTTPException(status_code=400, detail="Invalid request payload")

    fixed_string = '{"examType": "sample_type", "date": "sample_date", "patientName": "sample_name", "requestinDoctorName": "sample_doctor", "metrics": [{"metricName": "sample_metric", "metricValueUnit": "sample_unit", "metricValue": 0.0, "metricReferenceValueMin": 0.0, "metricReferenceValueMax": 0.0, "metricMethodology": "sample_methodology", "examType": "sample_type", "date": "sample_date", "patientName": "sample_name", "requestinDoctorName": "sample_doctor", "metrics": []}]}'
    return ResponseModel(message=fixed_string)



