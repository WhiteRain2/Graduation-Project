<template>
    <div v-if="isVisible" class="modal-backdrop" @click.self="closeModal">
      <div class="modal-content">
        <!-- 关闭按钮 -->
        <button class="close-btn" @click="closeModal">&times;</button>
        <!-- 插槽内容 -->
        <slot></slot> 
      </div>
    </div>
  </template>
  
  <script>
  export default {
    name: 'ModalContext',
    props: {
      isVisible: {
        type: Boolean,
        default: false
      }
    },
    emits: ['update:isVisible'],
    methods: {
      closeModal() {
        this.$emit('update:isVisible', false);
      }
    }
  };
  </script>
  
  <style scoped>
  /* 模态框背景遮罩层 */
  .modal-backdrop {
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background-color: rgba(0, 0, 0, 0.6); /* 半透明黑色背景 */
    display: flex;
    align-items: center; /* 垂直居中 */
    justify-content: center; /* 水平居中 */
    z-index: 1050; /* 高于大多数元素 */
    opacity: 0; /* 初始不可见 */
    visibility: hidden; /* 初始不显示 */
    transition: opacity 0.5s ease-in-out, visibility 0.5s ease-in-out; /* 渐变效果 */
  }
  
  /* 模态框容器 */
  .modal-content {
    position: relative; /* 相对定位，用于定位关闭按钮 */
    display: block; /* 默认显示 */
    width: 75%; /* 75% 的宽度 */
    height: 75%; /* 75% 的高度 */
    background-color: #fff; /* 白色背景 */
    padding: 20px;
    border-radius: 4px; /* 圆角 */
    box-shadow: 0 2px 10px rgba(0, 0, 0, 0.2); /* 阴影效果 */
    z-index: 1051; /* 高于遮罩层 */
    overflow: auto; /* 如果内容超出，则显示滚动条 */
    transition: transform 0.3s ease; /* 过渡效果 */
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.25); /* 更深的阴影效果 */
    transition: transform 0.5s ease-in-out; /* 缓慢的变换效果 */
    will-change: transform; /* 优化动画性能 */
  }
  
  /* 当模态框可见时的样式 */
  .modal-backdrop {
    opacity: 1;
    visibility: visible;
  }

  .modal-backdrop .modal-content {
    transform: scale(1); /* 缩放至正常大小 */
  }
  
  /* 关闭按钮样式 */
  .close-btn {
    position: absolute; /* 绝对定位 */
    top: 10px; /* 距离顶部10px */
    right: 10px; /* 距离右侧10px */
    border: none; /* 无边框 */
    background: transparent; /* 透明背景 */
    font-size: 24px; /* 字体大小 */
    cursor: pointer; /* 手形光标 */
  }

  /* 入场动画效果 */
@keyframes modalFadeIn {
  from {
    transform: scale(0.5); /* 开始时缩放至更小的尺寸 */
    opacity: 0; /* 开始时不透明度为0 */
  }
  to {
    transform: scale(1); /* 结束时恢复原尺寸 */
    opacity: 1; /* 结束时不透明度为1 */
  }
}

/* 出场动画效果 */
@keyframes modalFadeOut {
  from {
    transform: scale(1); /* 开始时保持原尺寸 */
    opacity: 1; /* 开始时不透明度为1 */
  }
  to {
    transform: scale(0.5); /* 结束时缩放至更小的尺寸 */
    opacity: 0; /* 结束时不透明度为0 */
  }
}

/* 模态框显示时应用入场动画 */
.modal-backdrop[data-closing="false"] .modal-content {
  animation: modalFadeIn 0.5s ease-in-out forwards;
}

/* 模态框隐藏时应用出场动画 */
.modal-backdrop[data-closing="true"] .modal-content {
  animation: modalFadeOut 0.5s ease-in-out forwards;
}
  
  /* 删除媒体查询，因为模态框宽高已经定为了75% */
  /* ... 如果您还需要对特定屏幕大小定制样式，可以添加新的媒体查询 ... */
  </style>