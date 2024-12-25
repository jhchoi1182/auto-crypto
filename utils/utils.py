from deep_translator import GoogleTranslator
from .logger_config import logger

def translate_text_to_korean(text: str) -> str:
    if not text:
        return text
        
    try:
        translator = GoogleTranslator(source='en', target='ko')
        result = translator.translate(text)
        return result
    except Exception as e:
        logger.error(f"번역 중 오류 발생: {str(e)}")
        return text