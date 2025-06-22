import logging
import os
import time

from google import genai
from google.genai import types
import dtlpy as dl

logger = logging.getLogger("Google Gemini Adapter")


class ModelAdapter(dl.BaseModelAdapter):

    def load(self, local_path, **kwargs):
        if os.environ.get("GOOGLE_API_KEY", None) is None:
            raise ValueError("Missing Google API key")

        self.api_key = os.environ.get("GOOGLE_API_KEY", None)
        self.max_output_tokens = self.configuration.get('max_output_tokens', 1024)
        self.temperature = self.configuration.get('temperature', 0.2)
        self.top_p = self.configuration.get('top_p', 0.7)
        self.seed = self.configuration.get('seed', None)
        self.stream = self.configuration.get('stream', False)
        self.thinking_budget = self.configuration.get('thinking_budget', 128)
        self.debounce_interval = self.configuration.get('debounce_interval', 2)
        self.system_prompt = self.configuration.get('system_prompt', None)


        self.client = genai.Client(api_key=self.api_key)

    @staticmethod
    def _get_gemini_massages(prompt_item):
        chat_history = []
        for message in prompt_item.to_messages():
            role = 'user' if message['role'] == 'user' else 'model'
            parts = []
            for part in message['content']:
                if part['type'] == 'text':
                    parts.append(types.Part.from_text(text=part['text']))
                elif part['type'] == 'image_url':
                    parts.append(types.Part.from_bytes(data=part['image_url']['url'].replace('data:image/jpeg;base64,',''),mime_type='image/jpeg'))
            chat_history.append(types.Content(role=role, parts=parts))

        # remove the last massage if it is a model message
        while True:
            if chat_history[-1].role == 'model':
                chat_history.pop()
            else:
                break

        return chat_history

    def add_response_to_prompt(self, prompt_item, response_text, mimetype=dl.PromptType.TEXT):
        """Adds the generated response back to the prompt item."""
        # Ensure response_text is not None before adding
        if response_text is None:
            logger.warning(f"Attempted to add None response to prompt item. Skipping.")
            return

        prompt_item.add(message={"role": "assistant",
                                "content": [{"mimetype": mimetype,
                                            "value": response_text}]},
                        model_info={
                            'name': self.model_entity.name,
                            'confidence': 1.0, # Assuming high confidence, adjust if needed
                            'model_id': self.model_entity.id
                        })

    def _handle_response(self, prompt_item, response_stream_or_obj):
        """Handles both streaming and non-streaming responses."""
        if self.stream:
            full_response_text = ""
            last_update_time = time.time()
            
            for chunk in response_stream_or_obj:
                chunk_text = chunk.text
                if chunk_text: # Only process if text was extracted
                    full_response_text += chunk_text
                    current_time = time.time()
                    # Debounce updates for streaming
                    if current_time - last_update_time >= self.debounce_interval:
                        self.add_response_to_prompt(prompt_item, full_response_text)
                        last_update_time = current_time
    
            self.add_response_to_prompt(prompt_item, full_response_text)
        else:
            # Handle non-streaming response
            full_response_text = response_stream_or_obj.text
            self.add_response_to_prompt(prompt_item, full_response_text)
    
    def _call_api(self, prompt_data):
        if self.stream:
            response = self.client.models.generate_content_stream(
                model=self.model_entity.name,
                contents=prompt_data,
                config=types.GenerateContentConfig(
                    temperature=self.temperature,
                    top_p=self.top_p,
                    seed=self.seed,
                    max_output_tokens=self.max_output_tokens,
                    system_instruction=self.system_prompt,
                    thinking_config=types.ThinkingConfig(thinking_budget=self.thinking_budget)
                )
            )
            return response
        else:
            response = self.client.models.generate_content(
                model=self.model_entity.name,
                contents=prompt_data,   
                config=types.GenerateContentConfig(
                    temperature=self.temperature,
                    top_p=self.top_p,
                    seed=self.seed,
                    max_output_tokens=self.max_output_tokens,
                    system_instruction=self.system_prompt
                )
            )
            return response

    def predict(self, batch, **kwargs):
        """Runs prediction on a batch of prompts."""
        predictions = [] # Adapters should return a list of annotations, often empty for LLMs
        for prompt_item in batch:
            try:
                prompt_data = self._get_gemini_massages(prompt_item)
                if not prompt_data: # Skip if prompt data could not be extracted
                     raise ValueError(f"Prompt data could not be extracted for item.")

                response = self._call_api(prompt_data)
                self._handle_response(prompt_item, response)

            except Exception as e:
                 raise ValueError(f"Error processing prompt item: {e}")
               
        return predictions # Return empty list as per Dataloop adapter standard for LLMs
    
