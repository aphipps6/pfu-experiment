pfu-experiment

This experiment is an economic lab experiment intended to test how participants allocate time between various inputs -- completing simple addition problems.

Admin Instructions:
once the server is running, you can access the admin console at https:\\your-url.com\admin

1. Generating an experiment: Enter a unique name for your expeirment, and then click "Generate Experiment." This will create a full experiment with all the addition problems using the default settings for time, length of problems, etc. Once generated, the experiment is now "active" in the administrator's dashboard.
2. If returning to a previously generated experiment, enter the experiment's unique name and click "Get", which will load that experiment into the admin dashbord.
3. "Reset Experiment": this just locks all the progress gates again. In other words, this is necessary when running a new session of the same experiment in order to control the flow of participants through the experiment. It locks participants at the "Welcome Screen" when they first log in.
4. Running the experiment:
     Once the experiment is generated, participants can log into it by visiting the app's homepage and entering the unique experiment id. They will see the welcome screen with the continue button disabled.
     The administrator can check who is logged in by clicking "List Participants." This will display all the email addresses of those who have logged in.
     Once ready, the administrator clicks "Randomize Treatments," which will randomly assign participants to having the control first or the treatment first. THIS IS IMPORTANT -- it needs to be done now once all participants are entered so the system knows how to randomize correctly.
     Once the basic instructions are read, the administrator can then enable the Risk Assessment and the Tutorial. Depending on the desired progress, the administrator can unlock all of the parts of the experiment for participants to work through on their own, or the administrator can require participants to wait between each section.
     Once all participants have completed, the administrator can show the earnings of all completed experiments in order to pay participants.

5. "Generate Fake Participants": This is useful for debugging purposes, and it will automatically generate 10 fake participant emails for debugging purposes.

Changing Parameters:
Payment parameters can be changed in the "admin_constants.py" file. This includes the value of time left on the clock, payments for participation, completing survey, etc

Changing the parameters of the experiment, such as time in each round, number of rounds, difficulty of questions, etc. requires editing the python code. Around line 600 in "administrator.py", there is a static function "generate_experiment". Below is a snippet of that function with comments on what to adjust:

```
 # Number of numbers to add in a "hard" question
   hard_n = 6
   # Number of digits for each number to be added in a "hard" question
   hard_digits = 2
   # Number of numbers to be added in an "easy" question
   easy_n = 3
   # Number of digits for each number in an "easy" question
   easy_digits = 2
            
   # Just a name for this class of questions -- questions will be stored by this name.
   # For consistency, these can be used repeatedly when generating experiments. If there
   # already exists a "question class name", the program will automatically use the
   # questions previously generated with that name.
   question_class_name = "add_hn06d2_en03d2"
   
   # How many possible questions are there in a round
   questions_per_round = 30
   # How many rounds are there in Control and Treatment
   number_of_rounds = 8
   # What is the time limit of each round?
   time_limit_minutes = 3
   # What is the value of leaving time on the clock? (set in AdminConstants)
   time_value = AdminConstants.TIME_VALUE

   # Time allowed for the practice session
   practice_time_limit = 2
   # Number of rounds in the practice session
   practice_n_rounds = 3
   
   generate_new_rc_rounds = True

   # Set the lower and upper limits of the payoff distribution for hard questions in the "high Variance" treatment
   a = 0.08
   b = 0.18

   # No need to adjust these
   sigma_squared = (1 / 12 * (b - a)) ** 2
   m = (b + a) / 2
   hard_payoff_distribution_high_variance = dict(name='uniform', a=a, b=b, sigma_squared=sigma_squared, mean=m)
            
   # BE SURE TO UPDATE HERE AS WELL
   hard_payoff_generating_function_high_variance = lambda: random.uniform(0.08, 0.18)
'''
