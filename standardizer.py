import pandas as pd
import re
import os


'''
Notes on dictionaries:
1. Sources are various open-source dictionaries, with a special thanks to Matthias Buchmeier for compiling significant Ding-formatted OS dictionaries from Wiktionary
2. formatted dictionaries are saved with formatted Tesseract-OCR lang codes, e.g. chi_sim_dictionary.csv 

3. for MDict parsing, https://github.com/binhetech/mdict-parser. 
4. for persian - https://github.com/0xdolan/AryanpourDictionary
5. indonesian - https://seasite.niu.edu/Indonesian/download_the_indonesian_dictiona.htm


'''

def standardize_wiktionary_dictionary(filepath: str, lang_code: str, aggregate_duplicate_terms: bool=True) -> None: # Ding-formatted, sourced from https://en.wiktionary.org/wiki/User:Matthias_Buchmeier/download
    entries = []
    re_string = r'(\S*) \{([\S ]*)\} \[?([\S ]*)?\]? ?:: (.*)'
    with open(filepath,'r', encoding='utf-8') as f:
        for i, line in enumerate(f): 
            if re.match(re_string, line):
                term, POS, notes, definition = re.match(re_string, line).groups() # type: ignore
                entries.append([term, definition, POS, notes])

    lang_codes_dict = {'de-en':'deu',  'es-en':'spa', 'fr-en':'fra', 'ru-en':'rus'} # found in startup.py - these are Tesseract-OCR codes
    lang_dict_save_filepath = os.path.join("standardized_dictionaries", f"{lang_codes_dict[lang_code]}_dictionary.csv") 
    df = pd.DataFrame(entries)
    df.columns = ['term','definition','POS','notes']
    
    if aggregate_duplicate_terms: # aggregate definitions of same-term, multiple-definition cases
        df = df.groupby('term').agg({'definition': '; '.join,
                                    'POS': '/'.join,
                                    'notes': ' '.join}).reset_index()
    
    df.to_csv(lang_dict_save_filepath, index=False) 
    return

def standardize_korean_dictionary(filepath: str) -> None: # TODO: find better korean dictionary
    '''
    id	surface	hanja	gloss	level	created	source
    36653	등친의		removed		2006-01-16T09:52:46Z	engdic-151556@ezcorean:151556
    36654	등퇴장	登退場			2009-01-01T20:23:14Z	mr.hanja-215801@ezcorean:215801
     '''
    
    entries = []
    re_string = r'([\S; \-]*)?\t?([\S; \-]*)?\t?([\S_ ]*)?\t?([\S_ ]*)?\t?([\S_ ]*)?\t?([\S_ ]*)?\t?([\S_ ]*)\n'
    with open(filepath,'r', encoding='utf-8') as f:
        for line in f:
            if line.startswith('id'):
                continue
            if re.match(re_string, line):
                _, term, hanja, definition, _, _, _  = re.match(re_string, line).groups() # type: ignore
                entries.append([term, definition, hanja])

    korean_lang_code = 'kor'
    # lang_dict_save_filepath = f"{config.get_data_directory()}\\dictionaries\\{korean_lang_code}_dictionary.csv" # have to switch hyphen for underscore
    lang_dict_save_filepath = os.path.join("standardized_dictionaries", f"{korean_lang_code}_dictionary.csv")
    df = pd.DataFrame(entries)
    print(entries)
    print(df.shape)
    
    df.columns = ['term','definition','notes']

    df.to_csv(lang_dict_save_filepath, index=False)
    return

