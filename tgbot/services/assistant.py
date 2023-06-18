import datetime
import logging

from infrastructure.function_services.functions.manage_calendar import (
    CALENDAR_ASSISTANT_PROMPT,
    call_function,
)
from infrastructure.openai_api.types import Conversation, FunctionCall


class ChatAssistant:
    MAX_STEPS = 5

    def __init__(self, message, state, openai, calendar_service, function_definitions):
        self.message = message
        self.state = state
        self.openai = openai
        self.calendar_service = calendar_service
        self.function_definitions = function_definitions
        self.service_messages = ""
        self.total_tokens = 0
        self.final_answer = None

    async def process_message(self):
        await self._send_initial_reply()
        conversation = await self._init_conversation()
        await self._process_conversation(conversation)
        await self._final_reply(conversation)

    async def _send_initial_reply(self):
        self.service_message = await self.message.reply(
            "Processing... Press /reset to reset conversation"
        )

    async def _init_conversation(self):
        state_data = await self.state.get_data()
        conversation_history = state_data.get("history", [])
        conversation = Conversation.from_raw(conversation_history)
        conversation.add_system_message(
            content=CALENDAR_ASSISTANT_PROMPT.format(today_time=datetime.datetime.now())
        )
        conversation.add_user_message(
            content=self.message.text, name=self.message.from_user.username
        )
        return conversation

    async def _process_conversation(self, conversation):
        self.final_answer = None
        for step in range(self.MAX_STEPS):
            try:
                if self.final_answer:
                    break
                await self._step_conversation(conversation, step)
            except Exception as e:
                await self.message.reply(f"Error: {e}")
                return

    async def _step_conversation(self, conversation, step):
        opanai_answer = await self._get_openai_answer(conversation)
        logging.info(f"conversation: {conversation}")
        self.total_tokens += opanai_answer.usage.total_tokens
        function_call: FunctionCall = opanai_answer.choices[0].message.function_call
        if function_call:
            await self._process_function_call(conversation, function_call, step)
        else:
            text = opanai_answer.choices[0].message.content
            conversation.add_assistant_message(text)
            self.final_answer = text

    async def _get_openai_answer(self, conversation):
        return await self.openai.request_chat_completion(
            messages=conversation.messages,
            user_id=self.message.from_user.id,
            model="gpt-3.5-turbo-0613",
            temperature=0.2,
            max_tokens=1000,
            functions=self.function_definitions,
        )

    async def _process_function_call(self, conversation, function_call, step):
        await self._add_service_message(
            f"\n{step + 1}. Function call: {function_call.name}"
        )
        output = call_function(self.calendar_service, function_call)
        conversation.add_function_output(
            function_call.arguments + f'\nOUTPUT: {output}',
            function_call.name)
        await self._add_service_message(f" ✅" + "\nPreparing answer...\n\n")
        text = f"Successfully called function {function_call.name}"
        return text

    async def _add_service_message(self, text):
        self.service_messages += text
        await self.service_message.edit_text(self.service_messages)

    async def _final_reply(self, conversation):
        final_text = self.final_answer or "No answer"
        final_text += (
            "\n\n"
            f"ℹ️Total tokens: {self.total_tokens}"
            "\n"
            "To reset conversation press /reset"
        )
        await self.state.update_data(history=conversation.to_raw())
        await self.message.reply(final_text)
