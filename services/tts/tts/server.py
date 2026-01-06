import grpc
from concurrent import futures

from tts.tts_service import tts_model
from tts.service_impl import TextToSpeechServicer
import tts.text2speech_pb2_grpc as text2speech_pb2_grpc

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=4))
    text2speech_pb2_grpc.add_Text2SpeechServiceServicer_to_server(
        TextToSpeechServicer(tts_model), server
    )
    server.add_insecure_port("[::]:50052")
    server.start()
    print("Text-to-Speech gRPC server started on port 50052.")
    server.wait_for_termination()

if __name__ == "__main__":
    serve()