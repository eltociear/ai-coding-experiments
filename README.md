## Analysis of AI-assisted coding using GPT-4

This reposistory includes code to reproduce all analyses used in the preprint:

Poldrack RA, Lu T, Begu\v{s} G (2023).  AI-assisted coding: Experiments with GPT-4. 

The entire workflow can be reproduced with the following commands (on a Mac or Linux system):

- Install (Conda)[https://conda.io/projects/conda/en/latest/user-guide/getting-started.html]
- Create a fresh conda environment using python 3.11: `conda create -n aicoding python=3.11`
- Activate the environment: `conda activate aicoding`
- Clone the repository: `git clone https://github.com/poldrack/ai-coding-experiments.git`
- Cd into the directory: `cd ai-coding-experiments`
- Install the requirements: `pip install -r requirements.txt`
- Run the entire workflow: `make all`


### Step 0: download code from github

- `download_github_code.py` uses the github api to download code files labeled as Python files.  The code used an invalid search term (dates are not actually accepted for github API calls) so the code was not date-limited.  Because the github search API is heavily rate-limited, the throughput is on the order of two files per minute.

For each file, the API is also used to load the commit history (to obtain the date of the commit) and the license information for the repository.

After running for a number of hours, a total of 2129 code files were downloaded.

These data are placed into `data/github/code`.

### Step 1: excluded bad files

`move_autogenerated_files.py` processes each of the downloaded files to remove files that violate some of the exclusion criteria (based primarily on the filtering approach used in the Codex paper) including:

    -  guessed as a Python file by `guesslang.Guess()`
    -  the presence of non-English language in the code according to `pycld2.detect()`
    -  the presence of potential markers of automatic generation
    -  the presence of potential obfuscation (the "if x - y:" pattern)
    -  the lack of any function definitions
    -  ntokens > 2500 or < 200
    -  max line length > 1000
    -  mean line length > 100
    -  

The excluded files are moved into `data/github/excluded`

### Step 2: process and filter code

Steps 2 and 3 is required for each dataset (both the initial github data and the subsequent data generated by GPT).

- `process_code.py` performs a set of analyses on each code file from a given source:
  - It runs the `flake8` linter and stores all messages.
  - It performs code quality analyses using the `radon` package, including cylcomatic complexity, Halstead metrics, and maintainability metric, along with raw metrics such as lines of code and comments and number of defined functions


Results from this step are saved to `results/<source>/code_analytics.json`.

### Step 3: summarize code metrics

- `summarize_code_info.py` summarizes the results from step 2 into a tabular data frame for further analysis.

Results from this step are saved to `results/<source>/code_analytics.csv`


### Step 3.5: Generating prompts for GPT 

This step is run after initially running steps 2-3 on the github code, to generate prompts for submission to the API.

- `generate_code_prompts.py` takes the code files from the intended source (with filtering if specified) and outputs the files to the specified directory. The files are given hashed names, with the key to the hashes stored in a json file with the same name as the output directory.


### Step 4: analysis of code metrics

`CodeAnalysis.py` is a notebook file (using jupytext py:percent mode) to analyze the results.


## Experiment history

Prompt 1:

- first analysis used the following prompt: "please recode the following Python code.  Please return the code within an explicit code cell."
- files used for analysis saved in github_code_for_recoding_prompt1.tgz and github_code_for_recoding_info_prompt1.json
- these resulted in some files that were difficult to extract code from, leading to use of Prompt 2

Prompt 2 (analyses included in preprint):
- second analysis used the following prompt: "Please refactor the following Python code to be more readable, adding or rewriting comments as needed. Please embed the code within an explicit code block, surrounded by triple-backtick markers."


### Coding prompts

- Please generate 20 prompts to ask a chatbot to create Python code to solve a variety of {statistical and data science, physics, theoretical computer science, ecology, economics} problems.  Please embed the code within an explicit code block, surrounded by triple-backtick markers.

- Resulting prompts (after additional prepartion with `prepare_code_prompts.py`) are in `data/conceptual_prompting/coding_prompts_clean_v2.txt`

These were submitted to the GPT-4 API.  The resulting output is found in `data/conceptual_prompting/outputs_of_ConceptualPromptingV2Split.json`.  
- These outputs were split into individual files using `prepare_conceptual_prompting_outputs.py`, and the results were stored in `data/conceptual_prompting/code`
- These files were further organized into individual testing directories by `prepare_conceptual_prompting_outputs.py`, with the outputs stored into `data/conceptual_prompting/testdirs`.  

## Testing analysis

- Test coverage was estimated using `run_coverage_tests_CP.py`, with outputs stored to `results/conceptual_prompting/code_coverage.csv`
- Execution was tested using `run_execution_tests_CP.py`, with output printed to screen
- Pytest tests were executed using `run_pytest_tests_CP.py`, with outputs stored to `results/conceptual_prompting/code_coverage.csv` (note that this assumes that coverage was already run).

