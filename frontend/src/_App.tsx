/**
 * WebSocketでsnapshotとstatusを受信し、PixiJSで粒子を描画するmain component。
 * cameraの移動とzoom、keyboard shortcut(space / r / s / esc / 矢印)、
 * 操作console(開閉、pause、restart、speed_multiplier、save)を担う。
 */
import { Application, Container, Graphics } from "pixi.js";
import { type ReactElement, useEffect, useRef, useState } from "react";

import { uiConfig } from "./_ui_config";

type _Particle = {
  x: number;
  y: number;
  radius: number;
  species: number;
  alive: boolean;
};

type _SnapshotMessage = {
  type: "snapshot";
  tick: number;
  width: number;
  height: number;
  particles: _Particle[];
};

type _StatusMessage = {
  type: "status";
  paused: boolean;
  compute_backend: string;
  speed_multiplier: number;
  speed_multiplier_min: number;
  speed_multiplier_max: number;
  speed_multiplier_step: number;
  tick: number;
  dt_simu: number;
  dt_required: number;
  elapsed_average: number;
  snapshot_hz_render: number;
  snapshot_hz_render_real: number;
  performance: "normal" | "lagging";
  run_results_enabled: boolean;
  run_started: boolean;
};

type _SaveResultMessage = {
  type: "save_result";
  tick: number;
  path: string;
};

type _ErrorMessage = {
  type: "error";
  message: string;
};

type _ServerMessage = _SnapshotMessage | _StatusMessage | _SaveResultMessage | _ErrorMessage;

type _Command =
  | { type: "toggle_pause" }
  | { type: "restart" }
  | { type: "save" }
  | { type: "set_speed"; speed_multiplier: number };

type _MapView = {
  worldWidth: number;
  worldHeight: number;
  viewportX: number;
  viewportY: number;
  viewportWidth: number;
  viewportHeight: number;
};

type _FootprintPoint = {
  x: number;
  y: number;
};

type _PanDirection = "up" | "down" | "left" | "right";

const _websocketUrl = import.meta.env.VITE_ALIFE_WS_URL ?? "ws://127.0.0.1:8000/ws";
function _isServerMessage(value: unknown): value is _ServerMessage {
  return typeof value === "object" && value !== null && "type" in value;
}

