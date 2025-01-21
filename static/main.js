(function () {
  const staticEndpoint = "https://widgetcontact.myfindata.com/static";
  const endpointURL = "https://widgetcontact.myfindata.com/widgets";

  const link = document.createElement("link");
  link.rel = "stylesheet";
  link.href = `${staticEndpoint}/index.css`;
  document.head.appendChild(link);

  const script = document.createElement("script");
  script.src = `${staticEndpoint}/appointment2.js`;
  script.defer = true;
  script.charset = "UTF-8";
  document.head.appendChild(script);

  const widgetDiv = document.querySelector('div[class^="cont-app-"]');

  if (!widgetDiv) {
    console.log("Widget Not Id not found");
    return;
  }

  const uuid = widgetDiv.className.split("cont-app-")[1];

  function loadWidget() {
    fetch(`${endpointURL}/booking/${uuid}`)
      .then((response) => {
        return response.json();
      })
      .then((res) => {
        console.log(res);
        if (window.renderReactApp) {
          window.renderReactApp(widgetDiv, res);
        } else {
          console.error("React app is not loaded.");
        }
      });
  }
  loadWidget();
})();
