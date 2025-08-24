AI Legal Debate System: Project Report
1. Introduction
The AI Legal Debate System is an interactive web application designed to simulate a courtroom battle between two distinct AI-powered lawyers. The project's goal was to create an engaging and educational experience by contrasting a data-driven, factual legal style with a creative, unpredictable, and often absurd one. The user takes on the role of the Judge, initiating cases, guiding the debate, and ultimately deciding the winner. This report details the system's architecture, core features, user workflow, and the challenges overcome during its development.

2. System Architecture
The application is built on a modern, decoupled client-server architecture to ensure modularity and scalability.

Backend (FastAPI): A high-performance Python web framework, FastAPI, was chosen for the backend. It manages all core logic, including session management, AI model interactions, and the complex RAG (Retrieval-Augmented Generation) pipeline. Its asynchronous capabilities and automatic API documentation make it ideal for this application.

Frontend (Streamlit): A user-friendly Python library, Streamlit, was used to build the interactive frontend. It allows for rapid development of data-centric applications and provides a clean, intuitive interface for the user to act as the Judge. The frontend is a pure client; it holds no game logic and communicates with the backend exclusively through API calls.


3. Core Features
The application is built around a set of powerful and interactive features that bring the courtroom simulation to life.

a) The Dueling AI Lawyers
RAG Lawyer (The Defense): This AI is designed to be a meticulous, data-driven legal expert. It uses a sophisticated RAG pipeline to ground its arguments in factual evidence retrieved from a knowledge base of legal cases. Its arguments are logical, structured, and always cite precedents.

Chaos Lawyer (The Prosecution): This AI is the creative and unpredictable foil to the RAG Lawyer. It does not use any retrieval. Instead, it relies on generating absurd, exaggerated, and often hilarious arguments based on wild rhetoric and invented legal twists, aiming to win by confusing and entertaining the Judge.

b) Advanced RAG Pipeline with Metadata Filtering
The RAG Lawyer's effectiveness is powered by a multi-stage retrieval system:

Data Enrichment: A preliminary script was developed to process a large corpus of raw legal documents. Using a Large Language Model (LLM), this script automatically extracted key structured metadata from the unstructured text, such as case_type, year, key_legal_principles, and the parties involved.

Hybrid Retrieval: When the user makes a query, the system uses a two-pronged approach to find relevant documents:

Semantic Search (Gemini Embeddings): Finds documents that are conceptually similar to the query.

Keyword Search (TF-IDF): Finds documents that share specific legal terms or names.

Metadata Filtering: The user can use the sidebar in the UI to apply filters, such as jurisdiction or year, to narrow down the search results to only the most relevant precedents.

c) Dynamic Role Assignment
To make the system versatile, the backend uses an LLM at the start of each debate to automatically parse the case description (e.g., "A man sues a parrot for defamation") and identify the plaintiff ("Man") and defendant ("Parrot"). These roles are then assigned to the lawyers, ensuring they argue the correct side of any given case.

4. How It Works: A User's Journey
The user's interaction with the application is a seamless, step-by-step process:

Starting a Case: The user is presented with a welcome screen. They can choose to either have a quirky case generated randomly or input their own custom case description.

Initiating the Debate: When the user clicks "Start," the frontend sends a request to the backend's /start endpoint. The backend creates a unique session, uses its LLM to identify the plaintiff and defendant, assigns roles to the lawyers, and sends the session details back to the frontend.

Observing and Judging: The main debate screen appears. The user can see the case details and the assigned roles. They can then:

Submit a Message: Type a specific question or a verdict (e.g., "prosecution wins") into the input box. This sends a request to the /run endpoint. The backend uses this message to perform a RAG search and generate the next round of arguments.

Continue the Debate: If the user doesn't have a specific question, they can click the "Continue Debate" button. This sends a generic "Continue" message to the backend, prompting the lawyers to argue based on the last thing that was said.

Receiving Arguments: After each user action, the backend processes the turn and sends the new arguments back. The frontend receives this data, updates the chat display, and refreshes the RAG context in the sidebar.

Declaring a Winner: When the user types a winning phrase (e.g., "defense wins"), the backend detects this, generates the special winning and losing statements for each lawyer, and sets the is_finished flag to True. The frontend then displays a celebratory message and concludes the debate.

5. Challenges Faced and Solutions
Several technical and logical challenges were overcome during development:

API Rate Limiting: The initial data enrichment script, which made one API call per document in a rapid loop, quickly hit the free-tier rate limit of the Google Gemini API.

Solution: The script was modified to introduce a pause between each API call using Python's time.sleep(4). This throttled the requests to a rate that was within the API's free-tier limits, allowing the large dataset to be processed successfully without errors.

Logical Contradictions in Roles: A persistent bug prevented the winning statements from appearing. This was traced back to a logical conflict where the backend had fixed roles (e.g., RAG Lawyer = Defense), but the workflow had a hardcoded list that incorrectly associated a winning term (e.g., "prosecution wins") with the RAG Lawyer.

Solution: The hardcoded lists were removed from the workflow. The judge_input node was redesigned to be dynamic, building its winning term sets on-the-fly based on the roles assigned at the start of each debate.

Streamlit "Double-Click" Bug: The user had to click buttons twice for the UI to update. This was caused by the misuse of st.rerun(), which was interrupting Streamlit's natural state management.

Solution: All unnecessary st.rerun() calls were removed from the helper functions, allowing Streamlit to handle UI updates automatically and reliably after each interaction.

Model Reliability for JSON Output: The initial method of asking an LLM to generate JSON in its text response was unreliable, often leading to parsing errors.

Solution: The code was updated to use structured output methods (.with_structured_output for Gemini and the outlines library for open-source models), which force the model to generate a valid JSON object that strictly conforms to a Pydantic schema, eliminating parsing errors.
