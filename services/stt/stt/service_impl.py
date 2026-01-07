# stt/service_impl.py
import tempfile
from stt import transcriber_pb2
from stt import transcriber_pb2_grpc

class TranscriptionService(transcriber_pb2_grpc.TranscriptionServiceServicer):
    def __init__(self, model_pipeline):
        self.pipe = model_pipeline

    def Transcribe(self, request, context):
        # Save audio bytes to a temp file
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
            f.write(request.audio)
            audio_path = f.name

        # Whisper inference
        result = self.pipe(
            audio_path,
            generate_kwargs={
                "language": request.language or None,
            }
        )

        return transcriber_pb2.TranscriptionResponse(
            text=result["text"]
        )
