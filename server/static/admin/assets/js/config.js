(function () {
  var configData = sessionStorage.getItem("__CONFIG__");
  var htmlElement = document.getElementsByTagName("html")[0];
  var defaultConfig = {
    // theme: "light",
    nav: "vertical",
    layout: { mode: "fluid", position: "fixed" },
    topbar: { color: "dark" },
    menu: { color: "dark" },
    sidenav: { size: "default", user: false },
  };

  var config = Object.assign({}, defaultConfig);

  // var theme = htmlElement.getAttribute("data-bs-theme");
  // config.theme = theme !== null ? theme : defaultConfig.theme;

  var layout = htmlElement.getAttribute("data-layout");
  config.nav = layout !== null ? (layout === "topnav" ? "horizontal" : "vertical") : defaultConfig.nav;

  var layoutMode = htmlElement.getAttribute("data-layout-mode");
  config.layout.mode = layoutMode !== null ? layoutMode : defaultConfig.layout.mode;

  var layoutPosition = htmlElement.getAttribute("data-layout-position");
  config.layout.position = layoutPosition !== null ? layoutPosition : defaultConfig.layout.position;

  var topbarColor = htmlElement.getAttribute("data-topbar-color");
  config.topbar.color = topbarColor !== null ? topbarColor : defaultConfig.topbar.color;

  var sidenavSize = htmlElement.getAttribute("data-sidenav-size");
  config.sidenav.size = sidenavSize !== null ? sidenavSize : defaultConfig.sidenav.size;

  var sidenavUser = htmlElement.getAttribute("data-sidenav-user");
  config.sidenav.user = sidenavUser !== null ? sidenavUser : defaultConfig.sidenav.user;

  var menuColor = htmlElement.getAttribute("data-menu-color");
  config.menu.color = menuColor !== null ? menuColor : defaultConfig.menu.color;

  window.defaultConfig = JSON.parse(JSON.stringify(config));

  if (configData !== null) {
    config = JSON.parse(configData);
  }

  window.config = config;

  if (htmlElement.getAttribute("data-layout") === "topnav") {
    config.nav = "horizontal";
  } else {
    config.nav = "vertical";
  }

  if (config) {
    htmlElement.setAttribute("data-layout-mode", config.layout.mode);
    htmlElement.setAttribute("data-menu-color", config.menu.color);
    htmlElement.setAttribute("data-topbar-color", config.topbar.color);
    htmlElement.setAttribute("data-layout-position", config.layout.position);

    if (config.nav === "vertical") {
      let sidenavSize = config.sidenav.size;
      if (window.innerWidth <= 767) {
        sidenavSize = "full";
      } else if (window.innerWidth > 767 && window.innerWidth <= 1140 && config.sidenav.size !== "full") {
        sidenavSize = "condensed";
      }
      htmlElement.setAttribute("data-sidenav-size", sidenavSize);

      if (config.sidenav.user && config.sidenav.user.toString() === "true") {
        htmlElement.setAttribute("data-sidenav-user", true);
      } else {
        htmlElement.removeAttribute("data-sidenav-user");
      }
    }
  }
})();
