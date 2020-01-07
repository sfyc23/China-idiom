成语与成语接龙查询工具（Python 版）
=============================
[![pypi](https://img.shields.io/badge/pypi-0.0.2-yellow.svg)](https://pypi.org/project/china-idiom/) 
![python_vesion](https://img.shields.io/badge/python-%3E3-green.svg)  

   
用于成语接龙。

## 关于

* GitHub: <https://github.com/sfyc23/China-idiom>  
* PyPI: <https://pypi.org/project/china-idiom/> 
* Python version: >= 3.5
* License: MIT license  

## 特性

1. 用于玩转成语接龙的种种方法。


## 安装

    $ pip install china-idiom

## 升级

    $ pip install -U china-idiom
     

## 依赖库

    pandas>=0.23.4

## 使用示例

首先导入库 
```
import china_idiom as idiom
``` 

### 1. 判断一个词是否是成语。 
```
idiom.is_idiom('一心一意')
>>> True
```

### 2.  搜索成语 
功能说明：
``` 
search_idiom(word, position=0, count=1, is_detail=False)
    :param word: str,关键词
    :param position: int, 所在位置，默认为：0
    :param count: int ，返回最大数量 默认为： 1
    :param is_detail: bool,是否返回详细内容（包括：拼音，拼音缩写，解释，来源，造句）
    :return: list
```

实用式例 1：简单查询    

```
idiom.search_idiom(word='猪')
>>> ['指猪骂狗']
```
  
实用式例 2：查询成语第 2 个字是『心』的成语，最大查询数量为 2, 返回详细内容。  

```
idiom.search_idiom(word='心', position=2, count=2, is_detail=True)
>>> 
[{'word': '热心快肠',
  'pinyin': 'rè xīn kuài cháng',
  'abbreviation': 'rxkc',
  'explanation': '形容热情直爽。',
  'derivation': '柯岩《奇异的书简·东方的明珠三》也许因为是她热心快肠，群众有事爱找她拿主意，帮个忙。”',
  'example': '无'},
 {'word': '人心大快',
  'pinyin': 'rén xīn dà kuài',
  'abbreviation': 'rxdk',
  'explanation': '快痛快。指坏人坏事受到惩罚或打击，使大家非常痛快。',
  'derivation': '明·沈德符《万历野获编·立枷》东山受恩反噬，其罪盖浮于诸龙光。当时人心大快，佐以此得缙绅闻声，然亦不云立枷。”',
  'example': '无'}]
```

### 3. 成语接龙  

功能说明：  

```
def next_idioms_solitaire(word, count=1, heteronym=True, smaller=False):
    """
    :param word: str, 成语
    :param count: int, 返回数量
    :param heteronym: bool,是否可以使用同音字
    :param smaller: bool, 是否选择尽可能的少的后续
    :return: list
    """
```

式例代码 1 :  
```
idiom.next_idioms_solitaire('一生一世')
>>> ['逝将去汝']
```

式例代码 2 ：

```
idiom.next_idioms_solitaire('一生一世', count=3, heteronym=False)
>>> ['世态炎凉', '世代书香', '世上无难事']
```
代码说明：获取可接『一生一世』的成语。返回最大数量为 3。不能用于同音字。 

### 4. 判断两个成语是否能接龙。

示例代码：
  
```
idiom.is_idiom_solitaire('一生一世', '逝将去汝')
>>> True

idiom.is_idiom_solitaire('一生一世', '生生世世')
>>> False

```

### 5. 自动接龙模式。  

输入一个汉字或者成语，程序自动输出一组成语接龙的结果。  

功能说明： 

```
def auto_idioms_solitaire(word, max_count=10, heteronym=True):
    """
    自动接龙模式 - 输入一个汉字或者成语，程序自动输出一组成语接龙的结果。
    :param word: str 起始汉字或者成语。
    :param max_count: int, 最大长度。默认最大长度：20。
    :param heteronym: bool, 是否可以用同音字。默认 True。
    :return: list
    """
```

示例代码：  
```
idiom.auto_idioms_solitaire('一生一世')
>>>
["一生一世", "适心娱目", "目兔顾犬", "犬马之力", "立时三刻", "刻意经营", "蝇粪点玉", "鬻驽窃价", "驾轻就熟", "熟路轻辙"]
```

## 资源文件

* 源数据来源：https://github.com/pwxcoo/chinese-xinhua。  

    经过大量较正后，得到下一份数据：  

* [idiom.csv](https://github.com/sfyc23/China-idiom/blob/master/china_idiom/idiom.csv)


## Lincese

    MIT License
    
    Copyright (c) 2019  Thunder Bouble
    
