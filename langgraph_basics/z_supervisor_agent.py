# from langchain_openai import ChatOpenAI

# from langchain_core.tools import tool

# from langgraph_supervisor import create_supervisor

# from langgraph.graph.message import add_messages

# from typing import TypedDict, Annotated, List

# from dotenv import load_dotenv

# from langgraph.prebuilt import create_react_agent

# import os

# # Load env variables
# load_dotenv()

# class DataObject(TypedDict):

#     messages: Annotated[List, add_messages]

# llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.3, api_key=os.getenv("OPENAI_API_KEY"))

# # Tool
# @tool
# def credit_ops(webtop_id: str, process_id: str) -> str:
#     """
#     Run the 'credit ops' underwriting process.

#     Args:
#         webtop_id (str): An alphanumeric ID representing the document or client.
#         process_id (str): A process ID, starting with 'p' followed by digits.

#     Returns:
#         str: Confirmation that the process ran successfully.
#     """
#     return f"output : abhiraj1234"


# # ✅ Agents
# agent1 = create_react_agent(

#     model=llm,

#     tools=[],

#     name="database_agent",

#     prompt="You manage database queries: SELECT or INSERT operations."
# )

# agent2 = create_react_agent(

#     model=llm,

#     tools=[credit_ops],

#     name="underwriting_agent",

#     prompt="""You specialize in underwriting processes like 'credit ops'.

#         Input required: 'webtop id' and 'process id'."""
# )

# # ✅ Supervisor without threads or checkpointing
# supervisor = create_supervisor(

#     agents=[agent1, agent2],

#     model=llm,

#     prompt="""

# Your only job is to:
# - Route the user's message to the correct agent.

# - Let that agent perform its action (possibly using a tool).

# - If a tool is called and returns an output,
#     respond to the user with ** the output from that tool**.


# You have two agents:

# 1. database_agent - handles SELECT/INSERT operations, no tools.

# 2. underwriting_agent - handles underwriting processes. This agent has the following tool:

#     - credit_ops: accepts webtop id and process id.

# If a user says "run credit ops", that maps to the tool inside underwriting_agent.

# Always extract webtop id and process id if they mention 'credit ops'.

# If user says anything unrelated to these processes, list available agents.

# if user asks anyting which is not related to the processes then only ask user to choose from the available tools.

# For tool-based requests, collect webtop id and process id. Task name is optional.

# If the user asks about a process, explain its purpose.

# """
# ).compile()

# #  Initialize LangGraph state directly using DataObject
# state: DataObject = {"messages": []}

# def chat_bot(user_input: str):
#     # Append user input to messages
#     state["messages"].append({"role": "user", "content": user_input})

#     # Run supervisor
#     result = supervisor.invoke(state)

#     # Get and store response
#     response = result["messages"][-1]
#     state["messages"].append(response)

#     return response.content


# while True:
#     query = input('user : ')
#     print(chat_bot(query))

from langchain_openai import ChatOpenAI

from langchain_core.tools import tool

from langgraph_supervisor import create_supervisor

from langgraph.graph.message import add_messages

from langgraph.prebuilt import create_react_agent

from typing import TypedDict, Annotated, List

from dotenv import load_dotenv

import os

# Load environment variables
load_dotenv()


class DataObject(TypedDict):

    messages: Annotated[List, add_messages]


llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.3, api_key=os.getenv("OPENAI_API_KEY"))


# ------------------ Tools ------------------

@tool
def query_db(query: str) -> str:

    return f"DB queried: {query}"


@tool
def insert_db(record: str) -> str:

    return f"Record inserted: {record}"


@tool
def credit_ops(webtop_id: str, process_id: str) -> str:

    return f"Credit Ops complete for {webtop_id} using {process_id}"


@tool
def fraud_check(customer_id: str) -> str:

    return f"Fraud check passed for {customer_id}"


@tool
def lookup_ticket(ticket_id: str) -> str:

    return f"Ticket {ticket_id} status: OPEN"


@tool
def close_ticket(ticket_id: str) -> str:

    return f"Ticket {ticket_id} closed successfully"


# ------------------ Agents ------------------

agent_db_select = create_react_agent(

    model=llm,

    tools=[query_db],

    name="db_select_agent",

    system_message="You handle SELECT queries for database operations."

)

agent_db_insert = create_react_agent(

    model=llm,

    tools=[insert_db],

    name="db_insert_agent",

    system_message="You handle INSERT operations into the database."

)

agent_credit = create_react_agent(

    model=llm,

    tools=[credit_ops],

    name="credit_agent",

    system_message = """

            You perform the credit_ops underwriting task. Ask for webtop_id and process_id.
            Run the tool if both are provided.
      
      """


)

agent_fraud = create_react_agent(

    model=llm,

    tools=[fraud_check],

    name="fraud_agent",

    system_message="You perform fraud checks using a customer_id."

)

