"""Keep omitted source features visible in both logs and generated decks."""
from core.fea.dataframe import dataframe
from utilities.logger import logger


def unconverted(message, source=None):
    location = getattr(source, 'source_context', None) or source
    text = f'{location}: {message}' if location else message
    dataframe.storge['conversion_notes'][text] = text
    logger.warning(message, source=location)
