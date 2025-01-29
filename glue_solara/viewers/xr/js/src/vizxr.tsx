import React, {
  useState,
  createContext,
  useContext,
  useMemo,
  useEffect,
} from "react";
import * as THREE from "three";
import { Canvas } from "@react-three/fiber";
import { OrbitControls } from "@react-three/drei";
import { XR, createXRStore, IfInSessionMode, useXR } from "@react-three/xr";

const defaultStore = createXRStore();

const XRStoreContext = createContext(defaultStore);

export function XRStoreProvider(props: { children: React.ReactNode }) {
  const store = useMemo(() => createXRStore(), []);
  const { children } = props;
  return (
    <XRStoreContext.Provider value={store}>
      {...Array.isArray(children) ? children : [children]}
    </XRStoreContext.Provider>
  );
}

export function XRButtons() {
  const store = useContext(XRStoreContext);
  // Check if the immersive-ar or immersive-vr session mode is supported
  if (!navigator.xr) {
    return null;
  }
  const [supportsAR, setSupportsAR] = useState(false);
  const [supportsVR, setSupportsVR] = useState(false);
  useEffect(() => {
    const modes: XRSessionMode[] = ["immersive-ar", "immersive-vr"];
    const detectSupport = async () => {
      const [ar, vr] = await Promise.all(
        modes.map(async (mode) => await navigator.xr!.isSessionSupported(mode)),
      );
      setSupportsAR(ar);
      setSupportsVR(vr);
    };
    detectSupport();
  });

  return (
    <>
      {supportsAR && (
        <button onClick={() => store.enterAR()} style={{ padding: "12px" }}>
          Enter AR
        </button>
      )}
      {supportsVR && (
        <button onClick={() => store.enterVR()} style={{ padding: "12px" }}>
          Enter VR
        </button>
      )}
    </>
  );
}

export function XRStore(props: { children: React.ReactNode }) {
  const store = useContext(XRStoreContext);
  const { children } = props;
  console.log("XRStore", { store, defaultStore, children });
  return (
    <XR store={store}>{...Array.isArray(children) ? children : [children]}</XR>
  );
}

export function ConditionalOrbitControls() {
  return (
    <IfInSessionMode deny={["immersive-ar", "immersive-vr"]}>
      <OrbitControls />
    </IfInSessionMode>
  );
}
