import dotenv

from src.static.ChatBedrockWrapper import ChatBedrockWrapper
from src.static.submission import Submission
from langgraph.graph import StateGraph, END
from typing import TypedDict, Annotated
import operator
from langchain_core.messages import AnyMessage, SystemMessage, HumanMessage, ToolMessage

import src.submission.tools.csv_handling as csv_tools
import src.submission.tools.database as db_tools
import src.submission.tools.web_crawl as web_tools
import src.submission.tools.data_viz as viz_tools
import src.submission.tools.stats_analysis as stats_analysis_tools
import src.submission.prompts.system_prompt as system_prompt
# import src.submission.tools.pdf_handling as pdf_tools

dotenv.load_dotenv()

class AgentState(TypedDict):
    messages: Annotated[list[AnyMessage], operator.add]
    

tools_researcher = [db_tools.query_database, db_tools.get_possible_answers_to_question, db_tools.get_questions_of_given_type]
tools_chart = [viz_tools.custom_plot_from_string_to_s3]
tools_web = [web_tools.get_unesco_data, web_tools.crawl_subpages, web_tools.scrape_text, web_tools.duckduckgo_search]
tools_file = [csv_tools.process_first_sheet_to_json_from_url, csv_tools.extract_table_from_url_to_string_with_auto_cleanup]
# tools_pdf = [pdf_tools.extract_top_paragraphs_from_url]
tools_stats_analysis = [stats_analysis_tools.calculate_pearson_multiple, stats_analysis_tools.calculate_quantile_regression_multiple]
tools = tools_researcher + tools_chart + tools_web + tools_file + tools_stats_analysis # + tools_pdf

class PIRLSAgent:
    def __init__(self, model, tools, system_prompt=""):
        self.system_prompt = system_prompt
        
        # initialising graph with a state 
        graph = StateGraph(AgentState)
        
        # adding nodes 
        graph.add_node("llm", self.call_llm)
        graph.add_node("function", self.execute_function)
        graph.add_conditional_edges(
            "llm",
            self.exists_function_calling,
            {True: "function", False: END}
            )
        graph.add_edge("function", "llm")
        
        # setting starting point
        graph.set_entry_point("llm")
        
        self.graph = graph.compile()
        self.tools = {t.name: t for t in tools}
        self.model = model.bind_tools(tools)

    def exists_function_calling(self, state: AgentState):
        result = state['messages'][-1]
        return len(result.tool_calls) > 0

    def call_llm(self, state: AgentState):
        messages = state['messages']
        if self.system_prompt:
            messages = [SystemMessage(content=self.system_prompt)] + messages
        message = self.model.invoke(messages)
        print(message)
        return {'messages': [message]}

    def execute_function(self, state: AgentState):
        tool_calls = state['messages'][-1].tool_calls
        results = []
        for t in tool_calls:
            print(f"Calling: {t}")
            if not t['name'] in self.tools:      # check for bad tool name from LLM
                print("\n ....bad tool name....")
                result = "bad tool name, retry"  # instruct LLM to retry if bad
            else:
                result = self.tools[t['name']].invoke(t['args'])
            results.append(ToolMessage(tool_call_id=t['id'], name=t['name'], content=str(result)))
        print(result)
        return {'messages': results}
    
    def run(self, initial_messages):
        try:
            # Execute the graph and get the final state
            final_state = self.graph.invoke({"messages": [HumanMessage(content=initial_messages)]}, {"recursion_limit": 50})

            # Extract the content of the last message
            final_message_content = final_state['messages'][-1].content

            # Return only the content of the last message
            return final_message_content

        except Exception as e:
            # Return the error message if an exception occurs
            return ("**I'm sorry, but I can't process your request regarding PIRLS 2021 data right now because the server is currently unreachable. Please try again later.**\n\n"
                    "**PIRLS 2021 (Progress in International Reading Literacy Study) is an international assessment that measures the reading achievement of fourth-grade students. "
                    "Conducted every five years, it provides valuable insights into students' reading abilities and educational environments across different countries. "
                    "For more information, you can visit the PIRLS 2021 website.**\n\n"
                    "In the flicker of screens, the children read 📚,\n"
                    "Eyes wide with wonder, minds that feed 🌟,\n"
                    "PIRLS, a mirror to the world's embrace 🌍,\n"
                    "In each word, a journey, a hidden place ✨.")

prompt = system_prompt.prompt

# This function is used to run evaluation of your model.
# You MUST NOT change the signature of this function! The name of the function, name of the arguments,
# number of the arguments and the returned type mustn't be changed.
# You can modify only the body of this function so that it returned your implementation of the Submission class.
def create_submission(call_id: str) -> Submission:
    llm = ChatBedrockWrapper(
        model_id='anthropic.claude-3-5-sonnet-20240620-v1:0',
        model_kwargs={'temperature': 0, "max_tokens": 81920, 'top_p': 0.9, 'top_k': 100},
        call_id=call_id
    )

    doc_agent = PIRLSAgent(model=llm, tools=tools, system_prompt=prompt)
    return doc_agent
    # raise NotImplementedError('create_submission is not yet implemented.')
