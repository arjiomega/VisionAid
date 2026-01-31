import tempfile
from stt import transcriber_pb2
from stt import transcriber_pb2_grpc

class TranscriptionService(transcriber_pb2_grpc.TranscriptionServiceServicer):
    def __init__(self, model_pipeline):
        self.pipe = model_pipeline

    def Transcribe(self, request, context):
        # Whisper inference
        result = self.pipe(
            request.audio,
            generate_kwargs={
                "language": request.language or None,
            }
        )

        return transcriber_pb2.TranscriptionResponse(
            text=result["text"]
        )
