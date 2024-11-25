(function () {
  const staticFileEndpoint = "";
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

  const endpointUrl = `http://127.0.0.1:8000/contact-form`;

  fetch(`${endpointUrl}/${uuid}`)
    .then((response) => {
      if (!response.ok) {
        console.log(`Error fetching widget: ${response.statusText}`);
      }
      return response.json();
    })
    .then((res) => {
      widgetDiv.innerHTML = res.html;

      const form = widgetDiv.querySelector("form");

      const fields = Array.from(form.querySelectorAll("input")).map((input) => {
        return {
          originalId: input.getAttribute("id"),
          element: input,
          isRequired: input.getAttribute("aria-required") === "true",
          type: input.getAttribute("type"),
        };
      });

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

        fetch(`${endpointUrl}/${uuid}`, {
          method: "POST",
          body: formData,
        })
          .then((response) => response.json())
          .then((res) => {
            const originalContent = widgetDiv.innerHTML;
            widgetDiv.innerHTML = "";
            const messageParagraph = document.createElement("p");
            messageParagraph.textContent = res.message;
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
          });
      });
    })
    .catch((error) => {
      console.error("Failed to load widget:", error);
    });
})();
