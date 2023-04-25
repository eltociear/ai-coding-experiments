import json
import os
import argparse


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

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--input', type=str, default='data/gpt4/outputs_of_selected_for_recoding_prompt2.json')
    parser.add_argument('-o', '--outdir', type=str, default='data/gpt4/code')
    parser.add_argument('--save_raw', action='store_true')
    parser.add_argument('--raw_outdir', type=str, default='data/gpt4/raw_output')
    return parser.parse_args()

if __name__ == "__main__":
    args = parse_args()

    with open(args.input, 'r') as f:
        model_outputs = json.load(f)
    print(f'Loaded {len(model_outputs)} recoded files')

    if os.path.exists('data/github/selected.json'):
        print('Loading key info for github files')
        with open('data/github/selected.json', 'r') as f:
            github_info = json.load(f)
    else:
        github_info = None

    os.makedirs(args.outdir, exist_ok=True)

    if args.save_raw:
        # in case we want to save the full raw output for debugging
        raw_outdir = 'github_code_recoded_gpt4_raw_output'
        os.makedirs(raw_outdir, exist_ok=True)
   

    items = {}
    for item in model_outputs:
        key = item['key']
        print(key)
        items[key] = item
        # this was missed in the earlier filter, so we remove them here
        if 'Generated by Django' in item['answer']:
            print('Skipping Django file')
            continue
        if args.save_raw:
            raw_filename = github_info[key]['filename'].replace(
                'github_code', raw_outdir)
            assert raw_filename != github_info[key]['filename']
            with open(raw_filename, 'w') as f:
                f.write(item['answer'])
        items[key]['code'] = extract_python_code(item['answer'], key)
        #text = extract_text_from_comments_and_strings(item['code'])
        if github_info is not None and key in github_info:
            filename = github_info[key]['filename'].replace(
                'github', 'gpt4')
            assert filename != github_info[key]['filename']
        else:
            filename = os.path.join(args.outdir, key.replace('/', '_') + '.py')

        with open(filename, 'w') as f:
            f.write('\n'.join(item['code']))
        
