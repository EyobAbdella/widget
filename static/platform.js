(function () {
  const staticFileEndpoint = "";
  const RECAPTCHA_SITE_KEY = "";
  const endpointUrl = "";
  const link = document.createElement("link");
  link.rel = "stylesheet";
  link.href = `${staticFileEndpoint}/static/style.css`;
  document.head.appendChild(link);

  const widgetDiv = document.querySelector('div[class^="cont-app-"]');
  if (!widgetDiv) {
    console.log("Widget div not found.");
    return;
  }

  const uuid = widgetDiv.className.split("cont-app-")[1];
  if (!uuid) {
    console.log("UUID not found in div class.");
    return;
  }

  function getUrlParams() {
    const params = new URLSearchParams(window.location.search);
    return params.toString();
  }

  function submitData(url) {
    return fetch(url, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(),
    })
      .then((response) => response.json())
      .catch((error) => {
        console.error(error);
      });
  }

  function submitFormDataWithFiles(url, formData) {
    return fetch(`${url}/${uuid}`, {
      method: "POST",
      body: formData,
    })
      .then((response) => response.json())
      .catch((error) => {
        console.error("Failed to submit form data:", error);
      });
  }

  function handleFormSubmission(form, fields, spam_protection) {
    form.addEventListener("submit", function (event) {
      event.preventDefault();

      form
        .querySelectorAll(".error")
        .forEach((errorDiv) => (errorDiv.textContent = ""));

      let validationFailed = false;

      fields.forEach(({ originalId, element, isRequired, type }) => {
        const errorDiv = element.nextElementSibling;

        if (isRequired) {
          if (type === "file") {
            if (element.files.length === 0) {
              validationFailed = true;
              errorDiv.textContent = "This field is required.";
            } else {
              errorDiv.textContent = "";
            }
          } else {
            if (!element.value.trim()) {
              validationFailed = true;
              errorDiv.textContent = "This field is required.";
            } else {
              errorDiv.textContent = "";
            }
          }
        }
      });

      if (validationFailed) {
        return;
      }

      const formData = new FormData();

      fields.forEach(({ originalId, element, type }) => {
        if (type === "file") {
          const fileInput = element;
          if (fileInput.files.length > 0) {
            Array.from(fileInput.files).forEach((file) => {
              formData.append(originalId, file);
            });
          }
        } else {
          formData.append(originalId, element.value.trim());
        }
      });

      if (spam_protection) {
        grecaptcha.ready(function () {
          grecaptcha
            .execute(RECAPTCHA_SITE_KEY, {
              action: "submit",
            })
            .then(function (token) {
              formData.append("recaptchaToken", token);

              submitFormDataWithFiles(endpointUrl, formData)
                .then((res) => {
                  handleFormResponse(res);
                })
                .catch((error) => {
                  console.error("Failed to submit form:", error);
                });
            });
        });
      } else {
        submitFormDataWithFiles(endpointUrl, formData)
          .then((res) => {
            handleFormResponse(res);
          })
          .catch((error) => {
            console.error("Failed to submit form:", error);
          });
      }
    });
  }

  function handleFormResponse(res) {
    const originalContent = widgetDiv.innerHTML;

    if (res.action === "success_msg") {
      widgetDiv.innerHTML = "";
      const messageParagraph = document.createElement("p");
      messageParagraph.textContent = res.value;
      messageParagraph.className =
        "text-xl font-semibold text-black py-6 text-center mt-10";
      widgetDiv.appendChild(messageParagraph);
      const closeButton = document.createElement("button");
      closeButton.textContent = "Close";
      closeButton.className =
        "block mx-auto mt-4 px-4 py-2 bg-red-500 text-white rounded";
      widgetDiv.appendChild(closeButton);

      closeButton.addEventListener("click", () => {
        widgetDiv.innerHTML = originalContent;
      });
    } else if (res.action === "redirect_url") {
      window.location.href = res.value;
    } else if (res.action === "hide_form") {
      widgetDiv.style.display = "none";
    }
  }

  const urlParams = getUrlParams();

  if (urlParams !== "") {
    console.log(urlParams);
    submitData(`${endpointUrl}/widget/${uuid}/form/?${urlParams}`)
      .then((res) => {
        console.log("URL parameters sent:", res);
        alert("submitted successfully!");
      })
      .catch((error) => {
        console.error("Failed to send URL parameters:", error);
      });
  } else {
    loadWidget();
  }

  function loadWidget() {
    fetch(`${endpointUrl}/${uuid}`)
      .then((response) => {
        if (!response.ok) {
          console.log(`Error fetching widget: ${response.statusText}`);
        }
        return response.json();
      })
      .then((res) => {
        widgetDiv.innerHTML = res.html;
        const spam_protection = res.spam_protection;

        const form = widgetDiv.querySelector("form");
        const fields = Array.from(form.querySelectorAll("input")).map(
          (input) => {
            return {
              originalId: input.getAttribute("id"),
              element: input,
              isRequired: input.getAttribute("aria-required") === "true",
              type: input.getAttribute("type"),
            };
          }
        );

        if (spam_protection) {
          const recaptchaScript = document.createElement("script");
          recaptchaScript.src = `https://www.google.com/recaptcha/api.js?render=${RECAPTCHA_SITE_KEY}`;
          recaptchaScript.async = true;
          recaptchaScript.defer = true;
          document.head.appendChild(recaptchaScript);
        }

        handleFormSubmission(form, fields, spam_protection);
      })
      .catch((error) => {
        console.error("Failed to load widget:", error);
      });
  }
})();
