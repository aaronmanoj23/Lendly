// Lendly front-end JS — vanilla, no framework.

function getCookie(name) {
  const v = `; ${document.cookie}`.split(`; ${name}=`);
  if (v.length === 2) return v.pop().split(";").shift();
  return "";
}
const CSRF = () => getCookie("csrftoken");

// ---------- Image preview on create_listing ----------
(function initImagePreview() {
  const input = document.getElementById("image-input");
  const preview = document.getElementById("image-preview");
  if (!input || !preview) return;
  input.addEventListener("change", () => {
    preview.innerHTML = "";
    [...input.files].forEach((file) => {
      const url = URL.createObjectURL(file);
      const img = document.createElement("img");
      img.src = url;
      img.className = "w-24 h-24 object-cover rounded-lg border";
      preview.appendChild(img);
    });
  });
})();

// ---------- AI price suggestion ----------
(function initAiPrice() {
  const btn = document.getElementById("ai-price-btn");
  const input = document.getElementById("image-input");
  const result = document.getElementById("ai-price-result");
  if (!btn || !input || !result) return;
  btn.addEventListener("click", async () => {
    if (!input.files || input.files.length === 0) {
      result.textContent = "Pick a photo first.";
      return;
    }
    result.textContent = "Analyzing image...";
    const fd = new FormData();
    fd.append("image", input.files[0]);
    try {
      const r = await fetch("/listings/ai-price/", {
        method: "POST",
        headers: { "X-CSRFToken": CSRF() },
        body: fd,
      });
      const data = await r.json();
      if (data.suggested_price) {
        result.textContent = `Suggested: $${data.suggested_price}/day`;
        const priceField = document.querySelector("[name=price_per_day]");
        if (priceField && !priceField.value) priceField.value = data.suggested_price;
      } else {
        result.textContent = data.error || "Could not suggest a price.";
      }
    } catch (e) {
      result.textContent = "Request failed.";
    }
  });
})();

// ---------- Booking AJAX ----------
(function initBookingForm() {
  const form = document.getElementById("booking-form");
  if (!form) return;
  const result = document.getElementById("booking-result");
  form.addEventListener("submit", async (e) => {
    e.preventDefault();
    const listingId = form.dataset.listing;
    const fd = new FormData(form);
    result.textContent = "Sending request...";
    try {
      const r = await fetch(`/bookings/request/${listingId}/`, {
        method: "POST",
        headers: { "X-CSRFToken": CSRF() },
        body: fd,
      });
      const data = await r.json();
      if (data.ok) {
        result.innerHTML = `<span class="text-green-600">Request sent! Total: $${data.total}.</span> <a class="text-indigo-600 underline" href="/bookings/${data.booking_id}/">View booking</a>`;
        form.reset();
      } else {
        result.textContent = "Error: " + JSON.stringify(data.error);
      }
    } catch (err) {
      result.textContent = "Request failed.";
    }
  });
})();

// ---------- Chat polling ----------
(function initChat() {
  const box = document.getElementById("messages");
  const form = document.getElementById("chat-form");
  if (!box || !form) return;

  const convoId = box.dataset.convo;
  const currentUser = box.dataset.user;
  let lastId = 0;
  box.querySelectorAll("[data-msg-id]").forEach((el) => {
    const id = parseInt(el.dataset.msgId, 10);
    if (id > lastId) lastId = id;
  });

  function appendMessage(m) {
    const wrap = document.createElement("div");
    wrap.className = "flex " + (String(m.sender_id) === currentUser ? "justify-end" : "");
    const bubble = document.createElement("div");
    bubble.className =
      "px-3 py-2 rounded-2xl max-w-xs " +
      (String(m.sender_id) === currentUser ? "bg-indigo-600 text-white" : "bg-gray-100");
    bubble.textContent = m.body;
    wrap.appendChild(bubble);
    wrap.dataset.msgId = m.id;
    box.appendChild(wrap);
    box.scrollTop = box.scrollHeight;
    if (m.id > lastId) lastId = m.id;
  }

  form.addEventListener("submit", async (e) => {
    e.preventDefault();
    const fd = new FormData(form);
    const r = await fetch(`/messages/${convoId}/send/`, {
      method: "POST",
      headers: { "X-CSRFToken": CSRF() },
      body: fd,
    });
    if (r.ok) {
      const m = await r.json();
      appendMessage(m);
      form.reset();
    }
  });

  async function poll() {
    try {
      const r = await fetch(`/messages/${convoId}/poll/?after=${lastId}`);
      const data = await r.json();
      (data.messages || []).forEach(appendMessage);
    } catch (e) {}
  }
  setInterval(poll, 3000);
  box.scrollTop = box.scrollHeight;
})();

// ---------- Stripe checkout redirect ----------
(function initPay() {
  const btn = document.getElementById("pay-btn");
  if (!btn) return;
  btn.addEventListener("click", async () => {
    const bookingId = btn.dataset.booking;
    btn.disabled = true;
    btn.textContent = "Redirecting...";
    try {
      const r = await fetch(`/payments/checkout/${bookingId}/session/`, {
        method: "POST",
        headers: { "X-CSRFToken": CSRF() },
      });
      const data = await r.json();
      if (data.url) {
        window.location = data.url;
      } else {
        btn.textContent = "Error";
      }
    } catch (e) {
      btn.textContent = "Failed";
    }
  });
})();
