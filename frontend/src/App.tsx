import { Application, Graphics } from "pixi.js";
import { type ReactElement, useEffect, useRef, useState } from "react";

type Particle = {
  x: number;
  y: number;
  radius: number;
  species: number;
  alive: boolean;
};

type Snapshot = {
  tick: number;
  width: number;
  height: number;
  particles: Particle[];
};

const websocketUrl = import.meta.env.VITE_ALIFE_WS_URL ?? "ws://127.0.0.1:8000/ws";

export function App(): ReactElement {
  const canvasContainer = useRef<HTMLDivElement>(null);
  const [status, setStatus] = useState("connecting");
  const [tick, setTick] = useState(0);

  useEffect(() => {
    const container = canvasContainer.current;
    if (container === null) {
      return;
    }

    let disposed = false;
    let socket: WebSocket | undefined;
    let application: Application | undefined;

    const start = async (): Promise<void> => {
      const nextApplication = new Application();
      await nextApplication.init({
        width: 800,
        height: 500,
        background: "#121212",
        antialias: true,
      });
      if (disposed) {
        nextApplication.destroy(true);
        return;
      }

      application = nextApplication;
      container.appendChild(nextApplication.canvas);
      const particles = new Graphics();
      nextApplication.stage.addChild(particles);

      socket = new WebSocket(websocketUrl);
      socket.onopen = () => setStatus("connected");
      socket.onerror = () => setStatus("connection error");
      socket.onclose = () => setStatus("disconnected");
      socket.onmessage = (message) => {
        const snapshot = JSON.parse(message.data as string) as Snapshot;
        setTick(snapshot.tick);
        const scaleX = 800 / snapshot.width;
        const scaleY = 500 / snapshot.height;
        particles.clear();
        for (const particle of snapshot.particles) {
          if (!particle.alive) {
            continue;
          }
          particles
            .circle(particle.x * scaleX, particle.y * scaleY, particle.radius * scaleX)
            .fill(0xe6e6e1);
        }
      };
    };

    void start();
    return () => {
      disposed = true;
      socket?.close();
      application?.destroy(true);
      container.replaceChildren();
    };
  }, []);

  return (
    <main>
      <header>
        <div>
          <p className="eyebrow">CPU reference simulation</p>
          <h1>Particle field</h1>
        </div>
        <div className="status">
          <span className="dot" />
          <span>{status}</span>
          <span>tick {tick}</span>
        </div>
      </header>
      <section ref={canvasContainer} className="canvas-frame" aria-label="particle simulation" />
    </main>
  );
}
