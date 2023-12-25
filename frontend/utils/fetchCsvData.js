export async function fetchCsvData(url) {
    const response = await fetch(url);
    const text = await response.text();
    const lines = text.split("\n");
    
    // Exclude empty rows and the first row (header)
    const data = lines
        .filter(line => line.trim() !== "") // Exclude empty rows
        .slice(1) // Exclude the first row (header)
        .map(line => line.split(","));
    
    return data;
}