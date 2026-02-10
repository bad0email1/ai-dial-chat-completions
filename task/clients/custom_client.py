import json
import aiohttp
import requests

from task.constants import DIAL_ENDPOINT, API_KEY
from task.models.message import Message
from task.models.role import Role


class CustomDialClient:
    _endpoint: str
    _api_key: str

    def __init__(self, deployment_name: str, debug: bool = False):
        super().__init__()
        self._endpoint = (
            DIAL_ENDPOINT + f"/openai/deployments/{deployment_name}/chat/completions"
        )
        self._debug = debug

    def get_completion(self, messages: list[Message]) -> Message:
        # TODO:
        # Take a look at README.md of how the request and regular response are looks like!
        # 1. Create headers dict with api-key and Content-Type
        headers_dict = {"Api-Key": API_KEY, "Content-Type": "application/json"}
        # 2. Create request_data dictionary with:
        #   - "messages": convert messages list to dict format using msg.to_dict() for each message
        request_data = {
            "messages": [msg.to_dict() for msg in messages],
            "stream": False,
        }
        # 3. Make POST request using requests.post() with:
        #   - URL: self._endpoint
        #   - headers: headers from step 1
        #   - json: request_data from step 2
        if self._debug:
            print(request_data)
        response = requests.post(
            url=self._endpoint, headers=headers_dict, json=request_data, timeout=60
        )
        # 4. Get content from response, print it and return message with assistant role and content
        if response.status_code == 200:
            data = response.json()
            if not "choices" in data:
                raise Exception("No choices in response found")
            content = data["choices"][0]["message"]["content"]
            print(content)
            if self._debug:
                usage = data["usage"]
                print(
                    f'prompt_tokens={usage["prompt_tokens"]}, completion_tokens={usage["completion_tokens"]}'
                )
            return Message(Role.AI, content)

        # 5. If status code != 200 then raise Exception with format: f"HTTP {response.status_code}: {response.text}"
        raise Exception(f"HTTP {response.status_code}: {response.text}")

    async def stream_completion(self, messages: list[Message]) -> Message:
        # TODO:
        # Take a look at README.md of how the request and streamed response chunks are looks like!
        # 1. Create headers dict with api-key and Content-Type
        headers_dict = {"Api-Key": API_KEY, "Content-Type": "application/json"}
        # 2. Create request_data dictionary with:
        #    - "stream": True  (enable streaming)
        #    - "messages": convert messages list to dict format using msg.to_dict() for each message
        request_data = {
            "messages": [msg.to_dict() for msg in messages],
            "stream": True,
        }
        # 3. Create empty list called 'contents' to store content snippets
        contents = []
        # 4. Create aiohttp.ClientSession() using 'async with' context manager
        async with aiohttp.ClientSession() as session:
            # 5. Inside session, make POST request using session.post() with:
            #    - URL: self._endpoint
            #    - json: request_data from step 2
            #    - headers: headers from step 1
            #    - Use 'async with' context manager for response
            if self._debug:
                print(request_data)
            async with session.post(
                url=self._endpoint, headers=headers_dict, json=request_data
            ) as response:
                # 6. Get content from chunks (don't forget that chunk start with `data: `, final chunk is `data: [DONE]`), print
                #    chunks, collect them and return as assistant message
                if response.status == 200:
                    usage = None
                    async for item in response.content:
                        line = item.decode("utf-8").strip()
                        if not line:
                            continue
                        if line == "data: [DONE]":
                            break

                        data = json.loads(line[6:])  # Remove "data: " prefix
                        if self._debug:
                            print()
                            print(data)

                        if not "choices" in data:
                            raise Exception("No choices in response found")

                        delta = data["choices"][0]["delta"]
                        if "content" in delta:
                            content = delta["content"]
                            contents.append(content)
                            print(content, end="", flush=True)
                        elif "usage" in data:
                            usage = data["usage"]

                    print()
                    if self._debug and usage is not None:
                        print(
                            f'prompt_tokens={usage["prompt_tokens"]}, completion_tokens={usage["completion_tokens"]}'
                        )

                    return Message(Role.AI, "".join(contents))

                raise Exception(f"HTTP {response.status_code}: {response.text}")
