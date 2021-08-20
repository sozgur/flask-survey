from flask import Flask, request, render_template, redirect, flash, session
from flask_debugtoolbar import DebugToolbarExtension
from surveys import surveys

app = Flask(__name__)

# the toolbar is only enabled in debug mode:
app.debug = True
app.config['SECRET_KEY'] = "asdfasdfsdafdsfdasfaf"
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False
debug = DebugToolbarExtension(app)



satisfaction_survey = surveys["satisfaction"]

@app.route("/")
def home():
    """ Home Page of Survey """

    instructions = satisfaction_survey.instructions
    title = satisfaction_survey.title

    return render_template("home.html", title=title, instructions=instructions)

@app.route("/start")
def start():
    """ Start the survey """

    session["responses"] = []
    return redirect("/questions/0")


@app.route("/questions/<question_id>")
def show_question(question_id):
    """ Show questions and answers """
    idx = int(question_id)
    responses = session.get("responses")
    answered_count = len(responses)
    if answered_count != idx:
        flash("Invalid URL")
        return redirect(f"/questions/{answered_count}")

    question = satisfaction_survey.questions[idx]
    return render_template("question.html", question = question.question, choices = question.choices, next_id = idx+1)

@app.route("/thanks")
def thanks_page():
    """ Thank you page """

    return render_template("thanks.html")

@app.route("/answer")
def answer():
    """ Save the user's answer and 
        Redirect next question if there are no more questions redirect to thanks page """
    next_question_id = int(request.args["next_id"])
    answer = request.args.get("answer", None)

    if answer is None:
        flash("Before go to next page, you must select your answer!")
        return redirect(f"/questions/{next_question_id-1}")

    responses = session.get("responses", [])
    responses.append(answer)
    session["responses"] = responses
   
    if len(satisfaction_survey.questions) == next_question_id:
        return redirect("/thanks")
    return redirect(f"/questions/{next_question_id}")


