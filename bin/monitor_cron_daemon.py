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


date_format = ' '.join("""
[A-Z][a-z][a-z]
[A-Z][a-z][a-z] 
[0-9]+
[0-9][0-9]:[0-9][0-9]:[0-9][0-9]
[A-Z][A-Z]
[A-Z][A-Z][A-Z]
[0-9][0-9][0-9][0-9]
""".strip().split('\n'))


# In[5]:


cron_sessions = []
for line in output.strip().split('\n'):
    if re.match(date_format, line):
        cron_session = datetime.datetime.strptime(line, '%a %b %d %I:%M:%S %p %Z %Y')
        cron_sessions.append(cron_session.date())
cron_sessions = sorted(set(cron_sessions))


# In[6]:


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
    xticks.append(str(curr_day))
    curr_day += datetime.timedelta(1)
    
streaks = np.array(streaks)
incomplete = np.array(incomplete)


# In[7]:


plt.bar(np.arange(len(streaks)), streaks, color='limegreen')
plt.bar(np.arange(len(streaks)), incomplete*streaks.max(), color='red')
plt.xticks(np.arange(len(streaks)), xticks, rotation=45)
plt.yticks(np.arange(streaks.max()+1))
plt.ylabel('Days Since Last Failed Wake')
plt.title('Cron Activity')
plt.tight_layout()
plt.savefig(f"{script_dir}/../cron_log/plot_cron_activity.png")
plt.close()

