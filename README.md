Link: <mark> (https://youtu.be/YozrJlcCEeU) </mark>

AI Legal Debate System: Project Report

Introduction The AI Legal Debate System is a web-based, interactive application created to stage a virtual courtroom duel between two different AI-powered attorneys. The objective of the project was to provide a fascinating and enlightening experience by pitting a factual, data-driven style of law against a creative, unpredictable, and frequently absurd one. The Judge plays the role of the user, opening cases, steering the argument, and determining the winner in the end. This report outlines the architecture of the system, its main features, user workflow, and the hurdles it bridged to come into existence.



Backend (FastAPI): A fast Python web framework, FastAPI, was selected for the backend. It handles all major logic, such as session management, AI model interactions, and the intricate RAG (Retrieval-Augmented Generation) pipeline. Its asynchronous nature and automatic API documentation make it the perfect choice for this application.

Frontend (Streamlit): Streamlit,  was utilized to create the interactive frontend. It provides fast development of data-driven applications and a clean and simple interface for the user to perform the role of the Judge. The frontend is purely a client; it does not contain any game logic and only interacts with the backend via API calls.

Core Features The application is centered on a collection of robust and interactive features that give the courtroom simulation life.
a) The Dueling AI Lawyers RAG Lawyer (The Defense): This lawyer is programmed as a careful, fact-based legal specialist. It employs a cutting-edge RAG pipeline for basing its arguments on factual evidence obtained from a database of legal cases. Its arguments are rational, organized, and always referenced with precedents.

Chaos Lawyer (The Prosecution): This AI is the imaginative and erratic opposite of the RAG Lawyer. It makes no use of any retrieval. It depends instead on producing ridiculous, overblown, and frequently laughable arguments founded on wild rhetoric and made-up legal angles and tries to win through bamboozling and amusing the Judge.

b) Advanced RAG Pipeline with Metadata Filtering
The success of the RAG Lawyer is fueled by a multi-stage retrieval system:

Data Enrichment: An initial script was written to crawl a  corpus of unstructured raw legal documents. An LLM was utilized by this script to extract critical structured metadata from the unstructured text autonomously, including case_type, year, key_legal_principles, and parties.

Hybrid Retrieval: When a query is made by the user, the system employs a two-fold strategy to discover pertinent documents:

Semantic Search (Gemini Embeddings): Identifies documents that are semantically close to the query.

Metadata Filtering: The user is able to make use of the sidebar in the UI to apply filters, like jurisdiction or year, to limit the search results to just the most pertinent precedents.

c) Dynamic Role Assignment To ensure that the system is flexible, the backend applies an LLM to automatically analyze the case description (e.g., "A man sues a parrot for defamation") and determine the plaintiff ("Man") and defendant ("Parrot") at the beginning of each debate. The lawyers are then assigned these roles so that they argue the appropriate side of any case.

How It Works: A User's Journey The process of the user interacting with the application is an easy, step-by-step one:
Starting a Case: A welcome screen greets the user. They can either have a whimsical case randomly generated or type in their own personal case description.

Starting the Debate: When the user clicks on "Start," the frontend makes a request to the backend's /start endpoint. The backend generates a new session, employs its LLM to determine the plaintiff and defendant, assigns roles to the attorneys, and returns the session information to the frontend.

Watching and Judging: The primary debate screen is displayed. The user sees the details of the case and the assigned roles. They can then:

Send a Message: Enter a particular question or a decision (e.g., "prosecution wins") in the input field. This triggers a request to the /run endpoint. The backend utilizes this message to conduct a RAG search and create the next set of arguments.

Continue the Debate: If the user does not have a particular question, they can hit the "Continue Debate" button. This sends a generic "Continue" request to the backend, challenging the lawyers to argue based on the previous thing mentioned.

Getting Arguments: With every user action, the backend processes the turn and returns the new arguments. The frontend updates this information, rebuilds the chat display, and refreshes the RAG context in the sidebar.

Declaring a Winner: When the user enters a winning sentence (e.g., "defense wins"), the backend recognizes this, creates the special winning and losing phrases for both lawyers, and marks the is_finished flag as True. A congratulatory message and the end of the debate are shown by the frontend.

Challenges Encountered and Solutions Various technical and logical issues were addressed during development:
API Rate Limiting: The first data enrichment script, which issued a single API call per document in a fast loop, rapidly exceeded the free-tier rate limit of the Google Gemini API.

Solution: The script was then changed to insert a pause between every API call by using Python's time.sleep(4). This slowed the requests to a rate within the API's free-tier limits, enabling the large dataset to be processed successfully without fail.

Logical Contradictions in Roles: A recurring issue caused the winning statements to not show up. This was traced to a logical contradiction in which the backend had static roles (e.g., RAG Lawyer = Defense), but the workflow had a hardcoded list that improperly linked a winning term (e.g., "prosecution wins") with the RAG Lawyer.

Solution: The hardcoded lists were taken out of the workflow. The judge_input node was re-engineered to be dynamic, creating its winning term sets on-the-fly from the roles assigned at each debate beginning.

Streamlit "Double-Click" Bug: The user needed to double-click buttons for the UI to refresh. This was due to repeated use of st.rerun() in the frontend helper functions, which was interfering with Streamlit's natural state management.

Solution: All redundant st.rerun() calls were eliminated from the helper functions, so Streamlit could automatically and reliably perform UI updates after every interaction.

Model Reliability for JSON Output: The original approach to requesting an LLM to provide JSON in its text reply was unreliable, tending to produce parsing errors.

Solution: The code was modified to utilize structured output functions (.with_structured_output for Gemini , which compel the model to produce a valid JSON object that conforms strictly to a Pydantic schema, thereby excluding parsing errors.
