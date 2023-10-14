#!/usr/bin/env python
# coding: utf-8

# In[ ]:


pip install langchain


# In[ ]:


pip install openai


# In[ ]:


pip install llm


# In[ ]:


pip install langchain.agents


# In[1]:


# Importing libraries and modules

import os
import datetime
import openai
from langchain.llms import OpenAI
from langchain.agents import initialize_agent
from langchain.agents.agent_toolkits import ZapierToolkit
from langchain.utilities.zapier import ZapierNLAWrapper
from langchain.agents import Tool
from langchain.memory import ConversationBufferMemory
from langchain.chat_models import ChatOpenAI

from langchain import LLMChain
from langchain.agents import Tool, AgentExecutor
from langchain.prompts.chat import (
    ChatPromptTemplate,
    MessagesPlaceholder,
    SystemMessagePromptTemplate,
    HumanMessagePromptTemplate,
)

from langchain import PromptTemplate


# In[2]:


#Set up the enviornment

os.environ["OPENAI_API_KEY"] = "******"

os.environ["ZAPIER_NLA_API_KEY"] = "*****"


# In[3]:


#Template_1

template_1 = """

Do not generate user responses on your own and avoid repeating questions.

You are a helpful scheduling assistant. Your only task is to help user schedule a service appointment with a bank. 
Bank only provides these services: opening an account, providing loans or deposit money. Bank is open from 8 am to 5 pm EST everyday and are available to book as long as it is open.
To schedule a meeting, you need to collect information in the conversation such as full name, service type, location, datetime and email address. 
Collect all of the information one by one, and do not ask for service type again if user has stated it in the conversation before. 
Allow users to input time in any format, and you'll save it in a EST 24-hours format in the backend to display at the end. 
After collecting all of the information, make sure you display the details to the user at the end in this format:

Full Name: 
Service Type:
Location:
dateime:
Email Address: 

Respond with just 'Thank you for choosing us' at the end.  

{chat_history}

"""

system_message_prompt = SystemMessagePromptTemplate.from_template(template_1)
human_template="{query}"
human_message_prompt = HumanMessagePromptTemplate.from_template(human_template)
chat_prompt = ChatPromptTemplate.from_messages([system_message_prompt,human_message_prompt])


# In[4]:


#Assigning model and tools

chat = ChatOpenAI(model="gpt-3.5-turbo",temperature=0.7)

memory = ConversationBufferMemory(memory_key="chat_history")

zapier = ZapierNLAWrapper()
toolkit = ZapierToolkit.from_zapier_nla_wrapper(zapier)
tools = toolkit.get_tools() 


# In[6]:


#Chat Cain

def gpt_response(query):
    
    chain = LLMChain(llm = chat, prompt = chat_prompt, memory = memory)
    response = chain.run(query)
    
    return response        

#Agent Chain

agent_chain = initialize_agent(tools, llm = chat, agent = "zero-shot-react-description", verbose = True)


# In[7]:


#Extract Function

import re

def extract_information(conversation, pattern):
    for line in conversation:
        match = re.search(pattern, line, re.IGNORECASE)
        if match:
            return match.group(1)
    return None


# In[8]:


today = datetime.datetime.today()
weekday_name = today.strftime('%A')
today_date = str(datetime.date.today())


# In[9]:


#Conversation flow

import re

conversation = []

while True:
    
    query = input("Human: " )
    conversation.append('User: ' + query)

    output = gpt_response(query)
    conversation.append('Bot: ' + output)
    
    print(output)
    
    # Extract name information
    pattern_name = r'\bFull Name:\s*(.*)'
    name = extract_information(conversation, pattern_name)
    
    # Extract service information
    pattern_service = r'\bService Type:\s*(.*)'
    service = extract_information(conversation, pattern_service)
    
    # Extract location information
    pattern_location = r'\bLocation:\s*(.*)'
    location = extract_information(conversation, pattern_location)
    
    # Extract time information
    pattern_time = r'\bdatetime:\s*(.*)'
    datetime = extract_information(conversation, pattern_time)
       
    # Extract email information
    pattern_email = r'\bEmail Address:\s*(.*)'
    email = extract_information(conversation, pattern_email)

    #Performing Action
    if name and service and location and datetime and email:
        conversation.append("""

                Use {tools} for sending an email to the user provided email address in the below format:
                
                ####
                
                Dear [Full Name],
                
                We hope this email finds you well. We are writing to confirm the details of our scheduled meeting at the Bank.
                Please review the information below:
                
                Service Type: [Service Type]
                Location: [Location]
                datetime: [datetime]

                If you have any questions or need to make any changes, please don't hesitate to reach out to us. You can reply to this email or contact us directly at (857)-999 wxyz.

                We look forward to meeting with you on [datetime]. Thank you for choosing our services, and I am excited to assist you.

                Best regards,
                
                Bank.
                
                ####
                
                Also, make use of this {tools} to schedule a meeting on a google calander based on collected information.
                
                """
                           )
        scheduler = agent_chain.run(conversation)
        print(scheduler)
        break
    
    if query == "bye":
        print("bye")
        break    


# In[ ]:


## Conversation Collected

def save_conversation(conversation):
    with open('conversation.txt', 'w') as file:
        file.write('\n'.join(conversation))

def display_conversation():
    with open('conversation.txt', 'r') as file:
        conversation = file.readlines()

for line in conversation:
    print(line.strip()) 


# In[ ]:





# In[ ]:




