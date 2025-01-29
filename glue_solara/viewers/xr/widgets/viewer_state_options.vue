<template>
  <div class="glue-viewer-scatter">
    <div>
      <v-subheader class="pl-0 slider-label">scaling factor</v-subheader>
      <glue-throttled-slider
        wait="300"
        min="0.1"
        max="10"
        step="0.01"
        :value.sync="glue_state.model_scaling_factor"
        hide-details
      />
    </div>
    <div>
      <v-select
        label="x axis"
        :items="x_att_items"
        v-model="x_att_selected"
        hide-details
      />
    </div>
    <div>
      <v-select
        label="y axis"
        :items="y_att_items"
        v-model="y_att_selected"
        hide-details
      />
    </div>
    <div>
      <v-select
        label="z axis"
        :items="z_att_items"
        v-model="z_att_selected"
        hide-details
      />
    </div>
  </div>
</template>

<style id="viewer_image">
.glue-viewer-scatter .v-subheader.slider-label {
  font-size: 12px;
  height: 16px;
  margin-top: 6px;
}
</style>
