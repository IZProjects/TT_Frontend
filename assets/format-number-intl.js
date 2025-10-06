var dmcfuncs = window.dashMantineFunctions = window.dashMantineFunctions || {};

dmcfuncs.formatNumberIntl = (value) => {
  if (value === null || value === undefined) return "";

  const absValue = Math.abs(value);

  if (absValue >= 1.0e9) {
    return (value / 1.0e9).toFixed(1).replace(/\.0$/, '') + "B";
  } else if (absValue >= 1.0e6) {
    return (value / 1.0e6).toFixed(1).replace(/\.0$/, '') + "M";
  } else if (absValue >= 1.0e3) {
    return (value / 1.0e3).toFixed(1).replace(/\.0$/, '') + "K";
  } else {
    return new Intl.NumberFormat('en-US').format(value);
  }
};