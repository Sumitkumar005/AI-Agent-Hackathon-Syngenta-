import datetime
from flask import render_template, request, redirect, url_for, flash, session, jsonify
from ..models import db, User, Questions, Plus_ones, Answers, Votes, Keywords, Organizations, CustomerSupport
import random
from langchain_community.llms.ollama import Ollama
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
import humanize
import random
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
import threading
import random
from ..utils.role_check import role_required
from ..utils.ai_part import lemmatize_text, is_abusive, keybertmodel
from ..utils.email_notification import notifications
from flask import Blueprint, current_app
from concurrent.futures import ThreadPoolExecutor
from ..utils.hybrid_rag import hybrid_search
from ..utils.simple_rag import search_answer
from langchain_community.tools import WikipediaQueryRun
from langchain_community.utilities import WikipediaAPIWrapper
import os
from sqlalchemy import create_engine, text

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

# Gemini LLM initialization
gemini_llm = ChatGoogleGenerativeAI(
    model="gemini-pro",  # or 'gemini-1.5-flash' etc.
    google_api_key=GOOGLE_API_KEY
)

# Prompt template to incorporate context + user question
rag_prompt = PromptTemplate.from_template(
    """You are a helpful and accurate AI assistant. 
Use the following context to answer the user's question accurately and succinctly.

Context:
{context}

Question:
{question}
"""
)

# Create the chain
gemini_chain = LLMChain(
    llm=gemini_llm,
    prompt=rag_prompt,
    verbose=True
)

QA_bpt = Blueprint('question_and_answer', __name__)
executor = ThreadPoolExecutor(max_workers=5)

api_wrapper = WikipediaAPIWrapper(top_k_results=1, doc_content_chars_max=200)
wiki_tool = WikipediaQueryRun(api_wrapper=api_wrapper)

# Database connection setup
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:password@postgres:5432/isource")

def classify_query(query):
    """Classify the query type based on keywords."""
    query_lower = query.lower()
    if any(keyword in query_lower for keyword in ["policy", "definition", "guideline", "procedure"]):
        return "document"
    elif any(keyword in query_lower for keyword in ["total", "how many", "inventory", "sales", "value", "debit", "cash", "transfer", "payment"]):
        return "database"
    elif ("policy" in query_lower or "definition" in query_lower) and ("total" in query_lower or "how many" in query_lower or "value" in query_lower):
        return "hybrid"
    else:
        return "document"  # Default to document-based for general queries

def execute_sql(sql):
    """Execute an SQL query and return the result."""
    try:
        engine = create_engine(DATABASE_URL)
        with engine.connect() as connection:
            result = connection.execute(text(sql)).fetchone()
        return result[0] if result else None
    except Exception as e:
        print(f"SQL execution error: {e}")
        return None

def handle_document_query(query, org_id):
    """Handle document-based queries using hybrid RAG."""
    context = hybrid_search(query, org_id)
    if not context:
        return "No relevant information found in documents."
    response = gemini_chain.run(context=context, question=query)
    return response

def handle_database_query(query):
    """Handle database queries by generating and executing SQL."""
    query_lower = query.lower()
    # Map query to SQL based on hackathon sample questions
    if "total sales amount" in query_lower:
        sql = "SELECT SUM(sales_amount) FROM supply_chain"
    elif "inventory" in query_lower and "no-movers" not in query_lower:
        sql = "SELECT COUNT(*) FROM supply_chain WHERE stock > 0"
    elif "southwest region" in query_lower and "sales" in query_lower:
        sql = "SELECT SUM(sales_amount) FROM supply_chain WHERE region = 'Southwest'"
    else:
        sql = "SELECT COUNT(*) FROM supply_chain"  # Fallback
    result = execute_sql(sql)
    return f"Database result: {result}" if result is not None else "No data found."

