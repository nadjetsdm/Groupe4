#!/usr/bin/env python
# coding: utf-8

# In[8]:


import pandas as pd
from langdetect import detect
import emoji
import deepl


# In[7]:


get_ipython().system('pip install deepl')
get_ipython().system('pip install emoji')
get_ipython().system('pip install langdetect')

# In[2]:


data = pd.read_csv(r"C:\Users\MOUENIS\Downloads\data (4).csv")


# In[3]:


data.shape


# In[4]:


#supprimer les lignes 23 car le détecteur ne fonctionne pas avec les emojis et les chiffres
print(data["review_text"][23])
data=data.drop(23).reset_index(drop=True) #emoji
data=data.drop(82).reset_index(drop=True) #  chiffres


# In[9]:


auth_key = "********"  # Replace with your key
translator = deepl.Translator(auth_key)



def translate_comments(comments):
    translated_comments = []
    for comment in comments:
        if detect_language(comment) == 'fr':
            translated_comments.append(comment)
        else:
            translation = translator.translate_text(comment, target_lang="FR")
            translated_comments.append(translation)
    return translated_comments



def detect_language(text):
    return detect(text)
data["review_text"] = translate_comments(data["review_text"])


# In[11]:


data.shape


# In[13]:


data.to_csv((r"C:\Users\MOUENIS\Downloads\data_cleaned.csv"), index=False)




