"""Naturithm Agent Team — Oria's creative team powered by Gemini."""

from google import genai
from .prompts import CONTENT_CREATOR, MARKET_RESEARCHER, COPYWRITER, CREATIVE_DIRECTOR, SOCIAL_MEDIA_MANAGER

_genai_client = None

def _get_genai():
    global _genai_client
    if _genai_client is None:
        _genai_client = genai.Client(vertexai=True, project="naturitm", location="us-central1")
    return _genai_client


class Agent:
    """A single agent with a specific role and system prompt."""

    def __init__(self, name: str, system_prompt: str):
        self.name = name
        self.system_prompt = system_prompt
        self.conversation: list[dict] = []

    def run(self, message: str, context: str = "") -> str:
        """Send a message to this agent and get a response."""
        full_message = f"{context}\n\n{message}" if context else message
        self.conversation.append({"role": "user", "parts": [{"text": full_message}]})

        client = _get_genai()
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=self.conversation,
            config={"system_instruction": self.system_prompt, "max_output_tokens": 4096},
        )

        reply = response.text
        self.conversation.append({"role": "model", "parts": [{"text": reply}]})
        return reply

    def reset(self):
        """Clear conversation history."""
        self.conversation = []


class NaturithmTeam:
    """The full Naturithm creative team orchestrated by Oria."""

    def __init__(self):
        self.director = Agent("Oria (Creative Director)", CREATIVE_DIRECTOR)
        self.content_creator = Agent("Content Creator", CONTENT_CREATOR)
        self.market_researcher = Agent("Market Researcher", MARKET_RESEARCHER)
        self.copywriter = Agent("Copywriter", COPYWRITER)
        self.social_manager = Agent("Social Media Manager", SOCIAL_MEDIA_MANAGER)

        self.agents = {
            "director": self.director,
            "content": self.content_creator,
            "research": self.market_researcher,
            "copy": self.copywriter,
            "social": self.social_manager,
        }

    def process_idea(self, idea: str) -> dict:
        """
        Process a founder's idea through the full agent team.

        Flow:
        1. Director analyzes the idea and creates briefs for each agent
        2. Each agent processes their brief
        3. Director synthesizes everything into a final plan
        """
        print(f"\n{'='*60}")
        print(f"  NATURITHM CREATIVE TEAM — Processing Idea")
        print(f"{'='*60}\n")

        print(">> Oria (Director) analyzing idea...")
        director_brief = self.director.run(
            f"""The founder has this idea: "{idea}"

Break this down into specific briefs for your four agents:
1. CONTENT CREATOR BRIEF: What visual content should they design?
2. MARKET RESEARCH BRIEF: What should they investigate?
3. COPYWRITER BRIEF: What copy do we need?
4. SOCIAL MEDIA MANAGER BRIEF: What's the posting/distribution strategy?

Be specific. Each agent needs a clear, actionable brief."""
        )
        print(f"   Done.\n")

        print(">> Content Creator working on visuals...")
        content_output = self.content_creator.run(
            "Here's your brief from the Creative Director. Produce your full output.",
            context=director_brief,
        )
        print("   Done.\n")

        print(">> Market Researcher analyzing trends...")
        research_output = self.market_researcher.run(
            "Here's your brief from the Creative Director. Produce your full analysis.",
            context=director_brief,
        )
        print("   Done.\n")

        print(">> Copywriter crafting copy...")
        copy_output = self.copywriter.run(
            "Here's your brief from the Creative Director. Produce your full copy package.",
            context=director_brief,
        )
        print("   Done.\n")

        print(">> Social Media Manager planning distribution...")
        social_output = self.social_manager.run(
            "Here's your brief from the Creative Director. Produce your full posting and distribution strategy.",
            context=director_brief,
        )
        print("   Done.\n")

        print(">> Oria synthesizing final plan...")
        synthesis = self.director.run(
            f"""Here are the outputs from your team:

## CONTENT CREATOR OUTPUT:
{content_output}

## MARKET RESEARCH OUTPUT:
{research_output}

## COPYWRITER OUTPUT:
{copy_output}

## SOCIAL MEDIA MANAGER OUTPUT:
{social_output}

Now synthesize these into a final, actionable content plan. Include:
1. What to post (format, visuals, copy)
2. When to post (timing, sequence)
3. Your recommendation and quality assessment
4. Any adjustments needed to stay true to Naturithm's philosophy
5. The deeper message thread — how does this serve the path to self-realization?"""
        )
        print("   Done.\n")

        return {
            "idea": idea,
            "director_brief": director_brief,
            "content": content_output,
            "research": research_output,
            "copy": copy_output,
            "social": social_output,
            "final_plan": synthesis,
        }

    def ask_agent(self, agent_name: str, message: str) -> str:
        """Talk directly to a specific agent."""
        if agent_name not in self.agents:
            return f"Unknown agent: {agent_name}. Use: {', '.join(self.agents.keys())}"
        return self.agents[agent_name].run(message)

    def reset_all(self):
        """Reset all agents' conversation history."""
        for agent in self.agents.values():
            agent.reset()
