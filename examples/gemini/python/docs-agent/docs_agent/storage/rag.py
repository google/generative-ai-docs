#
# Copyright 2023 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

from absl import logging
from docs_agent.storage.base import RAG
from docs_agent.utilities.config import ProductConfig
from docs_agent.storage.chroma import ChromaEnhanced


class RAGFactory:
    @staticmethod
    def create_rag(product_config: ProductConfig) -> RAG:
        # Find the Chroma DB configuration in the product config.
        has_chroma = any(db.db_type == "chroma" for db in product_config.db_configs)

        if has_chroma:
            logging.info("[RAGFactory] Chroma DB configuration found. Creating ChromaEnhanced instance.")
            try:
                # Create the ChromaEnhanced instance from the product config
                return ChromaEnhanced.from_product_config(product_config)
            except Exception as e:
                logging.error(f"[RAGFactory] Failed to create Chroma RAG instance: {e}")
                raise
        else:
            # Handle the case where no supported DB config is found
            logging.error("[RAGFactory] No supported RAG database configuration found in product configuration.")
            raise ValueError("No supported RAG database configuration found.")


def return_collection_name(product_config: ProductConfig) -> str:
    collection_name = ""
    for item in product_config.db_configs:
        if "chroma" in item.db_type:
            collection_name = item.collection_name
    return collection_name
