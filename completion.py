from dotenv import load_dotenv
from langchain.agents import initialize_agent, AgentType
from langchain.chat_models import ChatOpenAI
from langchain.agents.agent_toolkits import O365Toolkit


# Load environment variables
load_dotenv()

toolkit = O365Toolkit()
tools = toolkit.get_tools()


llm = ChatOpenAI(model='gpt-3.5-turbo', temperature=0)
agent = initialize_agent(
    tools, llm, agent=AgentType.STRUCTURED_CHAT_ZERO_SHOT_REACT_DESCRIPTION, verbose=False)


def get_completion(prompt):
    return agent.run(prompt)