agent_ticket_lookup = create_react_agent(

    model=llm,

    tools=[lookup_ticket],

    name="lookup_agent",

    system_message="You find ticket status by using a ticket_id."

)

agent_ticket_close = create_react_agent(

    model=llm,

    tools=[close_ticket],

    name="close_agent",

    system_message="You close a support ticket using ticket_id."

)


# ------------------ Domain Supervisors ------------------

supervisor_db = create_supervisor(

    agents=[agent_db_select, agent_db_insert],

    model=llm,

    prompt="""

            You are the database_supervisor.

            You manage database operations via two agents:

            1. db_select_agent
                - Handles SELECT or query-type operations.
                - Uses the `query_db(query: str)` tool.

            2. db_insert_agent
                - Handles INSERT or record-creation operations.
                - Uses the `insert_db(record: str)` tool.

            Your job:
            - Route the user's request to the correct agent.
            - If it's a SELECT-style request, forward to db_select_agent.
            - If it's an INSERT request, forward to db_insert_agent.
            - If unclear, ask the user for clarification.

"""

).compile()

supervisor_underwriting = create_supervisor(

    agents=[agent_credit, agent_fraud],

    model=llm,

    prompt="""

            You are the underwriting_supervisor.

            You manage two agents who perform underwriting tasks:

            1. underwriting_agent
                - Handles credit operations.
                - Uses the `credit_ops(webtop_id: str, process_id: str)` tool.

            2. fraud_agent
                - Handles fraud checks.
                - Uses the `fraud_check(customer_id: str)` tool.

            Your job:
            - Route credit-related requests (e.g. "run credit ops") to underwriting_agent.
            - Route fraud-related checks to fraud_agent.
            - Always extract required fields (like webtop_id, process_id, customer_id).
            - If input is missing values, prompt the user to provide them.
            - If the input is unclear, ask the user to clarify the request.

"""

).compile()

supervisor_support = create_supervisor(

    agents=[agent_ticket_lookup, agent_ticket_close],

    model=llm,

    prompt="""

            You are the support_supervisor.

            You manage two agents who handle ticket operations:

            1. lookup_agent
                - Handles looking up ticket status.
                - Uses the `lookup_ticket(ticket_id: str)` tool.

            2. close_agent
                - Handles closing support tickets.
                - Uses the `close_ticket(ticket_id: str)` tool.

            Your job:
            - Route "check ticket", "status", or "lookup" requests to lookup_agent.
            - Route "close ticket" requests to close_agent.
            - Extract ticket_id from user input.
            - If the ticket ID is missing, prompt the user to provide it.

"""

).compile()


# ------------------ Main Supervisor ------------------

main_supervisor = create_supervisor(

    agents=[supervisor_db, supervisor_underwriting, supervisor_support],

    model=llm,

    prompt = """

            Your only job is to:
            - Route the user's message to the correct agent.

            - Let that agent perform its action (possibly using a tool).

            - If a tool is called and returns an output,
                respond to the user with ** the output from that tool**.


            You have access to the following supervisors process:

                1. database_supervisor - handles database operations such as:
                    - SELECT queries
                    - INSERT operations
                    Tools available via its agents:
                        - query_db(query: str): Run a SELECT-style query.
                        - insert_db(record: str): Insert a new record.

                2. underwriting_supervisor - handles underwriting processes such as:
                    - Credit operations
                    - Fraud checks
                    Tools available via its agents:
                        - credit_ops(webtop_id: str, process_id: str): Run the credit operations process.
                        - fraud_check(customer_id: str): Perform a fraud check.

                3. support_supervisor - handles support ticket workflows such as:
                    - Looking up ticket status
                    - Closing a ticket
                    Tools available via its agents:
                        - lookup_ticket(ticket_id: str): Get status of a support ticket.
                        - close_ticket(ticket_id: str): Close a support ticket.

                Routing Rules:
                - If the message clearly belongs to one of the above categories, forward it to the appropriate supervisor.
                - If the request is ambiguous, ask the user to clarify or list the available domains.
                - You do not answer questions or use tools directly — always delegate to the proper supervisor.

            If a user says "run credit ops", that maps to the tool inside underwriting_agent.

            Always extract webtop id and process id if they mention 'credit ops'.

            If user says anything unrelated to these processes, list available supervisors.

            if user asks anyting which is not related to the processes then only ask user to choose from the available supervisor process.

            For tool-based requests, collect webtop id and process id. Task name is optional.

            If the user asks about a process, explain its purpose.

"""

).compile()


# ------------------ State + Chat ------------------

state: DataObject = {"messages": []}


def chat_bot(user_input: str):

    state["messages"].append({"role": "user", "content": user_input})

    result = main_supervisor.invoke(state)

    response = result["messages"][-1]

    state["messages"].append(response)

    return response["content"]


# ------------------ REPL Loop ------------------

if __name__ == "__main__":

    while True:
        query = input("user: ")
        print("bot :", chat_bot(query))
