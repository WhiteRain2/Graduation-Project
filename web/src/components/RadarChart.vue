<template>
  <div ref="radarChartRef" class="echart-container" :style="{ height: height + 'px' }"></div>
</template>
  
<script>
  import * as echarts from 'echarts/core';
  import { RadarChart } from 'echarts/charts';
  import { TitleComponent, TooltipComponent, LegendComponent } from 'echarts/components';
  import { CanvasRenderer } from 'echarts/renderers';
  import { onMounted, onBeforeUnmount, ref, watch, toRefs } from 'vue';
    
    // 注册 ECharts 必须的组件
  echarts.use([RadarChart, TitleComponent, TooltipComponent, LegendComponent, CanvasRenderer]);
    
  export default {
    name: 'RadarChart',
    props: {
      config: {
        type: Object,
        required: true,
        default: () => ({
          title: 'Default Title',
          indicators: [],
          data: [],
        }),
      },
      height: {
        type: [Number, String],
        default: 400, // 默认值为 400px
      },
    },
    setup(props) {
      const { config } = toRefs(props); // 更改这里为 config
      const radarChartRef = ref(null);
      let radarChartInstance = null;
      
      // 监视 config 响应性地更新雷达图
      watch(config, (newConfig) => {
        if (radarChartInstance) {
          const option = createChartOption(newConfig);
          radarChartInstance.setOption(option);
        }
      }, {
        immediate: true,
        deep: true
      });

      // 初始化 ECharts 实例
      onMounted(() => {
        radarChartInstance = echarts.init(radarChartRef.value);
        const option = createChartOption(config.value); // 更改这里使用 config.value
        radarChartInstance.setOption(option);
      });
      // 组件卸载前销毁 ECharts 实例
      onBeforeUnmount(() => {
        if (radarChartInstance) {
          radarChartInstance.dispose();
        }
      });

      return {
        radarChartRef,
      };
    },
  };
    
  function createChartOption(config) {
    return {
      title: {
        text: config.title,
        padding: 20
      },
      tooltip: {},
      // legend: {
      //   data: config.data.map(item => item.name),
      // },
      radar: {
        center: ['50%', '55%'], // 第一个值是水平位置，第二个值是垂直位置
        indicator: config.indicators,
      },
      series: [{
        name: 'Community Data',
        type: 'radar',
        data: config.data
      }],
    };
  }
</script>
  
<style scoped>
</style>