def handle_hybrid_query(query, org_id):
    """Handle hybrid queries combining document and database info."""
    doc_context = hybrid_search(query, org_id)
    query_lower = query.lower()
    if "no-movers" in query_lower and "policy" in query_lower:
        sql = "SELECT SUM(order_item_total) FROM supply_chain WHERE order_date < CURRENT_DATE - INTERVAL '180 days'"
        result = execute_sql(sql)
        return f"Policy: {doc_context}\nDatabase: Found items with total value {result} that are no-movers (unsold for 180 days)."
    elif "debit" in query_lower and "policy" in query_lower:
        sql = f"SELECT COUNT(*) FROM supply_chain WHERE payment_type = 'DEBIT'"
        result = execute_sql(sql)
        return f"Policy: {doc_context}\nDatabase: {result} orders were paid using DEBIT."
    return f"Document context: {doc_context}\nDatabase info not applicable."

def generate_insights(response):
    """Generate actionable insights using the language model."""
    prompt = f"Based on the following information, provide actionable insights: {response}"
    try:
        insights = gemini_llm.invoke(prompt).content
        return insights
    except Exception as e:
        print(f"Insight generation error: {e}")
        return "No insights available."

@QA_bpt.route('/api/chatbot', methods=['POST'])
def chatbot():
    try:
        data = request.get_json()
        conversation = data.get('conversation', [])
        if not conversation:
            return jsonify({"error": "No conversation provided"}), 400

        # Extract the last user message
        user_message = ""
        for msg in reversed(conversation):
            if msg.get('sender') == 'You':
                user_message = msg.get('message', '').strip()
                break

        if not user_message:
            return jsonify({"error": "No user message found"}), 400

        # Get user role and region from session
        user_role = session.get('role')
        user_region = session.get('region')
        org_id = session.get('org_id', 1)  # Fallback to 1 if not in session

        # Check for abusive content
        is_toxic, _ = is_abusive(user_message)
        if is_toxic:
            return jsonify({"reply": "Sorry, the input is inappropriate."}), 400

        # Classify and route the query
        query_type = classify_query(user_message)
        if query_type == "document":
            response = handle_document_query(user_message, org_id)
        elif query_type == "database":
            response = handle_database_query(user_message, user_region, user_role)  # Pass role
        elif query_type == "hybrid":
            response = handle_hybrid_query(user_message, org_id)
        else:
            response = "Sorry, I couldn't understand your query."

        # Generate insights
        insights = generate_insights(response)
        final_response = f"{response}\n\n**Insights:** {insights}"

        # Save interaction
        conversation.append({
            "sender": "Bot",
            "message": final_response,
            "messageId": f"msg_{int(datetime.datetime.now().timestamp())}_{random.randint(1000, 9999)}",
            "timestamp": datetime.datetime.now().strftime("%I:%M %p")
        })
        if session.get('user_id'):
            customersupport = CustomerSupport(
                userid=session.get('user_id'),
                conversation_json=conversation,
                date=datetime.datetime.now(),
                solution="pending"
            )
            db.session.add(customersupport)
            db.session.commit()

        return jsonify({"reply": final_response}), 200

    except Exception as e:
        print(f"Error in chatbot API: {e}")
        return jsonify({"error": "An error occurred"}), 500

def handle_database_query(query, region, role):
    """Handle database queries with geographic and role-based filtering."""
    query_lower = query.lower()
    
    # Role-based access control
    if any(keyword in query_lower for keyword in ["profit", "benefit"]) and role != "Finance":
        return "Access denied: Only Finance users can view profit-related data."
    
    # Map query to SQL with region filter
    if "total sales amount" in query_lower:
        if "debit" in query_lower:
            sql = f"SELECT SUM(sales) FROM supply_chain WHERE order_region = '{region}' AND payment_type = 'DEBIT'"
        elif "cash" in query_lower:
            sql = f"SELECT SUM(sales) FROM supply_chain WHERE order_region = '{region}' AND payment_type = 'CASH'"
        elif "transfer" in query_lower:
            sql = f"SELECT SUM(sales) FROM supply_chain WHERE order_region = '{region}' AND payment_type = 'TRANSFER'"
        elif "payment" in query_lower:
            sql = f"SELECT SUM(sales) FROM supply_chain WHERE order_region = '{region}' AND payment_type = 'PAYMENT'"
        else:
            sql = f"SELECT SUM(sales) FROM supply_chain WHERE order_region = '{region}'"
    elif "inventory" in query_lower and "no-movers" not in query_lower:
        sql = f"SELECT COUNT(*) FROM supply_chain WHERE stock > 0 AND order_region = '{region}'"
    elif "southwest region" in query_lower and "sales" in query_lower:
        if region != "Southwest":
            return "Access denied: You can only view data for your region."
        sql = f"SELECT SUM(sales) FROM supply_chain WHERE order_region = 'Southwest'"
    else:
        sql = f"SELECT COUNT(*) FROM supply_chain WHERE order_region = '{region}'"  # Fallback
    result = execute_sql(sql)
    return f"Database result: {result}" if result is not None else "No data found."


