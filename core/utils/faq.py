from google.cloud import dialogflow
import uuid
import os
print("GOOGLE_APPLICATION_CREDENTIALS:", os.environ.get("GOOGLE_APPLICATION_CREDENTIALS"))


# def detect_intent_texts(project_id, session_id, text, language_code):
def detect_intent_texts(text):
    session_client = dialogflow.SessionsClient()
    project_id = "api-project-187384296318"
    session_id = str(uuid.uuid4())
    language_code = "ru"

    session = session_client.session_path(project_id, session_id)
    print(f"Session path: {session}\n")

    text_input = dialogflow.TextInput(text=text, language_code=language_code)
    query_input = dialogflow.QueryInput(text=text_input)
    response = session_client.detect_intent(request={"session": session, "query_input": query_input})

    print(f"Query text: {response.query_result.query_text}")
    print(f"Fulfillment text: {response.query_result.fulfillment_text}")

    return response.query_result.fulfillment_text
