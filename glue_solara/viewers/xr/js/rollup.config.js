import { nodeResolve } from "@rollup/plugin-node-resolve";
import commonjs from "@rollup/plugin-commonjs";
import replace from "@rollup/plugin-replace";
import typescript from "@rollup/plugin-typescript";
import terser from "@rollup/plugin-terser";

const production = !process.env.ROLLUP_WATCH;

const plugins = [
  replace({
    "process.env.NODE_ENV": JSON.stringify(
      production ? "production" : "development",
    ),
  }),
  nodeResolve({
    browser: true,
    extensions: [".js", ".jsx", ".ts", ".tsx"],
  }),
  commonjs({
    namedExports: {
      scheduler: [
        "unstable_runWithPriority",
        "unstable_IdlePriority",
        "unstable_now",
        "unstable_scheduleCallback",
        "unstable_cancelCallback",
      ],
    },
  }),
  typescript({}),
  production && terser(),
];

const externals = [
  "react",
  "react-dom",
  "react-reconciler",
  "react-reconciler/constant",
];

const output = {
  dir: "build",
  entryFileNames: "[name].esm.js",
  format: "es",
  inlineDynamicImports: true,
};

const reactThreeConfig = {
  output,
  external: [...externals, "three", "@react-three/fiber"],
  plugins,
};

export default [
  {
    input: {
      "glue-xr-viewer": "./src/index.tsx",
    },
    output: {
      dir: "build",
      entryFileNames: "[name].esm.js",
      format: "es",
    },
    external: [
      ...externals,
      "@react-three/fiber",
      "@react-three/drei",
      "@react-three/xr",
      "three",
    ],
    plugins,
  },
  {
    input: {
      three: "./src/threejs.ts",
    },
    output,
    external: externals,
    plugins,
  },
  {
    input: {
      "@react-three/fiber": "./src/fiber.ts",
    },
    output,
    external: [...externals, "three"],
    plugins,
  },
  {
    input: {
      "@react-three/drei": "./src/drei.ts",
    },
    ...reactThreeConfig,
  },
  {
    input: {
      "@react-three/xr": "./src/xr.ts",
    },
    ...reactThreeConfig,
  },
];
