import google.generativeai as genai
from .base import LLMClient

class GeminiClient(LLMClient):
    def generate_response(self, prompt, system_prompt, config) -> str:
        genai.configure(api_key=self.api_key)
        model_name = config.get("model", "gemini-1.5-flash")
        model = genai.GenerativeModel(model_name=model_name, system_instruction=system_prompt)
        response = model.generate_content(prompt)
        self._log_telemetry("gemini", model_name,
                            response.usage_metadata.prompt_token_count,
                            response.usage_metadata.candidates_token_count)
        return response.text
