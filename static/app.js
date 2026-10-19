
async function refrescar() {
    const r = await fetch("/estado");
    const d = await r.json();
    const ahora = document.getElementById("ahora");
    if (ahora && d.ahora) ahora.textContent = d.ahora;
    const temp = document.getElementById("temp");
    if (temp && d.temp != null) temp.textContent = d.temp + " °C";
    const tempDif = document.getElementById("temp-dif");
    const deseada = 24;
    if (tempDif && d.temp != null) {
        const dif = d.temp - deseada;
        const signo = dif > 0 ? "+" : "";
        tempDif.textContent = " (" + signo + dif.toFixed(1) + " °C)";
        if (dif > 10) tempDif.style.color = "#c0392b";
        else if (dif < -10) tempDif.style.color = "#b8860b";
        else tempDif.style.color = "#1e7f4f";
    }
    const hum = document.getElementById("hum");
    if (hum && d.hum != null) hum.textContent = d.hum + " %";
    const img = document.getElementById("preview");
    if (img && d.preview_v && !img.src.endsWith("v=" + d.preview_v)) {
        img.src = "/foto/preview.jpg?v=" + d.preview_v;
    }
}
setInterval(refrescar, 3000);

async function actualizarReles() {
    try {
        const r = await fetch("/estado");
        const d = await r.json();
        document.getElementById("est-rele1").textContent = d.rele1;
        document.getElementById("est-rele2").textContent = d.rele2;
        document.getElementById("est-rele3").textContent = d.rele3;
        document.getElementById("est-rele4").textContent = d.rele4;
    } catch (e) { }
}
setInterval(actualizarReles, 1000);

document.querySelectorAll(".switch-input").forEach(function (sw) {
    sw.addEventListener("change", async function () {
        const url = sw.checked ? sw.dataset.on : sw.dataset.off;
        if (!url) return;

        await fetch(url, { method: "POST" });

        // Actualiza el texto ON/OFF que está al lado
        const section = sw.closest("section");
        const fuerte = section && section.querySelector("strong");
        if (fuerte) {
            fuerte.textContent = sw.checked ? "ON" : "OFF";
        }
    });
});
