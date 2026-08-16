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
    let particles: Graphics | undefined;
    let initializing: Promise<void> | undefined;

    const initialize = async (snapshot: Snapshot): Promise<void> => {
      const nextApplication = new Application();
      await nextApplication.init({
        width: snapshot.width,
        height: snapshot.height,
        background: "#121212",
        antialias: true,
      });
      if (disposed) {
        nextApplication.destroy(true);
        return;
      }

      application = nextApplication;
      container.appendChild(nextApplication.canvas);
      particles = new Graphics();
      nextApplication.stage.addChild(particles);
    };

    const start = (): void => {
      socket = new WebSocket(websocketUrl);
      socket.onopen = () => setStatus("connected");
      socket.onerror = () => setStatus("connection error");
      socket.onclose = () => setStatus("disconnected");
      socket.onmessage = (message): void => {
        const snapshot = JSON.parse(message.data as string) as Snapshot;
        const render = async (): Promise<void> => {
          if (application === undefined) {
            initializing ??= initialize(snapshot);
            await initializing;
            initializing = undefined;
          }
          if (disposed || particles === undefined) {
            return;
          }

          setTick(snapshot.tick);
          particles.clear();
          for (const particle of snapshot.particles) {
            if (!particle.alive) {
              continue;
            }
            particles.circle(particle.x, particle.y, particle.radius).fill(0xe6e6e1);
          }
        };
        void render();
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
