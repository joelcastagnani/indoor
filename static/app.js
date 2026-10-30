document.addEventListener("DOMContentLoaded", () => {

    const fsLabel = document.getElementById("fs");
    const fsCheckbox = fsLabel ? fsLabel.querySelector("input") : null;

    async function refrescar() {
        const r = await fetch("/estado");
        const d = await r.json();

        // Datos generales de texto en la web
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

        // ==========================================
        // ACTUALIZACIÓN DE LA TARJETA VISUAL (PC)
        // ==========================================

        // Temperatura con 1 decimal (ej: 24.5)
        const cardTemp = document.getElementById("card-temp");
        if (cardTemp && d.temp != null) {
            cardTemp.textContent = parseFloat(d.temp).toFixed(2);
        }

        // Diferencia de temperatura estética al lado de los grados
        const cardTempDif = document.getElementById("card-temp-dif");
        if (cardTempDif && d.temp != null) {
            const dif = d.temp - deseada;
            const signo = dif > 0 ? "+" : "";
            cardTempDif.textContent = "(" + signo + dif.toFixed(1) + "°)";

            if (dif > 5) cardTempDif.style.color = "#ffeb3b"; // Amarillo alerta calor
            else if (dif < -5) cardTempDif.style.color = "#90caf9"; // Azul alerta frío
            else cardTempDif.style.color = "#ffffff"; // Blanco si está OK
        }

        // Humedad en la tarjeta
        const cardHum = document.getElementById("card-hum");
        if (cardHum && d.hum != null) cardHum.textContent = "Hum: " + d.hum + "%";

        // Hora y Fecha en la tarjeta
        const cardHora = document.getElementById("card-hora");
        const cardFecha = document.getElementById("card-fecha");
        if (d.ahora) {
            cardHora.textContent = d.ahora.length > 8 ? d.ahora.slice(-8, -3) : d.ahora;
            cardFecha.textContent = d.ahora.length > 10 ? d.ahora.slice(0, 10) : d.ahora;
        }

        const logEl = document.getElementById("log");
        if (logEl && d.log) logEl.textContent = d.log;
    }
    setInterval(refrescar, 3000);


    async function actualizarReles() {
        try {
            const r = await fetch("/estado");
            const d = await r.json();

            // Actualiza textos
            const map = {
                "est-rele1": d.rele1,
                "est-rele2": d.rele2,
                "est-rele3": d.rele3,
                "est-rele4": d.rele4,
                "auto-estado": d.auto
            };
            for (const id in map) {
                const el = document.getElementById(id);
                if (el) el.textContent = map[id];
            }

            // Sincroniza los switches (checkbox) con el estado real
            const switches = {
                "sw-rele1": d.rele1,
                "sw-rele2": d.rele2,
                "sw-rele3": d.rele3,
                "sw-rele4": d.rele4,
                "sw-auto": d.auto
            };
            for (const id in switches) {
                const sw = document.getElementById(id);
                if (sw) sw.checked = (switches[id] === "ON");
            }
        } catch (e) { }
    }
    setInterval(actualizarReles, 1000);


    document.querySelectorAll(".switch-input").forEach(function (sw) {
        sw.addEventListener("change", async function () {
            const url = sw.checked ? sw.dataset.on : sw.dataset.off;
            if (!url) return;

            await fetch(url, { method: "POST" });

            // Actualiza el texto ON/OFF que está al lado
            const container = sw.closest(".rele") || sw.closest("section");
            const fuerte = container && container.querySelector("strong");
            if (fuerte) {
                fuerte.textContent = sw.checked ? "ON" : "OFF";
            }
        });
    });


    if (fsCheckbox) {
        fsCheckbox.addEventListener("change", function () {
            const foto = document.getElementById("preview");
            const target = foto || document.documentElement;
            if (fsCheckbox.checked) {
                const rfs = target.requestFullscreen || target.webkitRequestFullscreen || target.mozRequestFullScreen || target.msRequestFullscreen;
                if (rfs) rfs.call(target);
            } else {
                if (document.exitFullscreen) document.exitFullscreen();
                else if (document.webkitExitFullscreen) document.webkitExitFullscreen();
            }
        });

        // Cuando salís con ESC, desmarca el checkbox
        document.addEventListener("fullscreenchange", function () {
            if (!document.fullscreenElement) {
                fsCheckbox.checked = false;
            }
        });
        document.addEventListener("webkitfullscreenchange", function () {
            if (!document.webkitFullscreenElement) {
                fsCheckbox.checked = false;
            }
        });
    }

});