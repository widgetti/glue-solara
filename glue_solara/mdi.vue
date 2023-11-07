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
      v-for="(window, i) in orderedWindows(frontendWindows)"
      :set="(child = childFor(window))"
      :key="window.order"
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
        :class="[`glue-solara__window-header`, size]"
        style="line-height: 0; color: white"
        @mousedown.stop="mousedown($event, window, 'drag')"
      >
        <v-btn
          icon
          :x-small="size === 'x-small'"
          :small="size === 'small'"
          :large="size === 'large'"
          :x-large="size === 'x-large'"
          @click.stop="remove(window)"
          @mousedown.stop=""
        >
          <v-icon style="color: white">mdi-close-circle-outline</v-icon>
        </v-btn>
        <v-btn
          icon
          :x-small="size === 'x-small'"
          :small="size === 'small'"
          :large="size === 'large'"
          :x-large="size === 'x-large'"
          @click="fullscreen(window)"
          @mousedown.stop=""
        >
          <v-icon style="color: white">mdi-fullscreen</v-icon>
        </v-btn>
        <span style="position: relative; top: 2px">
          {{ window.title ? window.title : "" }}
        </span>
      </div>
      <div
        style="position: relative; flex-grow: 1"
        @click="bringToForeground(window)"
      >
        <div
          :id="`solara-window-content-${window.order}`"
          style="
            height: 100%;
            max-height: 100%;
            max-width: 100%;
            overflow: hidden;
          "
        >
          <jupyter-widget v-if="child" :widget="child" />
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
  font-size: 150%;
  padding-left: 6px;
}

.glue-solara__window-header .v-btn--icon {
  width: unset;
}

.glue-solara__window-header.x-small {
  font-size: 100%;
  padding-left: 2px;
}

.glue-solara__window-header.small {
  font-size: 125%;
  padding-left: 4px;
}

.glue-solara__window-header.large {
  font-size: 175%;
  padding-left: 8px;
}

.glue-solara__window-header.x-large {
  font-size: 200%;
  padding-left: 10px;
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
      this.bringToForeground(window);
      this.updateBackend();
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
      this.updateBackend();
    },
    remove(window) {
      this.close(
        this.frontendWindows.findIndex((w) => w.order === window.order)
      );
    },
    fullscreen(window) {
      if (document.fullscreenElement) {
        // If there is a fullscreen element, exit full screen.
        document.exitFullscreen();
        return;
      }
      // Make the .element div fullscreen.
      document
        .querySelector(`#solara-window-content-${window.order}`)
        .requestFullscreen();
    },
    bringToForeground(window) {
      this.orderedWindows(this.frontendWindows)
        .filter((w) => w.order !== window.order)
        .concat([window])
        .forEach((w, i) => {
          w.order = i;
        });
    },
    orderedWindows(windows) {
      return windows
        .concat()
        .sort((a, b) => (a.order > b.order ? 1 : a.order < b.order ? -1 : 0));
    },
    coalesceWindows(windows) {
      let xCount = 0;
      let yCount = 0;
      const orders = windows.filter((w) => w.order != null).map((w) => w.order);
      let max_order = orders && orders.length ? Math.max(...orders) : -1;
      return windows.map((w) => ({
        title: w.title,
        x: w.x === undefined ? 100 + 20 * xCount++ : w.x,
        y: w.y === undefined ? 100 + 20 * yCount++ : w.y,
        width: w.width === undefined ? 600 : w.width,
        height: w.height === undefined ? 300 : w.height,
        order: w.order === undefined ? ++max_order : w.order,
      }));
    },
    updateBackend() {
      if (this.deepEquals(this.frontendWindows, this.windows)) {
        return;
      }
      this.windows = _.cloneDeep(this.frontendWindows);
    },
    childFor(window) {
      return this.children[
        this.frontendWindows.findIndex((w) => w.order === window.order)
      ];
    },
    deepEquals(a, b) {
      /* _.isEqual does not work some of the time for some reason */
      return JSON.stringify(a) === JSON.stringify(b);
    },
  },
  created() {
    this.frontendWindows = this.coalesceWindows(this.windows);
    this.updateBackend();
  },
  watch: {
    windows(v) {
      if (this.currentWindow) {
        /* we don't want an outdated echo after mousedown from the backend during dragging */
        return;
      }
      if (this.deepEquals(this.frontendWindows, v)) {
        return;
      }
      const newWindows = this.coalesceWindows(v);
      if (!this.deepEquals(this.frontendWindows, newWindows)) {
        this.frontendWindows = this.coalesceWindows(v);
      }
      this.updateBackend();
    },
  },
};
</script>
