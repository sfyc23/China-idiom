# -*- coding: utf-8 -*-
"""
Project: China-idiom
Creator: DoubleThunder
Create time: 2019-10-12 11:45
Introduction:
"""

import pandas as pd
import os

current_dir = os.path.abspath(os.path.dirname(__file__))
csv_name = os.path.join(current_dir, 'idiom.csv')
idiom_df = pd.read_csv(csv_name, index_col=0, engine='python', encoding='utf-8')

clean_complie = r'[^\u4e00-\u9fa5]'
pinyin_complie = r'[, ，\s]+'
no_letter_complie = r'[āáǎàōó̀ǒòǒǜùǔǚǖüūǘúīíǐìēéěèêếềńňǹḿ]'
pinyin_letter_dict = {
    "ā": "a", "á": "a", "ǎ": "a", "à": "a",
    "ō": "o", "ó": "o", "̀ǒ": "o", "ò": "o", "ǒ":"o",
    "ǜ": "u", "ù": "u", "ǔ": "u", "ǚ": "u", "ǖ":"u",
    "ü": "u", "ū": "u", "ǘ": "u", "ú": "u",
    "ī": "i", "í": "i", "ǐ": "i", "ì": "i",
    "ē": "e", "é": "e", "ě": "e", "è": "e",
    "ê": "e", "ế": "e", "ề": "e",
    "ń": "n", "ň": "n", "ǹ": "n",
    "ḿ": "m"
}