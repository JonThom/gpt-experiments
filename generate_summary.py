import re
import os
import sys
import textwrap
from time import time,sleep
import PyPDF3
import openai


def open_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as infile:
        return infile.read()


def save_file(filepath, content):
    with open(filepath, 'w', encoding='utf-8') as outfile:
        outfile.write(content)

openai.api_key = os.getenv('OPENAI_API_KEY')

def gpt3_completion_wrapper(
        prompt,
        engine="text-davinci-003", # see https://platform.openai.com/docs/model-index-for-researchers
        temp=0,
        context_length=4096, # https://platform.openai.com/docs/api-reference/completions/create#completions/create-max_tokens
        freq_pen=0.0,
        pres_pen=0.0,
        stop=None
        ):
    """_summary_ a wrapper around openai.Completion.create() with custom parameter defaults and error robustness

    Args:
        prompt (_type_): _description_
        engine (str, optional): _description_. Defaults to 'text-davinci-003'.
        temp (int, optional): _description_. Defaults to 0.
        max_tokens (int, optional): _description_. Defaults to 500.
        freq_pen (float, optional): _description_. Defaults to 0.0.
        qpres_pen (float, optional): _description_. Defaults to 0.0.
        stop (list, optional): _description_. Defaults to ['asdfasdf', 'asdasdf'].

    Returns:
        _type_: _description_
    """
    max_retry = 5
    retry = 0
    prompt = prompt.encode(encoding='ASCII',errors='ignore').decode()  # force it to fix any unicode errors
    while True:
        try:
            response = openai.Completion.create(
                engine=engine,
                prompt=prompt,
                temperature=temp,
                max_tokens=context_length - len(prompt), # number of tokens to generate
                frequency_penalty=freq_pen,
                presence_penalty=pres_pen,
                stop=stop
                )
            text = response['choices'][0]['text'].strip()
            text = re.sub('\s+', ' ', text)
            filename = '%s_gpt3.txt' % time()
            save_file('gpt3_logs/%s' % filename, prompt + '\n\n==========\n\n' + text)
            return text
        except Exception as oops:
            retry += 1
            if retry >= max_retry:
                return "GPT3 error: %s" % oops
            print('Error communicating with OpenAI:', oops)
            sleep(1)


if __name__ == '__main__':
    
    # get file path
    file = sys.argv[1]

    # files = os.listdir('pdfs/')
    # print(files)
    # output = ''
    # for file in files:
    # print(file)
    pdffileobj = open(file, 'rb')
    # pdffileobj = open('pdfs/%s' % file, 'rb')
    pdfreader = PyPDF3.PdfFileReader(pdffileobj)
    x = pdfreader.numPages
    paper = ''
    for i in list(range(0,x)):
        pageobj = pdfreader.getPage(i)
        text = pageobj.extractText()
        paper = paper + '\n' + text
    #print(paper)
    #exit()
    chunks = textwrap.wrap(paper, 6000)
    result = ''
    for chunk in chunks:
        prompt = open_file('prompt_summary_4.txt').replace('<<PAPER>>', chunk)
        summary = gpt3_completion_wrapper(prompt)
        result = result + ' ' + summary
    # print(result)
    # output = output + '\n\n%s: %s' % (file, result)
    output = '\n\n%s: %s' % (file, result)
    
    save_file('literature_review.txt', output)