




import json
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.pydantic_v1 import BaseModel, Field
from typing import List
from dotenv import load_dotenv
load_dotenv()

class ExtractedMetadata(BaseModel):
    case_type: str = Field(description="Infer the legal category, e.g., 'Service Law', 'Contract Law', 'Criminal Law'.")
    year: int = Field(description="Extract the 4-digit year of the judgment.")
    key_legal_principles: List[str] = Field(description="List the core legal principles discussed, e.g., 'seniority-cum-merit', 'revised pay scales'.")
    plaintiff_details: str = Field(description="Briefly describe the plaintiff/petitioner, e.g., 'A group of teachers'.")
    defendant_details: str = Field(description="Briefly describe the defendant/respondent, e.g., 'The State of Punjab'.")
    outcome: str = Field(description="Summarize the final outcome or ruling, e.g., 'Appeals dismissed, High Court decision upheld'.")


llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash", temperature=0.5)
structured_llm = llm.with_structured_output(ExtractedMetadata)


prompt = ChatPromptTemplate.from_messages([
    ("system", "You are an expert legal assistant. Your task is to extract structured metadata from the full text of a legal judgment. Analyze the text and provide the information in the requested JSON format."),
    ("human", "Here is the full text of the judgment:\n\n{judgment_text}")
])

chain = prompt | structured_llm


import time


def enrich_cases(
    raw_file_path=r"C:\Users\hp\OneDrive\Desktop\LEGAL\.venv\cases.json", 
    sampled_file_path="enriched_cases_sampled.json",
    sample_size: int = 50
):
    print(f"Starting data enrichment process for a sample of {sample_size} cases...")
    
    with open(raw_file_path, 'r', encoding='utf-8') as f:
        raw_cases = json.load(f)


    cases_to_process = raw_cases[:sample_size]
    
    enriched_cases = []
    total_cases = len(cases_to_process)

    for i, case in enumerate(cases_to_process):
        print(f"Processing case {i+1}/{total_cases}: {case['case_name']}")
        try:
            extracted_data = chain.invoke({"judgment_text": case["full_text"]})
            
            new_case_data = {
                **case,
                "metadata": {
                    "case_type": extracted_data.case_type,
                    "jurisdiction": case.get("jurisdiction", "Unknown"),
                    "year": extracted_data.year,
                    "key_legal_principles": extracted_data.key_legal_principles,
                    "plaintiff_details": extracted_data.plaintiff_details,
                    "defendant_details": extracted_data.defendant_details,
                    "outcome": extracted_data.outcome
                }
            }
            enriched_cases.append(new_case_data)
        
        except Exception as e:
            print(f"  -> Failed to process case: {case['case_name']}. Error: {e}")
            
            continue

        # Keep the delay to respect the API rate limit
        time.sleep(4)

    
    with open(sampled_file_path, 'w', encoding='utf-8') as f:
        json.dump(enriched_cases, f, indent=2)
        
    print(f"\n Sample enrichment complete. {len(enriched_cases)} cases saved to '{sampled_file_path}'.")


if __name__ == "__main__":

    enrich_cases()
