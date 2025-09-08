from litellm.integrations.custom_logger import CustomLogger

class MyCustomHandler(CustomLogger):
    def log_pre_api_call(self, model, messages, kwargs):
        print("Pre-API Call")

    def log_post_api_call(self, kwargs, response_obj, start_time, end_time):
        print("Post-API Call")

    def log_success_event(self, kwargs, response_obj, start_time, end_time):
        print("On Success")

    def log_failure_event(self, kwargs, response_obj, start_time, end_time):
        print("On Failure")

    async def async_log_success_event(self, kwargs, response_obj, start_time, end_time):
        print("On Async Success")

    async def async_log_failure_event(self, kwargs, response_obj, start_time, end_time):
        print("On Async Failure")

logger = MyCustomHandler()