def standardize_u8_dictionary(filepath: str) -> None:
    '''
    trad /s sim /s [pinyin] /definition/
    B型超聲 B型超声 [B xing2 chao1 sheng1] /type-B ultrasound/
    B格 B格 [bi1 ge2] /variant of 逼格[bi1 ge2]/

    TODO: implement preference to not grab surnames instead of definition. surnames have capitalized pinyin e.g. 'Neng1' instead of 'neng1' in the dictionary
    '''
    
    entries = []
    re_string = r'(\S*) (\S*) \[(.*)\] \/(.*)\/'
    with open(filepath,'r', encoding='utf-8') as f:
        for line in f:
            if re.match(re_string, line):
                trad, sim, pinyin, definition = re.match(re_string, line).groups() # type: ignore
                print(sim)
                entries.append([trad, sim, pinyin, definition])
        
    # chi_sim_save_filepath = f'{config.get_data_directory()}\\dictionaries\\chi_sim_dictionary.csv'
    # chi_tra_save_filepath = f'{config.get_data_directory()}\\dictionaries\\chi_tra_dictionary.csv'
    chi_sim_save_filepath = os.path.join("standardized_dictionaries","dictionaries", f"chi_sim_dictionary.csv")
    chi_tra_save_filepath = os.path.join("standardized_dictionaries","dictionaries", f"chi_tra_dictionary.csv")
    
    df = pd.DataFrame(entries)
    
    df.columns = ['trad','term','pinyin','definition']
    df = df[['term','definition','pinyin', 'trad']]
    df.to_csv(chi_sim_save_filepath, index=False)
    df = df[['trad','definition','pinyin', 'term']]
    df.columns = ['term','definition','pinyin','sim']
    
    df.to_csv(chi_tra_save_filepath, index=False)
    return


def parse_fa_mdict_entries(entries):
    """
    file = 'AryanpourDictionary.txt'
    
    Args:
        entries (_type_): _description_

    Returns:
        _type_: _description_
    """
    
    parsed_entries = []

    for entry in entries:
        # Extract Persian term (text before first </div>)
        persian_term_match = re.search(r'^(.*?)</div>', entry)  # Match everything before the first </div>
        
        # Extract English definition (inside <div class="endef">)
        definition_match = re.search(r'<div class="endef.*?">(.*?)</div>', entry)  # Match inside <div class="endef"></div>

        # Get Persian term and English definition
        persian_term = persian_term_match.group(1).strip() if persian_term_match else None
        english_definition = definition_match.group(1).strip() if definition_match else None
        

        # Add the parsed entry to the list
        parsed_entries.append({
            'term': persian_term,
            'definition': english_definition,
        })

    return parsed_entries

def standardize_farsi_mdict(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        contents = f.read()

    split_contents = contents.split('faentry">')[1:] # first item in list is everything PRIOR to the farsi entries
    parsed_entries = parse_fa_mdict_entries(split_contents)
    df = pd.DataFrame((parsed_entries)) 
    df.to_csv(f'standardized_dictionaries/fa_dictionary.csv', index=False)

def standardize_indonesian_dict(filepath):
    '''
        In indonesian_dictionary.txt:
        lx = lexical entry
        de = definition (English)
        ge = gloss (one-word definition, English)
        dv = definition (vernacular)
        nt = note
        xv = example sentence (vernacular)
        dt = date last edited

    '''
    
    
    with open(filepath, 'r', encoding='utf-8') as f:
        contents = f.read()
    
    split_contents = contents.split('\\lx')[7:]
    entries = []
    for entry in split_contents:
        split_entry = entry.split('\n')
        term = split_entry[0].lstrip()
        short_definition, long_definition, vernacular_definition, note, example, = '','','','','' 
        for e in split_entry:
            
            if e.startswith('\\ge'):
                short_definition = e[4:]
            if e.startswith('\\de'):
                long_definition = e[4:]
            if e.startswith('\\dv'):
                vernacular_definition = e[4:]
            if e.startswith('\\nt'):
                note = e[4:]
            if e.startswith('\\xv'):
                example = e[4:]
        entries.append([term, short_definition,long_definition,vernacular_definition,note,example])
    columns = ['term','definition','long_definition','vernacular_definition','note','example']
    zipped = [dict(zip(columns,entry)) for entry in entries]
    df = pd.DataFrame(zipped)
    df.to_csv('standardized_dictionaries/ind_dictionary.csv', index=False)    
    
if __name__ == '__main__':
    # standardize_indonesian_dict('source_dictionaries/indonesian_dictionary.txt')
    filepath = 'source_dictionaries/kengdic.tsv'
    standardize_korean_dictionary(filepath)
    # langs = ['de-en', 'es-en', 'fr-en', 'ru-en']
    # for i, lang in enumerate(langs):
    #     dict_filepath = f'{config.get_data_directory()}\\dictionaries\\{lang}-enwiktionary.txt'
    #     standardize_wiktionary_dictionary(dict_filepath, lang)