# Keep existing routes unchanged
@QA_bpt.route('/questions', methods=['GET', 'POST', 'DELETE', 'PUT'])
def questions():
    filter = request.args.get('filter', 'date')
    if request.method == 'POST':
        question = request.form.get('question')
        question = Questions(question=question, userid=session['user_id'], plus_one=0, official_answer="")
        db.session.add(question)
        db.session.commit()
        flash(['Question added successfully', 'success'])
        return redirect(url_for('question_and_answer.questions'))
    elif request.method == 'DELETE':
        question_id = request.form.get('question_id')
        if question_id is None:
            flash('Please fill the required fields')
            return redirect(url_for('question_and_answer.questions'))
        question = Questions.query.filter_by(questionid=question_id).first()
        db.session.delete(question)
        db.session.commit()
        flash(['Question deleted successfully', 'success'])
        return redirect(url_for('question_and_answer.questions'))
    else:
        question_whole = []
        if session.get('org_id'):
            if filter == "date":
                questions = Questions.query.filter_by(orgid=session.get('org_id')).order_by(Questions.date.desc()).all()
            elif filter == "plus_one":
                questions = Questions.query.filter_by(orgid=session.get('org_id')).order_by(Questions.plus_one.desc()).all()
            elif filter == "plus_one_date":
                questions = Questions.query.filter_by(orgid=session.get('org_id')).order_by(Questions.date.desc(), Questions.plus_one.asc()).all()
            else:
                questions = Questions.query.filter_by(orgid=session.get('org_id')).all()
            for question in questions:
                question_whole.append(question.serializer())
            role = 'organization' if Organizations.query.filter_by(orgid=session.get('org_id')).first() else User.query.filter_by(userid=session.get('user_id')).first().role
            return render_template('questions.html', questions=question_whole, nav="All Questions", role=role, filter=filter)
        else:
            org_id = User.query.filter_by(userid=session.get('user_id')).first().organization
            if filter == "date":
                questions = Questions.query.filter_by(orgid=org_id).order_by(Questions.date.desc()).all()
            elif filter == "plus_one":
                questions = Questions.query.filter_by(orgid=org_id).order_by(Questions.plus_one.desc()).all()
            elif filter == "plus_one_date":
                questions = Questions.query.filter_by(orgid=org_id).order_by(Questions.date.desc(), Questions.plus_one.asc()).all()
            else:
                questions = Questions.query.filter_by(orgid=org_id).all()
            for question in questions:
                question_whole.append(question.serializer())
            role = User.query.filter_by(userid=session.get('user_id')).first().role
            return render_template('questions.html', questions=question_whole, nav="All Questions", role=role, filter=filter)

@QA_bpt.route('/answer_delete/<int:answerid>', methods=['GET'])
@role_required(['admin', 'moderator'])
def answer_delete(answerid):
    answer = Answers.query.get(answerid)
    official_ans = answer.answer
    question_id = answer.questionid
    db.session.delete(answer)
    db.session.commit()
    if Questions.query.filter_by(questionid=question_id).first().official_answer == official_ans:
        if len(Answers.query.filter_by(questionid=question_id, marked_as_official=True).all()) >= 1:
            Questions.query.filter_by(questionid=question_id).first().official_answer = Answers.query.filter_by(questionid=question_id, marked_as_official=True).order_by(Answers.date.desc()).first().answer
        else:
            Questions.query.filter_by(questionid=question_id).first().official_answer = ""
    db.session.commit()
    flash(['Answer deleted successfully', 'success'])
    return redirect(url_for('question_and_answer.questions_details', question_id=question_id))

