import asyncio,pytest
from project_brain.model import OpenAICompatibleProvider,ModelMessage,ModelProviderError

async def sample_transport(payload):
 assert payload["model"]=="brain-model"
 return {"choices":[{"message":{"content":"{\"task_id\":\"t\"}","tool_calls":[{"id":"c1","function":{"name":"search","arguments":"{\"q\":\"x\"}"}}]}}],"usage":{"total_tokens":12}}

def test_compatible_provider_normalizes_response():
 out=asyncio.run(OpenAICompatibleProvider(sample_transport,"brain-model").complete([ModelMessage(role="user",content="go")]))
 assert out.tool_calls[0].name=="search";assert out.tool_calls[0].arguments=={"q":"x"};assert out.usage["total_tokens"]==12

def test_compatible_provider_rejects_malformed_response():
 async def bad(payload):return {"wrong":[]}
 with pytest.raises(ModelProviderError):asyncio.run(OpenAICompatibleProvider(bad,"m").complete([]))

def test_compatible_provider_wraps_transport_failure():
 async def bad(payload):raise OSError("secret network detail")
 with pytest.raises(ModelProviderError,match="transport failed"):asyncio.run(OpenAICompatibleProvider(bad,"m").complete([]))


def test_compatible_provider_rejects_non_object_tool_arguments():
 async def bad(payload):return {"choices":[{"message":{"content":"","tool_calls":[{"id":"c","function":{"name":"x","arguments":"[1,2]"}}]}}]}
 with pytest.raises(ModelProviderError,match="invalid response"):
  asyncio.run(OpenAICompatibleProvider(bad,"m").complete([]))

def test_compatible_provider_times_out():
 async def slow(payload):
  await asyncio.sleep(0.05);return {"choices":[{"message":{"content":"ok"}}]}
 with pytest.raises(ModelProviderError,match="timed out"):
  asyncio.run(OpenAICompatibleProvider(slow,"m",timeout_seconds=0.001).complete([]))
