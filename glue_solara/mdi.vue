<template>
  <div
    ref="main"
    @mousemove="(e) => move(e)"
    style="
      height: 100%;
      max-height: 100%;
      max-width: 100%;
      position: relative;
      overflow: hidden;
    "
    @mouseup="mouseup"
  >
    <div
      v-for="(window, i) in frontendWindows"
      :key="window.id"
      class="elevation-8 glue-solara__window"
      :style="{
        position: 'absolute',
        top: window.y + 'px',
        left: window.x + 'px',
        height: window.height + 'px',
        width: window.width + 'px',
        userSelect: 'none',
        borderRadius: '8px',
        backgroundColor: 'white',
        opacity: currentWindow ? 0.9 : 1,
        display: 'flex',
        flexDirection: 'column',
      }"
    >
      <div
        :class="`glue-solara__window-header pl-${sizes.indexOf(size) + 1}`"
        style="line-height: 0"
        @mousedown.stop="mousedown($event, window, 'drag')"
      >
        <v-btn
          icon
          :x-small="size === 'x-small'"
          :small="size === 'small'"
          :large="size === 'large'"
          :x-large="size === 'x-large'"
          @click.stop="remove(window)"
        >
          <v-icon style="color: white" @mousedown.stop=""
            >mdi-close-circle-outline</v-icon
          >
        </v-btn>
        <v-btn
          icon
          :x-small="size === 'x-small'"
          :small="size === 'small'"
          :large="size === 'large'"
          :x-large="size === 'x-large'"
          @click="fullscreen(window)"
        >
          <v-icon style="color: white" @mousedown.stop=""
            >mdi-fullscreen</v-icon
          >
        </v-btn>
      </div>
      <div
        style="position: relative; flex-grow: 1"
        @click="bringToForeground(window)"
      >
        <div
          :id="`solara-window-content-${window.id}`"
          style="
            height: 100%;
            max-height: 100%;
            max-width: 100%;
            overflow: hidden;
          "
        >
          <jupyter-widget
            v-if="
              children && children[windows.findIndex((w) => w.id === window.id)]
            "
            :widget="children[windows.findIndex((w) => w.id === window.id)]"
          />
        </div>
        <!--        <div class="solara-mdi__resize-corner" @mousedown="mousedown($event, window, 'tl')" style="left: 0; top: 0; cursor: nwse-resize"></div>-->
        <!--        <div class="solara-mdi__resize-corner" @mousedown="mousedown($event, window, 'bl')"  style="left: 0; bottom: 0; cursor: nesw-resize;"></div>-->
        <!--        <div class="solara-mdi__resize-corner" @mousedown="mousedown($event, window, 'tr')"  style="right: 0; top: 0; cursor: nesw-resize;"></div>-->
        <div
          class="solara-mdi__resize-corner"
          @mousedown.stop="mousedown($event, window, 'br')"
          style="right: 0; bottom: 0; cursor: nwse-resize"
        ></div>
      </div>
    </div>
  </div>
</template>
<style id="solara-mdi">
.solara-mdi__resize-corner {
  position: absolute;
  width: 10px;
  height: 10px;
}
.glue-solara__window-header {
  background-color: gray;
  cursor: move;
  border-radius: 8px 8px 0 0;
  position: relative;
}

.glue-solara__window:last-child .glue-solara__window-header {
  background-color: #d0413e;
}
</style>
<script>
export default {
  data() {
    return {
      sizes: ["x-small", "small", null, "large", "x-large"],
      fillColors: ["yellow", "red"],
      frontendWindows: [],
      opp: null,
      currentWindow: null,
      currentWindowCopy: null,
      screenX: null,
      screenY: null,
      offsetX: null,
      offsetY: null,
    };
  },
  methods: {
    mousedown(e, window, opp) {
      this.opp = opp;
      this.currentWindow = window;
      this.currentWindowCopy = { ...window };
      this.screenX = e.screenX;
      this.screenY = e.screenY;
      this.offsetX = e.offsetX;
      this.offsetY = e.offsetY;
      /* render current window on top */
      this.frontendWindows = this.frontendWindows
        .filter((w) => w.id !== window.id)
        .concat([window]);
    },
    move(e) {
      if (e.buttons === 1) {
        if (this.opp === "drag") {
          const rect = this.$refs.main.getBoundingClientRect();
          this.currentWindow.x = e.clientX - this.offsetX - rect.x;
          this.currentWindow.y = e.clientY - this.offsetY - rect.y;
        } else if (this.opp === "br") {
          const dx = this.screenX - e.screenX;
          const dy = this.screenY - e.screenY;
          this.currentWindow.width = Math.max(
            40,
            this.currentWindowCopy.width - dx
          );
          this.currentWindow.height = Math.max(
            40,
            this.currentWindowCopy.height - dy
          );
        }
      }
    },
    mouseup() {
      this.currentWindow = null;
      this.opp = null;
      this.windows = this.frontendWindows.map((w) => ({ ...w }));
    },
    remove(window) {
      this.frontendWindows = this.frontendWindows.filter(
        (w) => w.id !== window.id
      );
      this.windows = this.frontendWindows.map((w) => ({ ...w }));
    },
    fullscreen(window) {
      if (document.fullscreenElement) {
        // If there is a fullscreen element, exit full screen.
        document.exitFullscreen();
        return;
      }
      // Make the .element div fullscreen.
      document
        .querySelector(`#solara-window-content-${window.id}`)
        .requestFullscreen();
    },
    bringToForeground(window) {
      const isLastWindow =
        window == this.frontendWindows[this.frontendWindows.length - 1];
      if (!isLastWindow) {
        this.frontendWindows = this.frontendWindows
          .filter((w) => w.id !== window.id)
          .concat([window]);
        this.windows = this.frontendWindows.map((w) => ({ ...w }));
      }
    },
    coalesceWindows(windows) {
      let xCount = 0;
      let yCount = 0;
      return windows.map((w) => ({
        id: w.id,
        x: w.x === undefined ? 100 + 20 * xCount++ : w.x,
        y: w.y === undefined ? 100 + 20 * yCount++ : w.y,
        width: w.width === undefined ? 600 : w.width,
        height: w.height === undefined ? 300 : w.height,
      }));
    },
  },
  created() {
    this.frontendWindows = this.coalesceWindows(this.windows);
  },
  watch: {
    windows(v) {
      this.frontendWindows = this.coalesceWindows(v);
    },
  },
};
</script>
