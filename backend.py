import uvicorn
import uuid
import random
import operator
from typing import TypedDict, Annotated, Literal, Optional, List
from schemas import RagLawyerOutput,ChaosLawyerOutput,Metadata
from workflow import DebateState,QUIRKY_SEEDS,graph,RAG_WINS_TERMS,CHAOS_WINS_TERMS
from fastapi import FastAPI, HTTPException
from rag_pipeline import RAGPipeline
from langchain_google_genai import ChatGoogleGenerativeAI,GoogleGenerativeAIEmbeddings
from pydantic import BaseModel, Field
from dotenv import load_dotenv


llm=ChatGoogleGenerativeAI(model='gemini-2.0-flash',temperature=0.5)

class CaseParties(BaseModel):
    """Defines the plaintiff and defendant in a legal case."""
    plaintiff: str = Field(description="The party initiating the lawsuit.")
    defendant: str = Field(description="The party being sued.")

extraction_llm=llm.with_structured_output(CaseParties)

class StartRequest(BaseModel):
    """Optional: provide a case to start with."""
    case: Optional[str] = None

class StartResponse(BaseModel):
    session_id: str
    case: str

class RunRequest(BaseModel):
    session_id: str
    user_message: str
    filters: Optional[dict]

class RunResponse(BaseModel):
    rag_lawyer_output: RagLawyerOutput
    chaos_lawyer_output: ChaosLawyerOutput
    rag_context: str
    is_finished: bool
    winner: Optional[str] = None

app=FastAPI(title="Legal debate game api")

SESSIONS={}

rag_pipeline=RAGPipeline(file_path="enriched_cases.json")



@app.post("/start",response_model=StartResponse)
async def start_session(request: StartRequest):
    """
    Initializes a new debate session.
    A random case is generated if one is not provided.
    """
    session_id = str(uuid.uuid4())
    case = request.case or random.choice(QUIRKY_SEEDS)


    try:
        parties = extraction_llm.invoke(f"Analyze the following case description and identify the plaintiff and the defendant: '{case}'")
        plaintiff = parties.plaintiff
        defendant = parties.defendant
    except Exception as e:
        # Fallback for safety if the LLM fails
        print(f"LLM extraction failed: {e}. Using generic roles.")
        plaintiff = "Plaintiff"
        defendant = "Defendant"
    
    # Create the initial state for the new session
    initial_state = DebateState(
        case=case,
        rag_context="", 
        judge_decision="",
        rag_history=[],
        rag_role=defendant,
        chaos_role=plaintiff,
        chaos_history=[],
        winner=None
    )
    
    SESSIONS[session_id] = initial_state
    print(f"Session started: {session_id} | Case: {case}")
    
    return {"session_id": session_id, "case": case}



@app.post("/run", response_model=RunResponse)
async def run_turn(request: RunRequest):
    """
    Runs one turn of the debate for a given session.
    """
    session_id = request.session_id
    if session_id not in SESSIONS:
        raise HTTPException(status_code=404, detail="Session not found.")

    current_state = SESSIONS[session_id]

    dynamic_query=f"{current_state["case"]} {request.user_message}"
    rag_context=rag_pipeline.generate_context(dynamic_query,filters=request.filters)
    current_state["rag_context"]=rag_context

    current_state['judge_decision'] = request.user_message
    
    final_state = graph.invoke(current_state)
    
  
    SESSIONS[session_id] = final_state
    
    winner = final_state.get("winner")

    
    rag_output = final_state.get("rag_lawyer")
    chaos_output = final_state.get("chaos_lawyer")

    
    if final_state['winner']=='rag_wins':
        # RAG Lawyer's sophisticated victory statement
        rag_output = RagLawyerOutput(
            argument="Victory was the only logical outcome. The evidence presented was unequivocal, and the principles of jurisprudence have been upheld.",
            citation="Res ipsa loquitur.", # The thing speaks for itself.
            metadata=rag_output.metadata if rag_output else Metadata(case_type="Concluded", jurisdiction="", key_legal_principles=[], outcome="Won")
        )
        # Chaos Lawyer's funny losing statement
        chaos_output = ChaosLawyerOutput(
            argument="A FIX! The system is rigged! My arguments were clearly too advanced for this court's primitive understanding of para-legal quantum mechanics!",
            rhetoric="I demand a retrial in the Court of Cosmic Opinion!"
        )

    elif final_state['winner']=='chaos_wins':
        
        rag_output = RagLawyerOutput(
            argument="A travesty. The court has been swayed by cheap theatrics over the bedrock of established law. The verdict is logically unsound.",
            citation="Aberratio ictus.",
            metadata=rag_output.metadata if rag_output else Metadata(case_type="Concluded", jurisdiction="", key_legal_principles=[], outcome="Lost")
        )
        
        chaos_output = ChaosLawyerOutput(
            argument="SILENCE! The court has recognized true genius! My irrefutable logic—a dazzling tapestry of chaos and brilliance—has prevailed!",
            rhetoric="Let this victory be a lesson to all who dare challenge the beautiful absurdity of the law!"
        )

    return RunResponse(
        rag_lawyer_output=rag_output,
        chaos_lawyer_output=chaos_output,
        rag_context=rag_context,
        is_finished=(winner is not None),
        winner=winner
    )

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)

  


