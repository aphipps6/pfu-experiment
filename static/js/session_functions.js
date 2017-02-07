/**
 * Created by Aaron on 8/30/2016.
 */

function generateExperiment() {
    var name = document.getElementById("name").value;
    window.location.href = '/admin/generate_experiment/?experiment_name='.concat(name);
}

function getExperiment() {
    var name = document.getElementById("name").value;
    window.location.href = '/admin/get_experiment/?experiment_name='.concat(name);
}

function resetExperiment() {
    var name = document.getElementById("name").value;
    window.location.href = '/admin/reset_experiment/?experiment_name='.concat(name);
}

function loadQuestionText(button_id, round_key, round_minutes, step) {
    var first = startClockIfFirstQuestion(round_minutes);
    var n_easy = parseInt($('#easy_completed').text());
    var n_hard = parseInt($('#hard_completed').text());
    var difficulty;
    var question_number;
    if (button_id == "btn_easy") {
        difficulty = "easy";
        question_number = n_easy;
    } else {
        difficulty = "hard";
        question_number = n_hard;
    }

    $.ajax({
        type: "POST",
        url: "/load_question/",
        dataType: 'json',
        data: JSON.stringify({"question_difficulty": difficulty, "round_key": round_key, "first_question": first, "question_number": question_number}),
        success: function (response) {
            if (response['end_round']){
                endRound(round_key, step)
            } else {
                $("#problem").html(response['question_text']);
                $("#problem").collapse('show');
                $("#submitted_question_key").val(response['submitted_question_key']);
            }
        }
    });
    //disableOtherButton(button_id);
    document.getElementById("btn_hard").disabled = true;
    document.getElementById("btn_easy").disabled = true;

    makeSubmitButtonVisible(true);
    makeAnswerFieldVisible(true);
}

function startClockIfFirstQuestion(round_minutes){
    var n = parseInt($('#hard_completed').text()) + parseInt($('#easy_completed').text());
    if (n==0){
        initializeClock('clockdiv', round_minutes);
        $('#start_instructions').text('');
        return 1
    }
    return 0
}

function submitQuestionAnswer(round_key) {
    var answer = document.getElementById("input_user_answer").value;
    var submitted_question_key = document.getElementById("submitted_question_key").value;

    var difficulty;
    $.ajax({
        type: "POST",
        url: "/submit_question/",
        dataType: 'json',
        data: JSON.stringify({"submitted_answer": answer, "submitted_question_key": submitted_question_key,
            "round_key": round_key}),
        success: function (response) {
            $("#alert_success").fadeTo(2000, 500).slideUp(500, function(){
                $('#alert_success').slideUp(500);
            });
            updateQuestionCounter(response['difficulty']);
        }
    });
    resetAfterSubmission();
}

function updateQuestionCounter(difficulty){
    var n_easy = parseInt($('#easy_completed').text());
    var n_hard = parseInt($('#hard_completed').text());
    if (difficulty=="easy") {
        n_easy = n_easy + 1;
        $('#easy_completed').text(n_easy);
    }
    else {
        n_hard = n_hard + 1;
        $('#hard_completed').text(n_hard);
    }
}

function disableOtherButton(this_button_id) {
    if(this_button_id == "btn_easy"){
        document.getElementById("btn_hard").disabled = true;
    } else {
        document.getElementById("btn_easy").disabled = true;
    }
}

function resetAfterSubmission() {
    document.getElementById("btn_hard").disabled = false;
    document.getElementById("btn_easy").disabled = false;
    makeSubmitButtonVisible(false);
    makeAnswerFieldVisible(false);

    $('#problem').collapse('hide');
}

function makeSubmitButtonVisible(button_visible) {
    var btn = document.getElementById("btn_submit");

    if(button_visible == true) {
        btn.style.visibility = 'visible';
    } else {
        btn.style.visibility = 'hidden';
    }
}

