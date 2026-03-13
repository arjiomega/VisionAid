"use client";

import { Dispatch, SetStateAction, useEffect, useRef, useState } from 'react';
import Image from "next/image";

const backend_base_url = process.env.NEXT_PUBLIC_BACKEND_BASE_URL ?? ""
const backend_ws_url = process.env.NEXT_PUBLIC_BACKEND_BASE_WS_URL ?? ""
const vlm_ws_endpoint = process.env.NEXT_PUBLIC_VLM_WS_ENDPOINT ?? ""
const healthcheck_endpoint = process.env.NEXT_PUBLIC_HEALTHCHECK_ENDPOINT ?? ""
const auth_endpoint = process.env.NEXT_PUBLIC_AUTH_ENDPOINT ?? ""

const wsURL = backend_ws_url + vlm_ws_endpoint
const healthCheckURL = backend_base_url + healthcheck_endpoint
const authURL = backend_base_url + auth_endpoint


type CameraProps = {
  setCurrentCanvas: (canvas: HTMLCanvasElement) => void
  CameraButton: React.ComponentType<{ className?: string}>
  recording: boolean
  startRecording: () => void
  stopRecording: () => void
}

function Camera({setCurrentCanvas, CameraButton, recording, startRecording, stopRecording}: CameraProps) {
  const videoRef = useRef<HTMLVideoElement | null>(null);
  const streamRef = useRef<MediaStream | null>(null);
  const canvasRef = useRef<HTMLCanvasElement | null>(null);
  const [hasPermission, setHasPermission] = useState<boolean | null>(null);
  const [facingMode, setFacingMode] = useState<"user" | "environment">("user");

  useEffect(() => {
    const setupCamera = async () => {
      try {
        // Stop any existing video stream before switching
        if (streamRef.current) {
            console.log("[Camera] stopping previous stream");
            streamRef.current.getTracks().forEach((track) => track.stop());
        }

        const stream = await navigator.mediaDevices.getUserMedia({
            video: { facingMode },
            audio: false,
        });

        console.log("[Camera] stream acquired");

        streamRef.current = stream;

        if (videoRef.current) {
          videoRef.current.srcObject = stream;
        }

        setHasPermission(true);
      } catch (err) {
        console.error("[Camera] getUserMedia failed", err);
        setHasPermission(false);
      }
    };

    setupCamera();

    // Stop camera when component unmounts
    return () => {
        streamRef.current?.getTracks().forEach((track) => track.stop());
    };
  }, [facingMode]); // re-run when user switches camera


  useEffect(() => {
    const video = videoRef.current;
    if (!video) {
        console.warn("[Camera] videoRef null");
        return;
    };

    const canvas = document.createElement('canvas');
    const ctx = canvas.getContext('2d');
    if (!ctx) {
      console.error("[Camera] no canvas context");
      return;
    }
    
    console.log("[Camera] canvas created");
    canvasRef.current = canvas;
    setCurrentCanvas(canvas);

    const drawLoop = () => {
      if (video.readyState === video.HAVE_ENOUGH_DATA) {
        if (canvas.width !== video.videoWidth) {
          canvas.width = video.videoWidth;
          canvas.height = video.videoHeight;
          console.log("[Camera] canvas resized", canvas.width, canvas.height);
        }
        ctx.drawImage(video, 0, 0, canvas.width, canvas.height);
        // setCurrentCanvas(canvas);
      }
      requestAnimationFrame(drawLoop);
    };

    drawLoop();

    return () => {
        console.log("[Camera] stopping draw loop");
        canvasRef.current = null;
    };
  }, []);

  const toggleCamera = () => {
    setFacingMode((prev) => (prev === "user" ? "environment" : "user"));
  };

  if (hasPermission === false) {
    return <p>Camera access denied. Please enable permissions.</p>;
  }

  return (
    <div className={`w-full rounded-2xl p-0.75`}> 
      {/* Video container */}
      <div className="relative h-full md:aspect-video overflow-hidden">
        <video
          ref={videoRef}
          autoPlay
          playsInline
          className="w-full object-cover inset-0 rounded-2xl"
        />

        <CameraButton className="absolute bottom-4 left-1/2 -translate-x-1/2" />
  

        {/* Overlay button */}
        <button
          onClick={toggleCamera}
          className="
            absolute bottom-4 right-4
            bg-black/70 text-white
            px-4 py-2 rounded-lg
            backdrop-blur-sm
            hover:bg-black/90
            transition
          "
        >
          <Image 
            src="/icons/switch-camera.png"
            alt="Switch Camera"
            width={24}
            height={24}
            priority
          />
          {/* Switch Camera */}
        </button>

        {recording ? 
        <div className="absolute top-4 right-4 flex items-center justify-center">
          <span className="absolute inline-flex h-10 w-10 rounded-full bg-red-500 opacity-75 animate-ping" />
          <span className="relative inline-flex">
            <Image
              src="/icons/listen.png"
              alt="Listening"
              width={30}
              height={30}
              priority
            />
          </span>
        </div> : ""}

        

      </div>
    </div>
  );
}


