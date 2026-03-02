"""
Chunking strategies for unstructured documents.

This module provides an abstract base class for chunking strategies and a concrete
implementation that limits the number of images per chunk while respecting text-based
chunking rules. It returns CompositeElements with metadata linking back to original elements.
"""

from unstructured.chunking.title import chunk_by_title
from unstructured.documents.elements import CompositeElement, ElementMetadata, Image
from abc import ABC, abstractmethod


class ChunkStrategies(ABC):
    """
    Abstract base class for document chunking strategies.
    """

    @abstractmethod
    def get_chunk(self, docs):
        """
        Generate chunks from a list of document elements.

        Args:
            docs (list): List of document elements.

        Returns:
            list: List of chunks (CompositeElements or other structures).
        """
        pass


class ChunkingWithMaxImages(ChunkStrategies):
    """
    Chunking strategy that limits the number of images per chunk.

    Attributes:
        max_images (int): Maximum number of images allowed in a single chunk.
    """

    def __init__(self, max_images=4):
        self.max_images = max_images

    def _create_chunk(self, elements):
        """
        Perform initial chunking based on titles and character count.

        Args:
            elements (list): List of document elements.

        Returns:
            list: Sections after title-based chunking.
        """
        chunk = chunk_by_title(
            elements,
            max_characters=3000,
            new_after_n_chars=2400,
            combine_text_under_n_chars=500
        )
        return chunk

    def _pack_into_composite(self, elements):
        """
        Combine a list of elements into a CompositeElement with metadata.

        Args:
            elements (list): List of document elements.

        Returns:
            CompositeElement: Combined chunk with metadata linking to original elements.
        """
        combined_text = '\n'.join(str(el) for el in elements)
        metadata = ElementMetadata()
        metadata.orig_elements = elements
        composite = CompositeElement(
            text=combined_text,
            metadata=metadata
        )
        return composite

    def get_chunk(self, docs):
        """
        Generate chunks from a document, limiting the number of images per chunk.

        Args:
            docs (list): List of document elements.

        Returns:
            list: List of CompositeElement chunks.
        """
        sections = self._create_chunk(docs)
        chunks = []
        current_chunk = []
        image_count = 0

        for el in sections:
            if hasattr(el, "metadata") and hasattr(el.metadata, 'orig_elements'):
                for element in el.metadata.orig_elements:
                    is_image = isinstance(element, Image)

                    # If adding this image exceeds limit → start new chunk
                    if is_image and image_count + 1 > self.max_images:
                        chunks.append(self._pack_into_composite(current_chunk))
                        current_chunk = []
                        image_count = 0

                    current_chunk.append(element)

                    if is_image:
                        image_count += 1

        if current_chunk:
            chunks.append(self._pack_into_composite(current_chunk))

        return chunks


def chunkwithmaximages(docs, max_images=4):
    """
    Convenience function to chunk documents with a maximum image limit.

    Args:
        docs (list): List of document elements.
        max_images (int, optional): Maximum images per chunk. Defaults to 4.

    Returns:
        list: List of CompositeElement chunks.
    """
    chunkmethod = ChunkingWithMaxImages(max_images)
    chunked_docs = chunkmethod.get_chunk(docs)
    return chunked_docs