function makeAnswerFieldVisible(field_visible) {
    var input = document.getElementById('div_input_user_answer');

    if(field_visible == true) {
        input.style.display = 'block';
    } else {
        $('#input_user_answer').val("");
        input.style.display = 'none';
    }
}

function navigationWarningMessage(){
    return "";
}

function endRound(round_key,step){
    window.onbeforeunload = null;
    window.location.href = '/end_round/?round_key='.concat(round_key).concat("&step=").concat(step);
}

function endRiskAssessment(menu_name,continue_link,participant) {
    var form = document.forms["risk_form"];
    var radioResults = [];
    for (var i = 0; i < form.elements.length; i++) {
        if (form.elements[i].type == 'radio') {
            if (form.elements[i].checked == true) {
                radioResults.push(form.elements[i].id);
            }
        }
    }
    var this_data = JSON.stringify({"radio_results": radioResults, "menu_name": menu_name, "participant": participant});
    $.ajax({
        type: "POST",
        url: "/risk_assessment_end/",
        dataType: 'json',
        data: this_data,
        success: function(result){
            window.location.href = continue_link;
        }
    });
}

function endSurvey(participant,continue_link) {
    var formResults = {
        'graduation_year': document.getElementById("graduation").value,
        'country': document.getElementById("country").value,
        'male': document.getElementById("male").checked,
        'female': document.getElementById("female").checked,
        'age': document.getElementById("age").value
    };

    var this_data = JSON.stringify({'results': formResults,'participant': participant});
    $.ajax({
        type: "POST",
        url: "/survey_end/",
        dataType: 'json',
        data: this_data,
        success: function(result){
            window.location.href = continue_link;
        }
    });
}


function startRoundTour() {
    // Instance the tour
    var tour = new Tour({
        steps: [
            {
                orphan: true,
                title: "Welcome!",
                content: "Welcome to the main page. This is a brief tour to help you get acquainted with how each round will work."
            },
            {
                element: "#round_header",
                title: "Round Counter",
                content: "This is the first round. Your session will be broken into rounds. You can always check how many rounds are left by looking up here.",
                placement: 'bottom'
            },
            {
                element: "#timer_column_div",
                title: "Timer",
                content: "This timer will start once you've selected a question. When it runs out, the round will automatically end."
            },
            {
                element: "#counter_column_div",
                title: "Counter",
                content: "This counts the number of attempted questions."
            },
            {
                element: "#btn_easy",
                title: "Easy Question",
                content: "Press this button to get an easy question. Go ahead, press it now!",
                reflex: true,
                template:   "<div class='popover tour'>\
                                <div class='arrow'></div>\
                                <h3 class='popover-title'></h3>\
                                <div class='popover-content'></div>\
                                <div class='popover-navigation'>\
                                    <button class='btn btn-default' data-role='prev'>« Prev</button>\
                                    <span data-role='separator'>|</span>\
                                    <button class='btn btn-default' data-role='next' disabled>Next »</button>\
                                    <button class='btn btn-default' data-role='end' disabled>End tour</button>\
                                </div>\
                              </div>"
            },
            {
                title: "delay",
                element: "#btn_easy",
                backdrop: false,
                template: "<div style=\"display: hidden\"></div>",
                duration: 2000
            },
            {
                element: "#input_user_answer",
                title: "Answer",
                content: "Now go ahead and answer the question! Don't worry, it doesn't matter if it's right this time.\
                            Just be sure you don't use spaces or any other characters. Press Next when you're done."
            },
            {
                element: "#btn_submit",
                title: "Submit",
                content: "Now go ahead and submit your answer!",
                reflex: true,
                template:   "<div class='popover tour'>\
                                <div class='arrow'></div>\
                                <h3 class='popover-title'></h3>\
                                <div class='popover-content'></div>\
                                <div class='popover-navigation'>\
                                    <button class='btn btn-default' data-role='prev'>« Prev</button>\
                                    <span data-role='separator'>|</span>\
                                    <button class='btn btn-default' data-role='next' disabled>Next »</button>\
                                    <button class='btn btn-default' data-role='end' disabled>End tour</button>\
                                </div>\
                              </div>",
                onNext: function (tour) {$("#btn_stop").prop("disabled",true);},
                duration: 2000
            },
            {
                element: "#round_main_div",
                backdrop: false,
                title: "Practice",
                content: "Now answer a few more questions just to get the hang of it. When you're done, press Next. \
                            Remember, this is just the tour so none of these answers matter!",
                duration: 25000,
                onNext: function (tour) {$("#btn_stop").prop("disabled",false);}
            },
            {
                element: "#btn_stop",
                title: "Stop Round",
                content: "Press this button to end the round. You will get some payoff for the time remaining",
                reflex: true,
                template:   "<div class='popover tour'>\
                                <div class='arrow'></div>\
                                <h3 class='popover-title'></h3>\
                                <div class='popover-content'></div>\
                                <div class='popover-navigation'>\
                                    <button class='btn btn-default' data-role='prev'>« Prev</button>\
                                    <span data-role='separator'>|</span>\
                                    <button class='btn btn-default' data-role='next' disabled>Next »</button>\
                                    <button class='btn btn-default' data-role='end' disabled>End tour</button>\
                                </div>\
                              </div>"
            }
        ],
        storage: false,
        backdrop: true,
        template:   "<div class='popover tour'>\
                        <div class='arrow'></div>\
                        <h3 class='popover-title'></h3>\
                        <div class='popover-content'></div>\
                        <div class='popover-navigation'>\
                            <button class='btn btn-default' data-role='prev'>« Prev</button>\
                            <span data-role='separator'>|</span>\
                            <button class='btn btn-default' data-role='next'>Next »</button>\
                            <button class='btn btn-default' data-role='end' disabled>End tour</button>\
                        </div>\
                      </div>"
    });

    // Initialize the tour
    tour.init();

    // Start the tour
    tour.start();
}

