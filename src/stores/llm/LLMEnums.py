from enum import Enum

class LLMEnum(Enum):

    OPENAI = "OPENAI"
    COHERE = "COHERE"

class OpenAIEnum(Enum):

    SYSTEM ="system"
    USER ="user"
    ASSISTANT = "assistant"

class CohereEnum(Enum):

    SYSTEM ="SYSTEM"
    USER ="USER"
    ASSISTANT = "CHATBOT"
    DOUCUMENT = "search_doucument"
    QUERY = "search_query"

class DoucumentTypeEnums(Enum):

    DOUCUMENT = "doucument"
    QUERY = "query"