@QA_bpt.route('/questions_details/<int:question_id>', methods=['GET', 'POST'])
@role_required(['user', 'moderator'])
def questions_details(question_id):
    if request.method == 'POST':
        answer = request.form.get('answer')
        if User.query.get(session['user_id']).role == 'moderator':
            isAnsOfficial = True if request.form.get('official_status') == "yes" else False
        else:
            isAnsOfficial = False
        if answer is None:
            flash('Please fill the required fields')
            return redirect(url_for('question_and_answer.questions'))
        newAnswer = Answers(answer=answer, questionid=question_id, userid=session['user_id'],
                           upvotes=0, downvotes=0, marked_as_official=isAnsOfficial, date=datetime.datetime.now())
        db.session.add(newAnswer)
        db.session.commit()
        if isAnsOfficial:
            question = Questions.query.filter_by(questionid=question_id).first()
            question.official_answer = answer
            db.session.commit()
        flash(['Answer added successfully', 'success', 'Answer Provided'])
        return redirect(url_for('question_and_answer.questions_details', question_id=question_id))
    else:
        questions = Questions.query.filter_by(questionid=question_id).first()
        timestamp = questions.date
        now = datetime.datetime.now()
        relative_time = humanize.naturaltime(now - timestamp)
        user_question = User.query.filter_by(userid=questions.userid).first()
        answer_all = Answers.query.filter_by(questionid=question_id).order_by(Answers.date.desc()).all()
        answers_list = [answer.serializer() for answer in answer_all]
        return render_template('QuestionDetails.html', question=questions.serializer(), relative_time=relative_time,
                               user_question=user_question, answers=answers_list, nav=f"Question {question_id}",
                               role=User.query.filter_by(userid=session['user_id']).first().role)

@QA_bpt.route('/questions_delete/<int:question_id>', methods=['GET'])
@role_required(['user', 'moderator', 'organization'])
def questions_delete(question_id):
    user = User.query.filter_by(userid=session['user_id']).first()
    question = Questions.query.filter_by(questionid=question_id).first()
    if question.userid != user.userid and user.role not in ['moderator', 'organization']:
        flash('You are not authorized to delete this question')
        return redirect(url_for('user.myquestions'))
    answers = Answers.query.filter_by(questionid=question_id).all()
    plus_ones = Plus_ones.query.filter_by(questionid=question_id).all()
    votes = Votes.query.filter_by(questionid=question_id).all()
    for answer in answers:
        db.session.delete(answer)
    for plus_one in plus_ones:
        db.session.delete(plus_one)
    for vote in votes:
        db.session.delete(vote)
    db.session.delete(question)
    db.session.commit()
    flash(['Question deleted successfully', 'success'])
    if user.role in ['moderator', 'organization']:
        return redirect(url_for('moderator.moderator_dashboard'))
    return redirect(url_for('user.myquestions'))

@QA_bpt.route('/ask_question', methods=["GET", "POST"])
@role_required('user')
def ask_question():
    if request.method == "POST":
        title = request.form.get('title')
        body = request.form.get('body')
        tags = request.form.get('tags')
        random_id = random.randint(1000, 9999)
        is_toxic, details = is_abusive(title + ' ' + body + ' ' + tags)
        if is_toxic:
            flash('The question content is toxic/abusive cannot be posted. We apologize for the inconvenience.', 'error')
            return redirect(url_for('question_and_answer.ask_question'))
        if not title or not body or not tags:
            flash('Please fill in all fields.', 'error')
            return redirect(url_for('question_and_answer.ask_question'))
        org_id = User.query.filter_by(userid=session.get('user_id')).first().organization
        tag_objects = [tag.strip() for tag in tags.split(',')]
        new_question = Questions(
            questionid=random_id,
            question_title=title,
            question_detail=body,
            date=datetime.datetime.now(),
            official_answer="",
            userid=session.get('user_id'),
            tags=tag_objects,
            orgid=org_id
        )
        db.session.add(new_question)
        db.session.commit()
        app = current_app._get_current_object()
        executor.submit(ask_question_function, app, random_id, org_id, title, body, tag_objects)
        flash(['Your question is being posted in the background!', 'success'])
        return redirect(url_for('question_and_answer.questions'))
    return render_template('AskQuestion.html', nav="Ask Question", role=User.query.filter_by(userid=session.get('user_id')).first().role)

