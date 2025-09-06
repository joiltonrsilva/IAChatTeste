from langchain.memory import ConversationBufferMemory
from langchain.schema import messages_from_dict, messages_to_dict

_user_memories = {}

def get_memory_for_user(phone_number: str) -> ConversationBufferMemory:
    '''
    Retorna a memória de um usuário, criando uma nova se necessário.
    '''
    if phone_number not in _user_memories:
        _user_memories[phone_number] = ConversationBufferMemory(
            # memory_key="chat_history",
            return_messages=True
        )
    return _user_memories[phone_number]

def export_memory(phone_number: str) -> dict:
    """
    Exporta a memória de um usuário para JSON.
    """
    get_mem = _user_memories.get(phone_number)
    if get_mem:
        return messages_to_dict(get_mem.messages)
    return []


def import_memory(phone_number: str, memory: dict):
    """
    Importa a memória de um usuário a partir de um JSON.
    """
    mem = get_memory_for_user(phone_number)
    mem.chat_memory.messages = messages_from_dict(memory)
        
    