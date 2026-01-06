
# 🎓 AI Agent Lab: For Beginners
This project is a simple demonstration of an **AI Agent System**. Unlike a normal chatbot, this Agent can "think" for itself, use the internet, write code, and manage databases to solve real-world tasks.

## 🌟 What can it do?

Imagine you have a team of three specialized experts working for you:

1. **🌐 The Search Expert**: Goes to the internet to find the latest news, facts, or real-time information.
2. **💻 The Programming Expert**: Writes and explains code to solve technical problems or automate tasks.
3. **💾 The Database Expert**: Creates and manages databases (SQL) to save and organize information for you.

Everything is managed by a **Planner (The Boss)** who listens to your request and decides which of these three experts to call.


## 🚀 How to use it?

### 1. Setup

* **Install requirements**: Run `pip install -r requirements.txt`.
* **Add API Keys**: find`.env` and add your keys:
* `OPENROUTER_API_KEY`: For the AI's brain.
* `TAVILY_API_KEY`: For searching the web.
* `MODEL_NAME`: You use specific model.

### 2. Run the App

Type this in your terminal:

```bash
streamlit run app.py

```

### 3. Try these commands:

* **Search**: *"What are the top 5 tech news stories today?"*
* **Programming**: *"Write a Python script to calculate the Fibonacci sequence."*
* **Database**: *"Create a table called 'inventory' and add 'Apples' with a quantity of 50."*
* **Combined**: *"Search for the current price of Bitcoin and save it into my database."*

---

## 📂 Project Folders

* `app.py`: The main user interface you see.
* `agents/`: Where the "brains" of the experts live (Search, Programming, and DB).
* `memory/`: Where your chat history is saved so the AI remembers you.
* `databases/`: Where your `.db` files are created.

---