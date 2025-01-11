import { type ThreeElements } from "@react-three/fiber";

declare global {
  namespace React {
    namespace JSX {
      interface IntrinsicElements extends ThreeElements {}
    }
  }
}

export type CoordinateArrayBinary = {
  dataView: DataView;
  dtype: string;
  shape: number[];
};
