from openai import OpenAI
from openai.types import Completion as CompletionMessage
from openai._types import NotGiven, NOT_GIVEN
from openai.types.chat import ChatCompletion, ChatCompletionChunk, ChatCompletionMessageParam, \
    ChatCompletionToolChoiceOptionParam, ChatCompletionToolParam, ChatCompletionMessageToolCall
from openai.types.chat.chat_completion_chunk import ChoiceDeltaToolCall, ChoiceDeltaFunctionCall,\
    Choice, ChoiceDelta, ChoiceDeltaToolCallFunction
from openai.types.chat.chat_completion import Choice as _ChatCompletionChoice, ChatCompletion as _ChatCompletion
from openai.types.chat.chat_completion_message import FunctionCall, ChatCompletionMessage
from openai.types.chat.chat_completion_message_tool_call import Function
from openai.types.completion_usage import CompletionUsage
from openai.resources.chat.completions import Completions
from openai import AzureOpenAI

import openai.types.chat.completion_create_params as completion_create_params

# import monkeypatch
from typing import List, Any, Generator, Union, Optional, Literal
from time import time, sleep
from json import dumps, loads

from core.model_runtime.errors.invoke import InvokeAuthorizationError

import re

class MockChatClass(object):
    @staticmethod
    def generate_function_call(
        functions: List[completion_create_params.Function] | NotGiven = NOT_GIVEN,
    ) -> Optional[FunctionCall]:
        if not functions or len(functions) == 0:
            return None
        function: completion_create_params.Function = functions[0]
        function_name = function['name']
        function_description = function['description']
        function_parameters = function['parameters']
        function_parameters_type = function_parameters['type']
        if function_parameters_type != 'object':
            return None
        function_parameters_properties = function_parameters['properties']
        function_parameters_required = function_parameters['required']
        parameters = {}
        for parameter_name, parameter in function_parameters_properties.items():
            if parameter_name not in function_parameters_required:
                continue
            parameter_type = parameter['type']
            if parameter_type == 'string':
                if 'enum' in parameter:
                    if len(parameter['enum']) == 0:
                        continue
                    parameters[parameter_name] = parameter['enum'][0]
                else:
                    parameters[parameter_name] = 'kawaii'
            elif parameter_type == 'integer':
                parameters[parameter_name] = 114514
            elif parameter_type == 'number':
                parameters[parameter_name] = 1919810.0
            elif parameter_type == 'boolean':
                parameters[parameter_name] = True

        return FunctionCall(name=function_name, arguments=dumps(parameters))
        
    @staticmethod
    def generate_tool_calls(
        tools: List[ChatCompletionToolParam] | NotGiven = NOT_GIVEN,
    ) -> Optional[List[ChatCompletionMessageToolCall]]:
        list_tool_calls = []
        if not tools or len(tools) == 0:
            return None
        tool: ChatCompletionToolParam = tools[0]

        if tools['type'] != 'function':
            return None
        
        function = tool['function']

        function_call = MockChatClass.generate_function_call(functions=[function])
        if function_call is None:
            return None
        
        list_tool_calls.append(ChatCompletionMessageToolCall(
            id='sakurajima-mai',
            function=Function(
                name=function_call.name,
                arguments=function_call.arguments,
            ),
            type='function'
        ))

        return list_tool_calls
    
    @staticmethod
    def mocked_openai_chat_create_sync(
        model: str,
        functions: List[completion_create_params.Function] | NotGiven = NOT_GIVEN,
        tools: List[ChatCompletionToolParam] | NotGiven = NOT_GIVEN,
    ) -> CompletionMessage:
        tool_calls = []
        function_call = MockChatClass.generate_function_call(functions=functions)
        if not function_call:
            tool_calls = MockChatClass.generate_tool_calls(tools=tools)

        sleep(1)
        return _ChatCompletion(
            id='cmpl-3QJQa5jXJ5Z5X',
            choices=[
                _ChatCompletionChoice(
                    finish_reason='content_filter',
                    index=0,
                    message=ChatCompletionMessage(
                        content='elaina',
                        role='assistant',
                        function_call=function_call,
                        tool_calls=tool_calls
                    )
                )
            ],
            created=int(time()),
            model=model,
            object='chat.completion',
            system_fingerprint='',
            usage=CompletionUsage(
                prompt_tokens=2,
                completion_tokens=1,
                total_tokens=3,
            )
        )
    
    @staticmethod
    def mocked_openai_chat_create_stream(
        model: str,
        functions: List[completion_create_params.Function] | NotGiven = NOT_GIVEN,
        tools: List[ChatCompletionToolParam] | NotGiven = NOT_GIVEN,
    ) -> Generator[ChatCompletionChunk, None, None]:
        tool_calls = []
        function_call = MockChatClass.generate_function_call(functions=functions)
        if not function_call:
            tool_calls = MockChatClass.generate_tool_calls(tools=tools)

        full_text = "Hello, world!\n\n```python\nprint('Hello, world!')\n```"
        for i in range(0, len(full_text) + 1):
            sleep(0.1)
            if i == len(full_text):
                yield ChatCompletionChunk(
                    id='cmpl-3QJQa5jXJ5Z5X',
                    choices=[
                        Choice(
                            delta=ChoiceDelta(
                                content='',
                                function_call=ChoiceDeltaFunctionCall(
                                    name=function_call.name,
                                    arguments=function_call.arguments,
                                ) if function_call else None,
                                role='assistant',
                                tool_calls=[
                                    ChoiceDeltaToolCall(
                                        index=0,
                                        id='misaka-mikoto',
                                        function=ChoiceDeltaToolCallFunction(
                                            name=tool_calls[0].function.name,
                                            arguments=tool_calls[0].function.arguments,
                                        ),
                                        type='function'
                                    )
                                ] if tool_calls and len(tool_calls) > 0 else None
                            ),
                            finish_reason='function_call',
                            index=0,
                        )
                    ],
                    created=int(time()),
                    model=model,
                    object='chat.completion.chunk',
                    system_fingerprint='',
                    usage=CompletionUsage(
                        prompt_tokens=2,
                        completion_tokens=17,
                        total_tokens=19,
                    ),
                )
            else:
                yield ChatCompletionChunk(
                    id='cmpl-3QJQa5jXJ5Z5X',
                    choices=[
                        Choice(
                            delta=ChoiceDelta(
                                content=full_text[i],
                                role='assistant',
                            ),
                            finish_reason='content_filter',
                            index=0,
                        )
                    ],
                    created=int(time()),
                    model=model,
                    object='chat.completion.chunk',
                    system_fingerprint='',
                )

    def chat_create(self: Completions, *,
        messages: List[ChatCompletionMessageParam],
        model: Union[str,Literal[
            "gpt-4-1106-preview", "gpt-4-vision-preview", "gpt-4", "gpt-4-0314", "gpt-4-0613",
            "gpt-4-32k", "gpt-4-32k-0314", "gpt-4-32k-0613",
            "gpt-3.5-turbo-1106", "gpt-3.5-turbo", "gpt-3.5-turbo-16k", "gpt-3.5-turbo-0301",
            "gpt-3.5-turbo-0613", "gpt-3.5-turbo-16k-0613"],
        ],
        functions: List[completion_create_params.Function] | NotGiven = NOT_GIVEN,
        response_format: completion_create_params.ResponseFormat | NotGiven = NOT_GIVEN,
        stream: Optional[Literal[False]] | NotGiven = NOT_GIVEN,
        tools: List[ChatCompletionToolParam] | NotGiven = NOT_GIVEN,
        **kwargs: Any,
    ):
        openai_models = [
            "gpt-4-1106-preview", "gpt-4-vision-preview", "gpt-4", "gpt-4-0314", "gpt-4-0613",
            "gpt-4-32k", "gpt-4-32k-0314", "gpt-4-32k-0613",
            "gpt-3.5-turbo-1106", "gpt-3.5-turbo", "gpt-3.5-turbo-16k", "gpt-3.5-turbo-0301",
            "gpt-3.5-turbo-0613", "gpt-3.5-turbo-16k-0613",
        ]
        azure_openai_models = [
            "gpt35", "gpt-4v", "gpt-35-turbo"
        ]
        if not re.match(r'^(https?):\/\/[^\s\/$.?#].[^\s]*$', self._client.base_url.__str__()):
            raise InvokeAuthorizationError('Invalid base url')
        if model in openai_models + azure_openai_models:
            if not re.match(r'sk-[a-zA-Z0-9]{24,}$', self._client.api_key) and type(self._client) == OpenAI:
                # sometime, provider use OpenAI compatible API will not have api key or have different api key format
                # so we only check if model is in openai_models
                raise InvokeAuthorizationError('Invalid api key')
            if len(self._client.api_key) < 18 and type(self._client) == AzureOpenAI:
                raise InvokeAuthorizationError('Invalid api key')
        if stream:
            return MockChatClass.mocked_openai_chat_create_stream(model=model, functions=functions, tools=tools)
        
        return MockChatClass.mocked_openai_chat_create_sync(model=model, functions=functions, tools=tools)