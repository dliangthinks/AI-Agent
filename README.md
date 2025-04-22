# AI Project Management Assistant

This project implements an AI assistant designed to help manage project information using a knowledge base. It leverages Large Language Models (LLMs) via the LangChain framework to understand user queries, retrieve relevant project details, and update the knowledge base with new information.

## Core Components

1.  **`agent.py`**: This is the central script containing the AI logic. It defines two LangChain agents:
    *   **Answering Agent**: Queries the `project_kb.json` file to answer user questions about the project based on the stored information.
    *   **Updating Agent**: Analyzes conversations (user input and AI responses) to identify and extract new project details, updating the `project_kb.json` accordingly.
2.  **`project_kb.json`**: A JSON file acting as the project's knowledge base. It stores information categorized under standard project management domains (e.g., scope, schedule, cost, risk, stakeholders).
3.  **UI Files (`chatUI-wx.py`, `PYSide6`, `PYSimpleGUI`, etc.)**: Various Python scripts implementing graphical user interfaces (GUIs) using different libraries (wxPython, PySide6, PySimpleGUI). These provide front-ends for interacting with the AI agent. *Note: It appears multiple UI frameworks have been explored.*

## Functionality

*   **Query Project Information**: Users can ask questions about the project (e.g., "What is the project schedule?", "Who are the key stakeholders?"). The AI consults the knowledge base to provide answers.
*   **Update Knowledge Base**: As users interact with the AI, the system can automatically identify relevant new information (e.g., changes in scope, new risks identified) and update the knowledge base.
*   **Multiple UI Options**: The project includes experiments with different GUI toolkits, offering potential choices for the user interface.

## Setup

1.  **Clone the repository:**
    ```bash
    git clone <repository_url>
    cd <repository_directory>
    ```
2.  **Install dependencies:**
    ```bash
    pip install langchain openai python-dotenv # Add other UI-specific dependencies (e.g., wxPython, PySide6, PySimpleGUI) if needed
    ```
3.  **Set up Environment Variables:** Create a `.env` file in the root directory and add your OpenAI API key:
    ```
    OPENAI_API_KEY='your_openai_api_key_here'
    ```
4.  **Initialize Knowledge Base:** Ensure `project_kb.json` exists. If not, running `agent.py` might create a default empty one, or you can create it manually with the basic structure seen in the `agent.py` `read_knowledge_base` function.

## Usage

1.  **Run a UI script:** Choose one of the UI scripts (e.g., `chatUI-wx.py`) and run it:
    ```bash
    python chatUI-wx.py
    ```
    *(Replace `chatUI-wx.py` with your preferred UI file)*
2.  **Interact with the AI:** Use the GUI to ask questions or provide information about the project.

## Future Development / Considerations

*   **Consolidate UI**: Choose a primary UI framework and remove or refactor the others for clarity.
*   **Error Handling**: Enhance error handling, especially around knowledge base updates and API interactions.
*   **Chat History**: Implement persistent chat history within the agents for more contextual conversations. The current implementation seems to reset history for each input.
*   **Knowledge Base Schema**: Potentially define a more rigid schema for `project_kb.json` for better validation and consistency.
*   **Tool Refinement**: Explore adding more LangChain tools for enhanced capabilities (e.g., web search, document loading). 