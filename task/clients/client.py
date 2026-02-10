from aidial_client import Dial, AsyncDial

from task.clients.base import BaseClient
from task.constants import DIAL_ENDPOINT
from task.models.message import Message
from task.models.role import Role


class DialClient(BaseClient):

    def __init__(self, deployment_name: str, debug: bool = False):
        super().__init__(deployment_name)
        # TODO:
        # Documentation: https://pypi.org/project/aidial-client/ (here you can find how to create and use these clients)
        # 1. Create Dial client
        self._client = Dial(api_key=self._api_key, base_url=DIAL_ENDPOINT)
        # 2. Create AsyncDial client
        self._async_client = AsyncDial(api_key=self._api_key, base_url=DIAL_ENDPOINT)
        self._debug = debug

    def get_completion(self, messages: list[Message]) -> Message:
        # TODO:
        # 1. Create chat completions with client
        #    Hint: to unpack messages you can use the `to_dict()` method from Message object
        good_messages = [msg.to_dict() for msg in messages]
        if self._debug:
            print()
            print(self._deployment_name)
            print(good_messages)

        try:
            completion = self._client.chat.completions.create(
                deployment_name=self._deployment_name,
                stream=False,
                messages=good_messages,
            )
            # 2. Get content from response, print it and return message with assistant role and content
            # 3. If choices are not present then raise Exception("No choices in response found")
            if not completion.choices:
                raise Exception("No choices in response found")
            content = completion.choices[0].message.content
            print(content)
            if self._debug:
                print(
                    f"prompt_tokens={completion.usage.prompt_tokens}, completion_tokens={completion.usage.completion_tokens}"
                )
            return Message(Role.AI, content)

        except Exception as ex:
            raise Exception(f"Error processing response: {str(ex)}") from ex

    async def stream_completion(self, messages: list[Message]) -> Message:
        # TODO:
        # 1. Create chat completions with async client
        #    Hint: don't forget to add `stream=True` in call.
        good_messages = [msg.to_dict() for msg in messages]
        if self._debug:
            print()
            print(self._deployment_name)
            print(good_messages)

        try:
            completion = await self._async_client.chat.completions.create(
                deployment_name=self._deployment_name,
                stream=True,
                messages=good_messages,
            )
            # 2. Create array with `contents` name (here we will collect all content chunks)
            contents = []
            usage = None
            # 3. Make async loop from `chunks` (from 1st step)
            async for chunk in completion:
                # 4. Print content chunk and collect it contents array
                content = chunk.choices[0].delta.content
                if content is not None:
                    contents.append(content)
                    print(content, end="", flush=True)
                elif chunk.usage is not None:
                    usage = chunk.usage
            # 5. Print empty row `print()` (it will represent the end of streaming and in console we will print input from a new line)
            print()
            if self._debug and usage is not None:
                print(
                    f"prompt_tokens={usage.prompt_tokens}, completion_tokens={usage.completion_tokens}"
                )
            # 6. Return Message with assistant role and message collected content
            return Message(Role.AI, "".join(contents))

        except Exception as ex:
            raise Exception(f"Error processing response: {str(ex)}") from ex
