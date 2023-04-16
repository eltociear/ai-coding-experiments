import json
from extract_text import extract_python_code, extract_text_from_comments_and_strings
import re
import os


def extract_python_code(text, key):
    # this is version for GPT4 where
    # all outputs have a code block

    lines = text.split('\n')
    python_code = []
    record = False
    for line in lines:
        # check for key
        if key in line:
            continue
        if not record and line.startswith('```'):
            record = True
            continue
        # deal with various unmarked endings
        if record and line.startswith('```'):
            break
        if record:
            python_code.append(line)
    return python_code

if __name__ == "__main__":
    with open('data/gpt4/outputs_of_selected_for_recoding_prompt2.json', 'r') as f:
        gpt4_recoded_output = json.load(f)
    print(f'Loaded {len(gpt4_recoded_output)} recoded files')

    with open('data/github/selected.json', 'r') as f:
        github_info = json.load(f)

    outdir = 'data/gpt4/code'
    os.makedirs(outdir, exist_ok=True)

    save_raw = False
    if save_raw:
        # in case we want to save the full raw output for debugging
        raw_outdir = 'github_code_recoded_gpt4_raw_output'
        os.makedirs(raw_outdir, exist_ok=True)
   

    items = {}
    for item in gpt4_recoded_output:
        key = item['key']
        print(key)
        items[key] = item
        # this was missed in the earlier filter, so we remove them here
        if 'Generated by Django' in item['answer']:
            print('Skipping Django file')
            continue
        if save_raw:
            raw_filename = github_info[key]['filename'].replace(
                'github_code', raw_outdir)
            assert raw_filename != github_info[key]['filename']
            with open(raw_filename, 'w') as f:
                f.write(item['answer'])
        items[key]['code'] = extract_python_code(item['answer'], key)
        #text = extract_text_from_comments_and_strings(item['code'])
        filename = github_info[key]['filename'].replace(
            'github', 'gpt4')
        assert filename != github_info[key]['filename']
        with open(filename, 'w') as f:
            f.write('\n'.join(item['code']))
        