export function App(): ReactElement {
  const canvasContainer = useRef<HTMLDivElement>(null);
  const socketRef = useRef<WebSocket | null>(null);
  const resetViewRef = useRef<(() => void) | null>(null);
  const startPanRef = useRef<((direction: _PanDirection) => void) | null>(null);
  const stopPanRef = useRef<((direction?: _PanDirection) => void) | null>(null);
  const [connectionStatus, setConnectionStatus] = useState("connecting");
  const [computeBackend, setComputeBackend] = useState("numpy");
  const [paused, setPaused] = useState(true);
  const [speedMultiplier, setSpeedMultiplier] = useState(uiConfig.speed_multiplier_default);
  const [speedMultiplierMin, setSpeedMultiplierMin] = useState(uiConfig.speed_multiplier_min);
  const [speedMultiplierMax, setSpeedMultiplierMax] = useState(uiConfig.speed_multiplier_max);
  const [speedInput, setSpeedInput] = useState(String(uiConfig.speed_multiplier_default));
  const [speedInputError, setSpeedInputError] = useState("");
  const [tick, setTick] = useState(0);
  const [dtSimu, setDtSimu] = useState(0.0);
  const [dtRequired, setDtRequired] = useState(0.0);
  const [elapsedAverage, setElapsedAverage] = useState(0.0);
  const [snapshotHzRender, setSnapshotHzRender] = useState(0.0);
  const [snapshotHzRenderReal, setSnapshotHzRenderReal] = useState(0.0);
  const [performance, setPerformance] = useState<"normal" | "lagging">("normal");
  const [runResultsEnabled, setRunResultsEnabled] = useState(true);
  const [runStarted, setRunStarted] = useState(false);
  const [consoleOpen, setConsoleOpen] = useState(true);
  const [activeShortcut, setActiveShortcut] = useState("");
  const [saveMessage, setSaveMessage] = useState("");
  const [mapView, setMapView] = useState<_MapView | null>(null);

  const _sendCommand = (command: _Command): void => {
    const socket = socketRef.current;
    if (socket?.readyState === WebSocket.OPEN) {
      socket.send(JSON.stringify(command));
    }
  };

  const _flashShortcut = (shortcut: string): void => {
    setActiveShortcut(shortcut);
    window.setTimeout(() => {
      setActiveShortcut((active) => (active === shortcut ? "" : active));
    }, 140);
  };

  const _setSpeedFromInput = (value: string): void => {
    setSpeedInput(value);
    const parsed = Number(value.trim());
    if (value.trim() === "" || !Number.isFinite(parsed)) {
      setSpeedInputError("speed_multiplier must be a float");
      return;
    }
    if (parsed < speedMultiplierMin || parsed > speedMultiplierMax) {
      setSpeedInputError(
        `speed_multiplier must be between ${speedMultiplierMin} and ${speedMultiplierMax}`,
      );
      return;
    }
    setSpeedInputError("");
    _sendCommand({ type: "set_speed", speed_multiplier: parsed });
  };

  const _setSpeedFromSlider = (value: number): void => {
    const formatted = String(value);
    setSpeedInput(formatted);
    setSpeedInputError("");
    _sendCommand({ type: "set_speed", speed_multiplier: value });
  };

  useEffect(() => {
    const container = canvasContainer.current;
    if (container === null) {
      return;
    }

    let disposed = false;
    let socket: WebSocket | undefined;
    let application: Application | undefined;
    let world: Container | undefined;
    let particles: Graphics | undefined;
    let footprint: Graphics | undefined;
    let initializing: Promise<void> | undefined;
    let renderChain: Promise<void> = Promise.resolve();
    let removeCanvasInteractions: (() => void) | undefined;
    let resizeObserver: ResizeObserver | undefined;
    const camera = { x: 0, y: 0, scale: 1.0 };
    const worldSize = { width: 0, height: 0 };
    const footprintHistory: Array<_FootprintPoint[]> = [];
    let lastSnapshotTick = -1;
    const heldPanDirections = new Set<_PanDirection>();
    let panAnimationFrame: number | null = null;

    const applyCamera = (): void => {
      if (world === undefined || application === undefined) {
        return;
      }
      world.position.set(camera.x, camera.y);
      world.scale.set(camera.scale);
      setMapView({
        worldWidth: worldSize.width,
        worldHeight: worldSize.height,
        viewportX: -camera.x / camera.scale,
        viewportY: -camera.y / camera.scale,
        viewportWidth: application.screen.width / camera.scale,
        viewportHeight: application.screen.height / camera.scale,
      });
    };

    resetViewRef.current = (): void => {
      if (application === undefined || worldSize.width === 0 || worldSize.height === 0) {
        return;
      }
      camera.scale = Math.min(
        uiConfig.camera.max_scale,
        Math.max(
          uiConfig.camera.min_scale,
          application.screen.width / worldSize.width,
          application.screen.height / worldSize.height,
        ),
      );
      camera.x = (application.screen.width - worldSize.width * camera.scale) / 2;
      camera.y = (application.screen.height - worldSize.height * camera.scale) / 2;
      applyCamera();
    };

    const _panCamera = (direction: _PanDirection): void => {
      const panStep = uiConfig.camera.pan_step / camera.scale;
      if (direction === "left") {
        camera.x += panStep;
      } else if (direction === "right") {
        camera.x -= panStep;
      } else if (direction === "up") {
        camera.y += panStep;
      } else {
        camera.y -= panStep;
      }
      applyCamera();
    };
    const _panAnimation = (): void => {
      if (heldPanDirections.size === 0) {
        panAnimationFrame = null;
        return;
      }
      for (const direction of heldPanDirections) {
        _panCamera(direction);
      }
      panAnimationFrame = requestAnimationFrame(_panAnimation);
    };

    const _startPan = (direction: _PanDirection): void => {
      heldPanDirections.add(direction);
      if (panAnimationFrame === null) {
        _panAnimation();
      }
    };

    const _stopPan = (direction?: _PanDirection): void => {
      if (direction === undefined) {
        heldPanDirections.clear();
      } else {
        heldPanDirections.delete(direction);
      }
      if (heldPanDirections.size === 0 && panAnimationFrame !== null) {
        cancelAnimationFrame(panAnimationFrame);
        panAnimationFrame = null;
      }
    };
    startPanRef.current = _startPan;
    stopPanRef.current = _stopPan;

    const _initialize = async (snapshot: _SnapshotMessage): Promise<void> => {
      const nextApplication = new Application();
      await nextApplication.init({
        resizeTo: container,
        background: "#121212",
        antialias: true,
      });
      if (disposed) {
        nextApplication.destroy(true);
        return;
      }

      application = nextApplication;
      worldSize.width = snapshot.width;
      worldSize.height = snapshot.height;
      container.appendChild(nextApplication.canvas);
      world = new Container();
      const wallThickness = uiConfig.wall.thickness;
      const wall = new Graphics()
        .rect(
          -wallThickness,
          -wallThickness,
          snapshot.width + wallThickness * 2,
          snapshot.height + wallThickness * 2,
        )
        .fill(0xd2d2cd)
        .rect(0, 0, snapshot.width, snapshot.height)
        .fill(0x121212);
      footprint = new Graphics();
      particles = new Graphics();
      world.addChild(wall);
      world.addChild(footprint);
      world.addChild(particles);
      nextApplication.stage.addChild(world);
      resetViewRef.current?.();
      resizeObserver = new ResizeObserver(() => resetViewRef.current?.());
      resizeObserver.observe(container);

      const canvas = nextApplication.canvas;
      canvas.style.touchAction = "none";
      let dragging = false;
      let lastClientX = 0;
      let lastClientY = 0;

      const pointerDown = (event: PointerEvent): void => {
        dragging = true;
        lastClientX = event.clientX;
        lastClientY = event.clientY;
        canvas.setPointerCapture(event.pointerId);
      };
      const pointerMove = (event: PointerEvent): void => {
        if (!dragging || application === undefined) {
          return;
        }
        const rect = canvas.getBoundingClientRect();
        const scaleX = application.screen.width / rect.width;
        const scaleY = application.screen.height / rect.height;
        camera.x += (event.clientX - lastClientX) * scaleX;
        camera.y += (event.clientY - lastClientY) * scaleY;
        lastClientX = event.clientX;
        lastClientY = event.clientY;
        applyCamera();
      };
      const pointerUp = (event: PointerEvent): void => {
        dragging = false;
        if (canvas.hasPointerCapture(event.pointerId)) {
          canvas.releasePointerCapture(event.pointerId);
        }
      };
      const wheel = (event: WheelEvent): void => {
        if (application === undefined) {
          return;
        }
        event.preventDefault();
        const rect = canvas.getBoundingClientRect();
        const scaleX = application.screen.width / rect.width;
        const scaleY = application.screen.height / rect.height;
        const pointerX = (event.clientX - rect.left) * scaleX;
        const pointerY = (event.clientY - rect.top) * scaleY;
        const worldX = (pointerX - camera.x) / camera.scale;
        const worldY = (pointerY - camera.y) / camera.scale;
        const zoom = event.deltaY < 0 ? 1.1 : 0.9;
        camera.scale = Math.min(
          uiConfig.camera.max_scale,
          Math.max(uiConfig.camera.min_scale, camera.scale * zoom),
        );
        camera.x = pointerX - worldX * camera.scale;
        camera.y = pointerY - worldY * camera.scale;
        applyCamera();
      };

      canvas.addEventListener("pointerdown", pointerDown);
      canvas.addEventListener("pointermove", pointerMove);
      canvas.addEventListener("pointerup", pointerUp);
      canvas.addEventListener("pointercancel", pointerUp);
      canvas.addEventListener("wheel", wheel, { passive: false });
      removeCanvasInteractions = (): void => {
        canvas.removeEventListener("pointerdown", pointerDown);
        canvas.removeEventListener("pointermove", pointerMove);
        canvas.removeEventListener("pointerup", pointerUp);
        canvas.removeEventListener("pointercancel", pointerUp);
        canvas.removeEventListener("wheel", wheel);
      };
    };

    const _renderFootprint = (snapshot: _SnapshotMessage): void => {
      if (snapshot.tick < lastSnapshotTick) {
        footprintHistory.length = 0;
      }
      lastSnapshotTick = snapshot.tick;
      if (!uiConfig.show_particle_footprint || footprint === undefined) {
        footprintHistory.length = 0;
        footprint?.clear();
        return;
      }

      const footprintGraphics = footprint;
      footprintGraphics.clear();
      snapshot.particles.forEach((particle, particleIndex) => {
        const history =
          footprintHistory[particleIndex] ?? (footprintHistory[particleIndex] = []);
        if (!particle.alive) {
          history.length = 0;
          return;
        }
        history.push({ x: particle.x, y: particle.y });
        if (history.length > uiConfig.max_particle_footprint_points) {
          history.shift();
        }
        for (let pointIndex = 1; pointIndex < history.length; pointIndex += 1) {
          const previous = history[pointIndex - 1];
          const current = history[pointIndex];
          footprintGraphics
            .moveTo(previous.x, previous.y)
            .lineTo(current.x, current.y)
            .stroke({
              color: 0xe6e6e1,
              alpha: (pointIndex / (history.length - 1)) * 0.35,
              width: 1.2,
            });
        }
      });
    };

    const _renderSnapshot = async (snapshot: _SnapshotMessage): Promise<void> => {
      if (application === undefined) {
        initializing ??= _initialize(snapshot);
        await initializing;
        initializing = undefined;
      }
      if (disposed || particles === undefined) {
        return;
      }

      setTick(snapshot.tick);
      _renderFootprint(snapshot);
      particles.clear();
      for (const particle of snapshot.particles) {
        if (!particle.alive) {
          continue;
        }
        particles.circle(particle.x, particle.y, particle.radius).fill(0xe6e6e1);
      }
    };

    const _handleMessage = (message: _ServerMessage): void => {
      if (message.type === "snapshot") {
        renderChain = renderChain.then(() => _renderSnapshot(message));
        return;
      }
      if (message.type === "status") {
        setPaused(message.paused);
        setComputeBackend(message.compute_backend);
        setSpeedMultiplier(message.speed_multiplier);
        setSpeedMultiplierMin(message.speed_multiplier_min);
        setSpeedMultiplierMax(message.speed_multiplier_max);
        setTick(message.tick);
        setDtSimu(message.dt_simu);
        setDtRequired(message.dt_required);
        setElapsedAverage(message.elapsed_average);
        setSnapshotHzRender(message.snapshot_hz_render);
        setSnapshotHzRenderReal(message.snapshot_hz_render_real);
        setPerformance(message.performance);
        setRunResultsEnabled(message.run_results_enabled);
        setRunStarted(message.run_started);
        return;
      }
      if (message.type === "save_result") {
        setSaveMessage(`saved: ${message.path}`);
        return;
      }
      setSaveMessage(message.message);
    };

    socket = new WebSocket(_websocketUrl);
    socketRef.current = socket;
    socket.onopen = (): void => setConnectionStatus("connected");
    socket.onerror = (): void => setConnectionStatus("connection error");
    socket.onclose = (): void => setConnectionStatus("disconnected");
    socket.onmessage = (event: MessageEvent<string>): void => {
      const value: unknown = JSON.parse(event.data);
      if (_isServerMessage(value)) {
        _handleMessage(value);
      }
    };

    const _keydown = (event: KeyboardEvent): void => {
      if (event.key === "Escape") {
        setConsoleOpen((open) => !open);
        return;
      }
      const target = event.target;
      const inFormControl =
        target instanceof HTMLElement &&
        target.closest("button, input, textarea, select") !== null;
      if (event.code === "Space") {
        // button にフォーカスがあっても常に pause/resume に割り当て、
        // ブラウザ既定の「space で button を激活」を preventDefault で無効化する。
        // input / textarea / select 内では入力を壊すため何もしない。
        if (
          !(target instanceof HTMLElement && target.closest("input, textarea, select") !== null)
        ) {
          event.preventDefault();
          _flashShortcut("space");
          _sendCommand({ type: "toggle_pause" });
        }
        return;
      }
      if (inFormControl) {
        return;
      }
      if (event.key === "r") {
        _flashShortcut("r");
        _sendCommand({ type: "restart" });
        return;
      }
      if (event.key === "s") {
        _flashShortcut("s");
        _sendCommand({ type: "save" });
        return;
      }
      if (event.key === "ArrowLeft") {
        setActiveShortcut("left");
        _startPan("left");
      } else if (event.key === "ArrowRight") {
        setActiveShortcut("right");
        _startPan("right");
      } else if (event.key === "ArrowUp") {
        setActiveShortcut("up");
        _startPan("up");
      } else if (event.key === "ArrowDown") {
        setActiveShortcut("down");
        _startPan("down");
      } else {
        return;
      }
      event.preventDefault();
    };
    const _keyup = (event: KeyboardEvent): void => {
      const direction =
        event.key === "ArrowLeft"
          ? "left"
          : event.key === "ArrowRight"
            ? "right"
            : event.key === "ArrowUp"
              ? "up"
              : event.key === "ArrowDown"
                ? "down"
                : undefined;
      if (direction === undefined) {
        return;
      }
      event.preventDefault();
      _stopPan(direction);
      setActiveShortcut((active) => (active === direction ? "" : active));
    };
    const _blur = (): void => {
      _stopPan();
      setActiveShortcut("");
    };
    window.addEventListener("keydown", _keydown);
    window.addEventListener("keyup", _keyup);
    window.addEventListener("blur", _blur);

    return () => {
      disposed = true;
      resetViewRef.current = null;
      startPanRef.current = null;
      stopPanRef.current = null;
      _stopPan();
      resizeObserver?.disconnect();
      window.removeEventListener("keydown", _keydown);
      window.removeEventListener("keyup", _keyup);
      window.removeEventListener("blur", _blur);
      removeCanvasInteractions?.();
      socket?.close();
      socketRef.current = null;
      application?.destroy(true);
      container.replaceChildren();
    };
  }, []);

  const _pressPan = (direction: _PanDirection): void => {
    setActiveShortcut(direction);
    startPanRef.current?.(direction);
  };

  const _releasePan = (direction: _PanDirection): void => {
    stopPanRef.current?.(direction);
    setActiveShortcut((active) => (active === direction ? "" : active));
  };

  const _panButton = (direction: _PanDirection, label: string, title: string): ReactElement => (
    <button
      className={`shortcut-button ${activeShortcut === direction ? "is-pressed" : ""}`}
      type="button"
      aria-label={`Pan camera ${direction}`}
      title={title}
      onPointerDown={(event) => {
        event.currentTarget.setPointerCapture(event.pointerId);
        _pressPan(direction);
      }}
      onPointerUp={(event) => {
        _releasePan(direction);
        if (event.currentTarget.hasPointerCapture(event.pointerId)) {
          event.currentTarget.releasePointerCapture(event.pointerId);
        }
      }}
      onPointerCancel={() => _releasePan(direction)}
      onKeyDown={(event) => {
        if (event.key === "Enter" && !event.repeat) {
          event.preventDefault();
          _pressPan(direction);
        }
      }}
      onKeyUp={(event) => {
        if (event.key === "Enter") {
          event.preventDefault();
          _releasePan(direction);
        }
      }}
    >
      {label}
    </button>
  );

  return (
    <main className="fullscreen-view">
      <section className="canvas-frame" aria-label="particle simulation">
        <div ref={canvasContainer} className="canvas-mount" />
        {mapView !== null && (
          <div className="minimap" aria-label="current simulation view">
            <svg
              viewBox={`0 0 ${mapView.worldWidth} ${mapView.worldHeight}`}
              role="img"
            >
              <rect
                className="minimap-world"
                x="0"
                y="0"
                width={mapView.worldWidth}
                height={mapView.worldHeight}
              />
              <rect
                className="minimap-viewport"
                x={mapView.viewportX}
                y={mapView.viewportY}
                width={mapView.viewportWidth}
                height={mapView.viewportHeight}
              />
            </svg>
          </div>
        )}
        <div className="overlay-info" aria-live="polite">
          <h1>Particle field</h1>
          <div className="status" aria-live="polite">
            <span className="dot" />
            <span>WebSocket: {connectionStatus}</span>
            <span className="simulation-state">
              <span aria-hidden="true">{paused ? "⏸" : "▶"}</span>
              <span>{paused ? "paused" : "running"}</span>
            </span>
          </div>
          <div className="runtime-info">
            <span>compute_backend: {computeBackend}</span>
            <span>speed_multiplier: {speedMultiplier.toFixed(2)}</span>
            <span className="performance-line">
              dt_simu: {dtSimu.toFixed(4)} sec. | elapsed_average: {elapsedAverage.toFixed(4)} sec. {performance === "normal" ? "<=" : ">"} dt_required: {dtRequired.toFixed(4)} sec. {" "}
              <span className={`performance ${performance}`}>{performance}</span>
            </span>
            <span>
              snapshot_hz_render: set {snapshotHzRender.toFixed(1)} | real {snapshotHzRenderReal.toFixed(1)}
            </span>
            <span>tick: {tick}</span>
          </div>
        </div>
        <div className={`console ${consoleOpen ? "console-open" : "console-closed"}`}>
          <button
            className="console-toggle"
            type="button"
            aria-expanded={consoleOpen}
            onClick={() => setConsoleOpen((open) => !open)}
          >
            {consoleOpen ? "Close console (esc)" : "Open console (esc)"}
          </button>
          {consoleOpen && (
            <aside className="console-panel" aria-label="simulation console">
              <button
                className={`shortcut-button ${activeShortcut === "space" ? "is-pressed" : ""}`}
                type="button"
                onClick={() => {
                  _flashShortcut("space");
                  _sendCommand({ type: "toggle_pause" });
                }}
              >
                <span aria-hidden="true">{paused ? "▶" : "⏸"}</span>{" "}
                {paused ? "Start (space)" : "Pause (space)"}
              </button>
              <button
                className={`shortcut-button ${activeShortcut === "r" ? "is-pressed" : ""}`}
                type="button"
                onClick={() => {
                  _flashShortcut("r");
                  _sendCommand({ type: "restart" });
                }}
              >
                Restart (r)
              </button>
              <div className="direction-control">
                <span className="direction-label">Camera pan</span>
                <div className="direction-pad" aria-label="camera pan shortcuts">
                  <span />
                  {_panButton("up", "↑", "Arrow up")}
                  <span />
                  {_panButton("left", "←", "Arrow left")}
                  <button
                    className="shortcut-button reset-view-button"
                    type="button"
                    aria-label="Reset camera view"
                    title="Reset view"
                    onClick={() => resetViewRef.current?.()}
                  >
                    ResetView
                  </button>
                  {_panButton("right", "→", "Arrow right")}
                  <span />
                  {_panButton("down", "↓", "Arrow down")}
                  <span />
                </div>
              </div>
              <button
                className={`shortcut-button ${activeShortcut === "s" ? "is-pressed" : ""}`}
                type="button"
                disabled={!runResultsEnabled || !runStarted}
                onClick={() => {
                  _flashShortcut("s");
                  _sendCommand({ type: "save" });
                }}
              >
                Save (s)
              </button>
              <div className="speed-control">
                <label htmlFor="speed-multiplier-input">
                  speed_multiplier
                  <input
                    id="speed-multiplier-input"
                    type="number"
                    inputMode="decimal"
                    step="any"
                    value={speedInput}
                    onChange={(event) => _setSpeedFromInput(event.target.value)}
                    aria-describedby="speed-multiplier-help"
                  />
                </label>
                <input
                  type="range"
                  min={Math.log10(speedMultiplierMin)}
                  max={Math.log10(speedMultiplierMax)}
                  step="any"
                  value={Math.log10(speedMultiplier)}
                  disabled={speedMultiplierMax <= speedMultiplierMin}
                  onChange={(event) => _setSpeedFromSlider(10 ** Number(event.target.value))}
                  aria-label="speed multiplier logarithmic slider"
                />
                <span id="speed-multiplier-help" className="speed-range">
                  range: {speedMultiplierMin} - {speedMultiplierMax} (log)
                </span>
                {speedInputError !== "" && (
                  <p className="console-warning" role="alert">{speedInputError}</p>
                )}
              </div>
              {!runResultsEnabled && (
                <p className="console-message">Save unavailable: --no-run-results</p>
              )}
              {runResultsEnabled && !runStarted && (
                <p className="console-message">Save available after start</p>
              )}
              {saveMessage !== "" && <p className="console-message">{saveMessage}</p>}
            </aside>
          )}
        </div>
      </section>
    </main>
  );
}
