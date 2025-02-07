(function () {
  const staticEndpoint = "http://127.0.0.1:8000/static";
  const endpointURL = "http://127.0.0.1:8000/widgets";

  const link = document.createElement("link");
  link.rel = "stylesheet";
  link.href = `${staticEndpoint}/pricing.css`;
  document.head.appendChild(link);

  const script = document.createElement("script");
  script.src = `${staticEndpoint}/pricing.js`;
  script.defer = true;
  script.charset = "UTF-8";

  script.onload = function () {
    console.log("pricing.js loaded successfully");
    const widgetDiv = document.querySelector('div[class^="cont-app-"]');

    if (!widgetDiv) {
      console.log("Widget Not Id not found");
      return;
    }

    const uuid = widgetDiv.className.split("cont-app-")[1];

    fetch(`${endpointURL}/v2/pricing/${uuid}/`)
      .then((response) => {
        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }
        return response.json();
      })
      .then((res) => {
        console.log(res);
        if (window.renderReactApp) {
          window.renderReactApp(widgetDiv, res);
        } else {
          console.error("React app is not loaded.");
        }
      })
      .catch((error) => {
        console.error("Failed to fetch widget data:", error);
      });
  };

  script.onerror = function () {
    console.error("Failed to load appointment.js");
  };

  document.head.appendChild(script);
})();
