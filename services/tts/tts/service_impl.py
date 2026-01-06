from tts import text2speech_pb2, text2speech_pb2_grpc

class TextToSpeechServicer(text2speech_pb2_grpc.Text2SpeechServiceServicer):
    def __init__(self, tts_model):
        self.tts_model = tts_model

    def Text2Speech(self, request, context) -> bytes:
        text = request.text
        audio_data = self.tts_model.to_speech(text)

        return text2speech_pb2.Text2SpeechResponse(audio=audio_data)