def ask_question_function(app, question_id, org_id, title, body, tags):
    """
    Integrates Gemini (via LangChain) into the ask_question_function 
    to produce AI-generated answers based on hybrid RAG context.
    """
    try:
        with app.app_context():
            hybrid_context = hybrid_search(f"{title} {body}", org_id, score_threshold=0.5)
            simple_context = search_answer(f"{title} {body}", org_id)
            wiki_context = ""
            if not hybrid_context and not simple_context:
                wiki_context = wiki_tool.run(title + " " + body)
            combined_context = ""
            if hybrid_context and simple_context:
                combined_context += f"Hybrid Search:\n{hybrid_context}\n\nQA Pair Context:\n{simple_context}\n"
            elif simple_context:
                combined_context += f"QA Pair Context:\n{simple_context}\n"
            elif hybrid_context:
                combined_context += f"Hybrid Search:\n{hybrid_context}\n"
            elif wiki_context:
                combined_context += f"Wikipedia Context:\n{wiki_context}\n"
            if not combined_context:
                combined_context = "No relevant context found. Use best available knowledge."
            response = gemini_chain.run(
                context=combined_context,
                question=f"{title}\n{body}"
            )
            is_toxic, details = is_abusive(response)
            if is_toxic:
                print("AI response flagged as toxic:", details)
                return None
            extracted_keywords = [keyword[0] for keyword in keybertmodel.extract_keywords(response)] + tags
            new_answer = Answers(
                answer=response,
                questionid=question_id,
                userid=1,  # or the relevant user ID
                upvotes=0,
                downvotes=0,
                marked_as_official=False,
                date=datetime.datetime.now(),
            )
            db.session.add(new_answer)
            question = Questions.query.filter_by(questionid=question_id).first()
            if question:
                question.ai_answer = True
            for key in extracted_keywords:
                key_lower = lemmatize_text(key.lower())
                keyword_record = Keywords.query.filter_by(keyword=key_lower).first()
                if keyword_record:
                    keyword_record.count += 1
                else:
                    db.session.add(Keywords(keyword=key_lower, organization=org_id, count=1))
            db.session.commit()
            print("Gemini successfully answered and saved the response.")
            return response
    except Exception as e:
        print("Error in ask_question_function:", str(e))
        return None

@QA_bpt.route('/api/feedback', methods=['POST'])
def feedback():
    if session.get('user_id') == None:
        return jsonify({"error": "User not logged in"}), 400
    try:
        data = request.get_json()
        list = []
        messages = {}
        for i in data['conversation']:
            if i['messageId'] == data['messageId']:
                i['feedback'] = data['feedback']
            list.append(i)
        user = session.get('user_id')
        customersupport = CustomerSupport(userid=user, conversation_json=list, date=datetime.datetime.now(), solution="pending")
        db.session.add(customersupport)
        db.session.commit()
        messages[user] = list
        conversation = data.get('conversation')
        feedback = data.get('feedback')
        if not conversation or not feedback:
            return jsonify({"error": "Missing response or feedback"}), 400
        return jsonify({"message": "Feedback received successfully"}), 200
    except Exception as e:
        print(f"Error in feedback API: {e}")
        return jsonify({"error": "An error occurred while processing the feedback"}), 500

@QA_bpt.route('/api/demo')
def demo():
    customers = CustomerSupport.query.all()
    for customer in customers:
        question = customer.conversation_json
        for i in range(0, len(customer.conversation_json)):
            try:
                if question[i]['feedback']:
                    print('user message:' + question[i-1]['message'])
                    print('chatbot response: ' + question[i]['message'])
                    print('feedback: ' + question[i]['feedback'])
            except:
                continue
    return jsonify({"message": "Feedback received successfully"}), 200