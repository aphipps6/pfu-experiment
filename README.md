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
Payment parameters can be changed in the "admin_constants.py" file.
