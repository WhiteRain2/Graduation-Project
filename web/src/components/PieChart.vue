<template>
    <div ref="pieChartRef" class="echart-container" :style="{ height: height + 'px' }"></div>
</template>
  
<script>
  import * as echarts from 'echarts/core';
  import { PieChart } from 'echarts/charts';
  import { TitleComponent, TooltipComponent, LegendComponent } from 'echarts/components';
  import { CanvasRenderer } from 'echarts/renderers';
  import { onMounted, onBeforeUnmount, ref, watch, toRefs } from 'vue';
  
  // 注册 ECharts 必须的组件
  echarts.use([
    PieChart, 
    TitleComponent, 
    TooltipComponent, 
    LegendComponent, 
    CanvasRenderer
  ]);
  
  export default {
    props: {
      config: {
        type: Object,
        required: true,
        default: () => ({
          title: 'Default Title',
          data: [],
        }),
      },
      height: {
        type: [Number, String],
        default: 400, // 默认值为 400px
      },
    },
    setup(props) {
      const { config } = toRefs(props);
      const pieChartRef = ref(null);
      let pieChartInstance = null;
  
      // 监视 config 响应性地更新饼图
      watch(config, (newConfig) => {
        if (pieChartInstance) {
          const option = createChartOption(newConfig);
          pieChartInstance.setOption(option);
        }
      }, {
        immediate: true,
        deep: true
      });
  
      // 初始化 ECharts 实例
      onMounted(() => {
        pieChartInstance = echarts.init(pieChartRef.value);
        const option = createChartOption(config.value);
        pieChartInstance.setOption(option);
      });
      
      // 组件卸载前销毁 ECharts 实例
      onBeforeUnmount(() => {
        if (pieChartInstance) {
          pieChartInstance.dispose();
        }
      });
  
      return {
        pieChartRef,
      };
    },
  };
  
  function createChartOption(config) {
    return {
      title: {
        text: config.title,
        left: 'center'
      },
      tooltip: {
        trigger: 'item',
      },
      legend: {
        orient: 'vertical',
        left: 'left'
      },
      series: [{
        name: config.title,
        type: 'pie',
        radius: '50%',
        data: config.data,
        emphasis: {
          itemStyle: {
            shadowBlur: 10,
            shadowOffsetX: 0,
            shadowColor: 'rgba(0, 0, 0, 0.5)'
          }
        }
      }]
    };
  }
  </script>
  
  <style scoped>
  </style>