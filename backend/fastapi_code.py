
import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict




from dotenv import load_dotenv,find_dotenv

#### Langchian ####
#OpenAI
from langchain_openai import ChatOpenAI
from langchain_openai import OpenAIEmbeddings

## Prompt 
from langchain_core.prompts import ChatPromptTemplate, PromptTemplate

#Document Loader
from langchain_community.document_loaders import DirectoryLoader, TextLoader
from langchain_community.document_loaders import JSONLoader
from langchain_community.document_loaders.merge import MergedDataLoader
from langchain_community.document_loaders import UnstructuredMarkdownLoader

#Splitter
from langchain.text_splitter import RecursiveCharacterTextSplitter


from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain.chains import create_history_aware_retriever, create_retrieval_chain
from langchain_core.messages import AIMessage, HumanMessage


from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_community.document_loaders import WebBaseLoader
from langchain_core.chat_history import BaseChatMessageHistory
from langchain_core.runnables.history import RunnableWithMessageHistory


# Index
from langchain_community.vectorstores import Chroma, LanceDB, FAISS
from langchain.retrievers import BM25Retriever, EnsembleRetriever
from langchain_core.documents import Document


##Memory
from langchain.chains import create_history_aware_retriever
from langchain_core.prompts import MessagesPlaceholder


## Others
from langchain_core.runnables import RunnableLambda
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough

#Helpers
import datetime
from typing import Literal, Optional, Tuple

import langchain



class RAG_Pipeline:
    def __init__(self):

        load_dotenv(find_dotenv())
        self.embedding = OpenAIEmbeddings()
        self.chat_history = []
        try:
             vectorstore = Chroma(persist_directory="./data/chroma_db", embedding_function=self.embedding)
             self.data_loaded = True
        except:
             self.data_loaded = False
       
        self.chatbot = self.initialize_chatbot_chain()



    #QA
    def initialize_chatbot_chain(self):
      
      #############
        # #Document Loader
        if self.data_loaded == False:
            # loader = DirectoryLoader('./data', glob="**/*.md", loader_cls=TextLoader)
            loader1 = UnstructuredMarkdownLoader('./data/full_data.md')
            
            loader_pdf = DirectoryLoader('./data/faq', glob="**/*.pdf")
            

            combined_loader = MergedDataLoader(loaders=[loader1, loader_pdf])
            docs = combined_loader.load()


            text_splitter = RecursiveCharacterTextSplitter.from_tiktoken_encoder(
                chunk_size=600,
                chunk_overlap=200)

            # Make splits
            splits = text_splitter.split_documents(docs)

            #The data is small so saving locally
            vectorstore = Chroma.from_documents(documents=splits,
                                        embedding=self.embedding, persist_directory="./data/chroma_db")
        
        
        ####################

        vectorstore = Chroma(persist_directory="./data/chroma_db", embedding_function=self.embedding)
       
        self.retriever = vectorstore.as_retriever(search_kwargs={"k": 5})

        # self.retriever = vectorstore.as_retriever(search_type="mmr",search_kwargs={"k": 5})

        
        chatbot_llm = ChatOpenAI(model_name="gpt-4o", temperature=0.4)

         ####################

        contextualize_q_system_prompt = (
        "Given a chat history and the latest user question "
        "which might reference context in the chat history, "
        "formulate a standalone question which can be understood "
        "without the chat history. Do NOT answer the question, "
        "just reformulate it if needed and otherwise return it as is."
        )
        contextualize_q_prompt = ChatPromptTemplate.from_messages(
        [
        ("system", contextualize_q_system_prompt),
        MessagesPlaceholder("chat_history"),
        ("human", "{input}"),
        ]
        )
        history_aware_retriever = create_history_aware_retriever(
            chatbot_llm, self.retriever, contextualize_q_prompt
        )


        ### Answer question ###
        system_prompt = (
            "You are an assistant for question-answering about how Artisan and its AI Assistant Eva. "
            "When asking you anything people are basically asking Artisan"
            "All the answers shoud be relevent to Artisan "
            "Use the following pieces of retrieved context to answer "
            "the question. If you don't know the answer, say that you "
            "don't know. Make sure to summarize slightly.  "
            "answer concise."
            "\n\n"
            "{context}"
        )
        qa_prompt = ChatPromptTemplate.from_messages(
            [
                ("system", system_prompt),
                MessagesPlaceholder("chat_history"),
                ("human", "{input}"),
            ]
        )
        question_answer_chain = create_stuff_documents_chain(chatbot_llm, qa_prompt)

        rag_chain = create_retrieval_chain(history_aware_retriever, question_answer_chain)


       
        return rag_chain
        


    #RUN
    def run(self, user_query):

        chatbot_response = self.chatbot.invoke({"chat_history": self.chat_history, "input": user_query})


        self.chat_history.extend(
        [
            HumanMessage(content=user_query),
            AIMessage(content=chatbot_response["answer"]),
        ]
        )

        # print(user_query)
        # print('MEMORY')
        # print(self.chat_history)
        # print(chatbot_response)

        # print('LEN OF MEM: ', len(self.chat_history))
        if len(self.chat_history) > 20:
            dummy = self.chat_history.pop(0)
            dummy = self.chat_history.pop(0)
            del dummy
        

        return chatbot_response["answer"]
        


app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

class UserQuery(BaseModel):
    userQuery: str

# def get_rag_pipeline():
#     return chatbot

 # Initialize models
print('Initializing RAG Pipeline and Databases')
chatbot = RAG_Pipeline()
print('Chatbot Ready!!')

@app.post("/api/get_ai_message")
async def get_ai_message(query: UserQuery) -> Dict[str, str]:
    
        # print('Query: ',query.userQuery)
        response_content = chatbot.run(query.userQuery)
        print(chatbot.chat_history)
        # print('Response: ',response_content) 

        return {
            "role": "assistant",
            "content": response_content
            # "content": "Hi form backend"
        }



if __name__ == '__main__':

    # #initilaize API KEYS
    # load_dotenv(find_dotenv())


   

    
    uvicorn.run("fastapi_code:app")
