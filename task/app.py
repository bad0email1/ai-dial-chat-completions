import asyncio

from task.clients.client import DialClient
from task.clients.custom_client import CustomDialClient
from task.constants import DEFAULT_SYSTEM_PROMPT
from task.models.conversation import Conversation
from task.models.message import Message
from task.models.role import Role


async def start(stream: bool, custom: bool, debug: bool) -> None:
    # TODO:
    # 1.1. Create DialClient
    # (you can get available deployment_name via https://ai-proxy.lab.epam.com/openai/models
    #  you can import Postman collection to make a request, file in the project root `dial-basics.postman_collection.json`
    #  don't forget to add your API_KEY)
    # "gpt-4", "gpt-4o", "gpt-4.1-mini-2025-04-14", "gpt-4.1-nano-2025-04-14"
    # "gpt-5-nano-2025-08-07", "gpt-5-mini-2025-08-07"
    # "claude-sonnet-4@20250514", "claude-sonnet-4-5@20250929"
    # "gemini-2.0-flash-lite", "gemini-2.0-flash", "gemini-2.5-flash-lite", "gemini-2.5-flash", "gemini-2.5-pro"
    # "gemini-3-flash-preview"
    model = "gemini-2.5-flash-lite"
    if not custom:
        dial_client = DialClient(deployment_name=model, debug=debug)
    # 1.2. Create CustomDialClient
    else:
        dial_client = CustomDialClient(deployment_name=model, debug=debug)
    # 2. Create Conversation object
    history = Conversation()
    # 3. Get System prompt from console or use default -> constants.DEFAULT_SYSTEM_PROMPT and add to conversation
    #    messages.
    custom_prompt = input("Enter system prompt (press Enter for default): ")
    history.add_message(
        Message(Role.SYSTEM, custom_prompt if custom_prompt else DEFAULT_SYSTEM_PROMPT)
    )
    # 4. Use infinite cycle (while True) and get yser message from console
    while True:
        # 5. If user message is `exit` then stop the loop
        user_input = input("\nAsk (or exit): ")

        if user_input.lower() == "exit":
            break
        # 6. Add user message to conversation history (role 'user')
        history.add_message(Message(Role.USER, user_input))
        # 7. If `stream` param is true -> call DialClient#stream_completion()
        #    else -> call DialClient#get_completion()
        if stream:
            answer = await dial_client.stream_completion(history.get_messages())
        else:
            answer = dial_client.get_completion(history.get_messages())
        # 8. Add generated message to history
        history.add_message(answer)
    # 9. Test it with DialClient and CustomDialClient
    # 10. In CustomDialClient add print of whole request and response to see what you send and what you get in response


asyncio.run(start(True, False, True))
