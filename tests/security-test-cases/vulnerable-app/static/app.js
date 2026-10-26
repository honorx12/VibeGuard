// SYNTHETIC FIXTURE
const key = process.env.NEXT_PUBLIC_SERVICE_ROLE_KEY;
localStorage.setItem("auth_token", token);
document.getElementById("out").innerHTML = location.hash.slice(1);
const cors = { origin: "*" };
