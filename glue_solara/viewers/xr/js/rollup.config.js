import { nodeResolve } from "@rollup/plugin-node-resolve";
import commonjs from "@rollup/plugin-commonjs";
import replace from "@rollup/plugin-replace";
import typescript from "@rollup/plugin-typescript";
import terser from "@rollup/plugin-terser";

const production = !process.env.ROLLUP_WATCH;

export default {
  input: "./src/index.tsx",
  output: [
    {
      file: "./build/glue-xr-viewer.esm.js",
      format: "es",
      inlineDynamicImports: true,
    },
  ],
  external: [
    "react",
    "react-dom",
    "react-reconciler",
    "react-reconciler/constant",
  ],
  plugins: [
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
    typescript({
      // clean: true,
    }),
    production && terser(),
  ],
};
