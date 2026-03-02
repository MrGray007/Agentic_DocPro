"""
LLM-based chunk summarization module.

This module provides abstract and concrete strategies for summarizing
document chunks into structured JSON outputs using AI models. It includes
support for text, table, and image content, as well as robust retry logic
for LLM calls.
"""

import json
import re
import time
from abc import ABC, abstractmethod
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
from langchain_core.documents import Document
from langchain_core.output_parsers import JsonOutputParser
from groq import Groq
from dotenv import load_dotenv
import os
from prompts.signal_summarizer_prompt import text_prompt, table_prompt, image_prompt, output_structure_prompt

load_dotenv()
api_key = os.getenv("GROQ_API_KEY")


class SummaryStrategies(ABC):
    """
    Abstract base class for chunk summarization strategies.
    """

    @abstractmethod
    def get_summarized_chunks(self, chunks):
        """
        Summarize a list of document chunks into structured outputs.

        Args:
            chunks (list): List of chunk elements or CompositeElements.

        Returns:
            list: List of summarized Document objects.
        """
        pass


class SummarizeChunks(SummaryStrategies):
    """
    Concrete implementation of SummaryStrategies that uses an LLM to
    summarize text, tables, and images in chunks into JSON.
    """

    def create_content_data(self, chunk):
        """
        Extract text, tables, images, and page numbers from a chunk.

        Args:
            chunk: A document chunk (CompositeElement) with metadata.

        Returns:
            dict: Content data with text, tables, images, types, and page numbers.
        """
        content_data = {
            'text': chunk.text,
            'images': [],
            'tables': [],
            'types': ['text'],
            'page_number': []
        }

        if hasattr(chunk, 'metadata') and hasattr(chunk.metadata, 'orig_elements'):
            for element in chunk.metadata.orig_elements:
                element_type = type(element).__name__
                page_number = getattr(element.metadata, "page_number", None)
                if page_number is not None:
                    content_data['page_number'].append(page_number)

                if element_type == 'Image' and hasattr(element.metadata, 'image_base64'):
                    content_data['types'].append('images')
                    images_bs64 = getattr(element.metadata, "image_base64")
                    content_data['images'].append(images_bs64)

                elif element_type == 'Table':
                    content_data['types'].append('table')
                    table_html = getattr(element.metadata, 'text_as_html', element.text)
                    content_data['tables'].append(table_html)

        content_data['types'] = list(set(content_data['types']))
        content_data['page_number'] = list(set(content_data['page_number']))
        return content_data

    def prompt_generator_for_summary_json(self, Text, Tables, Images):
        """
        Build a structured prompt for the LLM summarization.

        Args:
            Text (str): Raw text content.
            Tables (list): List of HTML table strings.
            Images (list): List of base64 image strings.

        Returns:
            list: List of message dicts suitable for Groq API call.
        """
        prompt = text_prompt.format(Text)

        if Tables:
            prompt += "\nTABLE CONTENT:\n"
            for count, table in enumerate(Tables, 1):
                prompt += f"\nTable {count}:\n{table}\n"
        prompt += table_prompt

        images_list = []
        if Images:
            prompt += image_prompt
            for imagebs64 in Images:
                images_list.append({
                    'type': 'image_url',
                    'image_url': {'url': f"data:image/jpeg;base64,{imagebs64}"}
                })

        prompt += output_structure_prompt
        messages = [{'type': 'text', 'text': prompt}]
        messages.extend(images_list)
        return messages

    def safe_json_parse(self, text):
        """
        Attempt to safely extract JSON content from a string.

        Args:
            text (str): Raw LLM output.

        Returns:
            dict/str: Parsed JSON or original content.

        Raises:
            ValueError: If no JSON found.
        """
        if not isinstance(text, str):
            return text

        text = re.sub(r"```json|```", "", text).strip()
        match = re.search(r"\{.*\}", text, re.DOTALL)
        if not match:
            raise ValueError("No JSON found in response")
        return match.group(0)

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=1, max=8),
        retry=retry_if_exception_type(Exception),
        reraise=True
    )
    def AiClient(self, Text, Tables, Images):
        """
        Call the Groq AI model to summarize chunk content with retry logic.

        Args:
            Text (str): Raw text content.
            Tables (list): HTML tables.
            Images (list): Base64 images.

        Returns:
            str: Raw JSON string returned by the model.
        """
        try:
            client = Groq(api_key=api_key)
            prompt = self.prompt_generator_for_summary_json(Text, Tables, Images)

            response = client.chat.completions.create(
                model="meta-llama/llama-4-scout-17b-16e-instruct",
                messages=[{"role": "user", "content": prompt}],
                temperature=0,
                response_format={"type": "json_object"}
            )
            raw_output = response.choices[0].message.content
            self.safe_json_parse(raw_output)
            return raw_output
        except Exception as e:
            print(f"Error occurred in AI call -->\n{e}")
            raise e

    def get_summarized_chunks(self, chunks):
        """
        Summarize a list of document chunks using AI and return as Document objects.

        Args:
            chunks (list): List of document chunks.

        Returns:
            list: List of Document objects with AI-generated summaries.
        """
        parser = JsonOutputParser()
        total_documents = []

        for count, chunk in enumerate(chunks, 1):
            print(f"Processing chunk {count}...")
            content_data = self.create_content_data(chunk)
            print("Content data extracted.")
            response = self.AiClient(
                content_data['text'],
                content_data['tables'],
                content_data['images']
            )
            print("AI response received.")

            total_documents.append(
                Document(
                    page_content=response,
                    metadata={
                        'original_content': {
                            'raw_text': content_data['text'],
                            'tables_html': content_data['tables'],
                            'image_base64': content_data['images'],
                            'page_number': content_data['page_number']
                        }
                    }
                )
            )
            print(f"Processed {len(total_documents)} chunks.")

        return total_documents


def summarizechunks(chunks):
    """
    Convenience function to summarize document chunks.

    Args:
        chunks (list): List of document chunks.

    Returns:
        list: List of summarized Document objects.
    """
    chunk_summarizer = SummarizeChunks()
    return chunk_summarizer.get_summarized_chunks(chunks)