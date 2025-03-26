function sendCommand() {
    let command = document.getElementById("commandInput").value;

    fetch("/execute", {
        method: "POST",
        body: JSON.stringify({ command: command }),
        headers: { "Content-Type": "application/json" }
    })
    .then(response => response.json())
    .then(data => {
        document.getElementById("parsedCommand").innerText = JSON.stringify(data.parsed_command, null, 2);
        document.getElementById("executionResult").innerText = data.execution_result;
    })
    .catch(error => console.error("Error:", error));
}

// Executes command when "Enter" is pressed
function handleKeyPress(event) {
    if (event.key === "Enter") {
        event.preventDefault();
        sendCommand();
    }
}
