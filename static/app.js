document.getElementById("loadBtn").addEventListener("click", async () => {
  const table = document.getElementById("myTable");

  try {
    const response = await fetch("http://10.0.30.3:5000/api/full_movies");
    const data = await response.json();
    const keys = Object.keys(data);
    const rowCount = Math.max(...keys.map((k) => data[k].length));

    let html = "<tr>" + keys.map((k) => `<th>${k}</th>`).join("") + "</tr>";

    data.forEach(movie => {
        const row = document.createElement("tr");
        Object.values(movie).forEach(text => {
            const cell = document.createElement("td");
            cell.textContent = text;
            row.appendChild(cell);
        });
        table.appendChild(row);
    });

  } catch (err) {
    document.getElementById("output").textContent = "Error: " + err.message;
  }
});