function HealthPing() {
  const [status, setStatus] = useState("unknown");

  useEffect(() => {
    const checkHealth = async () => {

      if (!healthCheckURL) {
        throw new Error('NEXT_PUBLIC_HEALTHCHECK_URL is not defined');
      }
      try {
        
        const res = await fetch(healthCheckURL);
        if (!res.ok) throw new Error("Network response not ok");
        const data = await res.json();
        setStatus(data.status);
      } catch (err) {
        setStatus("unhealthy");
        console.error("Health check failed:", err);
      }
    };

    checkHealth();

    // Optional: repeat every 30 seconds
    const interval = setInterval(checkHealth, 30 * 1000);
    return () => clearInterval(interval);
  }, []);

  const isHealthy = (status === "ok");

  return (
    <div
      className={`
        px-3 py-2 rounded-md text-sm font-bold
        ${isHealthy
          ? "bg-emerald-500/20 text-emerald-300"
          : "bg-red-500/20 text-red-300"}
      `}
    >
      Server Status: {isHealthy ? "Healthy" : "Server is Unavailable."}
    </div>
  );

}

async function getAccessToken(apiKey: string) {
  try {

    if (!authURL) {
      throw new Error('NEXT_PUBLIC_AUTH_URL is not defined');
    }

    const res = await fetch(authURL, {
      method: "POST",
      headers: {
        "X-API-Key": apiKey 
      },
      credentials: "include", // for refresh cookie
    })

    if (!res.ok) {
      return null;
    }

    const data = await res.json();
    return data.access_token;
  } catch (err) {
    console.error(err);
    return null;
  }
}

function PasswordInput({
  setAccessToken,
}: {
  setAccessToken: Dispatch<SetStateAction<string>>;
}) {
  const [input, setInput] = useState("");

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!input) return;

    const accessToken = await getAccessToken(input);
    if (accessToken) {
      setAccessToken(accessToken);           // save in context/sessionStorage
      setInput("false");            // close modal
    } else {
      alert("Invalid API key");
    }
  };

  return (
    <form onSubmit={handleSubmit} className='flex flex-row justify-between'>
      <div className=''>
        <label className="input validator">
          <svg
            className="h-[1em] opacity-50"
            xmlns="http://www.w3.org/2000/svg"
            viewBox="0 0 24 24"
          >
            <g strokeLinejoin="round" strokeLinecap="round" strokeWidth="2.5" fill="none" stroke="currentColor">
              <path d="M2.586 17.414A2 2 0 0 0 2 18.828V21a1 1 0 0 0 1 1h3a1 1 0 0 0 1-1v-1a1 1 0 0 1 1-1h1a1 1 0 0 0 1-1v-1a1 1 0 0 1 1-1h.172a2 2 0 0 0 1.414-.586l.814-.814a6.5 6.5 0 1 0-4-4z"></path>
              <circle cx="16.5" cy="7.5" r=".5" fill="currentColor"></circle>
            </g>
          </svg>
          <input
            type="password"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            required
            placeholder="API Key"
          />
        </label>
      </div>
      <div className=''>
        <button type="submit" className="btn">
          Submit
        </button>
      </div>
      
    </form>
  );
}

