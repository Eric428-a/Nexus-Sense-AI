import pytest
from nexus.agents.base import AgentContext
from nexus.agents.orchestrator import AgentOrchestrator
from nexus.agents.research_agent import ResearchAgent
@pytest.mark.asyncio
async def test_research_agent():
    result=await ResearchAgent().run(AgentContext(input={"query":"test"}))
    assert result.status=="completed"
