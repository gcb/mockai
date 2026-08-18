from fastapi import FastAPI, Request, HTTPException
from fastapi_mock import MockUtilities
from dataclasses import dataclass
from typing import List
import os
import json
import uvicorn
import pprint
import logging

# Configure the logger
logger = logging.getLogger('uvicorn.error')
logger.setLevel(logging.DEBUG)

try:
    port = int(os.getenv('MOCKAI_PORT'))
except ValueError:
    port = 8080

try:
    MOCK_MESSAGE = os.getenv('MOCKAI_MESSAGE')
except ValueError:
    MOCK_MESSAGE = 'hello world'

app = FastAPI( title="dummy opensplop api server", version="0.1.0",)

GLOBAL_ID_COUNT = 0; # used for request i count

# just create an instance of MockUtilities and pass FastAPI app as argument to it. It will add exception handlers to
# the app automatically.
#MockUtilities(app, return_example_instead_of_500=True)

@dataclass
class Message():
    role: str
    content: str
    #tool_calls: Optional[List[Any]] = None

@dataclass
class Choice():
    index: int
    message: Message
    finish_reason: str

@dataclass
class Usage():
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int

# this would be returned in case we use MockUtilities return instead of 500:
@dataclass
class ResponseModel():
    id: str
    object: str
    #created: int
    model: str
    choices: List[Choice]
    #usage: Usage

@app.post("/v1/chat/completions", status_code=200)
async def mockchat(request: Request) -> ResponseModel:
    return await mock(request)

# TODO: use a data file, like https://github.com/polly3d/mockai does. maybe even the same format?
@app.post("/v1/responses", status_code=200)
async def mock(request: Request) -> ResponseModel:
    try:
        body = await request.json()
    except Exception:
        logger.debug('not json')
        raise HTTPException(status_code=400, detail="Invalid request payload. not json")

    #logger.debug(json.dumps(body));
    if not isinstance(body, dict):
        logger.debug('not instance of dict')
        raise HTTPException(status_code=400, detail="Invalid request payload. not instance")

    if "model" not in body:
        logger.debug('no model')
        raise HTTPException(status_code=400, detail="Invalid request payload. no model")

    if "input" in body:
        inputs = body["input"] # responses
    elif "messages" in body:
        inputs = body["messages"] # responses
    else:
        logger.debug('no input|messages') # completions
        raise HTTPException(status_code=400, detail="Invalid request payload. no model")

    #logger.debug(pprint.pformat(inputs))
    if not isinstance(inputs, list):
        logger.debug('no input list')
        raise HTTPException(status_code=400, detail="Invalid request payload. no input")

    for item in inputs:
        if not isinstance(item, dict):
            logger.debug('item not instance of dict')
            raise HTTPException(status_code=400, detail="Invalid request payload. no item instance")
        if "role" not in item or "content" not in item:
            logger.debug('no role')
            raise HTTPException(status_code=400, detail="Invalid request payload. no role")
        content = item["content"]
        if not isinstance(content, list):
            logger.debug('no content list')
            raise HTTPException(status_code=400, detail="Invalid request payload. no content")
        for content_item in content:
            if not isinstance(content_item, dict):
                logger.debug('sub_item not dict')
                raise HTTPException(status_code=400, detail="Invalid request payload")
            if "type" not in content_item:
                logger.debug('no type in sub_item')
                raise HTTPException(status_code=400, detail="Invalid request payload")
            if content_item["type"] == "text":
                if "text" not in content_item:
                    logger.debug('no text in input_text sub_item')
                    raise HTTPException(status_code=400, detail="Invalid request payload")
            elif content_item["type"] == "image_url":
                if "image_url" not in content_item:
                    logger.debug('no image_url in input_image sub_item')
                    raise HTTPException(status_code=400, detail="Invalid request payload")
                #if "image_base64" not in sub_item:
                #    logger.debug('no image_base64 in input_image sub_item')
                #    logger.debug(sub_item)
                #    raise HTTPException(status_code=400, detail="Invalid request payload")
            else:
                logger.debug('unkown type ', content_item["type"])
                raise HTTPException(status_code=400, detail="Invalid request payload")

    msg = Message(role='assistant', content=MOCK_MESSAGE)
    choice = Choice(index=0, message=msg, finish_reason='stop')
    return ResponseModel(id='mock00001', object='chat.completions', model='Emily01', choices=[choice] )



if __name__ == "__main__":
    uvicorn.run(
        app=app,
        host="0.0.0.0",
        #host="127.0.0.1", # in docker, you must listen to the to-be-external-to-container-ip
        port=port,
        #reload=True,
        log_level="DEBUG"
    )

