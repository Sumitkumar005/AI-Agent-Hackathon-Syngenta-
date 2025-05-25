# Syngenta AI Agent Hackathon - Intelligent Supply Chain Assistant

Welcome to the **Syngenta AI Agent Hackathon** project! This is a powerful, intelligent assistant designed to help businesses manage their supply chain by answering questions about policies, inventory, sales, and more. Imagine a super-smart helper who can read company documents, crunch numbers from spreadsheets, and give clear, actionable advice—all in plain English! Whether you’re a manager asking about inventory policies or a team member checking sales data, this AI agent has you covered.

This project was built for the Syngenta AI Agent Hackathon, where we created a chatbot that combines artificial intelligence (AI) with real company data to provide accurate and secure answers. We added special features to make sure only the right people can see certain information, keeping data safe and organized. This README will walk you through everything we did, from start to finish, in a way that’s easy to understand, even if you’re not a tech expert.

---

## Table of Contents

- [What Does This Project Do?](#what-does-this-project-do)
- [Why Is It Useful?](#why-is-it-useful)
- [How It Works (In Simple Terms)](#how-it-works-in-simple-terms)
- [Step-by-Step: What We Built](#step-by-step-what-we-built)
- [Key Features](#key-features)
- [Technology Used](#technology-used)
- [How to Set It Up](#how-to-set-it-up)
- [How to Use It](#how-to-use-it)
- [What’s Next?](#whats-next)
- [Contributing](#contributing)
- [License](#license)
- [Thank You](#thank-you)
- [Project Structure](#project-structure)

---

## What Does This Project Do?

This project creates an AI-powered chatbot that helps businesses manage their supply chain. It can:

- Answer questions about company policies: For example, “What’s our policy on slow-moving inventory?”
- Provide data from spreadsheets: Like, “How much are our total sales?”
- Combine both: For instance, “Which items are slow-moving according to our policy, and what’s their total value?”
- Keep data secure: Only the right people (like Finance team members) can see sensitive information, and users only see data from their region (like India or USA).

Think of it as a super-smart assistant who knows everything about your company’s supply chain and can explain it clearly, while making sure private information stays private.

---

## Why Is It Useful?

Running a supply chain is complex. You have tons of documents (like policies) and data (like sales numbers) to keep track of. This AI agent makes it easy by:

- **Saving time:** No need to dig through files or spreadsheets—just ask the chatbot.
- **Giving clear answers:** It explains things in simple language, even for non-experts.
- **Keeping things secure:** Managers in India won’t see USA data, and only the Finance team can see profit margins.
- **Helping make decisions:** It offers smart suggestions, like “You’re low on inventory—time to reorder!”

This tool is perfect for companies like Syngenta, where quick, accurate, and secure answers can make a big difference.

---

## How It Works (In Simple Terms)

Imagine you have a giant filing cabinet with two sections:

- **Documents:** Company policies (PDFs) that explain rules, like how to handle inventory.
- **Data:** A spreadsheet (CSV file) with numbers, like sales or stock levels.

When you ask the AI agent a question, it:

1. **Listens:** Understands your question, like “What’s our total sales?”
2. **Searches:** Checks the right place—documents for policies, spreadsheet for numbers.
3. **Thinks:** Uses AI to turn the information into a clear answer.
4. **Checks permissions:** Makes sure you’re allowed to see the answer (e.g., only Finance sees profit margins).
5. **Answers:** Gives you a simple response, like “Your total sales are $10,000.”

It’s like having a super-smart librarian who knows exactly where to look and keeps secrets safe!

---

## Step-by-Step: What We Built

Here’s the full story of how we built this AI agent, from scratch to finish, explained so anyone can follow along.

### Step 1: Setting Up the Foundation

We started by creating a web application using Flask, a tool that helps build websites with Python. This app is the home for our chatbot, where users can log in, ask questions, and get answers.

**What we did:**

- Set up a Flask app with pages for login, dashboard, and chatting.
- Used Docker to make sure everything runs smoothly on any computer.
- Connected two databases:
  - PostgreSQL: To store spreadsheet data (like sales numbers).
  - Elasticsearch: To store and search document text (like policies).
- Added a user system so people can log in with roles (like “Finance” or “Sales”) and regions (like “India” or “USA”).

**Why it matters:** This gave us a solid base to build the chatbot and keep data organized.

### Step 2: Loading Supply Chain Data

The hackathon gave us a CSV file (like a spreadsheet) with supply chain data, such as sales amounts, inventory levels, and regions.

**What we did:**

- Created a script (`load_csv_to_db.py`) to load the CSV into PostgreSQL.
- Stored the data in a table called `supply_chain`, with columns like `sales_amount`, `stock`, and `region`.
- Made sure the data was ready for the chatbot to query with SQL (a language for asking databases questions).

**Why it matters:** This lets the chatbot answer questions like “How many items are in stock?” by looking at the spreadsheet data.

### Step 3: Processing Company Documents

The hackathon also provided PDF documents with company policies, like rules for inventory or ethical sourcing.

**What we did:**

- Created a script (`process_pdfs.py`) to read the PDFs and extract their text.
- Stored the text in Elasticsearch, a search engine that’s great for finding information in documents.
- Used a technique called Retrieval-Augmented Generation (RAG) to make the chatbot search these documents for answers.

**Why it matters:** This lets the chatbot answer questions like “What’s our policy on slow-moving inventory?” by finding the right document.

### Step 4: Building the Smart Chatbot

The heart of the project is the chatbot, which lives in `question_answer.py`. It’s smart because it uses AI (specifically, the Gemini language model) to understand questions and give clear answers.

**What we did:**

- Wrote code to classify questions into three types:
  - Document-based: Questions about policies (answered using PDFs in Elasticsearch).
  - Database-based: Questions about numbers (answered using the CSV data in PostgreSQL).
  - Hybrid: Questions needing both (e.g., combining policy text with data).
- Used the Gemini AI model to turn raw data into easy-to-understand answers.
- Added a feature to give insights, like suggesting actions based on the answer (e.g., “Low stock? Order more!”).

**Why it matters:** This makes the chatbot versatile, handling all kinds of questions with accurate, human-like responses.

### Step 5: Adding Security with Governance

To make the chatbot safe and fair, we added governance features to control who can see what. This was a bonus feature we added thanks to the deadline extension to May 28, 2025.

**What we did:**

- Role-Based Access Control (RBAC):
  - Modified `question_answer.py` to check the user’s role (e.g., “Finance” or “Sales”).
  - Example: Only Finance users can ask about profit margins; others get “Access denied.”
- Geographic Access Control:
  - Added a `region` field to the User model in `models.py` (e.g., “India”, “USA”).
  - Updated `question_answer.py` to filter database queries by region (e.g., `SELECT * FROM supply_chain WHERE region = 'India'`).
  - Changed `hybrid_rag.py` to only show documents matching the user’s region.
- Updated `user.py` to store role and region in the user’s session when they log in.

**Why it matters:** This keeps sensitive data secure. For example, a manager in India can’t see USA sales, and only the right team sees confidential info.

### Step 6: Testing and Polishing

Finally, we tested everything to make sure it worked perfectly.

**What we did:**

- Tested document questions (e.g., “What’s the policy on ethical sourcing?”).
- Tested database questions (e.g., “What’s the total sales amount?”).
- Tested hybrid questions (e.g., “How many items are slow-moving per our policy?”).
- Tested governance (e.g., ensuring non-Finance users can’t see profit margins).
- Fixed bugs and improved error messages (e.g., “No data found” if the query fails).

**Why it matters:** This ensures the chatbot is reliable and user-friendly for the hackathon judges.

---

## Key Features

- **Smart Question Answering:** Answers questions about policies, data, or both, using AI.  
  Example: “What’s our inventory policy?” or “How much stock do we have?”
- **Secure Access:** Only authorized users see sensitive data (e.g., Finance for profit margins). Data is filtered by region (e.g., India users see India data).
- **Actionable Insights:** Suggests next steps, like “Low inventory—consider reordering.”
- **Easy to Use:** Simple web interface for asking questions. Clear, human-like responses even for complex queries.
- **Scalable Design:** Built to handle lots of users and data, using Docker and databases.

---

## Technology Used

Here’s what we used to build this project, explained simply:

- **Flask:** A tool to create the website where users interact with the chatbot.
- **Python:** The main programming language for writing the code.
- **PostgreSQL:** A database to store spreadsheet data (like sales numbers).
- **Elasticsearch:** A search engine to store and find text from documents.
- **Gemini AI:** A smart AI model that understands questions and gives answers.
- **Docker:** A tool to package everything so it runs smoothly on any computer.
- **LangChain:** A library to connect the AI model with our data.

---

## How to Set It Up

Want to try this project yourself? Here’s how to get it running on your computer, step by step. Don’t worry if you’re not tech-savvy—we’ll explain everything!

### What You Need

- A computer with Python 3.8 or higher installed.
- Docker to run the databases and app easily.
- A Gemini API key (you can get one from Google’s AI platform).
- The project files (download them from our GitHub repository).

### Step-by-Step Installation

1. **Get the Code:**

   ```bash
   git clone https://github.com/yourusername/syngenta-ai-agent.git
   cd syngenta-ai-agent
   ```

2. **Set Up Docker:**

   Install Docker if you don’t have it (search “Install Docker” for your computer).  
   Run the databases (PostgreSQL and Elasticsearch) using our `docker-compose.yaml` file:

   ```bash
   docker-compose up -d
   ```

3. **Create a Virtual Environment:**

   This keeps the project’s tools separate from other programs on your computer.

   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

4. **Install Required Tools:**

   Install all the Python libraries we use:

   ```bash
   pip install -r requirements.txt
   ```

5. **Set Up Environment Variables:**

   Create a file called `.env` in the project folder and add:

   ```
   FLASK_APP=app.py
   FLASK_ENV=development
   DATABASE_URL=postgresql://user:password@postgres:5432/isource
   ELASTICSEARCH_HOST=elasticsearch
   ELASTICSEARCH_PORT=9200
   GOOGLE_API_KEY=your_gemini_api_key_here
   DOC_INDEX_NAME=documents
   ```

   Replace `your_gemini_api_key_here` with your actual Gemini API key.

6. **Load the Supply Chain Data:**

   Place the hackathon’s CSV file (e.g., `DataCoSupplyChainDataset.csv`) in the `data/csv/` folder.  
   Run the script to load it into PostgreSQL:

   ```bash
   python app/utils/load_csv_to_db.py
   ```

7. **Process the Documents:**

   Place the hackathon’s PDF files in the `data/documents/` folder.  
   Run the script to process them into Elasticsearch:

   ```bash
   python app/utils/process_pdfs.py
   ```

8. **Start the App:**

   Run the Flask app to start the chatbot:

   ```bash
   docker-compose up --build
   ```

9. **Open your browser and go to** [http://localhost:5000](http://localhost:5000).

10. **Log In:**

    Create a user account with a role (e.g., “Finance”) and region (e.g., “India”).  
    Log in to start asking questions.

---

## How to Use It

### Asking Questions

- Log in: Use your account to access the chatbot.
- Go to the chatbot page: Find the chat interface on the website.
- Type your question: Ask anything about the supply chain, like policies or data.
- Get an answer: The chatbot will reply with a clear response and suggestions.

### Examples of Questions

- **Document-based:** “What’s our policy on ethical sourcing?”  
  The chatbot searches PDFs and explains the policy.

- **Database-based:** “What’s the total sales amount in India?”  
  The chatbot checks the spreadsheet and gives a number.

- **Hybrid:** “How many items are slow-moving per our policy?”  
  The chatbot combines policy text with data to answer.

- **Restricted:** “What are the profit margins?”  
  Only Finance users get an answer; others see “Access denied.”

---

## What’s Next?

This project is a strong foundation, but there’s room to grow:

- More Languages: Let the chatbot answer in Spanish, Hindi, or other languages.
- Voice Support: Add a feature to talk to the chatbot instead of typing.
- More Insights: Make the chatbot suggest even smarter business moves.
- Mobile App: Create a phone app for easier access.

---

## Contributing

Want to help make this project even better? We’d love your ideas! Here’s how:

- Report bugs: Tell us if something doesn’t work.
- Suggest features: Share ideas for new things the chatbot could do.
- Write code: Fork the GitHub repo, make changes, and send us a pull request.

Check out our GitHub page for more details.

---

## License

This project is licensed under the MIT License, which means you can use, share, or modify it freely, as long as you give credit to us.

---

## Thank You

A huge thank you to:

- Syngenta for hosting this hackathon and inspiring us to build something amazing.
- The team for working hard to create this AI agent.
- You for reading this and trying our project!

We hope this AI agent makes your supply chain management easier, smarter, and more secure. Let’s keep building the future of business together!

---

## Project Structure

```
.
├── .DS_Store
├── .gitignore
├── README.md
├── NEW_README.md
├── app.py
├── cross_checkwithgrok.md
├── docker-compose.yaml
├── dockerfile
├── requirements.txt
├── app
│   ├── __init__.py
│   ├── .DS_Store
│   ├── models.py
│   ├── routes
│   │   ├── .DS_Store
│   │   ├── moderator.py
│   │   ├── organization.py
│   │   ├── other.py
│   │   ├── question_answer.py
│   │   ├── up_down_votes.py
│   │   ├── user.py
│   │   └── upload
│   │       ├── apple-privacy-policy-en-ww.pdf
│   │       ├── Business-Conduct-Policy.pdf
│   │       ├── ma144_macbook_pro_users_guide.pdf
│   │       └── ma507_imacg5_userguide.pdf
│   ├── Static
│   │   ├── .DS_Store
│   │   ├── css
│   │   │   └── style.css
│   │   ├── img
│   │   │   ├── ai.png
│   │   │   ├── answer.png
│   │   │   ├── answers.png
│   │   │   ├── ask.png
│   │   │   ├── idea.png
│   │   │   ├── leader.png
│   │   │   ├── question-mark.png
│   │   │   ├── reported.png
│   │   │   └── users.png
│   │   └── js
│   │       └── main.js
│   ├── templates
│   │   ├── .DS_Store
│   │   ├── admin_dashboard.html
│   │   ├── AskQuestion.html
│   │   ├── chat.html
│   │   ├── chatorg.html
│   │   ├── documents.html
│   │   ├── emailinvite.html
│   │   ├── GenericNavbar.html
│   │   ├── Landingpage.html
│   │   ├── layout_man.html
│   │   ├── layout.html
│   │   ├── Login.html
│   │   ├── moderate_questions.html
│   │   ├── ModeratorDashboard.html
│   │   ├── ModeratorNavbar.html
│   │   ├── my_questions.html
│   │   ├── navbar.html
│   │   ├── newNav.html
│   │   ├── OrganizationDashboard.html
│   │   ├── OrganizationNavbar.html
│   │   ├── organizationRegister.html
│   │   ├── OrgUserManager.html
│   │   ├── QuestionDetails.html
│   │   ├── questions.html
│   │   ├── register.html
│   │   ├── uploadDocs.html
│   │   ├── user_dashboard.html
│   │   └── UserNavbar.html
│   └── utils
│       ├── .DS_Store
│       ├── ai_part.py
│       ├── email_notification.py
│       ├── hybrid_rag.py
│       ├── load_csv_to_db.py
│       ├── other.py
│       ├── process_pdfs.py
│       └── role_check.py
└── data
    ├── csv
    │   └── DataCoSupplyChainDataset.csv
    └── documents
        ├── Anti-Counterfeit and Product Authenticity Policy.pdf
        ├── Circular Economy.pdf
        ├── COC.pdf
        ├── Communication and Crisis Management Policy for DataCo Global.pdf
        ├── Continuous Improvement.pdf
        ├── Cost Reduction.pdf
        ├── Data Security.pdf
        ├── DataCo Global Capacity Planning Policy.pdf
        ├── Dataco Global Change Management Policy for Supply Chain Processes.pdf
        ├── DataCo Global Contract Management and Negotiation Policy.pdf
        ├── Dataco Global Order Management Policy.pdf
        ├── Dataco Global Transportation and Logistics Policy.pdf
        ├── DataCo Global Warehouse and Storage Policy.pdf
        ├── Dataco Global_ Demand Forecasting and Planning Policy.pdf
        ├── Diversity and Inclusion in Supplier Base Policy for DataCo Global.pdf
        ├── Environmental Sustainability.pdf
        ├── Global Business Continuity.pdf
        ├── Global Returns.pdf
        ├── Health Safety and Environment (HSE) Policy for Supply Chain Management.pdf
        ├── Inventory.pdf
        ├── IOT.pdf
        ├── KPI.pdf
        ├── Labor Standards.pdf
        ├── Obsolete Inventory Handling Policy for Dataco Global.pdf
        ├── QA.pdf
        ├── Risk Management.pdf
        ├── Sourcing and Procurement Policy for DataCo Global.pdf
        ├── SRM.pdf
        ├── Supplier Selection.pdf
        └── Trade Compliance.pdf
