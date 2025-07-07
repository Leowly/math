document.addEventListener('DOMContentLoaded', () => {
  // 找到所有占位符
  document.querySelectorAll('.ggb-instance').forEach((el, i) => {

    // 没写 id 就自动补一个
    if (!el.id) el.id = `ggb-container-${i+1}`;

    // 从 data-* 里拼装参数
    const params = {
      appName:           el.dataset.appName || 'classic',
      width:             Number(el.dataset.width)  || 800,
      height:            Number(el.dataset.height) || 600,
      showToolBar:       el.dataset.showtoolbar      === 'true',
      showAlgebraInput:  el.dataset.showalgebrainput === 'true',
      showMenuBar:       el.dataset.showmenubar      === 'true',
      filename:          el.dataset.filename,

      // 页面加载完毕后再调整坐标系
      appletOnLoad(api) {
        const { xmin, xmax, ymin, ymax } = el.dataset;
        if (xmin && xmax && ymin && ymax) {
          api.setCoordSystem(
            parseFloat(xmin), parseFloat(xmax),
            parseFloat(ymin), parseFloat(ymax)
          );  // API 见官方文档 0
        }
      }
    };

    // 创建并注入
    new GGBApplet(params, /* useBrowserLocale = */ true).inject(el.id);
  });
});