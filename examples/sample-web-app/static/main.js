// SYNTHETIC DEMO
const STRIPE_KEY = "pk_demo_publishable";
async function load(q) {
  const r = await fetch("/search?q=" + q);
  document.getElementById("results").innerHTML = await r.text();
  localStorage.setItem("auth_token", window.token);
}
