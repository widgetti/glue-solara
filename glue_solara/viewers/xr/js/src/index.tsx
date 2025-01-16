import React, { useEffect, useRef } from "react";
import * as THREE from "three";
import type { CoordinateArrayBinary } from "./types";
import { Canvas } from "@react-three/fiber";

// re-export vizxr components
export {
  XRStoreProvider,
  XRButtons,
  XRStore,
  ConditionalOrbitControls,
} from "./vizxr";

export { HandSelection } from "./hand-selection";

export function CustomInstancedMesh({
  limit,
  dummy = new THREE.Object3D(),
  children = [],
  x,
  y,
  z,
  model_scaling_factor = 1,
}: {
  limit: number;
  dummy: THREE.Object3D;
  children: React.ReactNode;
  x: CoordinateArrayBinary;
  y: CoordinateArrayBinary;
  z: CoordinateArrayBinary;
  model_scaling_factor: number;
}) {
  const instanceRef = useRef<THREE.InstancedMesh>(null);
  console.log("InstancedMesh", children, x, y, z, limit, model_scaling_factor);
  useEffect(() => {
    const mesh = instanceRef.current!;
    if (limit === 0 || !x.dataView || !y.dataView || !z.dataView) {
      return;
    }
    const xar = new Float32Array(x.dataView.buffer);
    const yar = new Float32Array(y.dataView.buffer);
    const zar = new Float32Array(z.dataView.buffer);
    for (let i = 0; i < limit; i++) {
      const point = new THREE.Vector3(
        xar[i] * model_scaling_factor,
        yar[i] * model_scaling_factor,
        zar[i] * model_scaling_factor,
      );
      dummy.scale.setScalar(0.01);
      dummy.position.set(point.x, point.y, point.z);
      dummy.updateMatrix();
      mesh.setMatrixAt(i, dummy.matrix);
    }
    mesh.instanceMatrix.needsUpdate = true;
    console.log(
      "InstancedMesh data updated",
      limit,
      mesh.count,
      "with scaling factor",
      model_scaling_factor,
    );
  });

  return (
    <instancedMesh ref={instanceRef} args={[undefined, undefined, limit]}>
      {children}
    </instancedMesh>
  );
}
