(function () {
  const staticEndpoint = "https://widgetcontact.myfindata.com/static/style.css";
  //   const staticEndpoint = "http://localhost:8000/static/style.css";
  const link = document.createElement("link");
  link.rel = "stylesheet";
  link.href = staticEndpoint;
  document.head.appendChild(link);
  const endpointURL = "https://widgetcontact.myfindata.com";
  //   const endpointURL = "http://localhost:8000";
  const widgetDiv = document.querySelector('div[class^="clicflo-widget-"]');
  const uuid = widgetDiv.className.split("clicflo-widget-")[1];
  const cardHolder = document.createElement("div");
  cardHolder.className =
    "flex gap-x-4 items-center flex-wrap space-y-2 min-h-screen";
  cardHolder.id = "cardHolder";
  widgetDiv.appendChild(cardHolder);

  function handleButtonClick(linkType, linkValue, newTab) {
    if (linkType === "URL") {
      if (newTab) {
        window.open(linkValue, "_blank");
      } else {
        window.location.href = linkValue;
      }
    } else if (linkType === "EMAIL") {
      window.location.href = `mailto:${linkValue}`;
    }
  }
  const renderFeatureList = (features, appearance) => {
    const iconMap = {
      CH: `<svg xmlns="http://www.w3.org/2000/svg" class="w-4 h-4 text-green-500" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
              <path stroke-linecap="round" stroke-linejoin="round" d="M5 13l4 4L19 7" />
           </svg>`,
      CR: `<svg xmlns="http://www.w3.org/2000/svg" class="w-4 h-4 text-red-500" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
              <path stroke-linecap="round" stroke-linejoin="round" d="M6 18L18 6M6 6l12 12" />
           </svg>`,
      M: `<svg xmlns="http://www.w3.org/2000/svg" class="w-4 h-4 text-gray-500" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
              <path stroke-linecap="round" stroke-linejoin="round" d="M4 12h16" />
           </svg>`,
      N: "",
    };
    return features
      .map(
        (feature) => `
      <li style="color: ${appearance.color}; font-size: ${
          appearance.font
        }px;" class="flex items-center">
          <span style="margin-right: 8px;">
              ${iconMap[feature.icon] || ""}
          </span>
          ${feature.text}
          ${
            feature.hint
              ? `<span style="font-size: 12px; color: #6b7280; margin-left: 8px;">(${feature.hint})</span>`
              : ""
          }
      </li>
  `
      )
      .join("");
  };

  const getButtonStyles = (button, isFeaturedColumn) => {
    const sizes = {
      S: "padding: 5px 20px; font-size: 12px;",
      M: "padding: 9px 28px; font-size: 14px;",
      L: "padding: 9px 36px; font-size: 16px;",
    };

    const commonStyles = `
          display: inline-block;
          border-radius: 4px;
          text-align: center;
          cursor: pointer;
        `;

    if (button.type === "F" || isFeaturedColumn) {
      return `
            ${commonStyles}
            background-color: ${button.button_color};
            color: ${button.label_color};
            ${sizes[button.size] || sizes["M"]}
          `;
    } else if (button.type === "O") {
      return `
            ${commonStyles}
            background-color: transparent;
            border: 1px solid ${button.button_color};
            color: ${button.label_color};
            ${sizes[button.size] || sizes["M"]}
          `;
    }

    return commonStyles;
  };

  const renderCard = (item, appearance) => {
    const currencySymbol = item.price
      ? item.price.currency === "USD"
        ? "$"
        : item.price.currency === "EUR"
        ? "€"
        : item.price.currency
      : "";

    return `
        <div class="max-w-64 mx-auto bg-white border border-gray-200 rounded-lg shadow overflow-hidden relative ${
          item.featured_column ? "-translate-y-5" : ""
        }">
          ${
            item.featured_column
              ? `
            <div class="bg-yellow-400 w-fit px-8 py-1 absolute rotate-45 -right-8 top-4">${item.ribbon_text}</div>
          `
              : ""
          }
          ${
            item.picture
              ? `
            <img src="${item.picture}" alt="${item.title}" class="w-72 h-40 object-cover">
          `
              : ""
          }
          <div class="p-6">
               ${
                 item.title
                   ? `<h2 class="text-center" style="color: ${appearance.title.color}; font-size: ${appearance.title.font}px;">${item.title}</h2>`
                   : ""
               }
                <p class="text-center opacity-70" style="color: ${
                  appearance.title.caption_color
                }; font-size: ${appearance.title.font - 8}px;">${
      item.caption || ""
    }</p>
            ${
              item.features
                ? `<ul class="mt-4 space-y-2 text-xs text-gray-700 flex flex-col items-start mx-auto w-fit"> ${renderFeatureList(
                    item.features,
                    appearance.feature
                  )}</ul>`
                : ""
            }
            <div class="mt-6 flex flex-col">
            ${
              item.price
                ? `
                 <p class="text-center" style="color: ${
                   appearance.price.color
                 }; font-size: ${appearance.price.font}px;">
                   ${item.price.prefix || ""}
                   <span style="color: ${appearance.price.color}; font-size: ${
                    appearance.price.font + 4
                  }px;">
                     <sup>${currencySymbol}</sup>
                     ${item.price.amount}
                   </span>
                   ${item.price.postfix ? `/${item.price.postfix}` : ""}
                 </p>
                 <span class="text-xs mx-auto ">${
                   item.price.caption ? item.price.caption : ""
                 }</span>`
                : ""
            }
              ${
                item.button
                  ? `
                <button 
                    style="${getButtonStyles(
                      appearance.button,
                      item.featured_column
                    )}" 
                    class="mt-4 mx-auto hover:opacity-80 duration-150"
                    data-link-type="${item.button.link.link_type}"
                    data-link-value="${item.button.link.link_value}"
                    data-new-tab="${item.button.link.new_tab}">
                    ${item.button.text}
                </button>
                  <span class="text-xs mx-auto mt-1.5">${
                    item.button.caption ? item.button.caption : ""
                  }</span>`
                  : ""
              }
            </div>
          </div>
        </div>
      `;
  };

  const renderCards = (data) => {
    const cardHolder = document.getElementById("cardHolder");

    const sanitizedContent = data.content
      .map((item) => renderCard(item, data.appearance))
      .join("");

    cardHolder.innerHTML = DOMPurify.sanitize(sanitizedContent);
    const buttons = cardHolder.querySelectorAll("button");
    buttons.forEach((button) => {
      const linkType = button.getAttribute("data-link-type");
      const linkValue = button.getAttribute("data-link-value");
      const newTab = button.getAttribute("data-new-tab") === "true";

      button.addEventListener("click", () => {
        handleButtonClick(linkType, linkValue, newTab);
      });
    });
  };
  if (typeof DOMPurify === "undefined") {
    const script = document.createElement("script");
    script.src =
      "https://cdn.jsdelivr.net/npm/dompurify@2.4.0/dist/purify.min.js";
    script.onload = () => {
      loadWidget();
    };
    script.onerror = () => {
      console.error("Failed to load DOMPurify.");
    };
    document.head.appendChild(script);
    return;
  }

  function loadWidget() {
    fetch(`${endpointURL}/widgets/pr/${uuid}`)
      .then((res) => {
        if (!res.ok) {
          console.log(res);
        }
        return res.json();
      })
      .then((res) => {
        renderCards(res);
      });
  }
})();
