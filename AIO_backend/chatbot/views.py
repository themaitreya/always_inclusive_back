import os
import openai
from dotenv import load_dotenv

from django.http import StreamingHttpResponse
from django.utils import timezone
from rest_framework.views import APIView
from rest_framework.response import Response
from langchain.chat_models import ChatOpenAI
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.vectorstores import FAISS
from langchain.schema import HumanMessage, SystemMessage, AIMessage
from langchain_community.document_loaders import TextLoader
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework import status
import os
from dotenv import load_dotenv
from langchain_community.document_loaders import TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_openai import ChatOpenAI
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_core.prompts import ChatPromptTemplate

from .models import ChatMessage

load_dotenv()  # .env에서 OPENAI_API_KEY 등을 가져옴

class ChatbotView(APIView):
    permission_classes = [IsAuthenticated]
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        if not self.openai_api_key:
            raise ValueError("OPENAI_API_KEY is not set in environment.")

        self.chat_llm = ChatOpenAI(
            openai_api_key=self.openai_api_key,
            model_name="gpt-4o",
            streaming=True,
            temperature=0.7
        )

        # RAG 세팅
        loader = TextLoader('./chatbot/Merged_details.txt', encoding='UTF8', autodetect_encoding=False)
        videos = loader.load()

        splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=100,
            length_function=len,
            is_separator_regex=False,
        )
        splits = splitter.split_documents(videos)

        embeddings = OpenAIEmbeddings(model="text-embedding-ada-002")

        if os.path.exists('./db/faiss'):
            self.vectorstore = FAISS.load_local('./db/faiss', embeddings, allow_dangerous_deserialization=True)
        else:
            self.vectorstore = FAISS.from_documents(documents=splits, embedding=embeddings)
            self.vectorstore.save_local('./db/faiss')

    def post(self, request, *args, **kwargs):
        user = request.user
        user_message = request.data.get('message', '').strip()
        if not user_message:
            return Response({"error": "message is required"}, status=400)

        ChatMessage.objects.create(user=user, role='user', message=user_message)

        response = StreamingHttpResponse(
            streaming_content=self.stream_chat(user, user_message),
            content_type='text/event-stream'
        )
        response['Cache-Control'] = 'no-cache'
        response['X-Accel-Buffering'] = 'no'
        return response

    def stream_chat(self, user, user_message):
        past_messages = ChatMessage.objects.filter(user=user).order_by('-created_at')[:10]
        past_messages = reversed(past_messages)

        conversation = []
        # SystemMessage에서 '\n'과 마크다운, 줄바꿈을 강조
        conversation.append(SystemMessage(content="""
당신은 제공된 데이터에 기반하여 질문에 답변하는 AI입니다.
특히, 아래 사항을 꼭 지키세요:
1) 각 항목마다 '**반드시**' 줄바꿈(\n)을 넣어서 구분
2) 영화 정보를 마크다운 목록 형태(- 또는 번호)로 작성
3) 답변 마지막에 '즐거운 시청 되세요!'라고 꼭 작성

예시:
1) 영화 제목
   - 장르: ...
   - 평점: ...
2) 영화 제목
   - 장르: ...
   - 평점: ...
"""))

        for msg in past_messages:
            if msg.role == 'system':
                conversation.append(SystemMessage(content=msg.message))
            elif msg.role == 'assistant':
                conversation.append(AIMessage(content=msg.message))
            else:
                conversation.append(HumanMessage(content=msg.message))

        # RAG
        docs = self.vectorstore.similarity_search(user_message, k=5)
        context_text = "\n\n".join([d.page_content for d in docs])
        conversation.append(
            SystemMessage(content=f"아래 컨텍스트도 참고:\n{context_text}")
        )
        conversation.append(HumanMessage(content=user_message))

        final_answer = []

        for token in self.chat_llm.stream(conversation):
            chunk_text = token.content
            if chunk_text:
                final_answer.append(chunk_text)
                yield f"data: {chunk_text}\n\n"

        assistant_text = "".join(final_answer).strip()
        if assistant_text:
            ChatMessage.objects.create(user=user, role='assistant', message=assistant_text)

        yield "data: [DONE]\n\n"

class ChatbotView_Anonymous(APIView):
    permission_classes = [AllowAny]
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        if not self.openai_api_key:
            raise ValueError("OPENAI_API_KEY is not set in environment.")

        self.chat_llm = ChatOpenAI(
            openai_api_key=self.openai_api_key,
            model_name="gpt-4o",
            streaming=True,
            temperature=0.7
        )

        # RAG 세팅
        loader = TextLoader('./chatbot/Merged_details.txt', encoding='UTF8', autodetect_encoding=False)
        videos = loader.load()

        splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=100,
            length_function=len,
            is_separator_regex=False,
        )
        splits = splitter.split_documents(videos)

        embeddings = OpenAIEmbeddings(model="text-embedding-ada-002")

        if os.path.exists('./db/faiss'):
            self.vectorstore = FAISS.load_local('./db/faiss', embeddings, allow_dangerous_deserialization=True)
        else:
            self.vectorstore = FAISS.from_documents(documents=splits, embedding=embeddings)
            self.vectorstore.save_local('./db/faiss')

    def post(self, request, *args, **kwargs):
        user = request.user
        user_message = request.data.get('message', '').strip()
        if not user_message:
            return Response({"error": "message is required"}, status=400)

        response = StreamingHttpResponse(
            streaming_content=self.stream_chat(user, user_message),
            content_type='text/event-stream'
        )
        response['Cache-Control'] = 'no-cache'
        response['X-Accel-Buffering'] = 'no'
        return response

    def stream_chat(self, user, user_message):

        conversation = []
        # SystemMessage에서 '\n'과 마크다운, 줄바꿈을 강조
        conversation.append(SystemMessage(content="""
당신은 제공된 데이터에 기반하여 질문에 답변하는 AI입니다.
특히, 아래 사항을 꼭 지키세요:
1) 각 항목마다 '**반드시**' 줄바꿈(\n)을 넣어서 구분
2) 영화 정보를 마크다운 목록 형태(- 또는 번호)로 작성
3) 답변 마지막에 '즐거운 시청 되세요!'라고 꼭 작성

예시:
1) 영화 제목
   - 장르: ...
   - 평점: ...
2) 영화 제목
   - 장르: ...
   - 평점: ...
"""))

        # RAG
        docs = self.vectorstore.similarity_search(user_message, k=5)
        context_text = "\n\n".join([d.page_content for d in docs])
        conversation.append(
            SystemMessage(content=f"아래 컨텍스트도 참고:\n{context_text}")
        )
        conversation.append(HumanMessage(content=user_message))

        final_answer = []

        for token in self.chat_llm.stream(conversation):
            chunk_text = token.content
            if chunk_text:
                final_answer.append(chunk_text)
                yield f"data: {chunk_text}\n\n"

        assistant_text = "".join(final_answer).strip()
        yield "data: [DONE]\n\n"