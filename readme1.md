sumitkumar005-isource-hackathon/
├── README.md
├── app.py  # Main Flask app, updated to initialize database
├── docker-compose.yaml  # Updated to include PostgreSQL
├── dockerfile
├── requirements.txt  # Add psycopg2-binary, pandas
└── app/
    ├── __init__.py
    ├── models.py  # Updated for PostgreSQL schema if needed
    ├── .DS_Store
    ├── routes/
    │   ├── moderator.py
    │   ├── organization.py
    │   ├── other.py
    │   ├── **question_answer.py**  # Updated to handle all query types
    │   ├── up_down_votes.py
    │   ├── user.py
    │   ├── .DS_Store
    │   └── upload/
    ├── Static/
    │   ├── .DS_Store
    │   ├── css/
    │   │   └── style.css
    │   ├── img/
    │   └── js/
    │       └── main.js
    ├── templates/
    │   ├── admin_dashboard.html
    │   ├── AskQuestion.html
    │   ├── chat.html  # Optionally tweak for new features
    │   ├── chatorg.html
    │   ├── documents.html
    │   ├── emailinvite.html
    │   ├── GenericNavbar.html
    │   ├── Landingpage.html
    │   ├── layout.html
    │   ├── layout_man.html
    │   ├── Login.html
    │   ├── moderate_questions.html
    │   ├── ModeratorDashboard.html
    │   ├── ModeratorNavbar.html
    │   ├── my_questions.html
    │   ├── navbar.html
    │   ├── newNav.html
    │   ├── OrganizationDashboard.html
    │   ├── OrganizationNavbar.html
    │   ├── organizationRegister.html
    │   ├── OrgUserManager.html
    │   ├── QuestionDetails.html
    │   ├── questions.html
    │   ├── register.html
    │   ├── uploadDocs.html
    │   ├── user_dashboard.html
    │   ├── UserNavbar.html
    │   └── .DS_Store
    └── utils/
        ├── ai_part.py  # Update NLU for better intent detection
        ├── email_notification.py
        ├── **hybrid_rag.py**  # Updated to handle hybrid queries
        ├── other.py
        ├── role_check.py
        ├── **simple_rag.py**  # Updated to integrate insights
        ├── **database_query.py**  # New: SQL generation and execution
        ├── **query_classifier.py**  # New: Classify query types
        ├── **insight_generator.py**  # New: Add actionable insights
        └── .DS_Store


***************************

sumitkumar005-isource-hackathon/
├── data/
│   ├── csv/
│   │   └── dataco_supply_chain.csv  # The 95 MB CSV file
│   └── documents/
│       ├── Inventory_Management.pdf
│       ├── Supplier_Code_of_Conduct.pdf
│       └── ...  # Other PDFs
├── app/
│   ├── utils/
│   │   ├── load_csv_to_db.py  # New script for CSV
│   │   ├── process_pdfs.py    # New script for PDFs
│   │   └── ...  # Other utils files
│   └── ...  # Other app files
└── ...  # Other project files