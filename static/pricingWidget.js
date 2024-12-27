(function () {
  const staticEndpoint = "https://widgetcontact.myfindata.com/static/style.css";
  const link = document.createElement("link");
  link.rel = "stylesheet";
  link.href = staticEndpoint;
  document.head.appendChild(link);
  const endpointURL = "https://widgetcontact.myfindata.com";
  const widgetDiv = document.querySelector('div[class^="clicflo-widget-"]');
  const uuid = widgetDiv.className.split("clicflo-widget-")[1];
  const cardHolder = document.createElement("div");
  cardHolder.className =
    "flex gap-x-4 items-center flex-wrap space-y-2 min-h-screen";
  cardHolder.id = "cardHolder";
  widgetDiv.appendChild(cardHolder);

  const renderFeatureList = (features, appearance) => {
    console.log(features[0]);
    return features
      .map(
        (feature) => `
        <li style="color: ${appearance.color}; font-size: ${
          appearance.font
        }px; display: flex; align-items: center;">
  <span style="margin-right: 8px;">
      ${feature.icon === "CH" ? "✔" : feature.icon === "CR" ? "❌" : ""}
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
                ? `<ul class="mt-4 space-y-2 text-xs text-gray-700"> ${renderFeatureList(
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
                 <button style="${getButtonStyles(
                   appearance.button,
                   item.featured_column
                 )}" class="mt-4 mx-auto hover:opacity-80 duration-150">
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