function startRoundEndTour() {
    // Instance the tour
    var tour = new Tour({
        steps: [
            {
                element: "#table_results",
                title: "Results Table",
                content: "This table shows you detailed results of all your rounds",
                placement: 'top'
            },
            {
                element: "#easy_question_section",
                title: "Easy Questions",
                content: "Here you can see all the results relating to easy questions in each round.",
                placement: 'bottom'
            },
            {
                element: "#easy_payoff_row",
                title: "Easy Questions",
                content: "In particular, you should pay attention to how much each easy question is worth each round.",
                placement: 'top'
            },
            {
                element: "#hard_question_section",
                title: "Hard Questions",
                content: "You have the same information for hard questions.",
                placement: 'top'
            },
            {
                element: "#time_section",
                title: "Time Information",
                content: "Here you can see useful information about your speed and how much you are earning from \
                ending rounds early.",
                placement: 'top'
            },
            {
                element: "#btn_next_round",
                title: "Continue",
                content: "Once you've looked over your round results, click here to start the next round."
            }
        ],
        storage: false,
        backdrop: true,
        orphan: true
    });

    // Initialize the tour
    tour.init();

    // Start the tour
    tour.start();
}

function continueToNextRound(new_link){
    window.onbeforeunload = null;
    window.location.href = new_link;
}

function waitForCondition(this_link){
    check_link = this_link;
    checkPauseCondition();
}
function checkPauseCondition(){
    $.ajax({
        type: "GET",
        url: check_link,
        dataType: 'json',
        data: JSON.stringify({}),
        success: function(result){
            if (result.keep_going == false) {
                /*var h = document.createElement("P");
                var t = document.createTextNode("waiting");
                h.appendChild(t);
                document.body.appendChild(h);*/
                setTimeout('checkPauseCondition()', 2500);
            } else {
                $('#continue_button').removeClass('disabled');
            }
        }
    });
}