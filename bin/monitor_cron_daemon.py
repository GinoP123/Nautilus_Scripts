#!/usr/bin/env python3
# coding: utf-8

# In[1]:


import os, glob
import re
import matplotlib.pyplot as plt
import numpy as np
import ipynbname
import subprocess as sp
import datetime
import sys


# In[2]:


script_dir = os.path.dirname(sys.argv[0])


# In[3]:


with open(f"{script_dir}/../cron_log/cron_log.txt") as infile:
    output = infile.read()


# In[4]:


def char_to_match(ch):
    if ch.isnumeric():
        return '[0-9]'
    elif ch.isalpha() and ch == ch.upper():
        return '[A-Z]'
    elif ch.isalpha():
        return '[a-z]'
    else:
        return ch
char_to_match = np.vectorize(char_to_match)


# In[5]:


date_format = sp.run("date", shell=True, capture_output=True).stdout.decode().strip()
date_format = ''.join(char_to_match(list(date_format)))


# In[6]:


cron_sessions = []
for line in output.strip().split('\n'):
    if re.match(date_format, line):
        cron_session = datetime.datetime.strptime(line, '%a %b %d %I:%M:%S %p PST %Y')
        cron_sessions.append(cron_session.date())


# In[7]:


streaks = []
incomplete = []
xticks = []

index = 0
curr_day = cron_sessions[index]
while curr_day < datetime.datetime.now().date():
    if index < len(cron_sessions) and curr_day == cron_sessions[index]:
        streaks.append(streaks[-1] + 1 if streaks else 1)
        incomplete.append(0)
        index += 1
    else:
        streaks.append(0)
        incomplete.append(1)
    curr_day += datetime.timedelta(1)
    xticks.append(str(curr_day))
streaks = np.array(streaks)
incomplete = np.array(incomplete)


# In[8]:


plt.bar(np.arange(len(streaks)), streaks, color='limegreen')
plt.bar(np.arange(len(streaks)), incomplete*streaks.max(), color='red')
plt.xticks(np.arange(len(streaks)), xticks, rotation=45)
plt.yticks(np.arange(streaks.max()+1))
plt.ylabel('Days Since Last Failed Wake')
plt.title('Cron Activity')
plt.tight_layout()
plt.savefig(f"{script_dir}/../cron_log/plot_cron_activity.png")
plt.close()

