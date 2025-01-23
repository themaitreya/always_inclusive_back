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

load_dotenv()

class SimplePassThrough:
    def invoke(self, inputs, **kwargs):
        return inputs

class ContextToPrompt:
    def __init__(self, prompt_template):
        self.prompt_template = prompt_template

    def invoke(self, inputs):
        if isinstance(inputs, list):
            context_text = "\n".join([doc.page_content for doc in inputs])
        else:
            context_text = inputs

        formatted_prompt = self.prompt_template.format_messages(
            context=context_text,
            question=inputs.get("question", "")
        )
        return formatted_prompt

class RetrieverWrapper:
    def __init__(self, retriever):
        self.retriever = retriever

    def invoke(self, inputs):
        if isinstance(inputs, dict):
            query = inputs.get("question", "")
        else:
            query = inputs
        response_docs = self.retriever.get_relevant_documents(query)
        return response_docs

class ChatbotView(APIView):
    permission_classes = [AllowAny]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        openai_api_key = os.getenv("OPENAI_API_KEY")
        if not openai_api_key:
            raise ValueError("OPENAI_API_KEY is not set in the environment variables.")
        
        self.model = ChatOpenAI(model="gpt-4o")
        
        # 각 엔트리를 별도의 문서로 로드
        loader = TextLoader('./chatbot/Merged_details.txt', encoding='UTF8', autodetect_encoding=False)
        videos = loader.load()
        
        # 텍스트 분할을 최소화하여 각 문서를 개별적으로 유지
        # 필요 시, 텍스트 분할기를 제거하거나 큰 청크로 설정
        recursive_text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,  # 큰 청크로 설정
            chunk_overlap=100,  # 약간의 오버랩
            length_function=len,
            is_separator_regex=False,
        )
        splits = recursive_text_splitter.split_documents(videos)
        
        embeddings = OpenAIEmbeddings(model="text-embedding-ada-002")
        
        if os.path.exists('./db/faiss'):
            self.vectorstore = FAISS.load_local('./db/faiss', embeddings, allow_dangerous_deserialization=True)
        else:
            self.vectorstore = FAISS.from_documents(documents=splits, embedding=embeddings)
            self.vectorstore.save_local('./db/faiss')
        # self.vectorstore = FAISS.from_documents(documents=splits, embedding=embeddings)
        
        self.retriever = self.vectorstore.as_retriever(search_type="similarity", search_kwargs={"k": 10})
        
        self.contextual_prompt = ChatPromptTemplate.from_messages([
            ("system", "당신은 제공된 데이터에 기반하여 질문에 답변하는 AI 도우미입니다. 외부 지식이나 정보를 사용하지 말고, 오직 주어진 데이터만을 참고하여 응답하세요. 응답은 한국어로 작성되어야 합니다."),
            ("user", "데이터 컨텍스트: {context}\n\n질문: {question}\n\n제공된 데이터를 바탕으로 명확하고 구체적인 답변을 제공하세요. 가능한 경우, 요청한 조건에 맞는 후보군을 모두 나열해 주세요.")
        ])
        
        self.rag_chain = {
            "context": RetrieverWrapper(self.retriever),
            "prompt": ContextToPrompt(self.contextual_prompt),
            "llm": self.model
        }

    def post(self, request, *args, **kwargs):
        email = request.data.get('email')
        user_message = request.data.get('message')
        timestamp = request.data.get('timestamp')  # 실제 사용 여부는 선택

        if not user_message:
            return Response({"error": "message is required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            bot_response = self._generate_response(user_message)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response(
            {"responseMessage": bot_response},
            status=status.HTTP_200_OK
        )

    def _generate_response(self, query):
        response_docs = self.rag_chain["context"].invoke({"question": query})
        prompt_messages = self.rag_chain["prompt"].invoke({
            "context": response_docs,
            "question": query
        })
        response = self.rag_chain["llm"].invoke(prompt_messages)
        print(response.content)
        return response.content
