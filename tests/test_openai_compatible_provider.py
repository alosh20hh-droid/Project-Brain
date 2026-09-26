import asyncio,pytest
from project_brain.model import OpenAICompatibleProvider,ModelMessage,ModelProviderError

async def test_transport(payload):
 assert payload["model"]=="brain-model"
 return {"choices":[{"message":{"content":"{\"task_id\":\"t\"}","tool_calls":[{"id":"c1","function":{"name":"search","arguments":"{\"q\":\"x\"}"}}]}}],"usage":{"total_tokens":12}}

def test_compatible_provider_normalizes_response():
 out=asyncio.run(OpenAICompatibleProvider(test_transport,"brain-model").complete([ModelMessage(role="user",content="go")]))
 assert out.tool_calls[0].name=="search";assert out.tool_calls[0].arguments=={"q":"x"};assert out.usage["total_tokens"]==12

def test_compatible_provider_rejects_malformed_response():
 async def bad(payload):return {"wrong":[]}
 with pytest.raises(ModelProviderError):asyncio.run(OpenAICompatibleProvider(bad,"m").complete([]))

def test_compatible_provider_wraps_transport_failure():
 async def bad(payload):raise OSError("secret network detail")
 with pytest.raises(ModelProviderError,match="transport failed"):asyncio.run(OpenAICompatibleProvider(bad,"m").complete([]))
