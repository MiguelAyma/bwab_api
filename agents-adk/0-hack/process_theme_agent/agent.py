"""
Sequential Agent with a Minimal Callback

This example demonstrates a lead qualification pipeline with a minimal
before_agent_callback that only initializes state once at the beginning.
"""

from google.adk.agents import SequentialAgent

from .subagents.generate_theme_agent import theme_agent
from .subagents.generate_themejson_agent import themejson_agent
from .subagents.generate_roadmap_agent import roadmap_agent

# Import the subagents
# from .subagents.validator import lead_validator_agent

# Create the sequential agent with minimal callback
root_agent = SequentialAgent(
    name="process_theme_agent",
    sub_agents=[theme_agent, themejson_agent, roadmap_agent],
    description="A pipeline that generate content for theme and also create a roadmap to study",
)
