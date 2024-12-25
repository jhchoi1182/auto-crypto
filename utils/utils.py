import logging
from googletrans import Translator

def translate_text_to_korean(text: str) -> str:
    if not text:
        return text
        
    try:
        translator = Translator()
        result = translator.translate(text, dest='ko', src='en')
        return result.text if result and result.text else text
    except Exception as e:
        logging.error(f"번역 중 오류 발생: {str(e)}")
        return text