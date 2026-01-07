import grpc
import generated.transcriber_pb2 as transcriber_pb2
import generated.transcriber_pb2_grpc as transcriber_pb2_grpc

class STTClient:
    def __init__(self, host="localhost", port=50051):
        self.channel = grpc.insecure_channel(f"{host}:{port}")
        self.stub = transcriber_pb2_grpc.TranscriptionServiceStub(self.channel)

    def transcribe(self, audio_bytes: bytes, language="en"):
        request = transcriber_pb2.TranscriptionRequest(
            audio=audio_bytes,
            language=language
        )
        response = self.stub.Transcribe(request)
        return response.text