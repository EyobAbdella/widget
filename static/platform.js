(function () {
  const staticFileEndpoint = "https://widgetcontact.myfindata.com";
  // const staticFileEndpoint = "http://127.0.0.1:8000";
  const RECAPTCHA_SITE_KEY = "6LdL15YqAAAAAJADkgf9Nq9NGS88QA2WFcRtzWmu";
  const endpointUrl = "https://widgetcontact.myfindata.com/widgets";
  // const endpointUrl = "http://127.0.0.1:8000/widgets";

  // Add Tailwind CSS CDN
  const tailwindLink = document.createElement("script");
  tailwindLink.src = "https://cdn.tailwindcss.com";
  document.head.appendChild(tailwindLink);

  // Google Font
  const googleFontLink = document.createElement("link");
  googleFontLink.rel = "stylesheet";
  googleFontLink.href =
    "https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&family=Lato:wght@400;700&family=Montserrat:wght@400;500;600&family=Open+Sans:wght@400;600&family=Poppins:wght@400;500;600&family=Roboto:wght@400;500;700&display=swap";
  document.head.appendChild(googleFontLink);

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

  function initializeSignaturePad(container) {
    const signaturePads = container.querySelectorAll(".signature-pad-container");

    signaturePads.forEach((container) => {
      const canvas = container.querySelector("canvas");
      const ctx = canvas.getContext("2d");
      let isDrawing = false;
      let lastX = 0;
      let lastY = 0;

      // Set canvas size with proper scaling
      function resizeCanvas() {
        const rect = canvas.getBoundingClientRect();
        const dpr = window.devicePixelRatio || 1;

        // Set canvas display size (CSS pixels)
        canvas.style.width = "100%";
        canvas.style.height = "200px";

        // Set canvas buffer size (actual pixels)
        canvas.width = rect.width * dpr;
        canvas.height = 200 * dpr;

        // Scale the context to handle device pixel ratio
        ctx.scale(dpr, dpr);

        // Set drawing styles
        ctx.strokeStyle = "#000";
        ctx.lineWidth = 2;
        ctx.lineCap = "round";
        ctx.lineJoin = "round";
      }

      // Initialize canvas
      resizeCanvas();
      window.addEventListener("resize", resizeCanvas);

      // Convert page coordinates to canvas coordinates
      function getCanvasCoordinates(e) {
        const rect = canvas.getBoundingClientRect();
        const dpr = window.devicePixelRatio || 1;

        // Get the touch/mouse position
        const clientX = e.clientX || (e.touches && e.touches[0] ? e.touches[0].clientX : 0);
        const clientY = e.clientY || (e.touches && e.touches[0] ? e.touches[0].clientY : 0);

        // Calculate the position relative to the canvas
        return {
          x: (((clientX - rect.left) / rect.width) * canvas.width) / dpr,
          y: (((clientY - rect.top) / rect.height) * canvas.height) / dpr,
        };
      }

      function startDrawing(e) {
        isDrawing = true;
        const coords = getCanvasCoordinates(e);
        lastX = coords.x;
        lastY = coords.y;
      }

      function draw(e) {
        if (!isDrawing) return;
        e.preventDefault();

        const coords = getCanvasCoordinates(e);

        // Draw line
        ctx.beginPath();
        ctx.moveTo(lastX, lastY);
        ctx.lineTo(coords.x, coords.y);
        ctx.stroke();

        lastX = coords.x;
        lastY = coords.y;
      }

      function stopDrawing() {
        if (!isDrawing) return;
        isDrawing = false;

        // Save signature data
        const input = container.querySelector('input[type="hidden"]');
        if (input) {
          input.value = canvas.toDataURL();
          // Trigger change event
          const event = new Event("change", { bubbles: true });
          input.dispatchEvent(event);
        }
      }

      // Mouse event listeners
      canvas.addEventListener("mousedown", startDrawing);
      canvas.addEventListener("mousemove", draw);
      canvas.addEventListener("mouseup", stopDrawing);
      canvas.addEventListener("mouseout", stopDrawing);

      // Touch event listeners with passive: false to prevent scrolling
      canvas.addEventListener(
        "touchstart",
        (e) => {
          e.preventDefault();
          startDrawing(e.touches[0]);
        },
        { passive: false }
      );

      canvas.addEventListener(
        "touchmove",
        (e) => {
          e.preventDefault();
          draw(e.touches[0]);
        },
        { passive: false }
      );

      canvas.addEventListener(
        "touchend",
        (e) => {
          e.preventDefault();
          stopDrawing();
        },
        { passive: false }
      );

      // Clear button functionality
      const clearButton = container.nextElementSibling?.querySelector(".signature-clear-button");
      if (clearButton) {
        clearButton.addEventListener("click", () => {
          ctx.clearRect(0, 0, canvas.width, canvas.height);
          const input = container.querySelector('input[type="hidden"]');
          if (input) {
            input.value = "";
            const event = new Event("change", { bubbles: true });
            input.dispatchEvent(event);
          }
        });
      }
    });
  }

  function initializeRatingFields(container) {
    // Handle star-scale fields
    container.querySelectorAll('[data-field-type="star-scale"]').forEach((field) => {
      const stars = field.querySelectorAll("button");
      const input = field.querySelector('input[type="hidden"]');

      // Initial state setup
      if (input.value) {
        const currentValue = parseInt(input.value);
        stars.forEach((s, i) => {
          const starIcon = s.querySelector("svg");
          if (i < currentValue) {
            starIcon.setAttribute("fill", "currentColor");
            starIcon.classList.add("text-primary");
            starIcon.classList.remove("text-muted-foreground");
          } else {
            starIcon.setAttribute("fill", "none");
            starIcon.classList.remove("text-primary");
            starIcon.classList.add("text-muted-foreground");
          }
        });
      }

      stars.forEach((star, index) => {
        star.addEventListener("click", () => {
          const value = index + 1;
          input.value = value;

          // Update visual state
          stars.forEach((s, i) => {
            const starIcon = s.querySelector("svg");
            if (i < value) {
              starIcon.setAttribute("fill", "currentColor");
              starIcon.classList.add("text-primary");
              starIcon.classList.remove("text-muted-foreground");
            } else {
              starIcon.setAttribute("fill", "none");
              starIcon.classList.remove("text-primary");
              starIcon.classList.add("text-muted-foreground");
            }
          });

          // Trigger change event
          const event = new Event("change", { bubbles: true });
          input.dispatchEvent(event);
        });

        // Add hover effect
        star.addEventListener("mouseenter", () => {
          const starIcon = star.querySelector("svg");
          starIcon.classList.add("text-primary");
        });

        star.addEventListener("mouseleave", () => {
          const starIcon = star.querySelector("svg");
          const currentValue = parseInt(input.value) || 0;
          if (index >= currentValue) {
            starIcon.classList.remove("text-primary");
            starIcon.classList.add("text-muted-foreground");
          }
        });
      });
    });

    // Handle smiley-scale fields
    container.querySelectorAll('[data-field-type="smiley-scale"]').forEach((field) => {
      const smileys = field.querySelectorAll("button");
      const input = field.querySelector('input[type="hidden"]');

      // Initial state setup
      if (input.value) {
        const currentValue = parseInt(input.value);
        smileys.forEach((s, i) => {
          if (i === currentValue - 1) {
            s.classList.add("bg-primary", "text-primary-foreground");
            s.classList.remove("text-muted-foreground");
          } else {
            s.classList.remove("bg-primary", "text-primary-foreground");
            s.classList.add("text-muted-foreground");
          }
        });
      }

      smileys.forEach((smiley, index) => {
        smiley.addEventListener("click", () => {
          const value = index + 1;
          input.value = value;

          // Update visual state
          smileys.forEach((s, i) => {
            if (i === index) {
              s.classList.add("bg-primary", "text-primary-foreground");
              s.classList.remove("text-muted-foreground");
            } else {
              s.classList.remove("bg-primary", "text-primary-foreground");
              s.classList.add("text-muted-foreground");
            }
          });

          // Trigger change event
          const event = new Event("change", { bubbles: true });
          input.dispatchEvent(event);
        });
      });
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

      form.querySelectorAll(".error").forEach((errorDiv) => (errorDiv.textContent = ""));

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
            if (type === "scale" || type === "consent" || type === "choice" || type === "multiple_choice") {
              const choice = element.querySelectorAll('input[type="radio"], input[type="checkbox"]');
              let isChecked = false;
              for (const selectedChoice of choice) {
                if (selectedChoice.checked) {
                  isChecked = true;
                  break;
                }
              }
              if (isChecked) {
                errorDiv.textContent = "";
              } else {
                validationFailed = true;
                errorDiv.textContent = "This field is required.";
              }
            } else if (!element.value.trim()) {
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
        } else if (type === "consent") {
          const InputValue = element.querySelector('input[type="checkbox"]:checked');
          formData.append(originalId, InputValue ? InputValue.checked : false);
        } else if (type === "scale") {
          const scaleInput = element.querySelector('input[type="radio"]:checked');
          formData.append(originalId, scaleInput.value);
        } else if (type === "choice") {
          const selectedChoice = element.querySelector('input[name="choice"]:checked');
          formData.append(originalId, selectedChoice ? selectedChoice.value : null);
        } else if (type === "multiple_choice") {
          const choices = element.querySelectorAll('input[name="multiple-choice"]:checked');
          formData.append(
            originalId,
            Array.from(choices).map((checkbox) => checkbox.value)
          );
        } else if (type === "signature") {
          const signatureInput = element.querySelector('input[type="hidden"]');
          formData.append(originalId, signatureInput.value);
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
      messageParagraph.className = "text-xl font-semibold text-black py-6 text-center mt-10";
      widgetDiv.appendChild(messageParagraph);
      const closeButton = document.createElement("button");
      closeButton.textContent = "Close";
      closeButton.className = "block mx-auto mt-4 px-4 py-2 bg-red-500 text-white rounded";
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

  function loadWidget() {
    fetch(`${endpointUrl}/${uuid}`)
      .then((response) => {
        if (!response.ok) {
          console.log(`Error fetching widget: ${response}`);
        }
        return response.json();
      })
      .then((res) => {
        const scriptUrl = `${endpointUrl}/script/${uuid}.js`;
        const script = document.createElement("script");
        script.src = scriptUrl;
        script.async = true;
        script.onload = function () {};
        script.onerror = function () {
          console.error(`Failed to load script ${uuid}`);
        };
        document.body.appendChild(script);

        widgetDiv.innerHTML = res.html;

        // Initialize signature pads and rating fields
        initializeSignaturePad(widgetDiv);
        initializeRatingFields(widgetDiv);

        const preFillValues = res.pre_fill_values;
        const spam_protection = res.spam_protection;

        const adminData = res.admin_brand_info;
        const userData = res.user_brand_info;

        if (adminData) {
          const adminLink = document.querySelector("#admin_branding a");
          if (adminLink) adminLink.setAttribute("href", adminData.redirect_url || "#");

          const adminImg = document.querySelector("#admin_branding img");
          if (adminImg) {
            adminImg.setAttribute("src", adminData.logo || "");
            adminImg.setAttribute("alt", adminData.name || "");
          }

          const adminName = document.querySelector("#admin_branding_name");
          if (adminName) adminName.textContent = adminData.name || "";
        }

        if (userData) {
          const userLink = document.querySelector("#user_branding a");
          if (userLink) userLink.setAttribute("href", userData.redirect_url || "#");

          const userImg = document.querySelector("#user_branding img");
          if (userImg) {
            userImg.setAttribute("src", userData.logo || "");
            userImg.setAttribute("alt", userData.name || "");
          }

          const userName = document.querySelector("#user_branding_name");
          if (userName) userName.textContent = userData.name || "";
        }

        const form = widgetDiv.querySelector("form");
        const fields = Array.from(
          form.querySelectorAll(
            "[role='radiogroup'], [data-type='multiple_choice'], [data-type='consent'], [data-type='choice'], input:not([type='radio']):not([type='checkbox']), select, textarea, .signature-pad-container"
          )
        ).map((element) => {
          return {
            originalId: element.getAttribute("id"),
            element: element,
            isRequired: element.getAttribute("aria-required") === "true",
            type:
              element.getAttribute("data-type") ||
              (element.tagName.toLowerCase() === "textarea" ? "textarea" : element.getAttribute("type") || "signature"),
          };
        });

        const urlParams = new URLSearchParams(window.location.search);

        preFillValues.forEach(({ field_id, parameter_name }) => {
          const value = urlParams.get(parameter_name);
          if (value) {
            const field = fields.find((f) => f.originalId === field_id);

            if (!field || ["multiple_choice", "choice"].includes(field.type)) {
              return;
            }

            const element = field.element;
            if (["textarea", "text", "email"].includes(field.type)) {
              element.value = value;
            } else if (field.type === "radio" || field.type === "checkbox") {
              const matchingInput = element.querySelector(`input[value="${value}"]`);
              if (matchingInput) matchingInput.checked = true;
            }
          }
        });

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

  loadWidget();
})();
