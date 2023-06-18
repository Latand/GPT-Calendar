import datetime
import logging

from aiogram import types, Router, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext

from infrastructure.function_services.functions.manage_calendar import (
    CALENDAR_ASSISTANT_PROMPT,
    call_function,
)
from infrastructure.openai_api.api import OpenAIAPIClient
from infrastructure.openai_api.types import Conversation, FunctionCall
from tgbot.filters.admin import AdminFilter

calendar_router = Router()
calendar_router.message.filter(AdminFilter())

MAX_STEPS = 5


@calendar_router.message(Command("reset"))
async def reset(message: types.Message, state: FSMContext):
    await state.clear()
    await message.reply("Conversation was reset")


@calendar_router.message(F.text)
async def any_message(
    message: types.Message,
    state: FSMContext,
    openai: OpenAIAPIClient,
    calendar,
    function_definitions,
):
    service_message = await message.reply(
        "Processing... Press /reset to reset conversation"
    )

    state_data = await state.get_data()
    conversation_history = state_data.get("history", [])
    conversation = Conversation.from_raw(conversation_history)

    if not conversation.messages:
        conversation.add_system_message(
            content=CALENDAR_ASSISTANT_PROMPT.format(today_time=datetime.datetime.now())
        )

    conversation.add_user_message(content=message.text, name=message.from_user.username)

    service_messages = ""
    text = ""
    total_tokens = 0
    for step in range(MAX_STEPS):
        logging.info(f"{conversation.messages=}")
        opanai_answer = await openai.request_chat_completion(
            messages=conversation.messages,
            user_id=message.from_user.id,
            model="gpt-3.5-turbo-0613",
            temperature=0.2,
            max_tokens=1000,
            functions=function_definitions,
        )
        total_tokens += opanai_answer.usage.total_tokens
        function_call: FunctionCall = opanai_answer.choices[0].message.function_call
        if function_call:
            service_messages += f"{step + 1}. Function call: {function_call.name}\n"
            await service_message.edit_text(service_messages)
            try:
                output = call_function(calendar, function_call)
            except Exception as e:
                await message.reply(f"Error: {e}")
                return
            conversation.add_function_output(output, function_call.name)
            text = f"Successfully called function {function_call.name}"
        else:
            text = opanai_answer.choices[0].message.content
            conversation.add_assistant_message(text)
            break
    if not text:
        text = "No answer"

    text += (
        "\n\n" f"ℹ️Total tokens: {total_tokens}" "\n" "To reset conversation press /reset"
    )
    await state.update_data(history=conversation.to_raw())
    await message.reply(text)