export default function Home() {
  const [connected, setConnected] = useState(false);
  const [message, setMessage] = useState("");
  const [recording, setRecording] = useState(false);
  const [currentCanvas, setCurrentCanvas] = useState<HTMLCanvasElement | null>(null);
  const socketRef = useRef<WebSocket | null>(null);
  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  
  const audioSourceBuffer = useRef<SourceBuffer | null>(null);
  const mediaSource = useRef<MediaSource | null>(null);
  const audioElement = useRef<HTMLAudioElement | null>(null);

  const [userTranscription, setUserTranscription] = useState("");
  const [assistantTranscription, setAssistantTranscription] = useState("");
  const [currentStep, setCurrentStep] = useState(-1);
  const steps = ["Listening", "Transcribing", "Thinking", "Synthesizing", "Finished"];

  const [accessToken, setAccessToken] = useState("");

  useEffect(() => {
    if (recording) {
      setCurrentStep(0);
    } else {
      setCurrentStep(-1);
    }
  }, [recording]);

  const setupAudioStream = () => {
    return new Promise<void>((resolve) => {
      mediaSource.current = new MediaSource();
      const url = URL.createObjectURL(mediaSource.current);

      audioElement.current = new Audio(url);
      audioElement.current.play();

      mediaSource.current.addEventListener("sourceopen", () => {
        // "audio/webm; codecs=opus" matches your backend format
        audioSourceBuffer.current = mediaSource.current!.addSourceBuffer(
          'audio/webm;'
        );
        resolve();
      });
    });
  };

  const connectWebSocket = async (): Promise<WebSocket> => {
    // Reuse existing connection if already connected
    if (socketRef.current && socketRef.current.readyState === WebSocket.OPEN) {
      return socketRef.current;
    }

    if (
      socketRef.current &&
      socketRef.current.readyState === WebSocket.CONNECTING
    ) {
      return new Promise((resolve) => {
        socketRef.current?.addEventListener("open", () =>
          resolve(socketRef.current as WebSocket)
        );
      });
    }

    // Create new WebSocket connection
    if (!wsURL) {
      throw new Error('NEXT_PUBLIC_WS_URL is not defined');
    }
    const ws = new WebSocket(wsURL + `?token=${encodeURIComponent(accessToken)}`);
    socketRef.current = ws;

    return new Promise((resolve, reject) => {
      ws.onopen = () => {
        console.log("Connected to WebSocket");
        setConnected(true);
        setMessage("Connected!");
        // ws.send("Hello from Next.js!");
        resolve(ws);
      };

      ws.onmessage = async (event) => {
      
        if (typeof event.data === "string") {
          // Text message from server
          console.log("Received text:", event.data);
          setMessage(`Server says: ${event.data}`);

          let payload;
          try {
            payload = JSON.parse(event.data);
            switch (payload.type) {
              case "transcription":
                setUserTranscription(payload.text);
                break;
              case "assistantResponse":
                setAssistantTranscription(payload.text);
                break;
              case "status":
                switch (payload.status) {
                  case "transcribing":
                    setCurrentStep(1);
                    console.log("Transcribing");
                    break;
                  case "thinking":
                    setCurrentStep(2);
                    console.log("Thinking");
                    break;
                  case "synthesizing":
                    setCurrentStep(3);
                    console.log("Synthesizing");
                    break;
                  case "finished":
                    setCurrentStep(4);
                    console.log("Finished");
                    break;
                }
                break;
              default:
                console.warn("Unknown payload type: ", payload.type);
            }
       
              
          } catch {
            console.warn("Non-JSON text message: ", event.data);
          }

        } else if (event.data instanceof Blob) {

          const arrayBuffer = await event.data.arrayBuffer();

          if (
            mediaSource.current &&
            audioSourceBuffer.current &&
            !audioSourceBuffer.current.updating
          ) {
            audioSourceBuffer.current.appendBuffer(new Uint8Array(arrayBuffer));
          }

          // Binary audio data
          console.log("Received audio data");
          // const audioBlob = event.data; // Blob of WAV
          const audioBlob = new Blob([event.data], { type: "audio/webm" });
          const audioUrl = URL.createObjectURL(audioBlob);

          // Play audio
          const audio = new Audio(audioUrl);
          audio.play().catch(err => console.log("❌ Audio play failed:", err));;
        } else if (event.data instanceof ArrayBuffer) {
          // Some servers might send ArrayBuffer directly
          console.log("Received audio ArrayBuffer");
          const audioBlob = new Blob([event.data], { type: "audio/wav" });
          const audioUrl = URL.createObjectURL(audioBlob);

          const audio = new Audio(audioUrl);
          audio.play();
        } else {
          console.warn("Unknown WebSocket message type:", event.data);
        }
      };

      ws.onclose = () => {
        console.log("❌ Disconnected");
        setConnected(false);
        // setMessage("Disconnected");
      };

      ws.onerror = (event) => {
        console.log("WebSocket error occurred");
        console.error("WebSocket error:", {
          readyState: ws.readyState,
          event,
        });
        reject(event);
      };
    });    
  };
  
  const disconnectWebSocket = () => {
    const ws = socketRef.current;
    if (ws && ws.readyState === WebSocket.OPEN) {
      ws.close();
      socketRef.current = null;
      setConnected(false);
      setMessage("Disconnected");
      console.log("Disconnected from WebSocket");
    } else {
      console.warn("No active WebSocket to disconnect");
    }
  };

  const startRecording = async () => {
    console.log("🎙️ startRecording");

    const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
    const ws = await connectWebSocket();

    if (!ws || ws.readyState !== WebSocket.OPEN) {
      console.error("WebSocket not connected yet!");
      return;
    }

    const recorder = new MediaRecorder(stream, { mimeType: "audio/webm" });

    recorder.ondataavailable = (event) => {
      if (event.data.size > 0 && ws.readyState === WebSocket.OPEN) {
        event.data.arrayBuffer().then((buffer) => {
          ws.send(JSON.stringify({data_type: "audio"}));
          ws.send(buffer);
        });
      }
    };

    recorder.start(250); // send every 250ms
    mediaRecorderRef.current = recorder;
    setRecording(true);
    console.log("Recording started");
  };

  const stopRecording = async () => {
    if (mediaRecorderRef.current) {
      mediaRecorderRef.current.stop();
      setRecording(false);
      console.log("Recording stopped");
    }

    const ws = socketRef.current;
    if (!ws || ws.readyState !== WebSocket.OPEN) {
      console.warn("WebSocket is not open. Cannot send image.");
      return;
    }

    await setupAudioStream();

    // Step 1 — Tell server next message is image
    
    await new Promise((r) => setTimeout(r, 100)); // small delay to ensure order

    // Step 2 — Capture and send the image bytes
    if (currentCanvas) {
      console.log("Capturing canvas frame...");
      await new Promise<void>((resolve) => {
        currentCanvas.toBlob(async (blob) => {
          if (!blob) {
            console.warn("No blob created");
            return resolve();
          }
          const arrayBuffer = await blob.arrayBuffer();

          if (ws.readyState === WebSocket.OPEN) {
            ws.send(JSON.stringify({ data_type: "image" }));
            ws.send(arrayBuffer);
            console.log("Image bytes sent:", arrayBuffer.byteLength);
          } else {
            console.warn("WebSocket closed before sending image");
          }
          resolve();
        }, "image/png");
      });
    } else {
      console.warn("No currentCanvas to send");
    }

    // Step 3 — Tell server we're done
    ws.send("done");
    console.log("Sent 'done' to server");

    // Don't disconnect immediately - wait for audio response
    // The connection will stay open to receive the audio from the server
  };

  useEffect(() => {
    return () => {
      if (mediaRecorderRef.current) {
        mediaRecorderRef.current.stop();
      }
      if (socketRef.current) {
        socketRef.current.close();
      }
    };
  }, []);

  function CameraButton({ className }: { className?: string }) {
    return (
      <button
        onClick={recording ? stopRecording : startRecording}
        className={`flex items-center justify-center rounded-full 
                  w-12 h-12
                  border-4 border-white p-1 
                  ${className ?? ""}`}
      >
        {/* Inner shape: circle when idle, square when recording */}
        <div
          className={`transition-all duration-200 ${
            recording
              ? "w-6 h-6 bg-red-600 rounded-none" // square when recording
              : "w-8 h-8 bg-red-600 rounded-full" // circle when stopped
          }`}
        />
      </button>
    );
  }

  const [userData, setUserData] = useState(null);

  return (
    <main 
      className="
      flex flex-col
      md:flex-row md:justify-center md:mt-10 md:gap-5 md:mx-5
      "
    >
      <div className='shrink-0 md:flex-2 md:h-full'>
        <Camera 
          setCurrentCanvas={setCurrentCanvas} 
          CameraButton={CameraButton} 
          recording={recording}
          startRecording={startRecording}
          stopRecording={stopRecording}
        />
      </div>
    
      
      <div
        className="
          md:flex-1
          md:h-full
          p-5
          rounded-xl
          bg-slate-900
          text-slate-100
          shadow-lg
          flex flex-col
          gap-4
        "
      >
        <h1 className="text-lg font-semibold tracking-wide">
          VisionAID Dashboard
        </h1>

        {/* Status */}
        <HealthPing/>
        
        <ul className="steps bg-slate-800 p-2 font-bold text-sky-200 rounded-md">
          {steps.map((step, index) => (
            <li
              key={index}
              className={`step transition-colors duration-500 ease-in-out ${
                index <= currentStep ? "step-accent" : ""
              }`}
            >
              {step}
            </li>
          ))}
        </ul>
        
        {/* CHAT LOG */}
        <div className='bg-zinc-900 p-5'>
          <p className='pb-3 font-bold'>CHAT LOG</p>
          
          <div className="chat chat-start">
            <div className="chat-bubble bg-white text-black">
              {userTranscription ? userTranscription : "User Message"}
            </div>
          </div>
          <div className="chat chat-end">
            <div className="chat-bubble bg-white text-black">
              {assistantTranscription ? assistantTranscription : "AI Message"}
            </div>
          </div>
        </div>
        
      </div>

      {!accessToken && (
          <div className="modal modal-open" role="dialog">
            <div className="modal-box">
              <h3 className="text-lg font-bold">Hello!</h3>
              <p className="py-4">
                Enter your demo API key to continue.
              </p>
              <PasswordInput setAccessToken={setAccessToken}/>
  
            </div>
          </div>
      )}

     
    </main>
  );
}