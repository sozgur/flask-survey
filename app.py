from flask import Flask, request, render_template, redirect, flash, session, make_response
from flask_debugtoolbar import DebugToolbarExtension
from surveys import surveys

app = Flask(__name__)

# the toolbar is only enabled in debug mode:
app.debug = True
app.config['SECRET_KEY'] = "asdfasdfsdafdsfdasfaf"
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False
debug = DebugToolbarExtension(app)


@app.route("/", methods=["GET", "POST"])
def home():
    """ Home Page of Survey """

    if request.method == 'POST':
        # picked the survey and set session with picked survey
        survey_code = request.form["code"]

        #check if survey completed before
        if request.cookies.get(survey_code):
            return render_template("completed.html")

        survey = surveys[survey_code]
        session["picked_survey"] = survey_code
        return render_template("survey.html", title=survey.title, instructions=survey.instructions)
    else:
        # Show survey list for pick a survey
        return render_template("survey_list.html", surveys=surveys)


@app.route("/start")
def start():
    """ Start the survey """

    session["responses"] = []
    return redirect("/questions/0")


@app.route("/questions/<int:question_id>")
def show_question(question_id):
    """ Show questions and answers """
    responses = session.get("responses")
    picked_survey = session["picked_survey"]

    answered_count = len(responses)

    if answered_count != question_id:
        flash("Invalid URL")
        return redirect(f"/questions/{answered_count}")
    # take a question from picked survey
    question = surveys[picked_survey].questions[question_id]
    return render_template("question.html", question = question.question, choices = question.choices, next_id = question_id+1)


@app.route("/answer")
def answer():
    """ Save the user's answer and 
        Redirect next question if there are no more questions redirect to thanks page """
    next_question_id = int(request.args["next_id"])
    answer = request.args.get("answer", None)

    if answer is None:
        flash("Before go to next page, you must select your answer!")
        return redirect(f"/questions/{next_question_id-1}")

    picked_survey = session["picked_survey"]
    responses = session.get("responses", [])
    responses.append(answer)
    session["responses"] = responses
   
    if len(surveys[picked_survey].questions) == next_question_id:
        return redirect("/thanks")
    return redirect(f"/questions/{next_question_id}")


@app.route("/thanks")
def thanks_page():
    """ Thank you page """

    survey_code = session["picked_survey"]

    html = render_template("thanks.html")

    resp = make_response(html)
    resp.set_cookie(survey_code, "completed", max_age=60)

    return resp


