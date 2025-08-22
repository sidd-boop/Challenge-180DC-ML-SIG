from langgraph.graph import StateGraph,START,END
from typing import TypedDict,Annotated,Literal,Optional,List
import operator
from pydantic import BaseModel,Field
from langchain_core.messages import SystemMessage,HumanMessage
from langchain_google_genai import ChatGoogleGenerativeAI,GoogleGenerativeAIEmbeddings
from schemas import RagLawyerOutput,ChaosLawyerOutput,Metadata
from langchain_core.messages import SystemMessage,HumanMessage
import random
from dotenv import load_dotenv
load_dotenv()
embeddings=GoogleGenerativeAIEmbeddings(model='models/embedding-001')

llm=ChatGoogleGenerativeAI(model='gemini-2.0-flash',temperature=0.5)



rag_llm=generator_llm=llm.with_structured_output(RagLawyerOutput)

chaos_llm=generator_llm=llm.with_structured_output(ChaosLawyerOutput)

class DebateState(TypedDict, total=False):
    case: str
    judge_decision: str
    rag_lawyer: Optional[RagLawyerOutput]
    rag_context: Optional[str]
    rag_role: str
    chaos_lawyer: Optional[ChaosLawyerOutput]
    chaos_role: str
    rag_history: Annotated[list[str],operator.add]
    chaos_history: Annotated[list[str],operator.add]
    winner: Literal["rag_wins","chaos_wins","quit"]

CASE_TYPES = [
    "defamation", "property dispute", "criminal case",
    "contract breach", "intellectual property"
]

QUIRKY_SEEDS = [
    "A man sues a parrot for defamation.",
    "A neighbor claims ownership of sunlight entering their balcony.",
    "A magician sues an assistant for revealing a trick as 'trade secret'.",
    "A drone trespass case over mango orchards.",
    "An influencer alleges trademark over a catchphrase used by a politician."
]

STOP_TERMS = {
    "rag wins", "rag_lawyer wins", "prosecution wins",
    "chaos wins", "chaos_lawyer wins", "defense wins",
    "quit", "exit", "stop", "end", "finish"
}



def rag_lawyer(state: DebateState)->RagLawyerOutput:
    #add rag_context as well after some time
    try:
        messages = [

SystemMessage(content="You are a meticulous legal expert. "

 "Ground your arguments in precedent, citations, and principles."),

HumanMessage(content=f"""

Case Title: {state['case']}
Plaintiff: {state['chaos_role']}
Defendant: {state['rag_role']}

You are representing the defendant. Make sure to clearly take the side of the 
defendant and also make accusatory remarks on the plaintiff if necessary based on
present arguments and previous context.

Relevant Legal Context:
{state.get('rag_context','No specific context retrieved for this turn.')}




Your Previous Arguments:

{''.join(f'- {arg}' for arg in state['rag_history'])}



Chaos Lawyer's Previous Arguments:

{''.join(f'- {arg}' for arg in state['chaos_history'])}





Now prepare your next structured argument. 



    case_type: str :description="The legal category of the case, e.g., 'defamation'."
    jurisdiction: str :description="The relevant legal jurisdiction, e.g., 'Supreme Court of India'."
    year: int :description="The year the judgment was made."
    key_legal_principles: description="Core legal principles cited."
    plaintiff_details: description="Description of the plaintiff."
    defendant_details: description="Description of the defendant."
    outcome:


"""),

 ]
        output = rag_llm.invoke(messages)
        return {
            "rag_lawyer": output,
            "rag_history": [output.argument],
            
        }
    except Exception as e:
        print(f"!!! ERROR in rag_lawyer node: {e}")
        # If the LLM call fails, record the error and return a default value
        return {
            "error_message": f"RAG Lawyer failed: {str(e)}",
            #default output so next node doesn't crash.
            "rag_lawyer": RagLawyerOutput(
                argument="[An error occurred. I am unable to provide an argument.]",
                citation="N/A",
                metadata=Metadata(case_type="error", jurisdiction="error", key_legal_principles=[], outcome="error")
            )
        }






def chaos_lawyer(state: DebateState)->ChaosLawyerOutput:
    messages = [
        SystemMessage(content=
            "You are the CHAOS LAWYER. Your mission is to generate absurd, exaggerated, and over-the-top counterarguments. You thrive on wild rhetoric , nonsense and funny legal twists."
        ),
        HumanMessage(content=f"""
Case: {state['case']}
Plaintiff: {state['chaos_role']}
Defendant: {state['rag_role']}

You are representing the plaintiff. Make sure to clearly take the side of the 
plaintiff and also make accusatory remarks on the defendant if necessary based on
present arguments and previous context.
Your Previous Chaos Arguments: {''.join(f'- {arg}' for arg in state['chaos_history'])}
RAG Lawyer's Latest Argument: {state['rag_lawyer'].argument}

Generate a new, chaotic counterargument that is absurd and exaggerated.


"""),
    ]

    output: ChaosLawyerOutput= chaos_llm.invoke(messages)

    return {
        "chaos_lawyer":output,
        "chaos_history":[output.argument],
        
    }

RAG_WINS_TERMS = {"rag wins", "raglawyer wins", "prosecution wins","prosecutor_wins"}
CHAOS_WINS_TERMS = {"chaos wins", "chaos lawyer wins", "defense wins"}

def judge_input(state: DebateState) -> DebateState:
    user_message = state.get('judge_decision', '').lower().strip()
    if user_message in RAG_WINS_TERMS:
        state["winner"]="rag_wins"
    if user_message in CHAOS_WINS_TERMS:
        state["winner"]="chaos_wins"
    if user_message in STOP_TERMS:
        state["winner"]="quit"
    return state

def route(state:DebateState)->Literal["continue_debate","end_debate"] :
    return "end_debate" if state.get("winner") else "continue_debate"



        
workflow=StateGraph(DebateState)


workflow.add_node("user_input", judge_input)
workflow.add_node("rag_lawyer", rag_lawyer)
workflow.add_node("chaos_lawyer", chaos_lawyer)


workflow = StateGraph(DebateState)

workflow.add_node("judge_input", judge_input)
workflow.add_node("rag_lawyer", rag_lawyer)
workflow.add_node("chaos_lawyer", chaos_lawyer)


workflow.add_edge(START, "judge_input")
workflow.add_conditional_edges(
    "judge_input",
     route,
     {
         "continue_debate":"rag_lawyer",
         "end_debate":END
     }
)
workflow.add_edge("rag_lawyer", "chaos_lawyer")
workflow.add_edge("chaos_lawyer", END)

graph=workflow.compile()









    
    









    


