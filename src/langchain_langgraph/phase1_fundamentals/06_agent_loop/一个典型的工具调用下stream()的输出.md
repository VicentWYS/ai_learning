================================================================================
LangChain 1.0 - Agent 执行循环
================================================================================

========================================
示例2：流式输出
========================================

问题：北京天气如何？然后计算 4 * 25

流式输出（实时显示）
----------------------------------------


************************************************
------------------------------------------------
dict
{'model': {'messages': [AIMessage(content='', additional_kwargs={'refusal': None}, response_metadata={'token_usage': {'completion_tokens': 19, 'prompt_tokens': 333, 'total_tokens': 352, 'completion_tokens_details': None, 'prompt_tokens_details': {'audio_tokens': None, 'cached_tokens': 0}}, 'model_provider': 'openai', 'model_name': 'qwen-plus', 'system_fingerprint': None, 'id': 'chatcmpl-eccef2a1-4400-99f6-8fe2-4c7e7f7eeabc', 'finish_reason': 'tool_calls', 'logprobs': None}, id='lc_run--019c052a-8ebe-7613-936c-003bdeedbdae-0', tool_calls=[{'name': 'get_weather', 'args': {'city': '北京'}, 'id': 'call_b36747b96c384119931f28', 'type': 'tool_call'}], invalid_tool_calls=[], usage_metadata={'input_tokens': 333, 'output_tokens': 19, 'total_tokens': 352, 'input_token_details': {'cache_read': 0}, 'output_token_details': {}})]}}
------------------------------------------------
dict_items
dict_items([('model', {'messages': [AIMessage(content='', additional_kwargs={'refusal': None}, response_metadata={'token_usage': {'completion_tokens': 19, 'prompt_tokens': 333, 'total_tokens': 352, 'completion_tokens_details': None, 'prompt_tokens_details': {'audio_tokens': None, 'cached_tokens': 0}}, 'model_provider': 'openai', 'model_name': 'qwen-plus', 'system_fingerprint': None, 'id': 'chatcmpl-eccef2a1-4400-99f6-8fe2-4c7e7f7eeabc', 'finish_reason': 'tool_calls', 'logprobs': None}, id='lc_run--019c052a-8ebe-7613-936c-003bdeedbdae-0', tool_calls=[{'name': 'get_weather', 'args': {'city': '北京'}, 'id': 'call_b36747b96c384119931f28', 'type': 'tool_call'}], invalid_tool_calls=[], usage_metadata={'input_tokens': 333, 'output_tokens': 19, 'total_tokens': 352, 'input_token_details': {'cache_read': 0}, 'output_token_details': {}})]})])
------------------------------------------------
************************************************

[调用工具]：[{'name': 'get_weather', 'args': {'city': '北京'}, 'id': 'call_b36747b96c384119931f28', 'type': 'tool_call'}]


************************************************
------------------------------------------------
dict
{'tools': {'messages': [ToolMessage(content='晴天，温度 15°C，空气质量良好', name='get_weather', id='2432a6f4-8596-4bb4-985e-d1935692b10e', tool_call_id='call_b36747b96c384119931f28')]}}
------------------------------------------------
dict_items
dict_items([('tools', {'messages': [ToolMessage(content='晴天，温度 15°C，空气质量良好', name='get_weather', id='2432a6f4-8596-4bb4-985e-d1935692b10e', tool_call_id='call_b36747b96c384119931f28')]})])
------------------------------------------------
************************************************

[回复]：晴天，温度 15°C，空气质量良好


************************************************
------------------------------------------------
dict
{'model': {'messages': [AIMessage(content='北京目前是晴天，温度为15°C，空气质量良好。', additional_kwargs={'refusal': None}, response_metadata={'token_usage': {'completion_tokens': 15, 'prompt_tokens': 377, 'total_tokens': 392, 'completion_tokens_details': None, 'prompt_tokens_details': {'audio_tokens': None, 'cached_tokens': 0}}, 'model_provider': 'openai', 'model_name': 'qwen-plus', 'system_fingerprint': None, 'id': 'chatcmpl-382a3dec-fbe6-9c22-a9d6-815e41d55db0', 'finish_reason': 'stop', 'logprobs': None}, id='lc_run--019c052a-930c-7793-ad25-f56858b87702-0', tool_calls=[], invalid_tool_calls=[], usage_metadata={'input_tokens': 377, 'output_tokens': 15, 'total_tokens': 392, 'input_token_details': {'cache_read': 0}, 'output_token_details': {}})]}}
------------------------------------------------
dict_items
dict_items([('model', {'messages': [AIMessage(content='北京目前是晴天，温度为15°C，空气质量良好。', additional_kwargs={'refusal': None}, response_metadata={'token_usage': {'completion_tokens': 15, 'prompt_tokens': 377, 'total_tokens': 392, 'completion_tokens_details': None, 'prompt_tokens_details': {'audio_tokens': None, 'cached_tokens': 0}}, 'model_provider': 'openai', 'model_name': 'qwen-plus', 'system_fingerprint': None, 'id': 'chatcmpl-382a3dec-fbe6-9c22-a9d6-815e41d55db0', 'finish_reason': 'stop', 'logprobs': None}, id='lc_run--019c052a-930c-7793-ad25-f56858b87702-0', tool_calls=[], invalid_tool_calls=[], usage_metadata={'input_tokens': 377, 'output_tokens': 15, 'total_tokens': 392, 'input_token_details': {'cache_read': 0}, 'output_token_details': {}})]})])
------------------------------------------------
************************************************

[回复]：北京目前是晴天，温度为15°C，空气质量良好。

================================================================================
完成！
================================================================================
