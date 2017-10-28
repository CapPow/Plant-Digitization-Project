# Plant-Digitization-Project
Plant Digitization Project -- Python Tkintering
- csv View 
    - contains the code for selecting and displaying a basic csv data. 
    - It also has the processing functions added in.

- kralNotePostProcessing 
    - contains initial code for api interaction functions. It presumes the user has already added a new field "scientificName".
    - This code should be adaptable to the final GUI on a by function basis.
    
- pandas2
    - Jacob's virtual environment that contains all source code for current kraldesk prototype solution.
        - Don't waste your time tinkering with this yet, my code is in an unclean state (will look like jibberish).
    - Comments below are for future use...
    - The kraldesk.py file is the main entry point for the application, so run this to see the application in action.
    - The virtual environment also requires you to have TK for Python and uses pip3 as it's Python package manager.
        - You will probably have issues if you try to work with this venv using another Python package installer/manager.
    - Change Readme to reflect added features on future commits
        - DONE: Add automatic location generation for table
	  - Goes through entire table with one button click
	  - DONE: Still need to check for similar lat/long in subsequent rows to gain possibility of API call reduction
	    - Recall that most specimens should be from similar site; this fact should imply a super-low API call necessity
	    - DONE: Rounded GPS coordinates to 3 decimal places. (34.12345, -84.12345) becomes (34.123, -84.123)
	- TODO: Add automatic scientific name generation for table
