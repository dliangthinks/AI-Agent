import os
import json
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.agents.format_scratchpad import format_to_openai_function_messages
from langchain.agents import AgentExecutor
from langchain.agents.output_parsers import OpenAIFunctionsAgentOutputParser
from langchain.tools import StructuredTool

# Load the environment variables
OPENAI_API_KEY = os.environ["OPENAI_API_KEY"]

KB_FILE = "project_kb.json"

# Initialize the language model
llm = ChatOpenAI(model="gpt-3.5-turbo")

def read_knowledge_base():
    if os.path.exists(KB_FILE):
        with open(KB_FILE, 'r') as f:
            return json.load(f)
    return {
        "project_overview": {},
        "scope": {},
        "schedule": {},
        "cost": {},
        "quality": {},
        "resource": {},
        "communications": {},
        "risk": {},
        "procurement": {},
        "stakeholder": {}
    }

def write_knowledge_base(kb):
    with open(KB_FILE, 'w') as f:
        json.dump(kb, f, indent=2)

def get_knowledge_base(dummy: str) -> str:
    return json.dumps(read_knowledge_base())

get_kb_tool = StructuredTool.from_function(
    func=get_knowledge_base,
    name="get_knowledge_base",
    description="Retrieves the current project knowledge base"
)

# Agent for answering queries
ANSWER_SYSTEM_PROMPT = """You are an AI assistant tasked with answering questions about a project using the provided knowledge base.
Your goal is to provide informed and helpful answers based on the information available in the knowledge base.
Always refer to the knowledge base first when answering questions.
If the knowledge base doesn't contain relevant information, politely state that you don't have that information and suggest what kind of information might be helpful to add to the knowledge base."""

answer_prompt = ChatPromptTemplate.from_messages([
    ("system", ANSWER_SYSTEM_PROMPT),
    MessagesPlaceholder(variable_name="chat_history"),
    ("human", "{input}"),
    MessagesPlaceholder(variable_name="agent_scratchpad"),
])

answer_agent = (
    {
        "input": lambda x: x["input"],
        "agent_scratchpad": lambda x: format_to_openai_function_messages(x["intermediate_steps"]),
        "chat_history": lambda x: x["chat_history"],
    }
    | answer_prompt
    | llm
    | OpenAIFunctionsAgentOutputParser()
)

answer_agent_executor = AgentExecutor(agent=answer_agent, tools=[get_kb_tool], verbose=True)

# Agent for updating the knowledge base
UPDATE_SYSTEM_PROMPT = """You are an AI assistant tasked with updating a project knowledge base based on new information from user interactions.
Your goals are:
1. Extract relevant project management information from the user's message and the AI's response.
2. Categorize the information into the appropriate project management aspects.
3. Update the knowledge base with new or modified information.
4. Ensure the knowledge base remains consistent and well-structured.

The knowledge base is structured around the following aspects of Project Management:
- project_overview
- scope
- schedule
- cost
- quality
- resource
- communications
- risk
- procurement
- stakeholder

Provide your updates as a JSON string that can be merged into the existing knowledge base."""

update_prompt = ChatPromptTemplate.from_messages([
    ("system", UPDATE_SYSTEM_PROMPT),
    ("human", "User message: {user_message}\nAI response: {ai_response}\nCurrent KB: {current_kb}\n\nProvide KB updates:"),
])

update_agent = (
    {
        "user_message": lambda x: x["user_message"],
        "ai_response": lambda x: x["ai_response"],
        "current_kb": lambda x: x["current_kb"],
    }
    | update_prompt
    | llm
    | OpenAIFunctionsAgentOutputParser()
)

update_agent_executor = AgentExecutor(agent=update_agent, tools=[], verbose=True)

def process_user_input(user_input):
    # Step 1: Answer the query using the knowledge base
    knowledge_base = read_knowledge_base()
    kb_context = json.dumps(knowledge_base, indent=2)  # Convert the knowledge base to a formatted string

    answer_response = answer_agent_executor.invoke({
        "input": f"Knowledge Base:\n{kb_context}\n\nUser Question: {user_input}",
        "chat_history": []   # not using chat history for now
    })
    
    ai_response = answer_response['output']

    # Step 2: Update the knowledge base
    update_response = update_agent_executor.invoke({
        "user_message": user_input,
        "ai_response": ai_response,
        "current_kb": kb_context
    })

    # Parse the JSON string returned by the update agent
    try:
        kb_updates = json.loads(update_response['output'])
        kb = read_knowledge_base()
        for category, updates in kb_updates.items():
            if category in kb:
                kb[category].update(updates)
        write_knowledge_base(kb)
    except json.JSONDecodeError:
        print("Error: Could not parse knowledge base updates.")

    return ai_response

""" if __name__ == "__main__":
    chat_history = []
    while True:
        user_input = input("You: ")
        if user_input.lower() in ['exit', 'quit', 'bye']:
            break
        response = process_user_input(user_input, chat_history)
        print("AI:", response)
        chat_history.append(("human", user_input))
        chat_history.append(("ai", response)) """
