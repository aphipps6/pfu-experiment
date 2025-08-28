
This experiment is an economic lab experiment intended to test how participants allocate time between various inputs -- completing simple addition problems.

# Setting Up Local App Engine Development Server

## 1. Extract the application
After downloading the repository, extract the files to your desired location:
```bash
cd /path/to/your/project/folder
```

## 2. Install Google Cloud SDK
If you don't have it already:
- Download from https://cloud.google.com/sdk/docs/install
- Run the installer and follow the prompts
- Restart your terminal/command prompt after installation
  
Note that this will require Java 21+ to be installed

## 3. Initialize Google Cloud SDK
Set up authentication and default project:
```bash
gcloud init
```
Follow the prompts to log in and select your Google Cloud project.

## 4. Verify your project structure
Make sure you're in the directory containing your `app.yaml` file:
```bash
ls app.yaml
```
You should see your Flask app files, HTML templates, and the `app.yaml` configuration.

## 5. Install Python dependencies
The project has a `requirements.txt` file:
```bash
pip install -r requirements.txt
```

## 6. Run the local development server
```bash
dev_appserver.py .
```

Or using the newer gcloud command:
```bash
gcloud app run app.yaml
```

## 7. Access your application
Your app will be available at:
- http://localhost:8080

The development server automatically uses the Python version and dependencies specified in  `app.yaml` file.

## Troubleshooting
- **Port conflicts**: Use `--port=8081` to specify a different port
- **Authentication issues**: Run `gcloud auth login` if needed

# Admin Instructions:
once the server is running, you can access the admin console at https://your-url.com/admin

## Admin Console
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

## Downloading Data
Multitask performance data can be downloaded using the built-in function by first loading the experiment in the admin dashboard using "Get", and then visiting the url https://your-url.com/admin/download_multitask_data

Responses to the risk aversion questionaire can be downloaded similarly at https://your-url.com/admin/download_aversion_data


## Changing Parameters:
Payment parameters can be changed in the "admin_constants.py" file. This includes the value of time left on the clock, payments for participation, completing survey, etc

Changing the parameters of the experiment, such as time in each round, number of rounds, difficulty of questions, etc. requires editing the python code. Around line 600 in "administrator.py", there is a static function "generate_experiment". Below is a snippet of that function with comments on what to adjust. The specific upper and lower bounds of easy/hard questions in high/low variance is important to consider carefully for purposes of inference. The average of these bounds will automatically be used as the payoff in the "Control" rounds. The variance of high/low and easy/hard questions is also stored and reproduced when the data are downloaded.

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
```

# Generating your first experiment and using it
1. Navigate to https://your-url.com/admin
   <img width="1221" height="971" alt="image" src="https://github.com/user-attachments/assets/d628bd71-5e71-4a34-ad0a-46441de2593c" />


2. Enter a new name for the experiment, call it "my_first_experiment" and click "Generate". This can take a minute as the program generates hundreds of addition questions and assigns appropriate linking keys. When it's complete it should now display the name of your experiment at the top:
   <img width="1573" height="242" alt="image" src="https://github.com/user-attachments/assets/d9496a08-97fc-4479-982d-7968e75b5ade" />

Your expeirment is now ready to run.

3. In a separate window, navigate to https://your-url.com/ which will look like this:
   <img width="614" height="219" alt="image" src="https://github.com/user-attachments/assets/15df316f-b605-46c6-9b85-1b246d8342e7" />

4. Enter your experiment name, "my_first_experiment" and hit enter. This will take you to the loggin page:
   <img width="639" height="299" alt="image" src="https://github.com/user-attachments/assets/e275256a-4b57-42b8-8c55-52ec7fa729c6" />

5. Enter any email address -- note that this is only important as a user identifier; users do not need to use an email. If users somehow leave the experiment, they can return and use the same email and the experiment will attempt to put them back where they left off. For this demo, I've entered "first_participant@test.com" as the new user.
   
6. The user is now taken to the following introduction page
   <img width="1326" height="419" alt="image" src="https://github.com/user-attachments/assets/1f7a80f1-675f-4f51-aa75-11b378c5a405" />

7. Once they've entered, the admin console can be refreshed by clicking "refresh". It should now include the new participant as part of an expanding table
   <img width="1592" height="1012" alt="image" src="https://github.com/user-attachments/assets/c07d1ccb-56df-4914-b247-467d80ca1535" />

   This screen will provide updates as participants progress. It will show what they've completed and how many rounds in the treatment and control they've completed. The admin needs to refresh this page to see these updates.

8. Back to the user, if the user clicks "Continue" they will be brought to this screen (assuming the session has a lottery menu, which it does by default):
   <img width="1321" height="376" alt="image" src="https://github.com/user-attachments/assets/d28ea943-e0a6-4727-9d68-da32816717f1" />

9. Note that the user cannot progress unless the administrator unlocks it. THIS IS AN IMPORTANT PAUSE POINT: the administrator needs to randomize treatment and control, but that cannot be done until all participants are present. So the administrator waits until all participants are listed (the admin can also click "list participants" for a more concise list). Once they are all present, the administrator clicks "Randomize Treatments". Once randomized, then the admin clicks "Enable Risk"
    <img width="1494" height="189" alt="image" src="https://github.com/user-attachments/assets/5556c2a8-ff1c-46a9-8766-31a7beea93b2" />

NOTE: There is a small bug that will not correctly randomize unless there are more than one participants in the experiment. So for this demo, in order to see the full set of questions for participants, you will need to create two participants and walk them both through the experiment.

10. Once "enable Risk" is clicked, the "continue" button on the user screen will unlock. They enter the lottery menu:
<img width="1077" height="998" alt="image" src="https://github.com/user-attachments/assets/711c2240-b4e1-4adc-bddd-673b8dc5cd30" />

After completing the lottery menu, they click Continue and are brought to another holding screen for the tutorial.
<img width="1400" height="315" alt="image" src="https://github.com/user-attachments/assets/a8fdabfa-0a7f-4994-a746-ef72190804f3" />

11. Again, this is locked until the admin clicks "Enable Tutorial"
    <img width="1556" height="398" alt="image" src="https://github.com/user-attachments/assets/8a8663ee-6824-4ebd-8f63-58ac8412b832" />

12. As the user, you now go through a tutorial on how to use the app
    <img width="1098" height="803" alt="image" src="https://github.com/user-attachments/assets/6911ec13-04a6-4a10-b0f4-390a3f280f85" />

13. After the tutorial, the user enters the "Fixed Payment Session," in which they will answer questions but without a per-question payment. This is intended as practice for them as well as a rough baseline of their ability without any incentives. You can answer questions now or just hit "stop" through the three rounds.
    <img width="1343" height="760" alt="image" src="https://github.com/user-attachments/assets/d6e41444-4eb3-403f-8371-a25ffd6711a7" />

14. The user can then move on (assuming the next section is unlocked). In my case, the user was randomized to do the Constant Piece-Rate round first (Control)
    <img width="1346" height="641" alt="image" src="https://github.com/user-attachments/assets/d27e4c2d-180d-4d79-88ce-c24764da1c32" />

15. Once complete, the user will see a summary screen with their earnings
    <img width="679" height="620" alt="image" src="https://github.com/user-attachments/assets/6d0ad391-3986-4e26-b04c-e44154a9f7c0" />

