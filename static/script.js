async function generateDraft() {

    const timeline = document.getElementById("timeline").value;
    const severity = document.getElementById("severity").value;
    const tone = document.getElementById("tone").value;

    const btn = document.getElementById("generateBtn");

    btn.disabled = true;
    btn.innerText = "Generating...";

    document.getElementById("initial").innerText = "Generating...";
    document.getElementById("progress").innerText = "Generating...";
    document.getElementById("resolved").innerText = "Generating...";
    document.getElementById("summary").innerText = "Generating...";

    try {

        const response = await fetch("/generate", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                timeline,
                severity,
                tone
            })
        });

        const data = await response.json();

        document.getElementById("initial").innerText =
            data.initial;

        document.getElementById("progress").innerText =
            data.progress;

        document.getElementById("resolved").innerText =
            data.resolved;

        document.getElementById("summary").innerText =
            data.summary;

    }
    catch (error) {

        console.error(error);

        document.getElementById("initial").innerText =
            "Error generating update";

        document.getElementById("progress").innerText =
            "Error generating update";

        document.getElementById("resolved").innerText =
            "Error generating update";

        document.getElementById("summary").innerText =
            "Error generating summary";
    }

    btn.disabled = false;
    btn.innerText = "Generate";
}

function copyText(id) {

    const text =
        document.getElementById(id).innerText;

    navigator.clipboard.writeText(text);

    alert("Copied!");
}