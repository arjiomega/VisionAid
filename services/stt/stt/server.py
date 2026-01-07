# stt/server.py
import grpc
from concurrent import futures

from stt.model import load_transcription_model
from stt.service_impl import TranscriptionService
import stt.transcriber_pb2_grpc as transcriber_pb2_grpc


def serve():
    print("Loading Whisper model...")
    model_pipeline = load_transcription_model()
    print("Model loaded.")

    server = grpc.server(futures.ThreadPoolExecutor(max_workers=4))

    transcriber_pb2_grpc.add_TranscriptionServiceServicer_to_server(
        TranscriptionService(model_pipeline),
        server,
    )

    server.add_insecure_port("[::]:50051")
    print("STT gRPC server listening on port 50051")

    server.start()
    server.wait_for_termination()


if __name__ == "__main__":
    serve()
