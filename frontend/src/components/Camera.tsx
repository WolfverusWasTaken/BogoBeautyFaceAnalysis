import { useRef, useEffect, useState, useCallback } from "react";

interface CameraProps {
    onCapture: (blob: Blob) => void;
    isAnalyzing: boolean;
}

export function Camera({ onCapture, isAnalyzing }: CameraProps) {
    const videoRef = useRef<HTMLVideoElement>(null);
    const canvasRef = useRef<HTMLCanvasElement>(null);
    const [isStreaming, setIsStreaming] = useState(false);
    const [error, setError] = useState<string | null>(null);

    useEffect(() => {
        async function startCamera() {
            try {
                const stream = await navigator.mediaDevices.getUserMedia({
                    video: {
                        width: { ideal: 1280 },
                        height: { ideal: 720 },
                        facingMode: "user",
                    },
                    audio: false,
                });

                if (videoRef.current) {
                    videoRef.current.srcObject = stream;
                    setIsStreaming(true);
                    setError(null);
                }
            } catch (err) {
                console.error("Camera access error:", err);
                setError("Camera access denied. Please allow permissions.");
            }
        }

        startCamera();

        return () => {
            if (videoRef.current?.srcObject) {
                const tracks = (videoRef.current.srcObject as MediaStream).getTracks();
                tracks.forEach((track) => track.stop());
            }
        };
    }, []);

    const captureFrame = useCallback(() => {
        if (!videoRef.current || !canvasRef.current || !isStreaming) return;

        const video = videoRef.current;
        const canvas = canvasRef.current;
        const ctx = canvas.getContext("2d");

        if (!ctx) return;

        canvas.width = video.videoWidth;
        canvas.height = video.videoHeight;

        ctx.translate(canvas.width, 0);
        ctx.scale(-1, 1);
        ctx.drawImage(video, 0, 0);

        canvas.toBlob(
            (blob) => {
                if (blob) {
                    onCapture(blob);
                }
            },
            "image/jpeg",
            0.9
        );
    }, [isStreaming, onCapture]);

    return (
        <div className="h-full flex flex-col">
            <div
                className={`camera-container relative flex-1 min-h-0 ${isAnalyzing ? "pulse-glow" : ""}`}
            >
                {error ? (
                    <div className="flex items-center justify-center h-full p-4">
                        <div className="text-center">
                            <p className="text-[var(--muted)] text-sm">{error}</p>
                        </div>
                    </div>
                ) : (
                    <>
                        <video
                            ref={videoRef}
                            autoPlay
                            playsInline
                            muted
                            className="w-full h-full object-cover rounded-[var(--radius-lg)]"
                            style={{ transform: "scaleX(-1)" }}
                        />

                        <div className="absolute inset-0 bg-gradient-to-t from-black/20 to-transparent pointer-events-none rounded-[var(--radius-lg)]" />

                        {isAnalyzing && (
                            <div className="absolute inset-0 flex items-center justify-center bg-black/30 rounded-[var(--radius-lg)]">
                                <div className="text-center text-white">
                                    <div className="text-base sm:text-lg font-semibold animate-pulse">Analyzing...</div>
                                </div>
                            </div>
                        )}
                    </>
                )}

                <canvas ref={canvasRef} className="hidden" />
            </div>

            {/* Capture Button */}
            <div className="mt-3 flex justify-center">
                <button
                    onClick={captureFrame}
                    disabled={!isStreaming || isAnalyzing}
                    className="btn-primary py-2.5 sm:py-2 px-8 sm:px-6 text-sm w-full sm:w-auto"
                >
                    {isAnalyzing ? "Analyzing..." : "Analyze My Face"}
                </button>
            </div>
        </div>
    );
}
