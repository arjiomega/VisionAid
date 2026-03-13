import grpc
import generated.text2speech_pb2 as text2speech_pb2
import generated.text2speech_pb2_grpc as text2speech_pb2_grpc

class TTSClient:
    def __init__(self, host="localhost", port=50052):
        self.channel = grpc.insecure_channel(f"{host}:{port}")
        self.stub = text2speech_pb2_grpc.Text2SpeechServiceStub(self.channel)

    def synthesize(self, text: str) -> bytes:
        request = text2speech_pb2.Text2SpeechRequest(text=text)
        response = self.stub.Text2Speech(request)
        return response.audio