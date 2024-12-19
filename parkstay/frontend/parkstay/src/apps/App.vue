<template>
  <div id="app">
    <campgrounds></campgrounds>
  </div>
</template>

<script>
import campgrounds from './components/campgrounds.vue'

export default{
  name: 'app',
  components: {
    campgrounds
  }

};
</script>
