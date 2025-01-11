import React, { useRef } from "react";
import { useFrame } from "@react-three/fiber";
import * as THREE from "three";
import { ConvexGeometry } from "three/addons/geometries/ConvexGeometry.js";
import { useXR } from "@react-three/xr";

export function HandSelection({
  onHull,
  dummy = new THREE.Object3D(),
}: {
  onHull: (ar: number[]) => void;
  dummy: THREE.Object3D;
}) {
  const trail = useRef<THREE.Vector3[]>([]);
  const allPoints = useRef<THREE.Vector3[]>([]);
  const instanceRef = useRef<THREE.InstancedMesh>(null);
  const hullRef = useRef<THREE.LineSegments>(null); // Ref to manage the hull wireframe
  const hullGeometryRef = useRef<ConvexGeometry | null>(null); // Ref to store convex hull geometry
  const edgesGeometryRef = useRef<THREE.EdgesGeometry | null>(null); // Ref to store edges geometry

  const session = useXR((state) => state.session);
  const clickPosition = new THREE.Vector3();

  useFrame((state, delta) => {
    const hands = [state.gl.xr.getHand(0), state.gl.xr.getHand(1)];
    if (session && hands[0] && hands[1]) {
      hands.forEach((hand) => {
        const indexFinger = hand.joints["index-finger-tip"];
        const pinkyFinger = hand.joints["pinky-finger-tip"];
        const thumb = hand.joints["thumb-tip"];
        if (!indexFinger || !pinkyFinger || !thumb) {
          return;
        }
        // if thumb and index finger are close, then we have a click
        const clicked = indexFinger.position.distanceTo(thumb.position) < 0.01;
        if (!clicked) {
          const reset = pinkyFinger.position.distanceTo(thumb.position) < 0.01;
          if (reset) {
            trail.current = [];
            allPoints.current = [];
            return;
          }
          return;
        }
        const pos = indexFinger.getWorldPosition(clickPosition);
        let distance = trail.current.length
          ? pos.distanceTo(trail.current[trail.current.length - 1])
          : 10;
        if (distance > 0.0001) {
          trail.current.push(pos.clone());
          allPoints.current.push(pos.clone());
        }
        // only keep the last 500 points
        if (trail.current.length > 500) {
          trail.current.shift();
        }
        // set all 500 points to a very small scale
        for (let i = 0; i < 500; i++) {
          dummy.scale.setScalar(0.000001);
          dummy.position.set(0, 0, 0);
          dummy.updateMatrix();
          instanceRef.current!.setMatrixAt(i, dummy.matrix);
        }
        trail.current.forEach((point, i) => {
          dummy.scale.setScalar(0.001);
          dummy.position.set(point.x, point.y, point.z);
          dummy.updateMatrix();
          instanceRef.current!.setMatrixAt(i, dummy.matrix);
        });
        instanceRef.current!.instanceMatrix.needsUpdate = true;

        if (allPoints.current.length >= 4) {
          // Dispose of previous geometries to avoid memory leaks
          if (hullGeometryRef.current) hullGeometryRef.current.dispose();
          if (edgesGeometryRef.current) edgesGeometryRef.current.dispose();

          // Create new convex hull geometry
          hullGeometryRef.current = new ConvexGeometry(allPoints.current);
          edgesGeometryRef.current = new THREE.EdgesGeometry(
            hullGeometryRef.current,
          );
          if (onHull) {
            const ar = hullGeometryRef.current.attributes["position"].array;
            const data = [...ar];
            onHull(data);
          }

          // Update the edges geometry in the line segments
          if (hullRef.current) {
            hullRef.current.geometry = edgesGeometryRef.current;
          }
        }
      });
    }
  });

  return (
    <>
      <>
        <instancedMesh ref={instanceRef} args={[undefined, undefined, 500]}>
          <dodecahedronGeometry args={[0.05, 0]} />
          <meshBasicMaterial color="red" transparent={true} opacity={0} />
        </instancedMesh>
        {/* Draw Convex Hull Wireframe */}
        <lineSegments ref={hullRef}>
          <lineBasicMaterial color="cyan" />
        </lineSegments>
      </>
    </>
  );
}
