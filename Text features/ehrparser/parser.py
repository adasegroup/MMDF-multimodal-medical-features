from yargy import Parser, rule, and_, not_, or_
from yargy.pipelines import morph_pipeline
from yargy.interpretation import fact
from yargy.predicates import gram, normalized, eq, tag, dictionary, type, caseless, in_, gte,lte,custom
from joblib import Parallel, delayed
import re
from tqdm import tqdm
import pandas as pd
import sys
from multiprocessing import Pool
import string
import sys
from .mistakes_handler import multiple_replace, final_dict_k
sys.setrecursionlimit(999000)

def Version():
    print('This version was updated 10.05.2021')
    print(final_dict_k.keys())
    

import re
import string




def thyroid_diag(diagnosis):
    """
    The function determines if the patient has a symptom in the diagnosis.

    Args:
        diagnosis (dict): Patient electronic record card.

    Returns:
        bool: True if the patient has a symptom, False otherwise.
    """

    try:
        diagnosis = diagnosis['Диагноз']
    except:
        return False

    style = str.maketrans(dict.fromkeys(string.punctuation))
    diagnosis = diagnosis.translate(style).lower()

    match = re.search('\\s(эутиреоз)\\s', diagnosis)
    if match:
        return False
    else:
        pattern = '\\s(гипертиреоз|гипотиреоз|гипофункция щитовидной железы|гиперфункция щитовидной железы|тиреотоксикоз)\\s'
        match = re.search(pattern, diagnosis)
        if match:
            if re.search('\\s(субкомпенсация|субкомпенсированный)\\s', diagnosis):
                return True
            if re.search('\\s(компенсированный|медикаментозно|компенсация)', diagnosis):
                return False
            return True

    return False


def thyroid_lab(lab_res):
    """
    The function determines the presence of a symptom in the patient in these laboratory results.

    Args:
        lab_res (dict): Patient electronic record card.

    Returns:
        bool: True if the patient has a symptom, False otherwise.
    """

    try:
        lab_res = lab_res['Данные лабораторных исследований']
    except:
        return False

    match = re.search('(?:Т4|Т4 свободный|Т4 св|Т4 \(св\)|тироксин)[-\s:]+([0-9]*[.,]?[0-9]+)', \
                    lab_res, flags=re.IGNORECASE)
    if match:
        if float(match.group(1).replace(',','.')) < 12 or float(match.group(1).replace(',','.')) > 22:
            return True

    match = re.search('(?:трийодтиронин|Т3|Т3 своб|Т3 \(своб\)|Т3 св|Т3\(св\)|Т3 свободный)[-\s:]+([0-9]*[.,]?[0-9]+)', \
                    lab_res, flags=re.IGNORECASE)
    if match:
        if float(match.group(1).replace(',','.')) < 2.3 or float(match.group(1).replace(',','.')) > 6.3:
            return True

    match = re.search('(?:Тиреотропный гормон|ТТГ|ТТГ крови|тиреотропин)[-\s:]+([0-9]*[.,]?[0-9]+)', \
                    lab_res, flags=re.IGNORECASE)
    if match:
        if float(match.group(1).replace(',','.')) < 0.27 or float(match.group(1).replace(',','.')) > 4.2:
            return True

    return False


def extract_thyroid(record):
    """
    The function determines the presence of a feature in the Patient electronic record card.

    Args:
        record (dict): Patient electronic record card.

    Returns:
        bool: True if the patient has a symptom, False otherwise.
    """

    return thyroid_diag(record) or thyroid_lab(record)

def extract_AH(record):
    if (not 'Диагноз' in record.keys()):
        return None
    AH_predator = morph_pipeline([
        'артериальная гипертония',
        'артериальная гипертензия',
        'гипертоническая болезнь',
        'АГ',
        'ГБ'
    ])
    parser_ee = Parser(AH_predator)
    line = record['Диагноз']
    matches = list(parser_ee.findall(line))
    if len(matches) > 0:
        return True
    return False

# Works with df where a column has python dictionary
class EMHRParser:
    def __init__(self, progress_bar=tqdm):
        self._progress_bar = progress_bar


    def _process_record(self, record):
        result = {}
        result['thyroid_1'] = extract_thyroid(record)
        result['hyp'] = extract_AH(record)
        return result
    

    def __call__(self, records, n_jobs, lib):
        
        if lib == "joblib":
            tmp = Parallel(n_jobs=n_jobs)(self._progress_bar([delayed(self._process_record)(record)
                                                              for record in records]))
            results = {i : val for i, val in enumerate(tmp)}
            return pd.DataFrame.from_dict(results, orient='index')
        if lib == "multiprocessing":
            tmp = []
            with Pool(n_jobs) as p:
                max_ = len(records)
                with tqdm(total = max_) as pbar:
                    for _, value in self._progress_bar(enumerate(p.imap(self._process_record, records))):
                        tmp.append(value)
                        pbar.update()
            results = {i : val for i, val in enumerate(tmp)}
            return pd.DataFrame.from_dict(results, orient='index')
